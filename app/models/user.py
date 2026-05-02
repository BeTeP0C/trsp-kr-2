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


# --- Задание 6.2: модели для HTTP Basic аутентификации ---

class UserBase(BaseModel):
    username: str


class User(UserBase):
    password: str


class UserInDB(UserBase):
    hashed_password: str


# --- Задание 7.1: модель с ролью ---

class UserWithRole(BaseModel):
    username: str
    password: str
    role: str = "guest"


class UserInDBWithRole(UserBase):
    hashed_password: str
    role: str = "guest"


# --- Задание 8.2: модель Todo ---

class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None


class TodoUpdate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool


class TodoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool
