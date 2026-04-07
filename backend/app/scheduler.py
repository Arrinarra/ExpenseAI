from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import asyncio
from app.services.exchange_service import fetch_exchange_rates
from app.crud.exchange_rate import save_rates
from app.database import SessionLocal
from app.core.config import settings

def update_exchange_rates_job():
    """Синхронная обёртка для асинхронной функции."""
    print("Запуск обновления курсов валют...")
    # Создаём новый event loop для выполнения асинхронной функции
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        rates = loop.run_until_complete(fetch_exchange_rates())
        if rates:
            rates[settings.BASE_CURRENCY] = 1.0
            db = SessionLocal()
            try:
                save_rates(db, rates, base_currency=settings.BASE_CURRENCY)
                print(f"Курсы обновлены: {len(rates)} валют")
            finally:
                db.close()
        else:
            print("Не удалось получить курсы")
    except Exception as e:
        print(f"Ошибка обновления курсов: {e}")
    finally:
        loop.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    # Запуск через 10 секунд после старта для теста, затем ежедневно в 3:00
    scheduler.add_job(
        update_exchange_rates_job,
        trigger='cron',
        hour=3,
        minute=0,
        id="update_currencies",
        next_run_time=datetime.now() + timedelta(seconds=10)
    )
    scheduler.start()
    print("Планировщик запущен")