"""SQLite база для полной информации о моделях OpenRouter."""

import aiosqlite
from pathlib import Path
import json

DB_FILE = Path(__file__).parent.parent / "models.db"


async def init_models_db():
    """Создаёт таблицы для моделей со всеми параметрами."""
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS models (
                id TEXT PRIMARY KEY,
                name TEXT,
                created INTEGER,
                description TEXT,
                context_length INTEGER,
                architecture_tokenizer TEXT,
                architecture_modality TEXT,
                pricing_prompt TEXT,
                pricing_completion TEXT,
                pricing_image TEXT,
                pricing_request TEXT,
                top_provider_name TEXT,
                top_provider_status REAL,
                top_provider_max_tpm INTEGER,
                top_provider_max_rpm INTEGER,
                top_provider_is_moderated INTEGER,
                per_request_limits TEXT,
                supported_parameters TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_created ON models(created DESC)
        """)
        await db.commit()


async def upsert_models(models: list[dict]):
    """Обновляет или добавляет модели со всеми параметрами."""
    async with aiosqlite.connect(DB_FILE) as db:
        for m in models:
            pricing = m.get("pricing", {})
            arch = m.get("architecture", {})
            top = m.get("top_provider", {})
            limits = m.get("per_request_limits", {})

            await db.execute("""
                INSERT OR REPLACE INTO models (
                    id, name, created, description, context_length,
                    architecture_tokenizer, architecture_modality,
                    pricing_prompt, pricing_completion, pricing_image, pricing_request,
                    top_provider_name, top_provider_status, top_provider_max_tpm,
                    top_provider_max_rpm, top_provider_is_moderated,
                    per_request_limits, supported_parameters
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                m.get("id"),
                m.get("name"),
                m.get("created", 0),
                m.get("description"),
                m.get("context_length"),
                arch.get("tokenizer"),
                arch.get("modality"),
                pricing.get("prompt"),
                pricing.get("completion"),
                pricing.get("image"),
                pricing.get("request"),
                top.get("name"),
                top.get("status"),
                top.get("max_tpm"),
                top.get("max_rpm"),
                1 if top.get("is_moderated") else 0,
                json.dumps(limits),
                json.dumps(m.get("supported_parameters", []))
            ))
        await db.commit()


async def get_new_models(since_days: int = 1) -> list[dict]:
    """Получает модели созданные за последние N дней."""
    import time
    cutoff = int(time.time()) - (since_days * 24 * 60 * 60)

    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM models WHERE created > ? ORDER BY created DESC",
            (cutoff,)
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def get_models_count() -> int:
    """Возвращает общее количество моделей."""
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM models")
        return (await cursor.fetchone())[0]


async def get_model_by_id(model_id: str) -> dict | None:
    """Получает модель по ID."""
    async with aiosqlite.connect(DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM models WHERE id = ?", (model_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None