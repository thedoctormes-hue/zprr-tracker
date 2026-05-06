"""
Bot handlers for WebApp integration
Add these to your bot/handlers.py
"""

from aiogram import Router, F
from aiogram.types import Message, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
import json
from pathlib import Path

router = Router()


@router.message(Command("upload"))
async def cmd_upload_large(message: Message):
    """Send WebApp link for large file upload"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📤 Загрузить файл >20MB",
            web_app=WebAppInfo(url="https://files.stenographerobot.com")
        )]
    ])
    await message.answer(
        "📤 *Загрузка файлов до 2GB*\n\n"
        "• Аудио и видео файлы\n"
        "• Прогресс в реальном времени\n"
        "• Автоматическая обработка после загрузки\n\n"
        "Нажмите кнопку ниже 👇",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@router.message(F.web_app_data)
async def handle_webapp_data(message: Message):
    """Handle data sent from WebApp"""
    try:
        data = json.loads(message.web_app_data.data)
        
        if data.get("action") == "upload_complete":
            upload_id = data["upload_id"]
            filename = data["filename"]
            
            # Check if upload exists
            upload_path = Path(f"/var/lib/stenographer/uploads/{upload_id}")
            metadata_path = upload_path / "metadata.json"
            
            if metadata_path.exists():
                await message.answer(
                    f"✅ *Файл загружен!*\n\n"
                    f"📄 `{filename}`\n"
                    f"⚙️ Начинаю обработку...",
                    parse_mode="Markdown"
                )
                # TODO: Start transcription processing
                # process_upload(upload_id, message.chat.id)
            else:
                await message.answer("⚠️ Загрузка не найдена. Попробуйте ещё раз.")
                
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


# WebApp keyboard factory
def get_webapp_keyboard():
    """Create inline keyboard with WebApp button"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📤 Загрузить большой файл",
            web_app=WebAppInfo(url="https://files.stenographerobot.com")
        )]
    ])


# Integration with existing handlers example:
def add_to_existing_handler(router):
    """Use this to add handlers to your existing router"""
    router.message.register(cmd_upload_large, Command("upload"))
    router.message.register(handle_webapp_data, F.web_app_data)