# backend/app/crud/category.py
@"
from sqlalchemy.orm import Session
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate
from typing import List, Optional

class CRUDCategory:
    def get(self, db: Session, category_id: int) -> Optional[Category]:
        return db.query(Category).filter(Category.id == category_id).first()
    
    def get_by_name(self, db: Session, name: str) -> Optional[Category]:
        return db.query(Category).filter(Category.name == name).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Category]:
        return db.query(Category).offset(skip).limit(limit).all()
    
    def create(self, db: Session, category_in: CategoryCreate) -> Category:
        db_category = Category(**category_in.model_dump())
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    
    def update(self, db: Session, db_category: Category, category_in: CategoryUpdate) -> Category:
        update_data = category_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_category, field, value)
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    
    def remove(self, db: Session, category_id: int) -> Category:
        category = db.query(Category).filter(Category.id == category_id).first()
        db.delete(category)
        db.commit()
        return category

category = CRUDCategory()
"@ | Set-Content -Path backend\app\crud\category.py -Encoding UTF8