from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_async_session
from app.routes.auth import oauth2_scheme
from app.services.task_service import TaskService
from app.models.task import TaskCreate, TaskUpdate, TaskResponse
from app.services.auth_service import AuthService
from app.logging_config import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/tasks", tags=["tasks"])


async def get_current_user_and_session(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_async_session)
):
    user = await AuthService.get_current_user(token, session)
    return user, session


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    user_session: tuple = Depends(get_current_user_and_session)
) -> TaskResponse:
    user, session = user_session
    service = TaskService()
    try:
        task_id = await service.create_task(
            session=session,
            user_id=user.id,
            title=task.title,
            description=task.description,
            due_date=task.due_date,
            status=task.status
        )
        task_data = await service.get_task(session, task_id, user.id)
        if not task_data:
            logger.warning(f"Задача ID={task_id} не найдена для user_id={user.id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")
        logger.info(f"Маршрут: Задача создана, ID={task_id}, user_id={user.id}")
        return task_data
    except ValueError as e:
        logger.error(f"Ошибка создания задачи: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    user_session: tuple = Depends(get_current_user_and_session)
) -> TaskResponse:
    user, session = user_session
    service = TaskService()
    task = await service.get_task(session, task_id, user.id)
    if not task:
        logger.warning(f"Задача ID={task_id} не найдена для user_id={user.id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")
    logger.info(f"Маршрут: Задача получена, ID={task_id}, user_id={user.id}")
    return task


@router.get("/", response_model=list[TaskResponse])
async def get_tasks(
    status: str | None = None,
    due_date: datetime | None = None,
    user_session: tuple = Depends(get_current_user_and_session)
) -> list[TaskResponse]:
    user, session = user_session
    service = TaskService()
    tasks = await service.get_tasks(session, user.id, status, due_date)
    logger.info(f"Маршрут: Получено {len(tasks)} задач для user_id={user.id}")
    return tasks


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task: TaskUpdate,
    user_session: tuple = Depends(get_current_user_and_session)
) -> TaskResponse:
    user, session = user_session
    service = TaskService()
    try:
        success = await service.update_task(
            session=session,
            user_id=user.id,
            task_id=task_id,
            title=task.title,
            description=task.description,
            due_date=task.due_date,
            status=task.status
        )
        if not success:
            logger.warning(f"Задача ID={task_id} не найдена для user_id={user.id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")
        task_data = await service.get_task(session, task_id, user.id)
        if not task_data:
            logger.warning(f"Задача ID={task_id} не найдена после обновления для user_id={user.id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")
        logger.info(f"Маршрут: Задача обновлена, ID={task_id}, user_id={user.id}")
        return task_data
    except ValueError as e:
        logger.error(f"Ошибка обновления задачи: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    user_session: tuple = Depends(get_current_user_and_session)
) -> None:
    user, session = user_session
    service = TaskService()
    success = await service.delete_task(session, user.id, task_id)
    if not success:
        logger.warning(f"Задача ID={task_id} не найдена для user_id={user.id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")
    logger.info(f"Маршрут: Задача удалена, ID={task_id}, user_id={user.id}")