import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.services.exchange_service import fetch_exchange_rates
from unittest.mock import patch

# Тестовая БД
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@patch("app.services.exchange_service.httpx.AsyncClient.get")
@pytest.mark.asyncio
async def test_fetch_exchange_rates(mock_get):
    # Мокаем ответ API
    mock_response = {"rates": {"EUR": 0.92, "RUB": 85.0}}
    mock_get.return_value.__aenter__.return_value.json = pytest.MagicMock(return_value=mock_response)
    rates = await fetch_exchange_rates()
    assert rates["EUR"] == 0.92
    assert rates["RUB"] == 85.0

def test_update_currencies_endpoint():
    # Требуется авторизация, поэтому просто проверяем, что эндпоинт существует
    response = client.post("/api/v1/currencies/update")
    # Без токена вернёт 401
    assert response.status_code == 401