from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.category import Category, CategoryCreate, CategoryUpdate
from app.crud.category import category as category_crud

router = APIRouter()

@router.get("/", response_model=List[Category])
def read_categories(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 100
):
    categories = category_crud.get_multi(db, skip=skip, limit=limit)
    return categories

@router.post("/", response_model=Category)
def create_category(
    *,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    category_in: CategoryCreate
):
    category = category_crud.get_by_name(db, name=category_in.name)
    if category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )
    
    category = category_crud.create(db, category_in=category_in)
    return category

@router.put("/{category_id}", response_model=Category)
def update_category(
    *,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    category_id: int,
    category_in: CategoryUpdate
):
    category = category_crud.get(db, category_id=category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    category = category_crud.update(db, db_category=category, category_in=category_in)
    return category

@router.delete("/{category_id}", response_model=Category)
def delete_category(
    *,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    category_id: int
):
    category = category_crud.get(db, category_id=category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    category = category_crud.remove(db, category_id=category_id)
    return category