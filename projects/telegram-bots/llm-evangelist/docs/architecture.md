# 🏗️ Архитектура LLMevangelist

> Техническая документация по реализации бота для анализа LLM моделей

---

## 📁 Структура проекта

```
llm-evangelist/
├── main.py                    # Главный файл бота
├── scanner/
│   └── discover.py           # Сканер LLM проектов в лаборатории
├── analyzer/
│   └── self_analysis.py    # Самоанализ и рекомендации
├── cache/
│   ├── models_cache.py     # Кэширование моделей (TTL 1 час)
│   └── history_db.py       # SQLite БД для истории запросов
├── config.json             # Конфигурация проектов
├── .env.example           # Шаблон переменных окружения
└── requirements.txt       # Зависимости
```

---

## 🧩 Компоненты системы

### 1. Telegram Bot (main.py)

**Фреймворк:** aiogram 3.x с async/await

**Основные хэндлеры:**

| Команда | Функция | Описание |
|---------|---------|----------|
| `/start` | `cmd_start()` | Приветствие и список команд |
| `/compare` | `cmd_compare()` | Сравнение ответов моделей |
| `/models` | `cmd_models()` | Список моделей с ценами |
| `/top` | `cmd_top()` | Топ моделей по цена/качество |
| `/scan` | `cmd_scan()` | Сканирование проектов лаборатории |
| `/analyze` | `cmd_analyze()` | Самоанализ бота |
| `/stats` | `cmd_stats()` | Статистика запросов |
| `/history` | `cmd_history()` | История запросов |

**Daily Report Scheduler:**
```python
async def daily_report_scheduler():
    """Шедулер для ежедневных отчётов (раз в сутки)"""
    await post_daily_report()  # Первый отчёт сразу
    while True:
        await asyncio.sleep(24 * 60 * 60)
        await post_daily_report()
```

---

### 2. Scanner (scanner/discover.py)

**Назначение:** Сканирование проектов лаборатории на использование LLM

**Паттерны поиска LLM моделей:**
```python
LLM_PATTERNS = [
    (r'["\'](?:google/|mistralai/|anthropic/|deepseek/|openai/|x-ai/)[^"\']+["\']', "model_string"),
    (r'"model":\s*["\']([^"\']+)["\']', "model_json"),
    (r'MODEL\s*=\s*["\']([^"\']+)["\']', "model_constant"),
    (r'llm_primary["\']?\s*[:=]\s*["\']([^"\']+)["\']', "llm_config"),
    (r'LLM_MODEL["\']?\s*=\s*["\']([^"\']+)["\']', "llm_model"),
]
```

**Алгоритм работы:**
1. Рекурсивный обход `/root/LabDoctorM`
2. Поиск `.py` файлов
3. Применение regex паттернов
4. Сохранение результатов в `config.json`

**Исключаемые директории:**
```python
EXCLUDE_DIRS = {
    ".git", "__pycache__", ".venv", "venv",
    "node_modules", ".qwen", "tmp", "temp", "logs", "log"
}
```

---

### 3. Cache System

#### 3.1 Models Cache (cache/models_cache.py)

**Хранение:** JSON файл `models_cache.json`

**Структура кэша:**
```json
{
  "timestamp": 1714700000,
  "models": [...],
  "pricing": {...}
}
```

**TTL:** 3600 секунд (1 час)

#### 3.2 History DB (cache/history_db.py)

**База:** SQLite с FTS5 для полнотекстового поиска

**Схема таблицы:**
```sql
CREATE TABLE requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    model_type TEXT,
    prompt TEXT,
    models_used TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

### 4. API Интеграции

#### OpenRouter API

**Endpoint:** `https://openrouter.ai/api/v1`

**Методы:**
- `GET /models` — список всех моделей с ценами
- `POST /chat/completions` — запрос к конкретной модели

**Аутентификация:** Bearer token в заголовке

#### Telegram API

**Библиотека:** aiogram

**Функции:**
- Отправка сообщений в чат
- Публикация в канал `@LLMevangelist`
- Обработка команд через handlers

---

## 🔄 Поток данных

```
[User] → /compare free prompt
    ↓
[main.py] cmd_compare()
    ↓
[fetch_openrouter_models()] → кэш или API
    ↓
[fetch_model_response()] × N моделей
    ↓
[save_request()] → SQLite история
    ↓
[User] ← отформатированный ответ
```

---

## 📊 Daily Report Flow

```
daily_report_scheduler()
    ↓
post_daily_report()
    ↓
fetch_openrouter_models()
    ↓
load_config() → projects data
    ↓
format_report() → markdown
    ↓
bot.send_message(TELEGRAM_CHANNEL)
```

---

## 🛠️ Конфигурация

### .env переменные

| Переменная | Описание | Пример |
|------------|----------|--------|
| `OPENROUTER_API_KEY` | Ключ OpenRouter API | `sk-or-...` |
| `TELEGRAM_BOT_TOKEN` | Токен Telegram бота | `123456:ABC...` |
| `TELEGRAM_CHANNEL` | Канал для публикаций | `@LLMevangelist` |
| `ADMIN_CHAT_ID` | ID админа для уведомлений | `123456789` |

---

## 📈 Метрики и мониторинг

**Логи:**
- Уровень: INFO
- Формат: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

**Ключевые события:**
- Запуск бота
- Ошибки API
- Публикация отчётов
- Сканирование проектов

---

## 🔧 Расширение функционала

### Добавление нового источника моделей

1. Создайте класс в `scanner/`
2. Добавьте паттерн в `LLM_PATTERNS`
3. Обновите `scan_laboratory()`

### Добавление новой команды

```python
@dp.message(Command("newcommand"))
async def cmd_newcommand(message: Message):
    await message.answer("Результат команды")
```

---

## 🚀 Деплой

**Система:** systemd service

**Файл сервиса:** `/etc/systemd/system/llmevangelist.service`

```bash
systemctl restart llmevangelist
journalctl -u llmevangelist -f
```