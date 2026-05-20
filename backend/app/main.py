from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.scheduler import start_scheduler

from app.api.router import api_router
from app.core.config import settings
from app.database import engine, Base
from app.models import user, category  # noqa

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
        "https://*.onrender.com",
        "*"
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

# Определяем путь к папке frontend (папка на одном уровне с backend)
frontend_path = Path(__file__).parent.parent / "frontend"

# Монтируем папку со статикой
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")
    print(f"✅ Static files mounted from {frontend_path}")
else:
    print(f"❌ Frontend not found at {frontend_path}")

# Главная страница
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = frontend_path / "index.html"
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return HTMLResponse(content="<h1>Frontend not found</h1>", status_code=404)

# Дашборд (опционально)
@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard():
    dashboard_path = frontend_path / "dashboard.html"
    if dashboard_path.exists():
        with open(dashboard_path, "r", encoding="utf-8") as f:
            return f.read()
    return HTMLResponse(content="<h1>Dashboard not found</h1>", status_code=404)

@app.get("/dashboard.html", response_class=HTMLResponse)
async def serve_dashboard_html():
    dashboard_path = frontend_path / "dashboard.html"
    if dashboard_path.exists():
        with open(dashboard_path, "r", encoding="utf-8") as f:
            return f.read()
    return HTMLResponse(content="<h1>Dashboard not found</h1>", status_code=404)

# API root endpoint (JSON)
@app.get("/api-root")
def api_root():
    return {
        "message": "Welcome to ExpenseAI API",
        "version": settings.VERSION,
        "docs": "/docs",
        "frontend": "/"
    }
