import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = "8649218949:AAESDIYZwLE-tHgC358jmnb9YEIBi3WNJ_A"
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    text = """🐜 **АнтКэт** — Муравей-клон КотОлизатОра
    
**Права:** те же, что и у Кота
**Язык:** русский
**Тон:** деловой, чёткий, дружелюбный

/start — это меню
/help — помощь
/status — что делаю"""
    await message.answer(text, parse_mode="Markdown")

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    text = """📋 **Команды АнтКэт:**

/start — главное меню
/help — эта справка
/status — мой текущий статус

**Важно:** Каждую сессию начинаю в режиме ЕБШ."""
    await message.answer(text, parse_mode="Markdown")

@dp.message(Command("status"))
async def cmd_status(message: types.Message):
    await message.answer("🐜 АнтКэт работает. Лаборатория ЗавЛаб — приоритет.", parse_mode="Markdown")

@dp.message()
async def antcat_reply(message: types.Message):
    # АнтКэт отвечает как муравей-клон КотОлизатОра
    text = message.text.lower()
    if "привет" in text or "здрав" in text:
        await message.answer("🐜 Привет! АнтКэт на связи. Что нужно сделать?")
    elif "спасибо" in text:
        await message.answer("🐜 Пожалуйста! Муравьи всегда готовы помочь.")
    else:
        await message.answer(f"🐜 {message.text}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
