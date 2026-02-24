import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_register_user(client: TestClient, db: Session):
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert "id" in data

def test_register_duplicate_email(client: TestClient, db: Session):
    user_data = {
        "email": "duplicate@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    
    # Create user first time
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200
    
    # Try to create same user again
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_login_user(client: TestClient, db: Session):
    # Create user
    user_data = {
        "email": "login@example.com",
        "password": "testpassword123",
        "full_name": "Login User"
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    # Login
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client: TestClient, db: Session):
    # Create user
    user_data = {
        "email": "wrongpass@example.com",
        "password": "correctpassword",
        "full_name": "Test User"
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    # Login with wrong password
    login_data = {
        "username": user_data["email"],
        "password": "wrongpassword"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 401