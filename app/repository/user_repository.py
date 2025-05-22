from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User
from app.logging_config import setup_logger


# Настройка логирования
logger = setup_logger(__name__)


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_email(self, email: str) -> User | None:
        async with self.session.begin():
            result = await self.session.execute(select(User).filter_by(email=email))
            user = result.scalars().first()
            logger.debug(f"Поиск пользователя по email {email}: {'найден' if user else 'не найден'}")
            return user

    async def get_user_by_id(self, user_id: int) -> User | None:
        async with self.session.begin():
            result = await self.session.execute(select(User).filter_by(id=user_id))
            user = result.scalars().first()
            logger.debug(f"Поиск пользователя по id {user_id}: {'найден' if user else 'не найден'}")
            return user

    async def create_user(self, username: str, email: str, hashed_password: str) -> User:
        async with self.session.begin():
            user = User(username=username, email=email, hashed_password=hashed_password)
            self.session.add(user)
            await self.session.flush()
            await self.session.refresh(user)
            logger.info(f"Создан пользователь: {email}")
            return user