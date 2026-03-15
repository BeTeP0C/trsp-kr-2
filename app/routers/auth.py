"""Задания 5.1 - 5.3 - Аутентификация на основе cookie."""

import time

from fastapi import APIRouter, Request, Response, HTTPException

from app.config import settings
from app.models.user import LoginData
from app.services.auth import (
    authenticate,
    get_or_create_user_id,
    create_signed_token,
    verify_signed_token,
    find_username_by_id,
    check_session,
)

router = APIRouter(tags=["Auth"])

@router.post("/login")
def login(data: LoginData, response: Response):
    """
    Аутентификация пользователя.
    """
    user = authenticate(data.username, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user_id = get_or_create_user_id(data.username)
    now_ts = int(time.time())

    signed_token = create_signed_token(user_id, now_ts)

    response.set_cookie(
        key="session_token",
        value=signed_token,
        httponly=True,
        secure=False,
        max_age=settings.session_duration,
    )

    return {"message": "Login successful"}

@router.get("/user")
def get_user(request: Request, response: Response):
    """
    Задание 5.1 - защищённый маршрут.
    """
    token = request.cookies.get("session_token")
    if not token:
        response.status_code = 401
        return {"message": "Unauthorized"}

    user_id, _ = verify_signed_token(token)
    if user_id is None:
        response.status_code = 401
        return {"message": "Unauthorized"}

    username = find_username_by_id(user_id)
    if not username:
        response.status_code = 401
        return {"message": "Unauthorized"}

    return {
        "username": username,
        "user_id": user_id,
    }

@router.get("/profile")
def get_profile(request: Request, response: Response):
    """
    Задания 5.2/5.3 - защищённый маршрут с управлением сессией.
    """
    token = request.cookies.get("session_token")
    result = check_session(token)

    if not result["ok"]:
        response.status_code = result["error"]
        return {"message": result["message"]}

    # Обновляем cookie при необходимости
    if result["renew"]:
        response.set_cookie(
            key="session_token",
            value=result["new_token"],
            httponly=True,
            secure=False,
            max_age=settings.session_duration,
        )

    return {
        "username": result["username"],
        "user_id": result["user_id"],
        "message": "Profile retrieved successfully",
    }
