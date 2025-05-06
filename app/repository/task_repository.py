import asyncpg
from datetime import datetime
from app.logging_config import setup_logger

# Настройка логирования
logger = setup_logger(__name__)


class TaskRepository:
    """Репозиторий для работы с задачами в базе данных"""

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create_task(self, title: str, description: str | None, due_date: datetime | None, status: str) -> int:
        """Создание новой задачи"""
        async with self.pool.acquire() as connection:
            try:
                query = """
                    INSERT INTO tasks (title, description, due_date, status)
                    VALUES ($1, $2, $3, $4)
                    RETURNING id;
                """
                task_id = await connection.fetchval(query, title, description, due_date, status)
                logger.info(f"Задача успешно создана. ID = {task_id}")
                return task_id
            except Exception as e:
                logger.error(f"Ошибка при создании задачи: {e}")
                raise

    async def get_task(self, task_id: int) -> dict | None:
        """Получение задачи по ID"""
        async with self.pool.acquire() as connection:
            try:
                query = """
                    SELECT id, title, description, created_at, due_date, status
                    FROM tasks
                    WHERE id = $1;
                """
                task = await connection.fetchrow(query, task_id)
                if task:
                    logger.info(f"Получена задача с id={task_id}")
                    return dict(task)
                logger.warning(f"Задача с id={task_id} не найдена")
                return None
            except Exception as e:
                logger.error(f"Ошибка при получении задачи id={task_id}: {e}")
                raise

    async def get_tasks(self, status: str | None = None, due_date: datetime | None = None) -> list[dict]:
        """Получение списка задач с фильтрацией по статусу и сроку"""
        async with self.pool.acquire() as connection:
            try:
                query = """
                    SELECT id, title, description, created_at, due_date, status
                    FROM tasks
                    WHERE 1=1
                """
                params = []
                if status:
                    query += " AND status = $1"
                    params.append(status)
                if due_date:
                    query += f" AND due_date <= ${len(params) + 1}"
                    params.append(due_date)

                tasks = await connection.fetch(query, *params)
                tasks_list = [dict(task) for task in tasks]
                logger.info(f"Получено {len(tasks_list)} задач с фильтрами status={status}, due_date={due_date}")
                return tasks_list
            except Exception as e:
                logger.error(f"Ошибка при получении списка задач: {e}")
                raise

    async def update_task(self, task_id: int, title: str | None = None, description: str | None = None,
                         due_date: datetime | None = None, status: str | None = None) -> bool:
        """Обновление задачи"""
        async with self.pool.acquire() as connection:
            try:
                updates = []
                params = []
                param_index = 1

                if title is not None:
                    updates.append(f"title = ${param_index}")
                    params.append(title)
                    param_index += 1
                if description is not None:
                    updates.append(f"description = ${param_index}")
                    params.append(description)
                    param_index += 1
                if due_date is not None:
                    updates.append(f"due_date = ${param_index}")
                    params.append(due_date)
                    param_index += 1
                if status is not None:
                    updates.append(f"status = ${param_index}")
                    params.append(status)
                    param_index += 1

                if not updates:
                    logger.warning(f"Нет данных для обновления задачи id={task_id}")
                    return False

                params.append(task_id)
                query = f"""
                    UPDATE tasks
                    SET {', '.join(updates)}
                    WHERE id = ${param_index}
                    RETURNING id;
                """
                result = await connection.fetchval(query, *params)
                if result:
                    logger.info(f"Обновлена задача с id={task_id}")
                    return True
                logger.warning(f"Задача с id={task_id} не найдена для обновления")
                return False
            except Exception as e:
                logger.error(f"Ошибка при обновлении задачи id={task_id}: {e}")
                raise

    async def delete_task(self, task_id: int) -> bool:
        """Удаление задачи"""
        async with self.pool.acquire() as connection:
            try:
                query = """
                    DELETE FROM tasks
                    WHERE id = $1
                    RETURNING id;
                """
                result = await connection.fetchval(query, task_id)
                if result:
                    logger.info(f"Удалена задача с id={task_id}")
                    return True
                logger.warning(f"Задача с id={task_id} не найдена для удаления")
                return False
            except Exception as e:
                logger.error(f"Ошибка при удалении задачи id={task_id}: {e}")
                raise