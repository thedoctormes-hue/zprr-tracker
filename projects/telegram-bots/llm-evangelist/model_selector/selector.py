#!/usr/bin/env python3
"""LLM Model Selector — подбор модели под задачу."""

import json
from pathlib import Path

# Полный список параметров моделей (собирается из OpenRouter API)
MODEL_COLUMNS = [
    "id", "name", "description", "context_length", "created",
    "price_prompt", "price_completion", "price_web_search", "price_cache_read",
    "architecture_modality", "input_modalities", "output_modalities", "tokenizer",
    "max_completion_tokens", "is_moderated", "supported_parameters"
]

# База моделей с полными параметрами (будет обновляться из API)
MODEL_DATA_FILE = Path(__file__).parent / "models_full.json"

def load_full_models() -> dict:
    """Загружает полные данные моделей или создаёт пустой шаблон."""
    if MODEL_DATA_FILE.exists():
        return json.loads(MODEL_DATA_FILE.read_text())
    return {}

def save_full_models(models: dict):
    """Сохраняет полные данные моделей."""
    MODEL_DATA_FILE.write_text(json.dumps(models, indent=2))

# База моделей с параметрами (ручное описание важных моделей) - DEPRECATED, используем API
MODEL_REGISTRY = {
    # Кодинг
    "google/gemini-2.5-flash": {
        "task": "code, reasoning",
        "context": 1000000,
        "price_prompt": 0.0000003,
        "price_completion": 0.000002,
        "speed": "fast",
        "best_for": "сложный код, reasoning"
    },
    "openai/gpt-4.1": {
        "task": "code, chat",
        "context": 1000000,
        "price_prompt": 0.000002,
        "price_completion": 0.000008,
        "speed": "medium",
        "best_for": "промышленный код"
    },
    "deepseek/deepseek-v4-flash": {
        "task": "code",
        "context": 128000,
        "price_prompt": 0.00000014,
        "price_completion": 0.00000014,
        "speed": "fast",
        "best_for": "быстрый код, дешёво"
    },
    "deepseek/deepseek-chat": {
        "task": "code",
        "context": 128000,
        "price_prompt": 0.0,
        "price_completion": 0.0,
        "speed": "fast",
        "best_for": "бесплатный код"
    },
    # Creative
    "mistralai/mistral-small-creative": {
        "task": "creative, writing",
        "context": 32000,
        "price_prompt": 0.00000015,
        "price_completion": 0.00000015,
        "speed": "fast",
        "best_for": "креативные тексты"
    },
    "anthropic/claude-3.7-sonnet": {
        "task": "creative, analysis",
        "context": 200000,
        "price_prompt": 0.000003,
        "price_completion": 0.000015,
        "speed": "medium",
        "best_for": "длинные креативные задачи"
    },
    # Free
    "tencent/hy3-preview:free": {
        "task": "all",
        "context": 16000,
        "price_prompt": 0.0,
        "price_completion": 0.0,
        "speed": "fast",
        "best_for": "тесты, прототипы"
    },
    "google/gemma-3-27b:free": {
        "task": "chat, reasoning",
        "context": 96000,
        "price_prompt": 0.0,
        "price_completion": 0.0,
        "speed": "medium",
        "best_for": "бесплатные тесты"
    },
    # Reasoning
    "google/gemini-2.5-flash-thinking": {
        "task": "reasoning",
        "context": 1000000,
        "price_prompt": 0.0000003,
        "price_completion": 0.000002,
        "speed": "slow",
        "best_for": "complicated reasoning"
    },
    # Economy
    "google/gemini-2.0-flash-lite-001": {
        "task": "chat",
        "context": 1000000,
        "price_prompt": 0.000000075,
        "price_completion": 0.0000003,
        "speed": "fast",
        "best_for": "бюджетный чат"
    },
}

TASK_MAPPING = {
    "code": ["deepseek/deepseek-v4-flash", "openai/gpt-4.1", "google/gemini-2.5-flash"],
    "creative": ["mistralai/mistral-small-creative", "anthropic/claude-3.7-sonnet"],
    "fast": ["google/gemini-2.5-flash", "deepseek/deepseek-v4-flash", "tencent/hy3-preview:free"],
    "cheap": ["deepseek/deepseek-v4-flash", "google/gemini-2.0-flash-lite-001", "tencent/hy3-preview:free"],
    "free": ["tencent/hy3-preview:free", "google/gemma-3-27b:free", "deepseek/deepseek-chat"],
    "reasoning": ["google/gemini-2.5-flash-thinking", "anthropic/claude-3.7-sonnet"],
}


def select_model(task: str = None, budget: str = None, speed: str = None) -> list[dict]:
    """Подбирает модели под задачу."""
    results = []

    candidates = list(MODEL_REGISTRY.items())

    # Фильтр по задаче
    if task:
        if task in TASK_MAPPING:
            allowed = TASK_MAPPING[task]
            candidates = [(k, v) for k, v in candidates if k in allowed]
        else:
            candidates = []  # Неизвестная задача → пустой результат

    # Фильтр по бюджету
    if budget == "free":
        candidates = [(k, v) for k, v in candidates if v["price_prompt"] == 0]
    elif budget == "cheap":
        candidates = [(k, v) for k, v in candidates if v["price_prompt"] < 0.000001]

    # Фильтр по скорости
    if speed:
        candidates = [(k, v) for k, v in candidates if v["speed"] == speed]

    for model_id, params in candidates:
        price = params["price_prompt"] * 1_000_000
        results.append({
            "model": model_id,
            "task": params["task"],
            "context": params["context"],
            "price_per_1m": f"${price:.4f}",
            "speed": params["speed"],
            "best_for": params["best_for"]
        })

    return sorted(results, key=lambda x: float(x["price_per_1m"].replace("$", "")))


async def fetch_and_store_full_models() -> dict:
    """Загружает и сохраняет полные данные моделей из OpenRouter API."""
    import aiohttp
    import os

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return {}

    url = "https://openrouter.ai/api/v1/models"
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    models = {}

                    for m in data.get("data", []):
                        model_id = m["id"]
                        pricing = m.get("pricing", {})

                        models[model_id] = {
                            "id": model_id,
                            "name": m.get("name", ""),
                            "description": m.get("description", ""),
                            "context_length": m.get("context_length", 0),
                            "created": m.get("created", 0),
                            "price_prompt": float(pricing.get("prompt", 0)),
                            "price_completion": float(pricing.get("completion", 0)),
                            "price_web_search": float(pricing.get("web_search", 0) or 0),
                            "price_cache_read": float(pricing.get("input_cache_read", 0) or 0),
                            "architecture_modality": m.get("architecture", {}).get("modality", ""),
                            "input_modalities": m.get("architecture", {}).get("input_modalities", []),
                            "output_modalities": m.get("architecture", {}).get("output_modalities", []),
                            "tokenizer": m.get("architecture", {}).get("tokenizer", ""),
                            "max_completion_tokens": m.get("top_provider", {}).get("max_completion_tokens"),
                            "is_moderated": m.get("top_provider", {}).get("is_moderated", False),
                            "supported_parameters": m.get("supported_parameters", [])
                        }

                    save_full_models(models)
                    return models
    except Exception as e:
        print(f"Error fetching models: {e}")

    return {}


def analyze_model_family(family: str) -> dict:
    """Анализ семейства моделей (например, mistral)."""
    models = load_full_models()
    family_models = {k: v for k, v in models.items() if family.lower() in k.lower()}

    return {
        "family": family,
        "total_models": len(family_models),
        "avg_price": sum(m.get("price_prompt", 0) for m in family_models.values()) / len(family_models) if family_models else 0,
        "models": [(k, v.get("price_prompt", 0) * 1_000_000) for k, v in family_models.items()]
    }


def compare_models(model_a: str, model_b: str) -> dict:
    """Сравнение двух моделей."""
    if model_a not in MODEL_REGISTRY or model_b not in MODEL_REGISTRY:
        return {"error": "Model not found"}

    a, b = MODEL_REGISTRY[model_a], MODEL_REGISTRY[model_b]

    return {
        "comparison": [
            {"param": "task", "a": a["task"], "b": b["task"]},
            {"param": "context", "a": f"{a['context']:,}", "b": f"{b['context']:,}"},
            {"param": "price_prompt", "a": f"${a['price_prompt']*1_000_000:.4f}/1M", "b": f"${b['price_prompt']*1_000_000:.4f}/1M"},
            {"param": "speed", "a": a["speed"], "b": b["speed"]},
        ],
        "verdict": "winner_a" if a["price_prompt"] < b["price_prompt"] else "winner_b"
    }


if __name__ == "__main__":
    # Пример: подбор для кода
    print("🏆 Модели для кода:")
    for m in select_model(task="code")[:3]:
        print(f"  • {m['model']}: {m['price_per_1m']}/1M, {m['speed']}")

    # Пример: сравнение
    print("\n🆚 Сравнение:")
    result = compare_models("deepseek/deepseek-v4-flash", "openai/gpt-4.1")
    for row in result["comparison"]:
        print(f"  {row['param']}: {row['a']} vs {row['b']}")