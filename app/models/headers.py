"""Pydantic-модель общих заголовков запроса."""

from pydantic import BaseModel


class CommonHeaders(BaseModel):
    """Задание 5.5 — User-Agent и Accept-Language."""
    user_agent: str
    accept_language: str
