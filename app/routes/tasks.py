from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.services.task_service import TaskService
from app.models.task import TaskCreate, TaskUpdate, TaskResponse
from asyncpg import Pool
from app.logging_config import setup_logger
from datetime import datetime
from typing import List
from pydantic import ValidationError


# Настройка логирования
logger = setup_logger(__name__)

# Создание роутера
router = APIRouter(prefix="/tasks", tags=["Tasks"])


async def get_db_pool(request: Request) -> Pool:
    """Зависимость для получения пула соединений из состояния приложения"""
    pool = request.app.state.pool
    if pool is None:
        logger.error("Пул соединений не инициализирован")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Пул соединений не инициализирован")
    return pool


def get_task_service(db_pool: Pool = Depends(get_db_pool)) -> TaskService:
    """Зависимость для получения TaskService с пулом соединений"""
    return TaskService(db_pool)


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate, service: TaskService = Depends(get_task_service)):
    """Создание новой задачи.
    Вызывает service.create_task и возвращает созданную задачу как TaskResponse
    Статус ответа: 201 Created"""
    logger.info(f"Создание задачи: {task.model_dump()}")
    try:
        task_id = await service.create_task(
            title=task.title,
            description=task.description,
            due_date=task.due_date,
            status=task.status
        )
        task_dict = await service.get_task(task_id)
        return TaskResponse(**task_dict)
    except ValueError as e:
        logger.error(f"Ошибка при создании задачи: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Неизвестная ошибка при создании задачи: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Внутренняя ошибка сервера")


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, service: TaskService = Depends(get_task_service)):
    """Получение задачи по ID. Вызывает service.get_task и возвращает задачу как TaskResponse"""
    logger.info(f"Запрос задачи с id={task_id}")
    try:
        task = await service.get_task(task_id)
        return TaskResponse(**task)
    except ValueError as e:
        logger.error(f"Ошибка при получении задачи: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Неизвестная ошибка при получении задачи: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Внутренняя ошибка сервера")


@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    task_status: str | None = None,
    due_date: datetime | None = None,
    service: TaskService = Depends(get_task_service)
):
    """Получение списка задач с фильтрацией. Вызывает service.get_tasks
    Принимает необязательные query-параметры status и due_date
    Возвращает список задач как List[TaskResponse]"""
    logger.info(f"Запрос списка задач с фильтрами status={task_status}, due_date={due_date}")
    try:
        tasks = await service.get_tasks(status=task_status, due_date=due_date)
        return [TaskResponse(**task) for task in tasks]
    except ValueError as e:
        logger.error(f"Ошибка при получении списка задач: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Неизвестная ошибка при получении списка задач: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Внутренняя ошибка сервера")


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task: TaskUpdate, service: TaskService = Depends(get_task_service)):
    """Обновление задачи. Принимает task_id и TaskUpdate для частичного обновления.
    Вызывает service.update_task и возвращает обновленную задачу как TaskResponse."""
    logger.info(f"Обновление задачи с id={task_id}: {task.model_dump()}")
    try:
        updated = await service.update_task(
            task_id=task_id,
            title=task.title,
            description=task.description,
            due_date=task.due_date,
            status=task.status
        )
        if not updated:
            logger.error(f"Задача с id={task_id} не найдена")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Задача с id={task_id} не найдена")
        task_dict = await service.get_task(task_id)
        if task_dict is None:
            logger.error(f"Задача с id={task_id} не найдена после обновления")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Задача с id={task_id} не найдена")
        return TaskResponse(**task_dict)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Неизвестная ошибка при обновлении задачи: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Внутренняя ошибка сервера")


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, service: TaskService = Depends(get_task_service)):
    """Удаление задачи. Вызывает service.delete_task и возвращает статус 204 No Content."""
    logger.info(f"Удаление задачи с id={task_id}")
    try:
        deleted = await service.delete_task(task_id)
        if not deleted:
            logger.error(f"Задача с id={task_id} не найдена")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Задача с id={task_id} не найдена")
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Неизвестная ошибка при удалении задачи: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Внутренняя ошибка сервера")