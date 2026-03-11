from sqlalchemy import Column, Integer, String, Enum
from app.database import Base
import enum
from sqlalchemy.orm import relationship

class TransactionType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    description = Column(String)

    transactions = relationship("Transaction", back_populates="category")