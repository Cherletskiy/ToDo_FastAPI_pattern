from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, DataError
from datetime import datetime

from app.database.models import Task
from app.logging_config import setup_logger

# Настройка логирования
logger = setup_logger(__name__)


class TaskRepository:
    """Репозиторий для работы с задачами в базе данных"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_task(
        self,
        user_id: int,
        title: str,
        description: str | None = None,
        due_date: datetime | None = None,
        status: str = "not_started"
    ) -> int:
        """Создать новую задачу"""
        try:
            async with self.session.begin():
                task = Task(
                    user_id=user_id,
                    title=title,
                    description=description,
                    due_date=due_date,
                    status=status
                )
                self.session.add(task)
                await self.session.flush()
                task_id = task.id
                logger.info(f"Задача создана: ID={task_id}, user_id={user_id}, title={title}")
                return task_id
        except (IntegrityError, DataError) as e:
            logger.error(f"Ошибка создания задачи: {e}")
            raise ValueError(f"Ошибка создания задачи: {str(e)}")

    async def get_task(self, task_id: int, user_id: int) -> Task | None:
        """Получить задачу по ID, если она принадлежит пользователю"""
        query = select(Task).filter_by(id=task_id, user_id=user_id)
        result = await self.session.execute(query)
        task = result.scalars().first()
        logger.debug(f"Поиск задачи ID={task_id} для user_id={user_id}: {'найдена' if task else 'не найдена'}")
        return task

    async def get_tasks(
        self,
        user_id: int,
        status: str | None = None,
        due_date: datetime | None = None
    ) -> list[Task]:
        """Получить список задач пользователя с фильтрацией"""
        query = select(Task).filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
        if due_date:
            query = query.filter(Task.due_date <= due_date)
        result = await self.session.execute(query)
        tasks = result.scalars().all()
        logger.info(f"Получено {len(tasks)} задач для user_id={user_id}")
        return tasks

    async def update_task(
        self,
        user_id: int,
        task_id: int,
        title: str | None = None,
        description: str | None = None,
        due_date: datetime | None = None,
        status: str | None = None
    ) -> bool:
        """Обновить задачу, если она принадлежит пользователю"""
        query = select(Task).filter_by(id=task_id, user_id=user_id)
        result = await self.session.execute(query)
        task = result.scalars().first()
        if not task:
            logger.warning(f"Задача ID={task_id} не найдена для user_id={user_id}")
            return False

        async with self.session.begin():
            updates = {}
            if title is not None:
                task.title = title
                updates["title"] = title
            if description is not None:
                task.description = description
                updates["description"] = description
            if due_date is not None:
                task.due_date = due_date
                updates["due_date"] = due_date
            if status is not None:
                task.status = status
                updates["status"] = status
            logger.info(f"Задача ID={task_id} обновлена: {updates}")
            return True

    async def delete_task(self, user_id: int, task_id: int) -> bool:
        """Удалить задачу, если она принадлежит пользователю"""
        query = select(Task).filter_by(id=task_id, user_id=user_id)
        result = await self.session.execute(query)
        task = result.scalars().first()
        if not task:
            logger.warning(f"Задача ID={task_id} не найдена для user_id={user_id}")
            return False

        async with self.session.begin():
            await self.session.delete(task)
            logger.info(f"Задача ID={task_id} удалена для user_id={user_id}")
            return True