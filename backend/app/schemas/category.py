from pydantic import BaseModel
from typing import Optional
from app.models.category import TransactionType

class CategoryBase(BaseModel):
    name: str
    type: TransactionType
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[TransactionType] = None
    description: Optional[str] = None

class Category(CategoryBase):
    id: int
    
    class Config:
        from_attributes = True