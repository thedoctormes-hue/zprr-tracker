# Zakupki Drop Bot

🤖 Telegram-бот для поиска выгодных госзакупок для дропшипинга

## 📦 Файлы

- `zakupki_parser.py` — парсер zakupki.gov.ru
- `price_analyzer.py` — анализ цен vs рынок
- `zakupki_database.py` — PostgreSQL/SQLite хранилище
- `drop_shipping_bot.py` — Telegram бот

## 🔧 Установка

```bash
pip install -r requirements.txt
```

## ⚙️ Настройка

Создайте `.env`:
```
ZAKUPKI_BOT_TOKEN=your_bot_token
DATABASE_URL=postgresql://... (optional, defaults to SQLite)
```

## 🚀 Запуск

```bash
python drop_shipping_bot.py
```

## 📊 Команды бота

- `/start` — приветствие
- `/demo` — пример анализа
- `/analyze 150000 Медицинские маски` — анализ контракта
- `/stats` — статистика