import httpx
from app.core.config import settings

async def fetch_exchange_rates() -> dict:
    """
    Получает курсы валют относительно базовой валюты (USD) с внешнего API.
    Возвращает словарь {валюта: курс}.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(settings.EXCHANGE_API_URL)
        response.raise_for_status()
        data = response.json()
    # data содержит поле "rates" со словарём курсов
    return data.get("rates", {})