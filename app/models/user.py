"""Pydantic-модели пользователей."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserCreate(BaseModel):
    """Задание 3.1 — данные для создания пользователя."""
    name: str
    email: EmailStr
    age: Optional[int] = Field(None, gt=0)
    is_subscribed: Optional[bool] = None


class LoginData(BaseModel):
    """Задания 5.1–5.3 — данные для входа."""
    username: str
    password: str
