import pytest
from fastapi.testclient import TestClient
from app.core.security import get_password_hash
from app.models.user import User

def test_register_user(client: TestClient, db_session):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "new@example.com",
            "password": "secretlong",
            "full_name": "New User"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "new@example.com"
    assert "id" in data

def test_register_duplicate_email(client: TestClient, db_session):
    # Создаём пользователя напрямую в БД
    user = User(email="test@example.com", hashed_password=get_password_hash("secret"))
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "secretlong",
            "full_name": "Another User"
        }
    )
    assert response.status_code == 400
    data = response.json()
    assert "already exists" in data.get("detail", "").lower()

def test_login_user(client: TestClient, db_session):
    user = User(email="test@example.com", hashed_password=get_password_hash("secret"))
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "secret"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

def test_login_wrong_password(client: TestClient, db_session):
    user = User(email="test@example.com", hashed_password=get_password_hash("secret"))
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "wrong"}
    )
    assert response.status_code == 401