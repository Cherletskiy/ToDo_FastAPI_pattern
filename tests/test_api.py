import asyncio
import logging
from datetime import datetime, timedelta
import pytz
import httpx
from app.logging_config import setup_logger
import asyncpg


# Настройка логирования
logger = setup_logger(__name__)

BASE_URL = "http://127.0.0.1:8000"


async def clear_tasks():
    """Очистка таблицы tasks перед тестами."""
    dsn = "postgresql://postgres:postgres@localhost:5432/ToDo"
    try:
        conn = await asyncpg.connect(dsn)
        await conn.execute("TRUNCATE TABLE tasks RESTART IDENTITY")
        logger.info("Таблица tasks очищена перед тестами")
        await conn.close()
    except Exception as e:
        logger.error(f"Ошибка при очистке базы данных: {e}")
        raise


async def test_api():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # Очистка базы перед тестами
        await clear_tasks()

        # Тест 1: Создание задачи с полными данными
        due_date = (datetime.now(pytz.UTC) + timedelta(days=1)).replace(microsecond=0)
        task_data = {
            "title": "Тестовая задача",
            "description": "Описание тестовой задачи",
            "due_date": due_date.isoformat(),
            "status": "pending"
        }
        logger.info("Создание тестовой задачи с полными данными")
        response = await client.post("/tasks/", json=task_data)
        assert response.status_code == 201, f"Ожидался код 201, получен {response.status_code}"
        task = response.json()
        assert task["title"] == task_data["title"]
        assert task["description"] == task_data["description"]
        assert task["status"] == task_data["status"]
        logger.info(f"Задача создана: {task}")

        # Тест 2: Создание задачи с минимальными данными
        minimal_task = {"title": "Минимальная задача", "status": "pending"}
        logger.info("Создание задачи с минимальными данными")
        response = await client.post("/tasks/", json=minimal_task)
        assert response.status_code == 201
        minimal_task_response = response.json()
        assert minimal_task_response["title"] == minimal_task["title"]
        assert minimal_task_response["description"] is None
        assert minimal_task_response["due_date"] is None
        logger.info(f"Минимальная задача создана: {minimal_task_response}")

        # Тест 3: Получение задачи по id
        task_id = task["id"]
        logger.info(f"Получение задачи с id={task_id}")
        response = await client.get(f"/tasks/{task_id}")
        assert response.status_code == 200
        task_fetched = response.json()
        assert task_fetched["id"] == task_id
        assert task_fetched["title"] == task["title"]
        logger.info(f"Задача получена: {task_fetched}")

        # Тест 4: Получение списка задач с фильтром по статусу
        logger.info("Получение списка задач с фильтром task_status=pending")
        response = await client.get("/tasks/", params={"task_status": "pending"})
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) >= 2
        assert all(t["status"] == "pending" for t in tasks)
        logger.info(f"Список задач: {tasks}")

        # Тест 5: Получение списка всех задач
        logger.info("Получение списка задач без фильтров")
        response = await client.get("/tasks/")
        assert response.status_code == 200
        all_tasks = response.json()
        assert len(all_tasks) >= 2
        logger.info(f"Список всех задач: {all_tasks}")

        # Тест 6: Попытка получения списка задач с невалидным статусом
        logger.info("Получение списка задач с невалидным task_status 'lo'")
        response = await client.get("/tasks/", params={"task_status": "lo"})
        assert response.status_code == 400, f"Ожидался код 400, получен {response.status_code}"
        logger.info(f"Ожидаемая ошибка: {response.json()}")

        # Тест 7: Обновление задачи
        update_data = {
            "title": "Обновлённая задача",
            "description": "Обновлённое описание",
            "due_date": (datetime.now(pytz.UTC) + timedelta(days=2)).replace(microsecond=0).isoformat(),
            "status": "pending"
        }
        logger.info(f"Обновление задачи с id={task_id}")
        response = await client.patch(f"/tasks/{task_id}", json=update_data)
        assert response.status_code == 200
        updated_task = response.json()
        assert updated_task["title"] == update_data["title"]
        assert updated_task["description"] == update_data["description"]
        logger.info(f"Задача обновлена: {updated_task}")

        # Тест 8: Частичное обновление задачи
        partial_update = {"status": "completed"}
        logger.info(f"Обновление задачи с id={task_id} только по статусу")
        response = await client.patch(f"/tasks/{task_id}", json=partial_update)
        assert response.status_code == 200
        partial_updated_task = response.json()
        assert partial_updated_task["status"] == partial_update["status"]
        logger.info(f"Задача частично обновлена: {partial_updated_task}")

        # Тест 9: Попытка обновления с датой в прошлом
        past_due_date = (datetime.now(pytz.UTC) - timedelta(days=2)).replace(microsecond=0).isoformat()
        invalid_update = {
            "title": "string",
            "description": "string",
            "due_date": past_due_date,
            "status": "pending"
        }
        logger.info(f"Обновление задачи с id={task_id} с датой в прошлом")
        response = await client.patch(f"/tasks/{task_id}", json=invalid_update)
        assert response.status_code == 422, f"Ожидался код 422, получен {response.status_code}"
        logger.info(f"Ожидаемая ошибка валидации даты: {response.json()}")

        # Тест 10: Обновление несуществующей задачи
        logger.info("Обновление несуществующей задачи с id=999")
        response = await client.patch(f"/tasks/999", json=update_data)
        assert response.status_code == 404, f"Ожидался код 404, получен {response.status_code}"
        logger.info(f"Ожидаемая ошибка: {response.json()}")

        # Тест 11: Попытка обновления с невалидными данными
        invalid_update_data = {"title": "", "status": "invalid"}
        logger.info(f"Обновление задачи с id={task_id} с невалидными данными")
        response = await client.patch(f"/tasks/{task_id}", json=invalid_update_data)
        assert response.status_code == 422, f"Ожидался код 422, получен {response.status_code}"
        logger.info(f"Ожидаемая ошибка валидации: {response.json()}")

        # Тест 12: Попытка создания задачи с просроченной датой
        logger.info("Создание задачи с просроченной датой")
        overdue_task = {
            "title": "Просроченная задача",
            "due_date": (datetime.now(pytz.UTC) - timedelta(days=1)).replace(microsecond=0).isoformat(),
            "status": "pending"
        }
        response = await client.post("/tasks/", json=overdue_task)
        assert response.status_code == 422, f"Ожидался код 422, получен {response.status_code}"
        logger.info(f"Ожидаемая ошибка валидации даты при создании: {response.json()}")

        # Тест 13: Удаление задачи
        logger.info(f"Удаление задачи с id={task_id}")
        response = await client.delete(f"/tasks/{task_id}")
        assert response.status_code == 204, f"Ожидался код 204, получен {response.status_code}"
        logger.info("Задача удалена")

        # Тест 14: Удаление минимальной задачи
        minimal_task_id = minimal_task_response["id"]
        logger.info(f"Удаление минимальной задачи с id={minimal_task_id}")
        response = await client.delete(f"/tasks/{minimal_task_id}")
        assert response.status_code == 204, f"Ожидался код 204, получен {response.status_code}"
        logger.info("Минимальная задача удалена")

        # Тест 15: Удаление несуществующей задачи
        logger.info("Удаление несуществующей задачи с id=999")
        response = await client.delete(f"/tasks/999")
        assert response.status_code == 404, f"Ожидался код 404, получен {response.status_code}"
        logger.info(f"Ожидаемая ошибка: {response.json()}")

        # Тест 16: Попытка создания задачи с пустым title
        logger.info("Попытка создания задачи с пустым title")
        response = await client.post("/tasks/", json={"title": "", "description": "Описание", "status": "pending"})
        assert response.status_code == 422, f"Ожидался код 422, получен {response.status_code}"
        logger.info(f"Ожидаемая ошибка: {response.json()}")

        # Тест 17: Попытка создания задачи с невалидным статусом
        logger.info("Попытка создания задачи с невалидным status")
        response = await client.post("/tasks/", json={"title": "Задача", "status": "invalid"})
        assert response.status_code == 422, f"Ожидался код 422, получен {response.status_code}"
        logger.info(f"Ожидаемая ошибка валидации статуса: {response.json()}")

        # Тест 18: Попытка получения несуществующей задачи
        logger.info("Получение задачи с несуществующим id=999")
        response = await client.get("/tasks/999")
        assert response.status_code == 404, f"Ожидался код 404, получен {response.status_code}"
        logger.info(f"Ожидаемая ошибка: {response.json()}")

        # Тест 19: Попытка обновления с пустым title
        # Создаём задачу для теста
        temp_task = {"title": "Временная задача", "status": "pending"}
        response = await client.post("/tasks/", json=temp_task)
        assert response.status_code == 201
        temp_task_id = response.json()["id"]
        logger.info(f"Попытка обновления задачи с id={temp_task_id} с пустым title")
        response = await client.patch(f"/tasks/{temp_task_id}", json={"title": ""})
        assert response.status_code == 422, f"Ожидался код 422, получен {response.status_code}"
        logger.info(f"Ожидаемая ошибка: {response.json()}")

        # Тест 20: Фильтрация задач по due_date
        due_date_filter = (datetime.now(pytz.UTC) + timedelta(days=1)).replace(microsecond=0)
        task_with_due_date = {
            "title": "Задача с due_date",
            "due_date": due_date_filter.isoformat(),
            "status": "pending"
        }
        logger.info("Создание задачи для проверки фильтра по due_date")
        response = await client.post("/tasks/", json=task_with_due_date)
        assert response.status_code == 201
        logger.info(f"Задача для фильтра создана: {response.json()}")
        logger.info("Получение списка задач с фильтром по due_date")
        response = await client.get("/tasks/", params={"due_date": due_date_filter.isoformat()})
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) >= 1
        due_date_naive = due_date_filter.replace(tzinfo=None).isoformat()
        assert any(t["due_date"] == due_date_naive for t in tasks)
        logger.info(f"Список задач с фильтром due_date: {tasks}")


if __name__ == "__main__":
    asyncio.run(test_api())