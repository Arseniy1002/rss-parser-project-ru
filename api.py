# api.py
from fastapi import FastAPI, HTTPException
from typing import List, Optional
import aiosqlite
import logging

from config import settings

app = FastAPI(title="RSS Parser API")
logging.basicConfig(level=logging.INFO)

# --- Класс для работы с базой данных (для API) ---
class AsyncDatabaseAPI:
    def __init__(self, db_name: str):
        self.db_name = db_name

    async def get_all_posts(self) -> List[dict]:
        async with aiosqlite.connect(self.db_name) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT title, summary, link, keywords, published_date FROM posts ORDER BY published_date DESC LIMIT 100")
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_posts_by_keyword(self, keyword: str) -> List[dict]:
        async with aiosqlite.connect(self.db_name) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT title, summary, link, keywords, published_date FROM posts WHERE keywords LIKE ? ORDER BY published_date DESC LIMIT 100", (f"%{keyword}%",))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

db_api = AsyncDatabaseAPI(settings.db_name)

@app.get("/")
async def read_root():
    """Главная страница API."""
    return {"message": "Добро пожаловать в API RSS-парсера!"}

@app.get("/posts", response_model=List[dict])
async def get_posts():
    """Получить список последних постов."""
    posts = await db_api.get_all_posts()
    return posts

@app.get("/posts/search", response_model=List[dict])
async def search_posts(keyword: str):
    """Найти посты по ключевому слову."""
    posts = await db_api.get_posts_by_keyword(keyword)
    if not posts:
        raise HTTPException(status_code=404, detail=f"Постов с ключевым словом '{keyword}' не найдено.")
    return posts