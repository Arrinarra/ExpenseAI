from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionUpdate

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
    db_transaction = Transaction(**transaction.dict(), user_id=user_id)
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