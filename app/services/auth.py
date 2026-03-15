"""Сервис аутентификации."""

import uuid
import time
from typing import Optional

from itsdangerous import Signer, BadSignature

from app.config import settings

signer = Signer(settings.secret_key)

fake_users_db: dict[str, dict] = {
    "user123": {
        "username": "user123",
        "password": "password123",
    },
}

user_id_map: dict[str, str] = {}

def authenticate(username: str, password: str) -> Optional[dict]:
    """Проверяет учётные данные"""
    user = fake_users_db.get(username)
    if user and user["password"] == password:
        return user
    return None


def get_or_create_user_id(username: str) -> str:
    """Возвращает (или создаёт) UUID для указанного пользователя."""
    if username not in user_id_map:
        user_id_map[username] = str(uuid.uuid4())
    return user_id_map[username]


def create_signed_token(user_id: str, timestamp: int) -> str:
    """
    Формирует подписанный токен
    """
    data = f"{user_id}.{timestamp}"
    return signer.sign(data).decode("utf-8")


def verify_signed_token(token: str) -> tuple[Optional[str], Optional[int]]:
    """
    Проверяет подпись и возвращает (user_id, timestamp)
    """
    try:
        data = signer.unsign(token).decode("utf-8")
        idx = data.rfind(".")
        if idx == -1:
            return None, None
        user_id = data[:idx]
        timestamp = int(data[idx + 1:])
        return user_id, timestamp
    except (BadSignature, ValueError):
        return None, None


def find_username_by_id(user_id: str) -> Optional[str]:
    """Обратный поиск username по user_id."""
    for uname, uid in user_id_map.items():
        if uid == user_id:
            return uname
    return None


def check_session(token: str) -> dict:
    """
    Комплексная проверка сессии (Задание 5.3).
    """
    if not token:
        return {"ok": False, "error": 401, "message": "Unauthorized"}

    user_id, timestamp = verify_signed_token(token)
    if user_id is None or timestamp is None:
        return {"ok": False, "error": 401, "message": "Invalid session"}

    username = find_username_by_id(user_id)
    if not username:
        return {"ok": False, "error": 401, "message": "Invalid session"}

    now = int(time.time())
    elapsed = now - timestamp

    if elapsed >= settings.session_duration:
        return {"ok": False, "error": 401, "message": "Session expired"}

    renew = elapsed >= settings.renewal_threshold
    new_token = create_signed_token(user_id, now) if renew else None

    return {
        "ok": True,
        "username": username,
        "user_id": user_id,
        "renew": renew,
        "new_token": new_token,
    }
