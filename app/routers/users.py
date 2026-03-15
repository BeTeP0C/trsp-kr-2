"""Задание 3.1 - POST /create_user."""

from fastapi import APIRouter

from app.models.user import UserCreate

router = APIRouter(tags=["Users"])


@router.post("/create_user")
def create_user(user: UserCreate):
    """Принимает JSON с данными пользователя и возвращает их обратно."""
    return user.model_dump()
