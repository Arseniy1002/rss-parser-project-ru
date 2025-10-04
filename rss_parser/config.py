# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Класс для загрузки настроек из переменных окружения.
    Pydantic автоматически валидирует и загружает значения.
    """
    rss_feeds: list[str] = [
        'https://habr.com/ru/rss/hubs/python/all/',
        'https://lenta.ru/rss',
        'http://feeds.bbci.co.uk/news/rss.xml',
        'https://habr.com/ru/rss/hubs/django/all/'
    ]
    db_name: str = "news_database_ultimate.db"
    telegram_bot_token: str = "ci_dummy_token"
    telegram_chat_id: str = "ci_dummy_chat_id"
    request_timeout: int = 10
    retry_attempts: int = 3
    retry_wait_time: int = 5

    class Config:
        env_file = ".env"

settings = Settings()