"""Задания 6.4–6.5 — JWT-аутентификация с rate-limiting."""

import secrets

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.models.user import User, UserInDB
from app.services.password import hash_password, verify_password
from app.services.jwt_service import create_token, decode_token

router = APIRouter(prefix="/jwt", tags=["JWT Auth (6.4-6.5)"])

limiter = Limiter(key_func=get_remote_address)

bearer_scheme = HTTPBearer(auto_error=False)

fake_users_db: dict[str, UserInDB] = {}


@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("1/minute")
def register(request: Request, user_data: User):
    """Регистрация нового пользователя (задание 6.5)."""
    if user_data.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )

    hashed = hash_password(user_data.password)
    fake_users_db[user_data.username] = UserInDB(
        username=user_data.username,
        hashed_password=hashed,
    )

    return {"message": "New user created"}


@router.post("/login")
@limiter.limit("5/minute")
def login(request: Request, user_data: User):
    """Аутентификация и выдача JWT-токена (задания 6.4–6.5)."""
    found_user: UserInDB | None = None
    for stored_user in fake_users_db.values():
        if secrets.compare_digest(user_data.username, stored_user.username):
            found_user = stored_user
            break

    if found_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not verify_password(user_data.password, found_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization failed",
        )

    token = create_token({"sub": found_user.username})
    return {"access_token": token, "token_type": "bearer"}


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    """Зависимость: извлекает username из Bearer-токена."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is missing",
        )
    try:
        payload = decode_token(credentials.credentials)
        username: str | None = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


@router.get("/protected_resource")
def protected_resource(username: str = Depends(get_current_user)):
    """Защищённый ресурс — требуется валидный JWT (задание 6.4)."""
    return {"message": "Access granted"}
