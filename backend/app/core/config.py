from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "ExpenseAI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str = "postgresql://expenseai_user:expenseai_pass@postgres:5432/expenseai_db"
    
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    EXCHANGE_API_URL: str = "https://api.exchangerate-api.com/v4/latest/USD"
    BASE_CURRENCY: str = "USD"
    
    model_config = ConfigDict(case_sensitive=True)

settings = Settings()