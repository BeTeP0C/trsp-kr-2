"""Задание 8.2 — CRUD для Todo-элементов (SQLite)."""

from fastapi import APIRouter, HTTPException, status

from app.models.user import TodoCreate, TodoUpdate, TodoResponse
from app.database import get_db_connection

router = APIRouter(prefix="/todos", tags=["Todos (8.2)"])


@router.post("", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(todo: TodoCreate):
    """Создание нового Todo-элемента."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO todos (title, description, completed) VALUES (?, ?, ?)",
        (todo.title, todo.description, False),
    )
    conn.commit()
    todo_id = cursor.lastrowid
    conn.close()

    return TodoResponse(
        id=todo_id,
        title=todo.title,
        description=todo.description,
        completed=False,
    )


@router.get("/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int):
    """Получение Todo по ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, completed FROM todos WHERE id = ?", (todo_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    return TodoResponse(
        id=row["id"],
        title=row["title"],
        description=row["description"],
        completed=bool(row["completed"]),
    )


@router.put("/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo: TodoUpdate):
    """Обновление существующего Todo."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM todos WHERE id = ?", (todo_id,))
    if cursor.fetchone() is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Todo not found")

    cursor.execute(
        "UPDATE todos SET title = ?, description = ?, completed = ? WHERE id = ?",
        (todo.title, todo.description, todo.completed, todo_id),
    )
    conn.commit()
    conn.close()

    return TodoResponse(
        id=todo_id,
        title=todo.title,
        description=todo.description,
        completed=todo.completed,
    )


@router.delete("/{todo_id}")
def delete_todo(todo_id: int):
    """Удаление Todo по ID."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM todos WHERE id = ?", (todo_id,))
    if cursor.fetchone() is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Todo not found")

    cursor.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()
    conn.close()

    return {"message": "Todo deleted successfully"}
