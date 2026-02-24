# backend/app/schemas/__init__.py
@"

from app.schemas.user import User, UserCreate, UserLogin, Token
from app.schemas.category import Category, CategoryCreate, CategoryUpdate

"@ | Set-Content -Path backend\app\schemas\__init__.py -Encoding UTF8