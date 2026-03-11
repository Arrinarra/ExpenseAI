import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app

# URL для тестовой БД (обратите внимание: host = postgres, а не localhost)
SQLALCHEMY_DATABASE_URL = "postgresql://expenseai_user:expenseai_pass@postgres:5432/expenseai_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Переопределяем зависимость get_db на тестовую сессию
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Фикстура для создания/удаления таблиц (один раз на сессию тестов)
@pytest.fixture(scope="session")
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# Фикстура для чистой сессии БД в каждом тесте (с автоматическим откатом)
@pytest.fixture
def db_session(setup_db):
    """Создаёт новую сессию для теста и откатывает изменения после."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

# Фикстура клиента (переиспользуется во всех тестах)
@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c