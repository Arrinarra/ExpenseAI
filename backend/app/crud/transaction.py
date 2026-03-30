from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from app.crud.exchange_rate import get_latest_rate
from app.core.config import settings
from fastapi import HTTPException

def get_transaction(db: Session, transaction_id: int, user_id: int) -> Optional[Transaction]:
    return db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == user_id
    ).first()

def get_transactions(
    db: Session,
    user_id: int,
    category_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Transaction]:
    query = db.query(Transaction).filter(Transaction.user_id == user_id)
    if category_id is not None:
        query = query.filter(Transaction.category_id == category_id)
    if date_from is not None:
        query = query.filter(Transaction.date >= date_from)
    if date_to is not None:
        query = query.filter(Transaction.date <= date_to)
    return query.order_by(Transaction.date.desc()).offset(skip).limit(limit).all()

def create_transaction(db: Session, transaction: TransactionCreate, user_id: int) -> Transaction:
    # Получаем курс из валюты транзакции в базовую валюту (USD)
    rate = get_latest_rate(db, transaction.currency, settings.BASE_CURRENCY)
    if rate is None:
        # Если курс не найден, можно либо бросить ошибку, либо установить base_amount = None
        raise HTTPException(status_code=400, detail=f"Exchange rate for {transaction.currency} to {settings.BASE_CURRENCY} not found")
    base_amount = transaction.amount * rate  # переводим в базовую валюту

    db_transaction = Transaction(
        user_id=user_id,
        amount=transaction.amount,
        currency=transaction.currency,
        base_amount=base_amount,
        category_id=transaction.category_id,
        date=transaction.date,
        description=transaction.description
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def update_transaction(db: Session, db_transaction: Transaction, transaction_update: TransactionUpdate) -> Transaction:
    for field, value in transaction_update.dict(exclude_unset=True).items():
        setattr(db_transaction, field, value)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def delete_transaction(db: Session, db_transaction: Transaction) -> None:
    db.delete(db_transaction)
    db.commit()