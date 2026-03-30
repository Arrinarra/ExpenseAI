from fastapi import APIRouter
from app.api.endpoints import auth, users, categories, summary, currencies
from app.api.endpoints.transactions import router as transactions_router

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(transactions_router, prefix="/transactions", tags=["transactions"])
api_router.include_router(summary.router, prefix="/summary", tags=["summary"])
api_router.include_router(currencies.router, prefix="/currencies", tags=["currencies"])