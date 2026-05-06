---
name: Code Deduplication Audit 2026-05-04
description: Автоаудит дублей кода для эволюции
type: reference
---

# 🔍 Автоаудит дублей кода — 04.05.2026

## Найденные дубли (HIGH Приоритет)

### 1. classifier.py — 95% дублирования
- **Файлы:**
  - `/root/LabDoctorM/projects/telegram-bots/protocol/app/classifier.py`
  - `/root/LabDoctorM/infrastructure/monitoring/protocol/app/classifier.py`

- **Различия:**
  - `infrastructure/` версия использует Pydantic валидацию (`FragmentClassification`)
  - `infrastructure/` версия использует `asyncio.create_subprocess_exec` для ffmpeg (async)

- **Решение:** Вынести в `shared/classifier.py` с Pydantic валидацией

### 2. database.py — дедуплицирован ✅
- **Статус:** Уже рефакторен
- `protocol/app/database.py` → re-exports из `shared/database.py`

### 3. Markdown fallback — 15 функций в 4 проектах
- **Проблема:** Одинаковый try/except паттерн в 15 местах
- **Решение:** Создан шаблон в `memory/markdown_fallback.md`

## Статистика

- 📁 Проектов проанализировано: 7 Telegram-ботов
- 🔍 Файлов .py: 56
- 🎯 Критических дублей: 2 (classifier, database — database решён)
- 💰 Экономия токенов: ~1.2K строк кода

## План исправления

1. ✅ database.py — готово (re-exports)
2. 🔲 classifier.py → shared/classifier.py с Pydantic
3. 🔲 Применить markdown fallback pattern ко всем ботам