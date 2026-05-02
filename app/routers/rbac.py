"""Задание 7.1 — Управление доступом на основе ролей (RBAC) с JWT."""

import secrets
from typing import Callable

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.models.user import UserWithRole, UserInDBWithRole
from app.services.password import hash_password, verify_password
from app.services.jwt_service import create_token, decode_token

router = APIRouter(prefix="/rbac", tags=["RBAC (7.1)"])

bearer_scheme = HTTPBearer(auto_error=False)

ROLE_PERMISSIONS: dict[str, list[str]] = {
    "admin": ["create", "read", "update", "delete"],
    "user": ["read", "update"],
    "guest": ["read"],
}

fake_users_db: dict[str, UserInDBWithRole] = {}

# In-memory хранилище ресурсов для демонстрации CRUD
resources_db: dict[int, dict] = {}
_resource_counter: list[int] = [0]


def _get_current_user_with_role(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> UserInDBWithRole:
    """Извлекает пользователя (с ролью) из JWT."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is missing",
        )
    try:
        payload = decode_token(credentials.credentials)
        username: str | None = payload.get("sub")
        role: str | None = payload.get("role")
        if username is None or role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
        user = fake_users_db.get(username)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


def require_role(*allowed_roles: str) -> Callable:
    """Фабрика зависимостей: проверяет, входит ли роль пользователя в список разрешённых."""
    def dependency(
        user: UserInDBWithRole = Depends(_get_current_user_with_role),
    ) -> UserInDBWithRole:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user.role}' does not have access to this resource",
            )
        return user
    return dependency


# --- Регистрация и логин ---

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_data: UserWithRole):
    if user_data.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )
    if user_data.role not in ROLE_PERMISSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Allowed: {list(ROLE_PERMISSIONS.keys())}",
        )
    hashed = hash_password(user_data.password)
    fake_users_db[user_data.username] = UserInDBWithRole(
        username=user_data.username,
        hashed_password=hashed,
        role=user_data.role,
    )
    return {"message": "New user created"}


@router.post("/login")
def login(user_data: UserWithRole):
    found_user: UserInDBWithRole | None = None
    for stored_user in fake_users_db.values():
        if secrets.compare_digest(user_data.username, stored_user.username):
            found_user = stored_user
            break

    if found_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if not verify_password(user_data.password, found_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization failed",
        )

    token = create_token({"sub": found_user.username, "role": found_user.role})
    return {"access_token": token, "token_type": "bearer"}


# --- CRUD-эндпоинты с разграничением по ролям ---

@router.post("/resource", status_code=status.HTTP_201_CREATED)
def create_resource(
    data: dict,
    user: UserInDBWithRole = Depends(require_role("admin")),
):
    """Создание ресурса — только admin."""
    _resource_counter[0] += 1
    rid = _resource_counter[0]
    resources_db[rid] = {"id": rid, **data}
    return resources_db[rid]


@router.get("/resource")
def list_resources(
    user: UserInDBWithRole = Depends(require_role("admin", "user", "guest")),
):
    """Чтение всех ресурсов — admin, user, guest."""
    return list(resources_db.values())


@router.get("/resource/{resource_id}")
def get_resource(
    resource_id: int,
    user: UserInDBWithRole = Depends(require_role("admin", "user", "guest")),
):
    """Чтение одного ресурса — admin, user, guest."""
    if resource_id not in resources_db:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resources_db[resource_id]


@router.put("/resource/{resource_id}")
def update_resource(
    resource_id: int,
    data: dict,
    user: UserInDBWithRole = Depends(require_role("admin", "user")),
):
    """Обновление ресурса — admin и user."""
    if resource_id not in resources_db:
        raise HTTPException(status_code=404, detail="Resource not found")
    resources_db[resource_id].update(data)
    resources_db[resource_id]["id"] = resource_id
    return resources_db[resource_id]


@router.delete("/resource/{resource_id}")
def delete_resource(
    resource_id: int,
    user: UserInDBWithRole = Depends(require_role("admin")),
):
    """Удаление ресурса — только admin."""
    if resource_id not in resources_db:
        raise HTTPException(status_code=404, detail="Resource not found")
    deleted = resources_db.pop(resource_id)
    return {"message": "Resource deleted", "resource": deleted}
