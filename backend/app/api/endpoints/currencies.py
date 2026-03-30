from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.exchange_service import fetch_exchange_rates
from app.crud.exchange_rate import save_rates
from app.core.config import settings

router = APIRouter()

@router.post("/update")
async def update_currencies(db: Session = Depends(get_db)):
    try:
        rates = await fetch_exchange_rates()
        # Добавляем курс USD к USD = 1 (на всякий случай)
        rates[settings.BASE_CURRENCY] = 1.0
        save_rates(db, rates, base_currency=settings.BASE_CURRENCY)
        return {"status": "success", "message": f"Updated {len(rates)} currencies"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))