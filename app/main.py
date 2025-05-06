from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database.db import init_db_pool, close_db_pool, init_db
from app.logging_config import setup_logger


logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    logger.info("Запуск приложения")
    await init_db_pool()
    await init_db()
    yield
    logger.info("Остановка приложения")
    await close_db_pool()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    logger.info("Получен запрос на корневой маршрут")
    return {"message": "Test!"}