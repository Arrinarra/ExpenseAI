from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionOut
from app.crud import transaction as crud

router = APIRouter()

@router.post("/", response_model=TransactionOut)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud.create_transaction(db=db, transaction=transaction, user_id=current_user.id)

@router.get("/", response_model=List[TransactionOut])
def read_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    category_id: Optional[int] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    skip: int = 0,
    limit: int = 100
):
    transactions = crud.get_transactions(
        db, user_id=current_user.id,
        category_id=category_id,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=limit
    )
    return transactions

@router.get("/{transaction_id}", response_model=TransactionOut)
def read_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_transaction = crud.get_transaction(db, transaction_id, current_user.id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction

@router.put("/{transaction_id}", response_model=TransactionOut)
def update_transaction(
    transaction_id: int,
    transaction_update: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_transaction = crud.get_transaction(db, transaction_id, current_user.id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return crud.update_transaction(db, db_transaction, transaction_update)

@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_transaction = crud.get_transaction(db, transaction_id, current_user.id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    crud.delete_transaction(db, db_transaction)