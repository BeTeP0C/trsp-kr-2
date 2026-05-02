"""Задание 11.2 — Асинхронные тесты с pytest-asyncio, httpx.AsyncClient и Faker."""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from faker import Faker

from main import app
from app.routers.users_crud import reset_db

fake = Faker()


@pytest.fixture(autouse=True)
def clean_state():
    """Сброс in-memory хранилища до и после каждого теста."""
    reset_db()
    yield
    reset_db()


@pytest_asyncio.fixture
async def ac():
    """Асинхронный HTTP-клиент через ASGITransport (без запуска сервера)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


# ==================== Создание пользователя ====================

class TestCreateUser:
    @pytest.mark.asyncio
    async def test_create_user_returns_201(self, ac: AsyncClient):
        username = fake.user_name()
        age = fake.random_int(min=18, max=80)
        resp = await ac.post("/users", json={"username": username, "age": age})

        assert resp.status_code == 201
        data = resp.json()
        assert data["username"] == username
        assert data["age"] == age
        assert isinstance(data["id"], int)

    @pytest.mark.asyncio
    async def test_create_multiple_users_unique_ids(self, ac: AsyncClient):
        ids = []
        for _ in range(3):
            resp = await ac.post("/users", json={
                "username": fake.user_name(),
                "age": fake.random_int(min=18, max=80),
            })
            assert resp.status_code == 201
            ids.append(resp.json()["id"])

        assert len(set(ids)) == 3

    @pytest.mark.asyncio
    async def test_create_user_missing_age(self, ac: AsyncClient):
        resp = await ac.post("/users", json={"username": fake.user_name()})
        assert resp.status_code == 422


# ==================== Получение пользователя ====================

class TestGetUser:
    @pytest.mark.asyncio
    async def test_get_existing_user(self, ac: AsyncClient):
        username = fake.user_name()
        age = fake.random_int(min=18, max=80)
        create_resp = await ac.post("/users", json={"username": username, "age": age})
        user_id = create_resp.json()["id"]

        resp = await ac.get(f"/users/{user_id}")
        assert resp.status_code == 200
        assert resp.json()["username"] == username
        assert resp.json()["age"] == age

    @pytest.mark.asyncio
    async def test_get_nonexistent_user_returns_404(self, ac: AsyncClient):
        resp = await ac.get("/users/99999")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "User not found"

    @pytest.mark.asyncio
    async def test_get_user_after_creating_several(self, ac: AsyncClient):
        created = []
        for _ in range(5):
            resp = await ac.post("/users", json={
                "username": fake.user_name(),
                "age": fake.random_int(min=18, max=80),
            })
            created.append(resp.json())

        target = created[2]
        resp = await ac.get(f"/users/{target['id']}")
        assert resp.status_code == 200
        assert resp.json()["username"] == target["username"]


# ==================== Удаление пользователя ====================

class TestDeleteUser:
    @pytest.mark.asyncio
    async def test_delete_existing_user_returns_204(self, ac: AsyncClient):
        create_resp = await ac.post("/users", json={
            "username": fake.user_name(),
            "age": fake.random_int(min=18, max=80),
        })
        user_id = create_resp.json()["id"]

        resp = await ac.delete(f"/users/{user_id}")
        assert resp.status_code == 204

    @pytest.mark.asyncio
    async def test_get_after_delete_returns_404(self, ac: AsyncClient):
        create_resp = await ac.post("/users", json={
            "username": fake.user_name(),
            "age": fake.random_int(min=18, max=80),
        })
        user_id = create_resp.json()["id"]

        await ac.delete(f"/users/{user_id}")
        resp = await ac.get(f"/users/{user_id}")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_double_delete_returns_404(self, ac: AsyncClient):
        create_resp = await ac.post("/users", json={
            "username": fake.user_name(),
            "age": fake.random_int(min=18, max=80),
        })
        user_id = create_resp.json()["id"]

        await ac.delete(f"/users/{user_id}")
        resp = await ac.delete(f"/users/{user_id}")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "User not found"

    @pytest.mark.asyncio
    async def test_delete_nonexistent_user(self, ac: AsyncClient):
        resp = await ac.delete("/users/99999")
        assert resp.status_code == 404
