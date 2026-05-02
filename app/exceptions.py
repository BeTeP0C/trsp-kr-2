"""Задание 10.1 — Пользовательские исключения и обработчики."""

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel


# ---------- Модели ответов об ошибках ----------

class ErrorResponse(BaseModel):
    detail: str
    error_code: str


# ---------- Пользовательские исключения ----------

class CustomExceptionA(Exception):
    """Нарушение бизнес-правила (например, недостаточно средств)."""

    def __init__(self, detail: str = "Business rule violation"):
        self.detail = detail


class CustomExceptionB(Exception):
    """Ресурс не найден в системе."""

    def __init__(self, detail: str = "Resource not found"):
        self.detail = detail


# ---------- Обработчики исключений ----------

async def handle_custom_exception_a(request: Request, exc: CustomExceptionA):
    print(f"[CustomExceptionA] {request.method} {request.url} — {exc.detail}")
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            detail=exc.detail,
            error_code="BUSINESS_RULE_VIOLATION",
        ).model_dump(),
    )


async def handle_custom_exception_b(request: Request, exc: CustomExceptionB):
    print(f"[CustomExceptionB] {request.method} {request.url} — {exc.detail}")
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(
            detail=exc.detail,
            error_code="RESOURCE_NOT_FOUND",
        ).model_dump(),
    )
