# backend/app/api/endpoints/users.py
@"
from typing import Annotated
from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.user import User as UserSchema

router = APIRouter()

@router.get("/me", response_model=UserSchema)
def read_current_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user
"@ | Set-Content -Path backend\app\api\endpoints\users.py -Encoding UTF8