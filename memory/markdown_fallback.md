---
name: Markdown Fallback Pattern
description: Паттерн try/except для защиты от Bad Request в Telegram-ботах
type: reference
---

# Markdown Fallback Pattern для Telegram-ботов

## Проблема
Telegram API возвращает `Bad Request: can't parse entities` при спецсимволах в тексте.
🔥 Это ломает команды и портит UX.

## Решение
Паттерн try/except с fallback на plain text:

```python
try:
    await bot.send_message(
        chat_id=chat_id,
        text=formatted_text,
        parse_mode="MarkdownV2"
    )
except BadRequest as e:
    if "can't parse entities" in str(e):
        # Fallback без markdown
        await bot.send_message(
            chat_id=chat_id,
            text=plain_text,
            parse_mode=None
        )
```

## Экранирование спецсимволов
Перед отправкой MarkdownV2:

```python
import re

def escape_markdown(text: str) -> str:
    """Экранирует спецсимволы для MarkdownV2"""
    escape_chars = r'[_ * [ ] ( ) ~ ` > # + - = | { } . !]'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

# Использование
safe_text = escape_markdown(user_input)
```

## Автоматизация через декоратор

```python
from functools import wraps
from aiogram.exceptions import BadRequest

def markdown_safe(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except BadRequest as e:
            if "can't parse entities" in str(e):
                # Повторить без markdown
                kwargs['parse_mode'] = None
                return await func(*args, **kwargs)
            raise
    return wrapper
```

## Где применено
- /scan ✅  
- /models ✅
- /update_models ✅
- /spend ✅

## Чек-лист для новых команд
- [ ] Экранировать спецсимволы перед Markdown
- [ ] Добавить try/except вокруг send_message
- [ ] Fallback без parse_mode
- [ ] Логировать ошибки парсинга