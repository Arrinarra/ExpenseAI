from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
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

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500", 
        "http://localhost",
        "http://127.0.0.1",
        "https://*.onrender.com",  # разрешаем Render
        "*"  # временно для теста
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

# Монтируем папку со статикой (CSS, JS)
frontend_index = Path(__file__).parent.parent / "frontend" / "index.html"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")
    print(f"✅ Static files mounted from {frontend_path}")
else:
    print(f"❌ Frontend not found at {frontend_path}")

# Корневой эндпоинт - отдаём главную страницу
@app.get("/")
async def serve_index():
    index_path = Path(__file__).parent / "frontend" / "index.html"
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    return HTMLResponse(content="<h1>Frontend not found</h1>", status_code=404)

# Эндпоинт для дашборда (если нужно прямое открытие)
@app.get("/dashboard")
async def serve_dashboard():
    dashboard_path = Path(__file__).parent / "frontend" / "dashboard.html"
    if dashboard_path.exists():
        with open(dashboard_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    return HTMLResponse(content="<h1>Dashboard not found</h1>", status_code=404)
