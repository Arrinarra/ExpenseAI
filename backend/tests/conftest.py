import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app

# Тестовая БД (обратите внимание: host = postgres, а не localhost)
SQLALCHEMY_DATABASE_URL = "postgresql://expenseai_user:expenseai_pass@postgres:5432/expenseai_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Переопределение зависимости get_db
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Автоматическая фикстура: пересоздаёт таблицы перед каждым тестом
@pytest.fixture(scope="function", autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    # (опционально) можно удалять после теста, но не обязательно

# Фикстура сессии базы данных для ручного добавления данных в тестах
@pytest.fixture
def db_session(setup_db):
    db = TestingSessionLocal()
    yield db
    db.close()

# Фикстура HTTP-клиента
@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c