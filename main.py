# main.py
import asyncio
import httpx
import logging
from datetime import datetime
from functools import wraps
from typing import List, Callable
import os

from tenacity import retry, wait_fixed, stop_after_attempt, before_log
from prometheus_client import start_http_server, Summary, Counter

from config import settings
from database import AsyncDatabaseManager
from parser import parse_rss_feed_from_text, analyze_text_for_keywords_advanced, setup_nltk
from telegram import TelegramClient

# --- Настройка Prometheus-метрик ---
REQUEST_TIME = Summary('request_processing_seconds', 'Время обработки RSS-ленты')
PROCESSED_ITEMS = Counter('rss_items_processed_total', 'Общее количество обработанных постов')
HTTP_ERRORS = Counter('http_errors_total', 'Общее количество HTTP-ошибок')

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(levelname)s - %(message)s')

# --- Декоратор для логирования асинхронной функции ---
def log_async_execution(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = datetime.now()
        logging.info(f"Запуск асинхронной функции '{func.__name__}'...")
        result = await func(*args, **kwargs)
        end_time = datetime.now()
        duration = end_time - start_time
        logging.info(f"Асинхронная функция '{func.__name__}' завершена за {duration}.")
        return result
    return wrapper

# --- Асинхронный обработчик для одного RSS-канала ---
async def process_single_feed_async(client: httpx.AsyncClient, url: str, db_manager: AsyncDatabaseManager, telegram_client: TelegramClient, notification_queue: asyncio.Queue):
    logging.info(f"Начинаем асинхронную обработку RSS-ленты: {url}")
    with REQUEST_TIME.time():
        try:
            response = await client.get(url, timeout=settings.request_timeout)
            response.raise_for_status()
            content = response.text
            for post in parse_rss_feed_from_text(content):
                text_to_analyze = f"{post['title']} {post['summary']}"
                keywords = analyze_text_for_keywords_advanced(text_to_analyze)
                
                post_data = {
                    'title': post['title'],
                    'summary': post['summary'],
                    'link': post['link'],
                    'keywords': ', '.join(keywords),
                    'published_date': post.get('published') or datetime.now().isoformat()
                }
                
                is_new_post = await db_manager.insert_post(post_data)
                
                if is_new_post and telegram_client.is_enabled:
                    message = f"**Новая статья!**\n\n**Заголовок:** {post_data['title']}\n**Ссылка:** {post_data['link']}\n**Ключевые слова:** {post_data['keywords']}"
                    await notification_queue.put(message)
                PROCESSED_ITEMS.inc()
        except httpx.HTTPError as e:
            logging.error(f"Ошибка HTTP при загрузке URL {url}: {e}")
            HTTP_ERRORS.inc()
        except Exception as e:
            logging.error(f"Критическая ошибка при обработке URL {url}: {e}")
            HTTP_ERRORS.inc()
    logging.info(f"Завершили асинхронную обработку RSS-ленты: {url}")

# --- Фоновая задача для отправки уведомлений из очереди ---
async def notification_worker(client: httpx.AsyncClient, telegram_client: TelegramClient, notification_queue: asyncio.Queue):
    while True:
        message = await notification_queue.get()
        try:
            await telegram_client.send_notification(client, message)
        except Exception as e:
            logging.error(f"Ошибка при обработке уведомления из очереди: {e}")
        finally:
            notification_queue.task_done()

# --- Основная асинхронная функция ---
@log_async_execution
async def main_processor():
    db_manager = AsyncDatabaseManager()
    telegram_client = TelegramClient()
    
    await db_manager.initialize_pool()
    notification_queue = asyncio.Queue()

    start_http_server(8000)
    
    async with httpx.AsyncClient() as client:
        worker_task = asyncio.create_task(notification_worker(client, telegram_client, notification_queue))
        try:
            tasks = [process_single_feed_async(client, url, db_manager, telegram_client, notification_queue) for url in settings.rss_feeds]
            await asyncio.gather(*tasks)
            await notification_queue.join()
        finally:
            worker_task.cancel()
            await db_manager.close_pool()

# --- Точка входа в программу ---
if __name__ == "__main__":
    setup_nltk()
    try:
        asyncio.run(main_processor())
    except Exception as e:
        logging.critical(f"Произошла критическая ошибка: {e}")
    
    logging.info("\n--- Проверка базы данных (последние 5 записей) ---")
    async def print_results():
        async with aiosqlite.connect(settings.db_name) as conn:
            cursor = await conn.execute("SELECT title, keywords FROM posts ORDER BY published_date DESC LIMIT 5")
            rows = await cursor.fetchall()
            for row in rows:
                logging.info(f"Заголовок: {row[0]}\nКлючевые слова: {row[1]}\n---")
    
    asyncio.run(print_results())