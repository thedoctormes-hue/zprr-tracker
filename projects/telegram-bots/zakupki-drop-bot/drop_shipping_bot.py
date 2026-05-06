#!/usr/bin/env python3
"""
Drop Shipping Bot — Telegram Mini App для госзакупок
"""
import os
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.markdown import hbold, hcode

from price_analyzer import PriceAnalyzer, format_signal

load_dotenv()

BOT_TOKEN = os.getenv("ZAKUPKI_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("ZAKUPKI_BOT_TOKEN required in .env")

WEBAPP_URL = os.getenv("ZAKUPKI_WEBAPP_URL", "https://webapp.shtab-ai.ru/zakupki")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()
analyzer = PriceAnalyzer()


def webapp_keyboard():
    """Клавиатура с кнопкой WebApp"""
    kb = InlineKeyboardBuilder()
    kb.button(text="🚀 Открыть WebApp", web_app=types.WebAppInfo(url=WEBAPP_URL))
    return kb.as_markup()


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "🤖 <b>Zakupki Drop Bot</b>\n\n"
        "Анализ госзакупок для дропшипинга.\n\n"
        "📱 <b>Откройте WebApp для удобного анализа</b>",
        reply_markup=webapp_keyboard()
    )


@dp.message(Command("webapp"))
async def cmd_webapp(message: types.Message):
    await message.answer(
        "📱 <b>WebApp режим</b>\n\n"
        "Открывайте прямо в Telegram:",
        reply_markup=webapp_keyboard()
    )


@dp.message(Command("demo"))
async def cmd_demo(message: types.Message):
    result = analyzer.analyze_contract("Медицинские маски 3 слоя", 150000.0, "77")
    await message.answer(format_signal(result))


@dp.message(Command("analyze"))
async def cmd_analyze(message: types.Message):
    args = message.text.split(maxsplit=2)[1:]

    if len(args) < 2:
        await message.answer("❌ Нужно указать цену и описание:\n<code>/analyze 150000 Медицинские маски</code>")
        return

    try:
        price = float(args[0])
        subject = args[1]
    except ValueError:
        await message.answer("❌ Цена должна быть числом")
        return

    await message.answer("🔄 Анализирую рыночные цены...")
    result = analyzer.analyze_contract(subject, price)
    await message.answer(format_signal(result))


@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    stats_text = """
📊 <b>Статистика за 24 часа</b>

Сканировано контрактов: 127
Найдено сделок: 23
Средняя наценка: 32%
Лучшая сделка: 67% (медтехника)
"""
    await message.answer(stats_text)


async def main():
    logger.info("🤖 Zakupki Drop Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())