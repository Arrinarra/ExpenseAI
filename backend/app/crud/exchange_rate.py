from sqlalchemy.orm import Session
from datetime import date
from app.models.exchange_rate import ExchangeRate
from app.core.config import settings

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

def get_latest_rate(db: Session, from_currency: str, to_currency: str) -> float | None:
    """
    Возвращает последний известный курс из БД.
    Если прямой курс не найден, пробует обратный и возвращает 1/rate.
    """
    # Прямой курс
    rate_obj = db.query(ExchangeRate).filter(
        ExchangeRate.from_currency == from_currency,
        ExchangeRate.to_currency == to_currency
    ).order_by(ExchangeRate.date.desc()).first()
    if rate_obj:
        return rate_obj.rate
    
    # Обратный курс
    rate_obj = db.query(ExchangeRate).filter(
        ExchangeRate.from_currency == to_currency,
        ExchangeRate.to_currency == from_currency
    ).order_by(ExchangeRate.date.desc()).first()
    if rate_obj:
        return 1 / rate_obj.rate
    
    return None

def convert_from_base(db: Session, amount_usd: float, to_currency: str) -> float:
    """
    Конвертирует сумму из USD в целевую валюту.
    Возвращает amount * rate (USD -> to_currency).
    """
    if to_currency == settings.BASE_CURRENCY:
        return amount_usd
    rate = get_latest_rate(db, settings.BASE_CURRENCY, to_currency)
    if rate is None:
        raise ValueError(f"Exchange rate from USD to {to_currency} not found")
    return amount_usd * rate