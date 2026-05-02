"""Задание 8.1 — Регистрация пользователей в SQLite."""

from fastapi import APIRouter, HTTPException, status

from app.models.user import User
from app.database import get_db_connection

router = APIRouter(prefix="/db", tags=["DB Users (8.1)"])


@router.post("/register")
def register(user_data: User):
    """Сохраняет пользователя в таблицу users (SQLite)."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (user_data.username, user_data.password),
        )
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    finally:
        conn.close()

    return {"message": "User registered successfully!"}
