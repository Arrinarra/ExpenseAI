import pytest
from datetime import date
from fastapi.testclient import TestClient
from app.core.security import create_access_token, get_password_hash
from app.models.user import User
from app.models.category import Category

def test_create_transaction(client: TestClient, db_session):
    """Тест создания новой транзакции."""
    # Создаём пользователя
    user = User(email="test@example.com", hashed_password=get_password_hash("secret"))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Создаём категорию
    category = Category(name="Food", type="expense")
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    # Генерируем токен
    token = create_access_token(data={"sub": str(user.id)})

    response = client.post(
        "/api/transactions",
        json={
            "amount": -15.50,
            "currency": "USD",
            "category_id": category.id,
            "date": str(date.today()),
            "description": "Lunch"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == -15.50
    assert data["user_id"] == user.id

def test_get_transactions(client: TestClient, db_session):
    """Тест получения списка транзакций."""
    user = User(email="test@example.com", hashed_password=get_password_hash("secret"))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    category = Category(name="Food", type="expense")
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    token = create_access_token(data={"sub": str(user.id)})

    # Создаём транзакцию через API
    client.post(
        "/api/transactions",
        json={
            "amount": -15.50,
            "currency": "USD",
            "category_id": category.id,
            "date": str(date.today()),
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    response = client.get("/api/transactions", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1

def test_get_summary(client: TestClient, db_session):
    """Тест получения сводки доходов/расходов."""
    user = User(email="test@example.com", hashed_password=get_password_hash("secret"))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    category = Category(name="Food", type="expense")
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    token = create_access_token(data={"sub": str(user.id)})

    # Добавляем доход
    client.post(
        "/api/transactions",
        json={"amount": 1000, "currency": "USD", "category_id": category.id, "date": str(date.today())},
        headers={"Authorization": f"Bearer {token}"}
    )
    # Добавляем расход
    client.post(
        "/api/transactions",
        json={"amount": -200, "currency": "USD", "category_id": category.id, "date": str(date.today())},
        headers={"Authorization": f"Bearer {token}"}
    )

    response = client.get("/api/summary?period=month", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["total_income"] == 1000
    assert data["total_expense"] == 200
    assert data["balance"] == 800