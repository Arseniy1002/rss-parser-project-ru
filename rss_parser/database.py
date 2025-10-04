import aiosqlite
import hashlib
import logging
from typing import Dict

# CRITICAL FIX: Относительный импорт
from .config import settings

class AsyncDatabaseManager:
    def __init__(self):
        self.db_pool = None

    async def initialize_pool(self):
        """Создает пул соединений и инициализирует таблицу."""
        self.db_pool = await aiosqlite.connect(settings.db_name, isolation_level=None)
        await self.db_pool.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                summary TEXT,
                link TEXT NOT NULL,
                keywords TEXT,
                published_date TEXT,
                content_hash TEXT UNIQUE NOT NULL
            )
        ''')
        await self.db_pool.commit()

    async def close_pool(self):
        """Закрывает пул соединений."""
        if self.db_pool:
            await self.db_pool.close()

    async def insert_post(self, post_data: Dict) -> bool:
        """Вставляет один пост в базу данных асинхронно."""
        try:
            content_to_hash = post_data['title'] + post_data['summary'] + post_data['link']
            content_hash = hashlib.sha256(content_to_hash.encode('utf-8')).hexdigest()
            
            cursor = await self.db_pool.execute('''
                INSERT INTO posts (title, summary, link, keywords, published_date, content_hash)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                post_data['title'],
                post_data['summary'],
                post_data['link'],
                post_data['keywords'],
                post_data.get('published_date', None),
                content_hash
            ))
            if cursor.rowcount > 0:
                await self.db_pool.commit()
                logging.info(f"Новый пост добавлен: {post_data['title']}")
                return True
            return False
        except aiosqlite.IntegrityError:
            logging.debug(f"Пост уже существует (хеш): {post_data['link']}")
            return False
