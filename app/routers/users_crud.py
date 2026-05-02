"""Задания 11.1–11.2 — Простой CRUD пользователей (in-memory) для тестирования."""

from itertools import count
from threading import Lock

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel

router = APIRouter(tags=["Users CRUD (11.1-11.2)"])

db: dict[int, dict] = {}
_id_seq = count(start=1)
_id_lock = Lock()


def _next_user_id() -> int:
    with _id_lock:
        return next(_id_seq)


def reset_db():
    """Сброс хранилища — используется в тестах для изоляции состояния."""
    global _id_seq
    db.clear()
    _id_seq = count(start=1)


class UserIn(BaseModel):
    username: str
    age: int


class UserOut(BaseModel):
    id: int
    username: str
    age: int


@router.post("/users", response_model=UserOut, status_code=201)
def create_user(user: UserIn):
    user_id = _next_user_id()
    db[user_id] = user.model_dump()
    return {"id": user_id, **db[user_id]}


@router.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    if user_id not in db:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user_id, **db[user_id]}


@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    if db.pop(user_id, None) is None:
        raise HTTPException(status_code=404, detail="User not found")
    return Response(status_code=204)
