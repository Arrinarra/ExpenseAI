from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
from typing import Dict

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.transaction import Transaction
from app.crud.exchange_rate import get_latest_rate
from app.core.config import settings

router = APIRouter()

@router.get("/summary")
def get_summary(
    period: str = Query("month", pattern="^(week|month|year)$"),
    base_currency: str = Query("USD", description="Валюта для отображения сводки"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict:
    today = date.today()
    if period == "week":
        start_date = today - timedelta(days=today.weekday())
    elif period == "month":
        start_date = today.replace(day=1)
    else:  # year
        start_date = today.replace(month=1, day=1)

    # Доходы (amount > 0) в USD
    total_income_usd = db.query(func.sum(Transaction.base_amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= start_date,
        Transaction.amount > 0
    ).scalar() or 0.0

    # Расходы (amount < 0) в USD
    total_expense_usd = db.query(func.sum(Transaction.base_amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= start_date,
        Transaction.amount < 0
    ).scalar() or 0.0

    balance_usd = total_income_usd - total_expense_usd

    # Конвертация в целевую валюту
    if base_currency != settings.BASE_CURRENCY:
        rate = get_latest_rate(db, settings.BASE_CURRENCY, base_currency)
        if rate is None:
            # Если курс не найден, возвращаем USD
            total_income = total_income_usd
            total_expense = total_expense_usd
            balance = balance_usd
            actual_currency = settings.BASE_CURRENCY
        else:
            total_income = total_income_usd * rate
            total_expense = total_expense_usd * rate
            balance = balance_usd * rate
            actual_currency = base_currency
    else:
        total_income = total_income_usd
        total_expense = total_expense_usd
        balance = balance_usd
        actual_currency = settings.BASE_CURRENCY

    return {
        "period": period,
        "start_date": start_date.isoformat(),
        "end_date": today.isoformat(),
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance,
        "currency": actual_currency
    }