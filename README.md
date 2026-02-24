# ExpenseAI - Умный трекинг финансов с AI-рекомендациями

## 🚀 О проекте
Веб-приложение для мониторинга личных финансов с анализом паттернов трат, мультивалютностью и ML-рекомендациями.

## 🛠 Технологический стек
- **Backend**: Python + FastAPI, SQLAlchemy, Alembic, scikit-learn
- **Database**: PostgreSQL
- **Frontend**: HTML/JS, Chart.js
- **ML**: KMeans кластеризация, TF-IDF для анализа описаний
- **Java**: JavaFX десктоп-клиент (опционально)

## 📦 Установка и запуск

### Предварительные требования
- Docker и Docker Compose
- Python 3.11+ (для локальной разработки)
- Java 17+ (для JavaFX клиента)

### Запуск с Docker Compose
```bash
# Клонировать репозиторий
git clone https://github.com/Arrinarra/expenseai.git
cd expenseai

# Запустить сервисы
docker-compose up -d

# Проверить логи
docker-compose logs -f
