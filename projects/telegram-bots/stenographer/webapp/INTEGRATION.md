# Интеграция WebApp с Stenographer Bot

## 🚀 Быстрый старт

### 1. Установка зависимостей
```bash
cd /root/LabDoctorM/projects/telegram-bots/stenographer/webapp
pip install fastapi uvicorn python-multipart
```

### 2. Systemd сервис (webapp.service)
```ini
[Unit]
Description=Stenographer WebApp - Chunked File Upload
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/LabDoctorM/projects/telegram-bots/stenographer/webapp
ExecStart=/root/LabDoctorM/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### 3. Nginx конфигурация
```nginx
server {
    listen 80;
    server_name files.stenographerobot.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📱 Интеграция с ботом

### Добавьте в handlers.py:
```python
from aiogram.types import WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup

# В команде /start или меню
async def cmd_upload_large(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📤 Загрузить файл >20MB",
            web_app=WebAppInfo(url="https://files.stenographerobot.com")
        )]
    ])
    await message.answer(
        "Отправьте аудио/видео файл до 2GB\n"
        "Прогресс загрузки будет отображаться в реальном времени",
        reply_markup=keyboard
    )
```

### Обработка данных от WebApp:
```python
@dp.message(F.web_app_data)
async def handle_webapp_data(message: Message):
    data = json.loads(message.web_app_data.data)
    
    if data.get("action") == "upload_complete":
        upload_id = data["upload_id"]
        filename = data["filename"]
        
        # Получаем путь к файлу
        upload_path = Path(f"/var/lib/stenographer/uploads/{upload_id}")
        metadata_path = upload_path / "metadata.json"
        
        if metadata_path.exists():
            # Начинаем обработку
            await message.answer(f"✅ {filename} загружен! Начинаю расшифровку...")
            # Здесь ваш код обработки файла
```

## 📂 Структура загрузок

```
/var/lib/stenographer/uploads/
├── {upload_id}/
│   ├── {filename}      # Объединенный файл
│   └── metadata.json   # Метаданные
```

## 🔐 Безопасность

1. **Telegram Auth**: WebApp передает `initData` для верификации
2. **Путь загрузки**: Изолирован в `/var/lib/stenographer/uploads/`
3. **Размер**: Ограничен 2GB на файл
4. **Типы**: Только `audio/*` и `video/*`

## 🛠️ Debugging

```bash
# Посмотреть upload сессии
curl http://localhost:8000/api/upload/status/{upload_id}

# Проверить uploads
ls -la /var/lib/stenographer/uploads/
```