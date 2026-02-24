from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from app.api.router import api_router
from app.core.config import settings
from app.database import engine, Base
from app.models import user, category

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (frontend)
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend"))
if os.path.exists(frontend_path):
    app.mount("/frontend", StaticFiles(directory=frontend_path), name="frontend")

# Serve index.html at root
@app.get("/")
def root():
    return {
        "message": "Welcome to ExpenseAI API",
        "version": settings.VERSION,
        "docs": "/docs",
        "frontend": "/frontend/index.html"
    }

# Include routers
app.include_router(api_router, prefix=settings.API_V1_STR)