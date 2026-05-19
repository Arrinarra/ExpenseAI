import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date, timedelta

from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.models.category import Category
from app.models.transaction import Transaction
from app.core.security import get_password_hash

# --- SQLite в памяти для тестов ---
SQLALCHEMY_DATABASE_URL = "postgresql://expenseai_user:expenseai_pass@postgres:5432/expenseai_test"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаём таблицы
Base.metadata.create_all(bind=engine)

# Переопределяем get_db
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# --- Фикстуры с функциональной областью видимости ---
@pytest.fixture(scope="function")
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()

@pytest.fixture(scope="function")
def test_user(db_session):
    user = User(
        email="analytics@test.com",
        hashed_password=get_password_hash("testpass"),
        full_name="Analytics Tester"
    )
    db_session.add(user)
    db_session.commit()
    yield user
    db_session.delete(user)
    db_session.commit()

@pytest.fixture(scope="function")
def test_categories(db_session):
    cats = [
        Category(name="Еда", type="expense"),
        Category(name="Транспорт", type="expense"),
        Category(name="Доход", type="income")
    ]
    for cat in cats:
        db_session.add(cat)
    db_session.commit()
    for cat in cats:
        db_session.refresh(cat)
    yield {c.name: c for c in cats}
    for cat in cats:
        db_session.delete(cat)
    db_session.commit()

@pytest.fixture(scope="function")
def test_transactions(db_session, test_user, test_categories):
    today = date.today()
    transactions = [
        Transaction(
            user_id=test_user.id,
            amount=-100.0,
            currency="USD",
            base_amount=-100.0,
            category_id=test_categories["Еда"].id,
            date=today - timedelta(days=5),
            description="Продукты"
        ),
        Transaction(
            user_id=test_user.id,
            amount=-50.0,
            currency="USD",
            base_amount=-50.0,
            category_id=test_categories["Транспорт"].id,
            date=today - timedelta(days=2),
            description="Такси"
        ),
        Transaction(
            user_id=test_user.id,
            amount=200.0,
            currency="USD",
            base_amount=200.0,
            category_id=test_categories["Доход"].id,
            date=today - timedelta(days=1),
            description="Зарплата"
        ),
        Transaction(
            user_id=test_user.id,
            amount=-30.0,
            currency="USD",
            base_amount=-30.0,
            category_id=test_categories["Еда"].id,
            date=today - timedelta(days=35),
            description="Старый расход"
        ),
    ]
    for tx in transactions:
        db_session.add(tx)
    db_session.commit()
    yield transactions
    for tx in transactions:
        db_session.delete(tx)
    db_session.commit()

def get_access_token(test_user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": test_user.email, "password": "testpass"}
    )
    return response.json()["access_token"]

# --- Тесты ---
def test_analytics_monthly_structure(db_session, test_user, test_categories, test_transactions):
    token = get_access_token(test_user)
    response = client.get(
        "/api/v1/analytics/monthly?period=month&currency=USD",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    items = data["data"]
    assert len(items) == 2
    amounts = {item["category"]: item["amount"] for item in items}
    assert amounts["Еда"] == -100.0
    assert amounts["Транспорт"] == -50.0

def test_analytics_trends(db_session, test_user, test_categories, test_transactions):
    token = get_access_token(test_user)
    response = client.get(
        "/api/v1/analytics/trends?period=week&currency=USD",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)
    assert len(data["data"]) >= 1

def test_analytics_monthly_no_transactions(db_session):
    empty_user = User(
        email="empty@test.com",
        hashed_password=get_password_hash("pass"),
        full_name="Empty"
    )
    db_session.add(empty_user)
    db_session.commit()
    token = client.post(
        "/api/v1/auth/login",
        data={"username": empty_user.email, "password": "pass"}
    ).json()["access_token"]
    response = client.get(
        "/api/v1/analytics/monthly?period=month",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"] == []
    db_session.delete(empty_user)
    db_session.commit()