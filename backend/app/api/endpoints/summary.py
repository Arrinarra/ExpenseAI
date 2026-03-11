from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import date, timedelta
from typing import Dict

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.transaction import Transaction

router = APIRouter()

@router.get("/summary")
def get_summary(
    period: str = Query("month", pattern="^(week|month|year)$"),
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

    income = func.sum(case((Transaction.amount > 0, Transaction.amount), else_=0))
    expense = func.sum(case((Transaction.amount < 0, -Transaction.amount), else_=0))

    result = db.query(
        income.label("total_income"),
        expense.label("total_expense")
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= start_date
    ).first()

    total_income = result.total_income or 0.0
    total_expense = result.total_expense or 0.0
    balance = total_income - total_expense

    return {
        "period": period,
        "start_date": start_date.isoformat(),
        "end_date": today.isoformat(),
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance
    }