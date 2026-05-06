"""SQLite хранилище для истории запросов."""

import aiosqlite
from pathlib import Path

DB_FILE = Path(__file__).parent.parent / "llm_history.db"


async def init_db():
    """Инициализирует таблицы."""
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                model_type TEXT,
                prompt TEXT,
                models_used TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id INTEGER,
                model_id TEXT,
                response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (request_id) REFERENCES requests(id)
            )
        """)
        await db.commit()


async def save_request(user_id: int, username: str, model_type: str, prompt: str, models_used: list[str]):
    """Сохраняет запрос."""
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute(
            "INSERT INTO requests (user_id, username, model_type, prompt, models_used) VALUES (?, ?, ?, ?, ?)",
            (user_id, username, model_type, prompt, ",".join(models_used))
        )
        await db.commit()
        return cursor.lastrowid


async def save_response(request_id: int, model_id: str, response: str):
    """Сохраняет ответ модели."""
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute(
            "INSERT INTO responses (request_id, model_id, response) VALUES (?, ?, ?)",
            (request_id, model_id, response[:1000])  # Ограничиваем длину
        )
        await db.commit()


async def get_user_history(user_id: int, limit: int = 10) -> list[dict]:
    """Получает историю пользователя."""
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT r.prompt, r.model_type, r.models_used, r.created_at,
                   GROUP_CONCAT(resp.model_id || ': ' || resp.response, '|||') as responses
            FROM requests r
            LEFT JOIN responses resp ON resp.request_id = r.id
            WHERE r.user_id = ?
            GROUP BY r.id
            ORDER BY r.created_at DESC
            LIMIT ?
        """, (user_id, limit))
        rows = await cursor.fetchall()
        return [{"prompt": r["prompt"][:50], "model_type": r["model_type"],
                 "created_at": r["created_at"]} for r in rows]