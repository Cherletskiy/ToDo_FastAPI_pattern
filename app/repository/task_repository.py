from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, DataError
from datetime import datetime

from app.database.models import Task
from app.logging_config import setup_logger

logger = setup_logger(__name__)


class TaskRepository:
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
        try:
            if due_date is not None and due_date.tzinfo is not None:
                due_date = due_date.replace(tzinfo=None)
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
        query = select(Task).filter_by(id=task_id, user_id=user_id)
        result = await self.session.execute(query)
        task = result.scalars().first()
        if task:
            logger.debug(f"Задача ID={task_id} найдена для user_id={user_id}")
        else:
            logger.debug(f"Задача ID={task_id} не найдена для user_id={user_id}")
        return task

    async def get_tasks(
        self,
        user_id: int,
        status: str | None = None,
        due_date: datetime | None = None
    ) -> list[Task]:
        query = select(Task).filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
        if due_date:
            if due_date.tzinfo is not None:
                due_date = due_date.replace(tzinfo=None)
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
        query = select(Task).filter_by(id=task_id, user_id=user_id)
        result = await self.session.execute(query)
        task = result.scalars().first()
        if not task:
            logger.warning(f"Задача ID={task_id} не найдена для user_id={user_id}")
            return False

        updates = {}
        if title is not None:
            task.title = title
            updates["title"] = title
        if description is not None:
            task.description = description
            updates["description"] = description
        if due_date is not None:
            if due_date.tzinfo is not None:
                due_date = due_date.replace(tzinfo=None)
            task.due_date = due_date
            updates["due_date"] = due_date
        if status is not None:
            task.status = status
            updates["status"] = status
        logger.info(f"Задача ID={task_id} обновлена: {updates}")
        await self.session.flush()
        return True

    async def delete_task(self, user_id: int, task_id: int) -> bool:
        query = select(Task).filter_by(id=task_id, user_id=user_id)
        result = await self.session.execute(query)
        task = result.scalars().first()
        if not task:
            logger.warning(f"Задача ID={task_id} не найдена для user_id={user_id}")
            return False

        await self.session.delete(task)
        await self.session.flush()
        logger.info(f"Задача ID={task_id} удалена для user_id={user_id}")
        return True