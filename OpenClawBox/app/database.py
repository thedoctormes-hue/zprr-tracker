"""Database for OpenClawBox API - PostgreSQL with SQLite fallback."""

import os
from typing import Optional
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

DATABASE_URL = os.getenv("DATABASE_URL", "")

# Fallback to SQLite if PostgreSQL not configured
USE_SQLITE = not DATABASE_URL

if not USE_SQLITE:
    import psycopg2
    from psycopg2.extras import RealDictCursor

    @contextmanager
    def get_db():
        """Get PostgreSQL connection."""
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        try:
            yield conn
        finally:
            conn.close()
else:
    import sqlite3

    @contextmanager
    def get_db():
        """Get SQLite connection."""
        db_path = Path(__file__).parent.parent / "openclawbox.db"
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()


@dataclass
class User:
    telegram_id: int
    api_key: str
    tier: str = "freemium"
    daily_limit: int = 5000
    used_today: int = 0


def init_db():
    """Initialize database schema."""
    with get_db() as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                api_key TEXT UNIQUE NOT NULL,
                tier TEXT DEFAULT 'freemium',
                daily_limit INTEGER DEFAULT 5000,
                used_today INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS usage_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER,
                provider TEXT,
                tokens INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()


def create_user(telegram_id: int) -> str:
    """Create user and return API key."""
    import secrets
    api_key = f"ocb_sk_{secrets.token_urlsafe(24)}"

    with get_db() as conn:
        c = conn.cursor()
        if USE_SQLITE:
            c.execute(
                "INSERT OR IGNORE INTO users (telegram_id, api_key) VALUES (?, ?)",
                (telegram_id, api_key)
            )
            c.execute("SELECT api_key FROM users WHERE telegram_id = ?", (telegram_id,))
        else:
            c.execute(
                "INSERT INTO users (telegram_id, api_key) VALUES (%s, %s) "
                "ON CONFLICT (telegram_id) DO UPDATE SET api_key = EXCLUDED.api_key "
                "RETURNING api_key",
                (telegram_id, api_key)
            )
        result = c.fetchone()
        conn.commit()

    return result["api_key"]


def get_user_by_api_key(api_key: str) -> Optional[User]:
    """Get user by API key."""
    with get_db() as conn:
        c = conn.cursor()
        if USE_SQLITE:
            c.execute("SELECT * FROM users WHERE api_key = ?", (api_key,))
        else:
            c.execute("SELECT * FROM users WHERE api_key = %s", (api_key,))
        row = c.fetchone()

        if not row:
            return None

        return User(
            telegram_id=row["telegram_id"],
            api_key=row["api_key"],
            tier=row["tier"],
            daily_limit=row["daily_limit"],
            used_today=row["used_today"]
        )


def check_rate_limit(api_key: str, tokens: int) -> tuple[bool, int]:
    """Check if user can make request. Returns (allowed, remaining)."""
    user = get_user_by_api_key(api_key)
    if not user:
        return False, 0

    remaining = user.daily_limit - user.used_today
    return remaining >= tokens, remaining


def increment_usage(api_key: str, tokens: int, provider: str) -> bool:
    """Increment user usage. Returns True if under limit."""
    with get_db() as conn:
        c = conn.cursor()

        if USE_SQLITE:
            c.execute("SELECT used_today, daily_limit FROM users WHERE api_key = ?", (api_key,))
            c.execute(
                "UPDATE users SET used_today = used_today + ? WHERE api_key = ?",
                (tokens, api_key)
            )
            c.execute(
                "INSERT INTO usage_log (telegram_id, provider, tokens) "
                "SELECT telegram_id, ?, ? FROM users WHERE api_key = ?",
                (provider, tokens, api_key)
            )
        else:
            c.execute("SELECT used_today, daily_limit FROM users WHERE api_key = %s", (api_key,))
            c.execute(
                "UPDATE users SET used_today = used_today + %s WHERE api_key = %s",
                (tokens, api_key)
            )
            c.execute(
                "INSERT INTO usage_log (telegram_id, provider, tokens) "
                "SELECT telegram_id, %s, %s FROM users WHERE api_key = %s",
                (provider, tokens, api_key)
            )
        conn.commit()
        return True


# Initialize on import
init_db()