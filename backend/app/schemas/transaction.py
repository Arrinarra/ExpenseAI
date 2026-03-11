from pydantic import BaseModel, validator
from datetime import date
from typing import Optional
from pydantic import BaseModel, field_validator

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

    class Config:
        orm_mode = True