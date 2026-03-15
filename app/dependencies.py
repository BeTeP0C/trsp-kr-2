"""Общие зависимости (Depends) для FastAPI."""

import re
from typing import Optional, Annotated

from fastapi import Header, HTTPException

from app.models.headers import CommonHeaders

ACCEPT_LANGUAGE_RE = re.compile(
    r"^[a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})*(;q=\d(\.\d+)?)?"
    r"(,\s*[a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})*(;q=\d(\.\d+)?)?)*$"
)


def get_common_headers(
    user_agent: Annotated[Optional[str], Header()] = None,
    accept_language: Annotated[Optional[str], Header()] = None,
) -> CommonHeaders:
    """
    Извлекает и валидирует заголовки User-Agent и Accept-Language.
    Возвращает 400 при отсутствии или неверном формате.
    """
    if not user_agent:
        raise HTTPException(status_code=400, detail="Missing User-Agent header")
    if not accept_language:
        raise HTTPException(status_code=400, detail="Missing Accept-Language header")
    if not ACCEPT_LANGUAGE_RE.match(accept_language):
        raise HTTPException(status_code=400, detail="Invalid Accept-Language header format")
    return CommonHeaders(user_agent=user_agent, accept_language=accept_language)
