from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routes.tasks import router as tasks_router
from app.database.db import init_db_pool, init_db, close_db_pool
from app.logging_config import setup_logger


# Настройка логирования
logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    logger.info("Запуск приложения: инициализация пула соединений")
    app.state.pool = await init_db_pool()
    await init_db(app.state.pool)
    logger.info("Приложение запущено")

    try:
        yield
    finally:
        logger.info("Остановка приложения: закрытие пула соединений")
        await close_db_pool(app.state.pool)
        logger.info("Приложение остановлено")


# Создание приложения
app = FastAPI(
    title="ToDo API",
    description="API для управления задачами",
    version="1.0.0",
    lifespan=lifespan
)

# Подключение роутера
app.include_router(tasks_router)