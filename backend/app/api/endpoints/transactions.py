from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionOut
from app.crud import transaction as crud
from app.crud.exchange_rate import convert_from_base
from app.core.config import settings

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
    limit: int = 100,
    base_currency: str = Query("USD", description="Валюта для отображения сумм")
):
    transactions = crud.get_transactions(
        db, user_id=current_user.id,
        category_id=category_id,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=limit
    )
    result = []
    for tx in transactions:
        # Преобразуем SQLAlchemy объект в Pydantic схему
        out = TransactionOut.model_validate(tx)
        if base_currency != settings.BASE_CURRENCY:
            try:
                converted = convert_from_base(db, tx.base_amount, base_currency)
                out.converted_amount = converted
            except ValueError:
                # Если курс не найден, оставляем сумму в USD
                out.converted_amount = tx.base_amount
        else:
            # Если запрошена базовая валюта, показываем исходную сумму в валюте транзакции
            out.converted_amount = tx.amount
        result.append(out)
    return result

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