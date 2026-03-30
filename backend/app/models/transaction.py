from sqlalchemy import Column, Integer, Float, String, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from datetime import date
from app.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    base_amount = Column(Float, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    date = Column(Date, nullable=False, default=date.today)
    description = Column(Text, nullable=True)

    # Связи
    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")