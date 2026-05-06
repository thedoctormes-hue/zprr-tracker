#!/usr/bin/env python3
"""LLMevangelist 2.0 - Полноценый Telegram бот для обзора LLM моделей"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import aiohttp
import aiosqlite
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent

sys.path.insert(0, str(BASE_DIR))
from scanner.discover import scan_laboratory
from analyzer.self_analysis import analyze_self
from cache.models_cache import get_cached_models, save_models_cache
from cache.history_db import init_db, save_request, get_user_history
from cache.models_db import init_models_db, upsert_models, get_new_models, get_models_count

load_dotenv(override=True)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL = os.getenv("TELEGRAM_CHANNEL")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

if not all([OPENROUTER_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL]):
    raise ValueError("Не все переменные окружения заданы в .env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent
CONFIG_FILE = BASE_DIR / "config.json"
POSTED_MODELS_FILE = BASE_DIR / "posted_models.json"
LAST_CHECK_FILE = BASE_DIR / "last_check.json"

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


def load_config() -> dict:
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {"projects": []}


def load_posted_models() -> List[str]:
    if POSTED_MODELS_FILE.exists():
        return json.loads(POSTED_MODELS_FILE.read_text())
    return []


def save_posted_models(models: List[str]):
    POSTED_MODELS_FILE.write_text(json.dumps(models, indent=2))


def to_float(val) -> float:
    try:
        return float(str(val).replace("$", "").strip())
    except (ValueError, TypeError):
        return 0.0


def model_link(model_id: str) -> str:
    return f"[{model_id}](https://openrouter.ai/{model_id})"


async def fetch_openrouter_models(force_refresh: bool = False) -> tuple[List[dict], Dict[str, dict]]:
    """Получает список моделей с OpenRouter (с кэшированием 1 час)"""
    if not force_refresh:
        cached = get_cached_models()
        if cached:
            logger.info("Using cached models")
            return cached

    url = "https://openrouter.ai/api/v1/models"
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}"}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    models = data.get("data", [])
                    pricing = {m["id"]: m.get("pricing", {}) for m in models}
                    save_models_cache(models, pricing)
                    await upsert_models(models)
                    return models, pricing
    except Exception as e:
        logger.error(f"OpenRouter: {e}")
        cached = get_cached_models()
        if cached:
            logger.info("Using stale cache")
            return cached
    return [], {}


async def fetch_model_response(model_id: str, prompt: str) -> tuple[str, str]:
    """Получает ответ от конкретной модели (с поддержкой кэширования)"""
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "X-Cache-Control": "max-age=3600"
    }
    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "max_tokens": 500
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                cache_status = resp.headers.get("x-cache-status", "unknown")
                logger.info(f"Cache status for {model_id}: {cache_status}")
                if resp.status == 200:
                    data = await resp.json()
                    return data["choices"][0]["message"]["content"], cache_status
    except Exception as e:
        logger.error(f"Model {model_id}: {e}")
    return "Ошибка получения ответа", "error"


def format_top_models(models: List[dict], limit: int = 10) -> str:
    """Формирует топ моделей по соотношению цена/качество"""
    free_models = [m for m in models if ":free" in m.get("id", "")]
    paid_models = [m for m in models if ":free" not in m.get("id", "")]

    report = "🏆 **ТОП моделей по цене/качеству**\n\n"

    if free_models:
        report += "💎 **FREE модели:**\n"
        for i, m in enumerate(free_models[:5], 1):
            report += f"{i}. {model_link(m['id'])}\n"

    if paid_models:
        report += "\n💰 **Платные (топ 5):**\n"
        for i, m in enumerate(paid_models[:5], 1):
            pricing = m.get("pricing", {})
            cost = to_float(pricing.get("prompt", 0)) * 1_000_000
            report += f"{i}. {model_link(m['id'])} — ${cost:.2f}/1M\n"

    return report


def format_models_list(models: List[dict]) -> str:
    """Формирует список доступных моделей"""
    report = f"📊 **Доступно моделей: {len(models)}**\n\n"

    free = [m for m in models if ":free" in m.get("id", "")]
    paid = [m for m in models if ":free" not in m.get("id", "")]

    report += f"💎 FREE: {len(free)}\n"
    for m in free[:5]:
        report += f"• {m['id']}\n"

    report += f"\n💰 Платные: {len(paid)}\n"
    for m in paid[:5]:
        pricing = m.get("pricing", {})
        cost = to_float(pricing.get("prompt", 0)) * 1_000_000
        report += f"• {m['id']} — ${cost:.2f}/1M\n"

    return report


def format_new_models(models: List[dict]) -> str:
    """Формирует отчёт о новых моделях."""
    report = "🆕 **Новые модели (24 часа):**\n\n"

    for m in models:
        created = m.get("created", 0)
        date_str = datetime.datetime.fromtimestamp(created).strftime("%d.%m")
        pricing = m.get("pricing", {})
        cost = to_float(pricing.get("prompt", 0)) * 1_000_000
        report += f"• {model_link(m['id'])} — {date_str}\n"
        if cost > 0:
            report += f"  💰 ${cost:.2f}/1M\n"

    return report


@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Приветствие при старте"""
    total = await get_models_count()
    await message.answer(
        "🤖 **LLM Evangelist** — бот для обзора LLM моделей!\n\n"
        f"📊 В базе: {total} моделей\n\n"
        "Команды:\n"
        "• /compare [type] [prompt] — сравнить ответы моделей\n"
        "• /models — список моделей с ценами\n"
        "• /top — топ моделей\n"
        "• /new — новые модели за 24 часа\n"
        "• /scan — сканировать проекты\n"
        "• /analyze — самоанализ\n"
        "• /stats — статистика\n"
        "• /history — история запросов\n"
        "• /help — справка"
    )


@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Справка по командам"""
    help_text = (
        "📖 **Справка по командам:**\n\n"
        "• `/start` — запуск бота\n"
        "• `/compare [type] [prompt]` — сравнить ответы моделей\n"
        "• `/models` — список доступных моделей с ценами\n"
        "• `/top` — топ моделей по соотношению цена/качество\n"
        "• `/new` — новые модели за последние 24 часа\n"
        "• `/scan` — сканировать проекты лаборатории на LLM\n"
        "• `/analyze` — самоанализ бота и рекомендации\n"
        "• `/stats` — ваша статистика запросов\n"
        "• `/history` — история ваших запросов\n\n"
        "💡 Бот автоматически постит отчёты в канал раз в сутки"
    )
    await message.answer(help_text)


@dp.message(Command("compare"))
async def cmd_compare(message: Message):
    """Сравнение ответов моделей на запрос"""
    args = message.text.split(maxsplit=2)

    model_type = "free"
    prompt = ""

    if len(args) < 2:
        await message.answer("❌ Использование: /compare [type] [prompt]\n  type: free (по умолч.), paid, all")
        return
    elif len(args) == 2:
        prompt = args[1]
    else:
        if args[1].lower() in ["free", "paid", "all"]:
            model_type = args[1].lower()
            prompt = args[2]
        else:
            prompt = args[1] + " " + args[2]

    await message.answer(f"⏳ Получаю ответы от {model_type} моделей...")

    models, _ = await fetch_openrouter_models()

    if model_type == "free":
        selected_models = [m["id"] for m in models if ":free" in m.get("id", "")]
    elif model_type == "paid":
        selected_models = [m["id"] for m in models if ":free" not in m.get("id", "")]
    else:
        selected_models = [m["id"] for m in models]

    if not selected_models:
        await message.answer(f"❌ Нет доступных {model_type} моделей")
        return

    selected = selected_models[:3]
    responses = []

    await save_request(
        message.from_user.id,
        message.from_user.username or "unknown",
        model_type,
        prompt,
        selected
    )

    for model_id in selected:
        response, cache_status = await fetch_model_response(model_id, prompt)
        responses.append((model_id, response, cache_status))

    result = f"🔍 **Сравнение по запросу:**\n`{prompt}`\n"
    result += f"**Тип моделей:** {model_type}\n\n"

    for model_id, response, cache_status in responses:
        cache_emoji = "✅" if cache_status == "HIT" else "💰"
        result += f"**{model_id}** {cache_emoji}:\n{response}\n\n---\n\n"

    if len(result) > 4000:
        result = result[:4000] + "\n\n... (сокращено)"

    await message.answer(result, parse_mode="Markdown")


@dp.message(Command("new"))
async def cmd_new(message: Message):
    """Новые модели за 24 часа"""
    await message.answer("⏳ Проверяю новые модели...")

    models, _ = await fetch_openrouter_models(force_refresh=True)

    if not models:
        await message.answer("❌ Не удалось получить модели")
        return

    new_models = await get_new_models(1)

    if not new_models:
        await message.answer("📭 Новых моделей за последние 24 часа не обнаружено")
        return

    report = format_new_models(new_models)
    await message.answer(report, parse_mode="Markdown")


@dp.message(Command("models"))
async def cmd_models(message: Message):
    """Список доступных моделей"""
    models, _ = await fetch_openrouter_models()
    if not models:
        await message.answer("❌ Не удалось получить список моделей")
        return

    report = format_models_list(models)
    await message.answer(report, parse_mode="Markdown")


@dp.message(Command("top"))
async def cmd_top(message: Message):
    """Топ моделей по цене/качеству"""
    models, _ = await fetch_openrouter_models()
    if not models:
        await message.answer("❌ Не удалось получить список моделей")
        return

    report = format_top_models(models)
    await message.answer(report, parse_mode="Markdown")


@dp.message(Command("stats"))
async def cmd_stats(message: Message):
    """Статистика запросов пользователя"""
    user_id = message.from_user.id
    total = await get_models_count()

    stats_text = (
        f"📊 **Ваша статистика:**\n\n"
        f"• ID: `{user_id}`\n"
        f"• Моделей в базе: {total}\n"
        f"• Канал: {TELEGRAM_CHANNEL}\n\n"
        f"Используйте `/compare` для тестирования моделей!"
    )
    await message.answer(stats_text, parse_mode="Markdown")


@dp.message(Command("history"))
async def cmd_history(message: Message):
    """История запросов пользователя"""
    user_id = message.from_user.id
    history = await get_user_history(user_id, limit=10)

    if not history:
        await message.answer("📭 История запросов пуста. Используйте `/compare` для сравнения моделей!")
        return

    report = f"📜 **История запросов (последние {len(history)}):**\n\n"
    for i, h in enumerate(history, 1):
        p = h['prompt'][:30]
        report += f"{i}. `{p}...` [{h['model_type']}]\n"

    await message.answer(report, parse_mode="Markdown")


@dp.message(Command("scan"))
async def cmd_scan(message: Message):
    """Сканировать проекты лаборатории на использование LLM"""
    await message.answer("⏳ Сканирую проекты лаборатории...")

    try:
        projects = scan_laboratory()
        config = load_config()

        report = f"🔍 **Результаты сканирования:**\n\n"
        report += f"• Найдено проектов: {len(config.get('projects', []))}\n\n"

        if config.get("projects"):
            report += "**Проекты:**\n"
            for proj in config.get("projects", [])[:10]:
                models = ', '.join(proj.get('models_used', [])[:2])
                report += f"• {proj['path']}: {models}\n"

        await message.answer(report, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Scan error: {e}")
        await message.answer("❌ Ошибка при сканировании")


@dp.message(Command("analyze"))
async def cmd_analyze(message: Message):
    """Самоанализ бота и рекомендации"""
    await message.answer("⏳ Анализирую бота...")

    try:
        result = analyze_self()

        report = f"🧪 **Самоанализ LLMevangelist:**\n\n"
        report += f"• Проект: {result.get('project', 'N/A')}\n"
        report += f"• Используемые модели: {', '.join(result.get('uses_models', []))}\n"
        report += f"• Цена за ревью: {result.get('cost_per_review', 'N/A')}\n\n"

        recommendations = result.get("recommendation", [])
        if recommendations:
            report += "**Рекомендации:**\n"
            for rec in recommendations:
                report += f"• [{rec.get('type', 'general')}] {rec.get('suggestion', 'N/A')}\n"
                if 'savings' in rec:
                    report += f"  💰 Экономия: {rec['savings']}\n"

        await message.answer(report, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Analyze error: {e}")
        await message.answer("❌ Ошибка при анализе")


async def post_daily_report():
    """Ежедневный отчёт в канал"""
    logger.info("Генерация ежедневного отчёта...")
    models, pricing = await fetch_openrouter_models()
    config = load_config()

    now = datetime.now().strftime("%d.%m %H:%M")

    total_models = len(models)
    free_models = [m for m in models if ":free" in m.get("id", "")]

    report = f"🔱 LLMevangelist Daily Report {now}\n"
    report += "━" * 38 + "\n\n"
    report += f"📊 Всего моделей: {total_models}\n"
    report += f"💎 FREE моделей: {len(free_models)}\n\n"

    report += "💎 **ЛУЧШИЕ FREE:**\n"
    for i, m in enumerate(free_models[:3], 1):
        report += f"{i}. {model_link(m['id'])}\n"

    if config.get("projects"):
        report += "\n🏢 **Используют LLM:**\n"
        for proj in config["projects"][:5]:
            report += f"• {proj['path']}: {', '.join(proj['models_used'][:2])}\n"

    try:
        await bot.send_message(
            chat_id=TELEGRAM_CHANNEL,
            text=report,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
        logger.info("Отчёт опубликован в канал")
    except Exception as e:
        logger.error(f"Ошибка публикации: {e}")


async def daily_report_scheduler():
    """Шедулер для ежедневных отчётов (раз в сутки)"""
    await post_daily_report()
    logger.info("Первый ежедневный отчёт отправлен")

    while True:
        try:
            await asyncio.sleep(24 * 60 * 60)
            await post_daily_report()
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            await asyncio.sleep(60 * 60)


async def on_startup():
    """Действия при запуске"""
    logger.info("LLMevangelist 2.0 запущен")

    await init_db()
    logger.info("SQLite БД инициализирована")

    await init_models_db()
    logger.info("Models DB инициализирована")

    asyncio.create_task(daily_report_scheduler())
    logger.info("Шедулер ежедневных отчётов запущен")

    if ADMIN_CHAT_ID:
        try:
            await bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text="🤖 LLMevangelist 2.0 запущен и готов к работе!"
            )
        except Exception as e:
            logger.error(f"Не удалось уведомить админа: {e}")


async def main():
    """Основная функция"""
    dp.startup.register(on_startup)
    logger.info("Запуск поллинга...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())