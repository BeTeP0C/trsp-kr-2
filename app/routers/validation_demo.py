"""Задание 10.2 — Валидация данных запроса и обработка ошибок валидации."""

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel, EmailStr, conint, constr

router = APIRouter(prefix="/validate", tags=["Validation (10.2)"])


class UserValidated(BaseModel):
    username: str
    age: conint(gt=18)
    email: EmailStr
    password: constr(min_length=8, max_length=16)
    phone: Optional[str] = "Unknown"


@router.post("/user")
def create_validated_user(user: UserValidated):
    """Принимает данные пользователя с валидацией полей."""
    return {
        "message": "User data is valid",
        "user": user.model_dump(),
    }
