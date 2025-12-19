from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Task
from app.logging_config import setup_logger
from app.repository.task_repository import TaskRepository

# Настройка логирования
logger = setup_logger(__name__)


class TaskService:
    """Сервис для обработки бизнес-логики задач"""

    async def create_task(
        self,
        session: AsyncSession,
        user_id: int,
        title: str,
        description: str | None,
        due_date: datetime | None,
        status: str,
    ) -> int:
        repo = TaskRepository(session)
        task_id = await repo.create_task(
            user_id=user_id,
            title=title,
            description=description,
            due_date=due_date,
            status=status,
        )
        logger.info(f"Сервис: Задача создана, ID={task_id}")
        return task_id

    async def get_task(
        self, session: AsyncSession, task_id: int, user_id: int
    ) -> Task | None:
        """Получить задачу по ID"""
        repo = TaskRepository(session)
        task = await repo.get_task(task_id, user_id)
        logger.debug(
            f"Сервис: Запрос задачи ID={task_id}, {'найдена' if task else 'не найдена'}"
        )
        return task

    async def get_tasks(
        self,
        session: AsyncSession,
        user_id: int,
        status: str | None = None,
        due_date: datetime | None = None,
    ) -> list[Task]:
        """Получить список задач с фильтрацией"""
        repo = TaskRepository(session)
        tasks = await repo.get_tasks(user_id, status, due_date)
        logger.info(f"Сервис: Получено {len(tasks)} задач для user_id={user_id}")
        return tasks

    async def update_task(
        self,
        session: AsyncSession,
        user_id: int,
        task_id: int,
        title: str | None = None,
        description: str | None = None,
        due_date: datetime | None = None,
        status: str | None = None,
    ) -> bool:
        """Обновить задачу"""
        repo = TaskRepository(session)
        try:
            success = await repo.update_task(
                user_id=user_id,
                task_id=task_id,
                title=title,
                description=description,
                due_date=due_date,
                status=status,
            )
            logger.info(
                f"Сервис: Задача ID={task_id} {'обновлена' if success else 'не найдена'}"
            )
            return success
        except ValueError as e:
            logger.error(f"Сервис: Ошибка обновления задачи: {e}")
            raise ValueError(f"Не удалось обновить задачу: {str(e)}")

    async def delete_task(
        self, session: AsyncSession, user_id: int, task_id: int
    ) -> bool:
        """Удалить задачу"""
        repo = TaskRepository(session)
        success = await repo.delete_task(user_id, task_id)
        logger.info(
            f"Сервис: Задача ID={task_id} {'удалена' if success else 'не найдена'}"
        )
        return success

    async def update_overdue_tasks(self, session: AsyncSession, user_id: int):
        """Обновить статус просроченных задач на 'overdue'"""
        try:
            current_time = datetime.utcnow()

            # Получаем все задачи пользователя со статусом "not_started" или "in_progress",
            # у которых due_date в прошлом
            query = select(Task).where(
                Task.user_id == user_id,
                Task.status.in_(["not_started", "in_progress"]),
                Task.due_date.isnot(None),
                Task.due_date < current_time,
            )

            result = await session.execute(query)
            overdue_tasks = result.scalars().all()

            if not overdue_tasks:
                return 0

            # Обновляем статус для каждой просроченной задачи
            updated_count = 0
            for task in overdue_tasks:
                task.status = "overdue"
                updated_count += 1

            await session.flush()

            logger.info(
                f"Обновлено {updated_count} просроченных задач для пользователя {user_id}"
            )
            return updated_count
        except Exception as e:
            logger.error(f"Ошибка при обновлении просроченных задач: {e}")
            return 0
