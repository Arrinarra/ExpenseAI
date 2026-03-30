from pydantic import BaseModel, field_validator
from datetime import date
from typing import Optional

class TransactionBase(BaseModel):
    amount: float
    currency: str = "USD"
    category_id: int
    date: date
    description: Optional[str] = None

    @field_validator('amount')
    def amount_must_be_non_zero(cls, v):
        if v == 0:
            raise ValueError('amount cannot be zero')
        return v

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    currency: Optional[str] = None
    category_id: Optional[int] = None
    date: Optional[date] = None
    description: Optional[str] = None

    @field_validator('amount')
    def amount_must_be_non_zero(cls, v):
        if v is not None and v == 0:
            raise ValueError('amount cannot be zero')
        return v

class TransactionOut(TransactionBase):
    id: int
    user_id: int
    base_amount: Optional[float] = None   # <-- добавлено
    converted_amount: Optional[float] = None

    class Config:
        from_attributes = True   # <-- заменено (вместо orm_mode)