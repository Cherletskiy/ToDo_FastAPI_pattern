import asyncpg
from dotenv import load_dotenv
import os
from app.logging_config import setup_logger


# Настройка логирования
logger = setup_logger(__name__)

# Загрузка переменных из .env
load_dotenv()

# Конфигурация пула соединений
DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}


pool = None


async def init_db_pool():
    """Функция для инициализации пула соединений"""
    global pool
    try:
        pool = await asyncpg.create_pool(**DATABASE_CONFIG)
        logger.info("Пул соединений успешно создан")
    except Exception as e:
        logger.error(f"Ошибка при создании пула соединений: {e}")
        raise


async def close_db_pool():
    """Функция для закрытия пула соединений"""
    global pool
    if pool:
        await pool.close()
        logger.info("Пул соединений закрыт")


async def init_db():
    """Функция для инициализации таблицы tasks"""
    async with pool.acquire() as connection:
        try:
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    due_date TIMESTAMP,
                    status VARCHAR(50) NOT NULL
                );
            """)
            logger.info("Таблица tasks успешно создана или уже существует")
        except Exception as e:
            logger.error(f"Ошибка при создании таблицы: {e}")
            raise