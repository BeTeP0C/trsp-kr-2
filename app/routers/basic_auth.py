"""Задания 6.1–6.2 — HTTP Basic аутентификация с хешированием паролей."""

import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.models.user import User, UserInDB
from app.services.password import hash_password, verify_password

router = APIRouter(prefix="/basic", tags=["Basic Auth (6.1-6.2)"])

security = HTTPBasic()

fake_users_db: dict[str, UserInDB] = {}


def auth_user(
    credentials: HTTPBasicCredentials = Depends(security),
) -> UserInDB:
    """Зависимость: проверяет HTTP Basic credentials против fake_users_db."""
    user: UserInDB | None = None
    for stored_user in fake_users_db.values():
        if secrets.compare_digest(credentials.username, stored_user.username):
            user = stored_user
            break

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    return user


@router.post("/register")
def register(user_data: User):
    """Регистрация пользователя с хешированием пароля."""
    if user_data.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )

    hashed = hash_password(user_data.password)
    user_in_db = UserInDB(username=user_data.username, hashed_password=hashed)
    fake_users_db[user_data.username] = user_in_db

    return {"message": f"User '{user_data.username}' registered successfully"}


@router.get("/login")
def login(user: UserInDB = Depends(auth_user)):
    """
    Задание 6.1: возвращает секретное сообщение при успешной Basic-аутентификации.
    Задание 6.2: возвращает приветствие с именем пользователя.
    """
    return {
        "secret": "You got my secret, welcome",
        "message": f"Welcome, {user.username}!",
    }
