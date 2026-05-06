---
name: Protocol Bot Analysis
description: Анализ для будущего рефакторинга protocol Telegram-бота
type: project
---

## Зоны для рефакторинга

### 1. Повторяющийся паттерн — получение пользователя
- `get_user_by_tg_id(tg_id)` вызывается в 6 местах (cmd_today, cmd_patterns, handle_search_query, handle_callbacks, today_fragments, today_patterns)

### 2. JWT helper
- `make_jwt()` в main.py → вынести в `app/jwt_utils.py`

### 3. Утилиты
- `get_category()` и `format_date()` → `app/utils/format.py`

### 4. Callback handlers
- 300+ строк в `handle_callbacks()` → разбить на отдельные хэндлеры

## План services

```
protocol/
├── services/
│   ├── __init__.py
│   ├── user_service.py      # get_user_by_tg_id, user helpers
│   ├── fragment_service.py  # search_fragments, get_today_fragments
│   └── pattern_service.py   # get_patterns, get_today_pattern
└── utils/
    └── format.py           # get_category, format_date
```

## Готово к рефакторингу при необходимости