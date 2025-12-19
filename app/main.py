from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.routes.tasks import router as tasks_router
from app.routes.auth import router as auth_router
from app.database.db import init_db, close_db
from app.logging_config import setup_logger

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request


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

# Настройка шаблонов и статики
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Подключение роутеров
app.include_router(tasks_router)
app.include_router(auth_router)
