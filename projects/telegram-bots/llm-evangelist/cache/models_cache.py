"""Кэширование моделей OpenRouter с TTL 1 час."""

import json
import time
from pathlib import Path

CACHE_FILE = Path(__file__).parent.parent / "models_cache.json"
CACHE_TTL = 3600  # 1 hour


def get_cached_models() -> tuple[list[dict], dict] | None:
    """Получает кэшированные модели если не истёк TTL."""
    if not CACHE_FILE.exists():
        return None

    try:
        data = json.loads(CACHE_FILE.read_text())
        cached_at = data.get("timestamp", 0)

        if time.time() - cached_at > CACHE_TTL:
            return None

        return data.get("models", []), data.get("pricing", {})
    except Exception:
        return None


def save_models_cache(models: list[dict], pricing: dict):
    """Сохраняет модели в кэш."""
    CACHE_FILE.write_text(json.dumps({
        "timestamp": time.time(),
        "models": models,
        "pricing": pricing
    }, indent=2))