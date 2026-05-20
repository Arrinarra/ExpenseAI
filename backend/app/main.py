from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.scheduler import start_scheduler

from app.api.router import api_router
from app.core.config import settings
from app.database import engine, Base
from app.models import user, category  # noqa
import os

# Создание таблиц (если не используете миграции)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS (добавлен localtunnel адрес для теста)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500", 
        "http://localhost",
        "http://127.0.0.1",
        "https://*.loca.lt",  # разрешаем localtunnel
        "*"  # временно для теста, потом можно убрать
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем единый роутер со всеми эндпоинтами
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
def startup_event():
    start_scheduler()

# Статика
frontend_path = Path(__file__).parent / "frontend"
if frontend_path.exists():
    app.mount("/frontend", StaticFiles(directory=str(frontend_path)), name="frontend")
    print(f"✅ Frontend mounted from {frontend_path}")
else:
    print(f"❌ Frontend not found at {frontend_path}")

@app.get("/")
def root():
    return {
        "message": "Welcome to ExpenseAI API",
        "version": settings.VERSION,
        "docs": "/docs",
        "frontend": "/frontend/index.html"
    }