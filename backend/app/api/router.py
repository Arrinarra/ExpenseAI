# backend/app/api/router.py
@"
from fastapi import APIRouter
from app.api.endpoints import auth, users, categories

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
"@ | Set-Content -Path backend\app\api\router.py -Encoding UTF8