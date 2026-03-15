"""Задания 5.4 - 5.5 - Работа с заголовками (Headers)."""

from datetime import datetime

from fastapi import APIRouter, Response, Depends

from app.models.headers import CommonHeaders
from app.dependencies import get_common_headers

router = APIRouter(tags=["Headers"])

@router.get("/headers")
def read_headers(commons: CommonHeaders = Depends(get_common_headers)):
    """Возвращает User-Agent и Accept-Language из входящего запроса."""
    return {
        "User-Agent": commons.user_agent,
        "Accept-Language": commons.accept_language,
    }

@router.get("/info")
def read_info(
    response: Response,
    commons: CommonHeaders = Depends(get_common_headers),
):
    """
    Возвращает заголовки + приветственное сообщение.
    """
    response.headers["X-Server-Time"] = datetime.now().isoformat()
    return {
        "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
        "headers": {
            "User-Agent": commons.user_agent,
            "Accept-Language": commons.accept_language,
        },
    }
