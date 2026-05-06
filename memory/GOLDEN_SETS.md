# 🏅 Golden Sets — Шаблоны для повторяющихся задач

## 1. 🔄 Рефакторинг Telegram-бота

**Контекст:**
- Проект: `projects/telegram-bots/{bot_name}/`
- Стек: aiogram 3.x, pydantic-settings

**Шаги:**
1. 📖 Прочитать `main.py` → понять flow
2. 🎯 Найти хэндлеры с похожей логикой
3. 🧠 Вынести бизнес-логику в `services/`
4. 🧪 Проверить тестами: `pytest {bot_name}/tests/`
5. 📦 Деплой: `systemctl restart {bot_name}`

**Экономия:** ~30% токенов за счёт шаблона

---

## 2. 🆕 Новый FastAPI endpoint

**Контекст:**
- Проект: `projects/telegram-bots/{service}/app/`
- Стек: FastAPI, SQLAlchemy

**Шаблон:**
```python
# routers/{resource}.py
from fastapi import APIRouter, Depends
from app.deps import get_current_user
from app.schemas import {Resource}Create, {Resource}Response

router = APIRouter(prefix="/{resource}", tags=["{resource}"])

@router.post("/", response_model={Resource}Response)
async def create_{resource}(
    data: {Resource}Create,
    user=Depends(get_current_user)
):
    # TODO: реализовать
    pass
```

**Экономия:** ~25% токенов

---

## 3. 🛠️ Исправление бага (debugging)

**Контекст:**
- Любой проект

**Шаги:**
1. 🔍 Найти ошибку: `journalctl -u {service} -n 50 --no-pager`
2. 📖 Прочитать traceback
3. 🔧 Исправить в `src/` или `app/`
4. ✅ Проверить: `python -m pytest {service}/tests/ -v`
5. 🔄 Перезапустить: `systemctl restart {service}`

**Экономия:** ~40% токенов

---

## 4. 🔧 Деплой React приложения

**Контекст:**
- Проект: `projects/web-apps/{app}/`

**Шаги:**
1. 🏗️ `npm run build` в директории проекта
2. 📦 `rsync -av dist/ /var/www/{app}/`
3. 🔄 `systemctl reload nginx` (если нужен reload)

**Экономия:** ~50% токенов

---

## 5. 🧪 Тестирование Telegram-бота

**Контекст:**
- Проект: `projects/telegram-bots/{bot}/`

**Шаги:**
1. 📖 Прочитать `test_logic.py` или `tests/`
2. ▶️ Запустить: `python -m pytest {bot}/tests/ -v`
3. 🐛 Если падает — добавить логирование в `main.py`
4. ✅ При успехе — commit + deploy

**Экономия:** ~35% токенов

---

## 6. 📊 Добавление в БД

**Контекст:**
- Проект с SQLAlchemy

**Шаги:**
1. 📖 Прочитать `app/database.py` или `shared/database.py`
2. 🗃️ Добавить модель в `models.py`
3. 🔄 Создать migration: `alembic revision --autogenerate`
4. 🔨 Применить: `alembic upgrade head`
5. 📦 Импортировать в `app/__init__.py`

**Экономия:** ~30% токенов

---

## Использование

> "Примени golden set #{номер}" — и я использую готовый шаблон.

**Пример:**
> "Примени golden set #1 для рефакторинга protocol"

---

*Создано: 2026-05-04 для экономии токенов на рутине*