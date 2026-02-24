# backend/app/models/__init__.py
@"
from app.models.user import User
from app.models.category import Category
"@ | Set-Content -Path backend\app\models\__init__.py -Encoding UTF8