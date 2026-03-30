from sqlalchemy.orm import Session
from datetime import date
from app.models.exchange_rate import ExchangeRate

def save_rates(db: Session, rates: dict, base_currency: str = "USD"):
    """
    Сохраняет курсы валют в БД.
    rates: словарь {currency: rate} относительно base_currency.
    """
    today = date.today()
    for currency, rate in rates.items():
        # Проверяем, есть ли уже курс на сегодня для этой пары
        existing = db.query(ExchangeRate).filter(
            ExchangeRate.date == today,
            ExchangeRate.from_currency == base_currency,
            ExchangeRate.to_currency == currency
        ).first()
        if existing:
            existing.rate = rate
        else:
            db.add(ExchangeRate(
                date=today,
                from_currency=base_currency,
                to_currency=currency,
                rate=rate
            ))
    db.commit()

def get_latest_rate(db: Session, from_currency: str, to_currency: str) -> float:
    """
    Возвращает последний известный курс из БД.
    """
    rate_obj = db.query(ExchangeRate).filter(
        ExchangeRate.from_currency == from_currency,
        ExchangeRate.to_currency == to_currency
    ).order_by(ExchangeRate.date.desc()).first()
    return rate_obj.rate if rate_obj else None