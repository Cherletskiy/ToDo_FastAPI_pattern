import jwt
import bcrypt

from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User
from app.logging_config import setup_logger
from app.repository.user_repository import UserRepository

import os
from dotenv import load_dotenv

load_dotenv()

logger = setup_logger(__name__)

# Настройки JWT
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))


class AuthService:

    @staticmethod
    def get_password_hash(password: str) -> str:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed_password: bytes) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode("utf-8"))

    @staticmethod
    def create_access_token(data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.debug(f"Создан JWT-токен, истекает: {expire}")
        return encoded_jwt

    @staticmethod
    async def authenticate_user(username: str, password: str, session: AsyncSession) -> User | None:
        repo = UserRepository(session)
        user = await repo.get_user_by_email(username)
        if not user:
            logger.warning(f"Не найден: {username}")
            return None
        if not AuthService.verify_password(password, user.hashed_password):
            logger.warning(f"Неверный пароль: {username}")
            return None
        return user

    @staticmethod
    async def get_current_user(token: str, session: AsyncSession) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                logger.warning("Токен не содержит user_id")
                raise credentials_exception
        except Exception as e:
            logger.warning(f"Ошибка декодирования токена: {e}")
            raise credentials_exception

        repo = UserRepository(session)
        user = await repo.get_user_by_id(int(user_id))

        if user is None:
            logger.warning(f"Пользователь с id {user_id} не найден")
            raise credentials_exception

        logger.debug(f"Получен текущий пользователь: {user.email}")
        return user
