# backend/app/crud/__init__.py
@"
from app.crud.user import user
from app.crud.category import category
"@ | Set-Content -Path backend\app\crud\__init__.py -Encoding UTF8