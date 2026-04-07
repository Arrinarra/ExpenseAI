from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import date, timedelta
from typing import List, Dict, Any

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.transaction import Transaction
from app.models.category import Category
from app.crud.exchange_rate import get_latest_rate, convert_from_base
from app.core.config import settings

router = APIRouter()

@router.get("/monthly")
def get_analytics_monthly(
    period: str = Query("month", pattern="^(week|month|year)$"),
    currency: str = Query("USD", description="Валюта для отображения сумм"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    # Определяем начальную дату
    today = date.today()
    if period == "week":
        start_date = today - timedelta(days=today.weekday())
    elif period == "month":
        start_date = today.replace(day=1)
    else:  # year
        start_date = today.replace(month=1, day=1)
    
    # Запрос: расходы (amount < 0) по категориям, сумма base_amount
    results = db.query(
        Category.name,
        func.sum(Transaction.base_amount).label("total")
    ).join(
        Transaction, Transaction.category_id == Category.id
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= start_date,
        Transaction.amount < 0  # только расходы
    ).group_by(Category.name).all()
    
    # Конвертируем суммы в целевую валюту
    total_spending_usd = sum(r.total for r in results)
    # Если запрошена не USD, конвертируем общую сумму и каждую категорию
    rate = 1.0
    if currency != settings.BASE_CURRENCY:
        rate = get_latest_rate(db, settings.BASE_CURRENCY, currency)
        if rate is None:
            rate = 1.0  # fallback
    # Формируем ответ
    categories_data = []
    for name, total in results:
        total_converted = total * rate
        percent = (total / total_spending_usd * 100) if total_spending_usd > 0 else 0
        categories_data.append({
            "category": name,
            "amount": round(total_converted, 2),
            "percent": round(percent, 2)
        })
    # Сортируем по убыванию суммы
    categories_data.sort(key=lambda x: x["amount"], reverse=True)
    return {
        "period": period,
        "start_date": start_date.isoformat(),
        "end_date": today.isoformat(),
        "currency": currency,
        "data": categories_data
    }

@router.get("/trends")
def get_analytics_trends(
    period: str = Query("month", pattern="^(week|month|year)$"),
    currency: str = Query("USD", description="Валюта для отображения сумм"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    today = date.today()
    if period == "week":
        # группировка по дням
        start_date = today - timedelta(days=today.weekday())
        # Для группировки используем date_trunc
        group_by = func.date_trunc('day', Transaction.date)
        date_format = '%Y-%m-%d'
    elif period == "month":
        start_date = today.replace(day=1)
        group_by = func.date_trunc('day', Transaction.date)
        date_format = '%Y-%m-%d'
    else:  # year
        start_date = today.replace(month=1, day=1)
        group_by = func.date_trunc('month', Transaction.date)
        date_format = '%Y-%m'
    
    # Запрос: сумма base_amount за каждый день/месяц
    results = db.query(
        group_by.label("date_group"),
        func.sum(Transaction.base_amount).label("balance")
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= start_date
    ).group_by("date_group").order_by("date_group").all()
    
    # Конвертация в целевую валюту
    rate = 1.0
    if currency != settings.BASE_CURRENCY:
        rate = get_latest_rate(db, settings.BASE_CURRENCY, currency)
        if rate is None:
            rate = 1.0
    
    trend_data = []
    for date_group, balance in results:
        # date_group может быть datetime или date, приводим к строке
        date_str = date_group.strftime(date_format)
        trend_data.append({
            "date": date_str,
            "balance": round(balance * rate, 2)
        })
    return {
        "period": period,
        "currency": currency,
        "data": trend_data
    }