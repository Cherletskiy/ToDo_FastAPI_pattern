import asyncpg
from datetime import datetime
from app.repository.task_repository import TaskRepository
from app.logging_config import setup_logger

# Настройка логирования
logger = setup_logger(__name__)


class TaskService:
    """Сервис для обработки бизнес-логики задач"""

    def __init__(self, pool: asyncpg.Pool):
        """Инициализация сервиса с пулом соединений и репозиторием"""
        self.repository = TaskRepository(pool)

    async def create_task(self, title: str, description: str | None, due_date: datetime | None, status: str) -> int:
        """Создание новой задачи с валидацией.
        Работа с репозиторием repository.create_task.
        :param title: Название задачи.
        :param description: Описание задачи. Опционально.
        :param due_date: Срок выполнения задачи. Опционально.
        :param status: Статус задачи. Опционально.
        Валидация:
        - Проверяет, что title не пустой и не состоит только из пробелов.
        - Проверяет, что status — один из допустимых (pending, completed, overdue).
        :return: id созданной задачи"""

        if not title or not title.strip():
            logger.error("Название задачи не может быть пустым")
            raise ValueError("Название задачи не может быть пустым")

        if status not in ["pending", "completed", "overdue"]:
            logger.error(f"Недопустимый статус: {status}")
            raise ValueError("Статус должен быть 'pending', 'completed' или 'overdue'")

        logger.info(f"Создание задачи: title={title}, status={status}")
        task_id = await self.repository.create_task(title, description, due_date, status)
        logger.info(f"Задача создана с id={task_id}")
        return task_id

    async def get_task(self, task_id: int) -> dict | None:
        """Получение задачи по ID. Работа с репозиторием repository.get_task.
        :param task_id: ID задачи.
        :return: Задача в виде словаря или None (+ ValueError), если задача не найдена."""

        logger.info(f"Запрос задачи с id={task_id}")
        task = await self.repository.get_task(task_id)
        if not task:
            logger.warning(f"Задача с id={task_id} не найдена")
            raise ValueError(f"Задача с id={task_id} не найдена")
        return task

    async def get_tasks(self, status: str | None = None, due_date: datetime | None = None) -> list[dict]:
        """Получение списка задач с фильтрацией.
        Работа с репозиторием repository.get_tasks.
        :param status: Статус задачи. Опционально.
        :param due_date: Срок выполнения задачи. Опционально.
        Валидация:
        - Проверяет, что status — один из допустимых (pending, completed, overdue).
        :return: Список задач в виде списка словарей."""

        if status and status not in ["pending", "completed", "overdue"]:
            logger.error(f"Недопустимый статус для фильтра: {status}")
            raise ValueError("Статус должен быть 'pending', 'completed' или 'overdue'")

        logger.info(f"Запрос списка задач с фильтрами status={status}, due_date={due_date}")
        tasks = await self.repository.get_tasks(status, due_date)
        logger.info(f"Получено {len(tasks)} задач")
        return tasks

    async def update_task(self, task_id: int, title: str | None = None, description: str | None = None,
                         due_date: datetime | None = None, status: str | None = None) -> bool:
        """Обновление задачи с валидацией. Работа с репозиторием repository.update_task.
        :param task_id: ID задачи.
        :param title: Название задачи. Опционально.
        :param description: Описание задачи. Опционально.
        :param due_date: Срок выполнения задачи. Опционально.
        :param status: Статус задачи. Опционально.
        Валидация:
        - Проверяет, что title не пустой и не состоит только из пробелов.
        - Проверяет, что status — один из допустимых (pending, completed, overdue).
        :return: True, если задача обновлена, False, если задача не обновлена (+ ValueError), если задача не найдена."""

        if title is not None and not title.strip():
            logger.error("Название задачи не может быть пустым")
            raise ValueError("Название задачи не может быть пустым")

        if status and status not in ["pending", "completed", "overdue"]:
            logger.error(f"Недопустимый статус: {status}")
            raise ValueError("Статус должен быть 'pending', 'completed' или 'overdue'")

        logger.info(f"Обновление задачи с id={task_id}")
        updated = await self.repository.update_task(task_id, title, description, due_date, status)
        if not updated:
            logger.warning(f"Задача с id={task_id} не найдена для обновления")
            raise ValueError(f"Задача с id={task_id} не найдена")
        logger.info(f"Задача с id={task_id} обновлена")
        return updated

    async def delete_task(self, task_id: int) -> bool:
        """Удаление задачи. Работа с репозиторием repository.delete_task.
        :param task_id: ID задачи.
        :return: True, если задача удалена, False, если задача не удалена (+ ValueError), если задача не найдена."""

        logger.info(f"Удаление задачи с id={task_id}")
        deleted = await self.repository.delete_task(task_id)
        if not deleted:
            logger.warning(f"Задача с id={task_id} не найдена для удаления")
            raise ValueError(f"Задача с id={task_id} не найдена")
        logger.info(f"Задача с id={task_id} удалена")
        return deleted