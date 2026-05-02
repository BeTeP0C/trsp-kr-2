"""Задание 11.1 — Синхронные модульные тесты с pytest + TestClient."""

import pytest
from fastapi.testclient import TestClient

from main import app
from app.routers.users_crud import reset_db


@pytest.fixture(autouse=True)
def clean_state():
    """Сброс in-memory хранилища перед каждым тестом."""
    reset_db()
    yield
    reset_db()


client = TestClient(app)


# ==================== Users CRUD ====================

class TestCreateUser:
    def test_create_user_success(self):
        resp = client.post("/users", json={"username": "alice", "age": 25})
        assert resp.status_code == 201
        data = resp.json()
        assert data["username"] == "alice"
        assert data["age"] == 25
        assert "id" in data

    def test_create_user_missing_field(self):
        resp = client.post("/users", json={"username": "alice"})
        assert resp.status_code == 422

    def test_create_user_invalid_type(self):
        resp = client.post("/users", json={"username": "alice", "age": "not_a_number"})
        assert resp.status_code == 422


class TestGetUser:
    def test_get_existing_user(self):
        create_resp = client.post("/users", json={"username": "bob", "age": 30})
        user_id = create_resp.json()["id"]

        resp = client.get(f"/users/{user_id}")
        assert resp.status_code == 200
        assert resp.json()["username"] == "bob"
        assert resp.json()["age"] == 30

    def test_get_nonexistent_user(self):
        resp = client.get("/users/9999")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "User not found"


class TestDeleteUser:
    def test_delete_existing_user(self):
        create_resp = client.post("/users", json={"username": "charlie", "age": 22})
        user_id = create_resp.json()["id"]

        resp = client.delete(f"/users/{user_id}")
        assert resp.status_code == 204

        resp2 = client.get(f"/users/{user_id}")
        assert resp2.status_code == 404

    def test_delete_nonexistent_user(self):
        resp = client.delete("/users/9999")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "User not found"

    def test_double_delete(self):
        create_resp = client.post("/users", json={"username": "dave", "age": 40})
        user_id = create_resp.json()["id"]

        client.delete(f"/users/{user_id}")
        resp = client.delete(f"/users/{user_id}")
        assert resp.status_code == 404


# ==================== Custom errors (10.1) ====================

class TestCustomErrors:
    def test_get_existing_item(self):
        resp = client.get("/errors/items/1")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Item A"

    def test_get_missing_item(self):
        resp = client.get("/errors/items/999")
        assert resp.status_code == 404
        assert resp.json()["error_code"] == "RESOURCE_NOT_FOUND"

    def test_purchase_success(self):
        resp = client.post("/errors/items/1/purchase?quantity=1")
        assert resp.status_code == 200
        assert "remaining_stock" in resp.json()

    def test_purchase_out_of_stock(self):
        resp = client.post("/errors/items/2/purchase?quantity=1")
        assert resp.status_code == 400
        assert resp.json()["error_code"] == "BUSINESS_RULE_VIOLATION"

    def test_purchase_missing_item(self):
        resp = client.post("/errors/items/999/purchase?quantity=1")
        assert resp.status_code == 404


# ==================== Validation (10.2) ====================

class TestValidation:
    def test_valid_user(self):
        resp = client.post("/validate/user", json={
            "username": "testuser",
            "age": 25,
            "email": "test@example.com",
            "password": "securepass1",
        })
        assert resp.status_code == 200
        assert resp.json()["user"]["username"] == "testuser"

    def test_age_too_young(self):
        resp = client.post("/validate/user", json={
            "username": "young",
            "age": 17,
            "email": "young@example.com",
            "password": "securepass1",
        })
        assert resp.status_code == 422
        assert resp.json()["detail"] == "Validation error"

    def test_invalid_email(self):
        resp = client.post("/validate/user", json={
            "username": "bademail",
            "age": 25,
            "email": "not-an-email",
            "password": "securepass1",
        })
        assert resp.status_code == 422

    def test_password_too_short(self):
        resp = client.post("/validate/user", json={
            "username": "shortpw",
            "age": 25,
            "email": "test@example.com",
            "password": "short",
        })
        assert resp.status_code == 422

    def test_password_too_long(self):
        resp = client.post("/validate/user", json={
            "username": "longpw",
            "age": 25,
            "email": "test@example.com",
            "password": "a" * 20,
        })
        assert resp.status_code == 422

    def test_optional_phone_default(self):
        resp = client.post("/validate/user", json={
            "username": "nophone",
            "age": 25,
            "email": "test@example.com",
            "password": "securepass1",
        })
        assert resp.status_code == 200
        assert resp.json()["user"]["phone"] == "Unknown"
