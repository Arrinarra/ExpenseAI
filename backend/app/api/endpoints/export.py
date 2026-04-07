from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import date, timedelta
import csv
from io import StringIO

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.transaction import Transaction
from app.crud.exchange_rate import get_latest_rate
from app.core.config import settings

router = APIRouter()

@router.get("/csv")
def export_csv(
    period: str = Query("month", pattern="^(week|month|year)$"),
    currency: str = Query("USD", description="Валюта для конвертации сумм"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    today = date.today()
    if period == "week":
        start_date = today - timedelta(days=today.weekday())
    elif period == "month":
        start_date = today.replace(day=1)
    else:  # year
        start_date = today.replace(month=1, day=1)
    
    # Получаем транзакции за период
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= start_date
    ).order_by(Transaction.date).all()
    
    # Конвертируем суммы в целевую валюту
    rate = 1.0
    if currency != settings.BASE_CURRENCY:
        rate = get_latest_rate(db, settings.BASE_CURRENCY, currency)
        if rate is None:
            rate = 1.0
    
    # Создаем CSV
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Category", "Description", "Amount", "Currency", "Amount (converted)", "Converted Currency"])
    
    for tx in transactions:
        # Получаем имя категории
        category_name = tx.category.name if tx.category else ""
        amount_converted = tx.base_amount * rate if tx.base_amount is not None else tx.amount
        writer.writerow([
            tx.date.isoformat(),
            category_name,
            tx.description or "",
            tx.amount,
            tx.currency,
            round(amount_converted, 2),
            currency
        ])
    
    # Возвращаем файл
    response = StreamingResponse(iter([output.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename=transactions_{period}_{today}.csv"
    return response