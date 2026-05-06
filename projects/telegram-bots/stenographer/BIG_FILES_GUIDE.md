# Гид по работе с большими аудиофайлами

## 🚨 Проблема
- **Telegram Bot API limit**: 20MB для скачивания файла
- **OpenAI Whisper limit**: 25MB / 30 минут длительность

## ✅ Решение 1: Local Bot API Server (рекомендуется)

Локальный сервер позволяет скачивать файлы до 2GB.

### Установка:
```bash
# Скачивание
wget https://github.com/telegram-bot-api/telegram-bot-api/releases/latest/download/telegram-bot-api
chmod +x telegram-bot-api

# Запуск (см. пример ниже)
./telegram-bot-api --local --max-file-size 2000 --token YOUR_BOT_TOKEN
```

### Systemd сервис:
```ini
[Unit]
Description=Telegram Local Bot API Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/telegram-bot-api
ExecStart=/opt/telegram-bot-api/telegram-bot-api --local --max-file-size 2000 --token YOUR_BOT_TOKEN --download-path /var/lib/tg-files
Restart=always

[Install]
WantedBy=multi-user.target
```

### Настройка stenographerobot:
В `.env` добавить:
```
LOCAL_API_URL=http://localhost:8081
```

## ✅ Решение 2: Внешнее хранилище (fallback)

Для файлов >20MB бот отправит инструкцию:
```
📤 Файл >20MB. Варианты:
1. Загрузить на https://send.tg или Google Drive
2. Отправить ссылку боту
3. Или разбить файл на части <20MB
```

## ✅ Решение 3: Чанкинг (автоматический)

Бот автоматически разбивает аудио >30 мин на части и объединяет результат.

### Требования:
- ffmpeg (`apt install ffmpeg`)
- pydub (в requirements.txt)

## ⚙️ Лимиты

| Метод | Макс. размер | Макс. длительность |
|-------|--------------|-------------------|
| Telegram API (облако) | 20 MB | - |
| Local Bot API | 2 GB | - |
| OpenAI Whisper | 25 MB | 30 мин |
| AssemblyAI | 5 GB | 10 часов |

## 🔧 Настройка под 3+ часа аудио

1. Установить Local Bot API Server
2. В `.env`: `LOCAL_API_URL=http://localhost:8081`
3. При получении файла >20MB — бот использует локальный сервер
4. Для >30 мин аудио — автоматический чанкинг