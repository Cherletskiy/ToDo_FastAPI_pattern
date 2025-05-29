from fastapi import APIRouter, HTTPException, Depends, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_async_session
from app.database.models import User
from app.models.user import UserCreate, UserResponse, Token
from app.repository.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.logging_config import setup_logger


logger = setup_logger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

# OAuth2 схема
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def login_form(
    email: str = Form(...),
    password: str = Form(...)
) -> dict:
    return {"email": email, "password": password}


@router.post("/login", response_model=Token)
async def login_for_access_token(
        form_data: dict = Depends(login_form),
        session: AsyncSession = Depends(get_async_session)
) -> Token:
    email = form_data.get("email")
    password = form_data.get("password")

    logger.info(f"Попытка аутентификации пользователя {email}")
    user = await AuthService.authenticate_user(email, password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = AuthService.create_access_token(
        data={"sub": user.id, "username": user.username, "email": user.email},
    )
    refresh_token = AuthService.create_refresh_token(
        data={"sub": user.id},
    )
    logger.info(f"Пользователь аутентифицирован: {user.email}")
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, session: AsyncSession = Depends(get_async_session)) -> User:
    repo = UserRepository(session)
    existing_user = await repo.get_user_by_email(user.email)
    if existing_user:
        logger.warning(f"Попытка регистрации с существующим email: {user.email}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email уже зарегистрирован")
    hashed_password = AuthService.get_password_hash(user.password)
    db_user = await repo.create_user(user.username, user.email, hashed_password)
    logger.info(f"Пользователь зарегистрирован: {db_user.email}")
    return db_user


@router.get("/me", response_model=UserResponse)
async def get_info_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_async_session)
):
    user = await AuthService.get_current_user(token, session)
    logger.info(f"Получены данные текущего пользователя: {user.email}")
    return user


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str = Form(...),
    session: AsyncSession = Depends(get_async_session)
) -> Token:
    user = await AuthService.get_current_user(refresh_token, session, expected_type="refresh")
    access_token = AuthService.create_access_token(
        data={"sub": user.id, "username": user.username, "email": user.email},
    )
    return Token(access_token=access_token, refresh_token=refresh_token)