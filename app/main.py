from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.routes.tasks import router as tasks_router
from app.routes.auth import router as auth_router
from app.database.db import init_db, close_db
from app.logging_config import setup_logger


# Настройка логирования
logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    logger.info("Запуск приложения: инициализация БД")
    await init_db()
    logger.info("Приложение запущено")

    try:
        yield
    finally:
        logger.info("Остановка приложения: закрытие БД")
        await close_db()
        logger.info("Приложение остановлено")


# Создание приложения
app = FastAPI(
    title="ToDo API",
    description="API для управления задачами",
    version="1.0.0",
    lifespan=lifespan
)

# Подключение роутеров
# app.include_router(tasks_router)
app.include_router(auth_router)
