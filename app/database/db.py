import asyncpg
from dotenv import load_dotenv
import os
from app.logging_config import setup_logger


# Настройка логирования
logger = setup_logger(__name__)

# Загрузка переменных окружения
load_dotenv()

DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}


async def init_db_pool() -> asyncpg.Pool:
    """Инициализация пула соединений с базой данных"""
    try:
        pool = await asyncpg.create_pool(**DATABASE_CONFIG)
        logger.info("Пул соединений успешно создан")
        return pool
    except Exception as e:
        logger.error(f"Ошибка при создании пула соединений: {e}")
        raise


async def init_db(pool: asyncpg.Pool):
    """Инициализация базы данных и создание таблицы tasks"""
    async with pool.acquire() as connection:
        try:
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    due_date TIMESTAMP,
                    status VARCHAR(20) NOT NULL
                )
            """)
            logger.info("Таблица tasks успешно создана или уже существует")
        except Exception as e:
            logger.error(f"Ошибка при создании таблицы: {e}")
            raise


async def close_db_pool(pool: asyncpg.Pool):
    """Закрытие пула соединений"""
    try:
        await pool.close()
        logger.info("Пул соединений закрыт")
    except Exception as e:
        logger.error(f"Ошибка при закрытии пула соединений: {e}")
        raise