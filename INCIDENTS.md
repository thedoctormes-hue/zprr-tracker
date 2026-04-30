# Инциденты безопасности

## 2026-05-06: Утечка токенов в git history

**SEVERITY:** CRITICAL 🔴

**Описание:**
Токены Telegram ботов и OpenRouter API были зафиксированы в git history в файле `AUDIT_2026.md` в контексте legacy-проекта `/root/bots` (теперь удалён). **Токены НЕ активны, под контролем.**

**Утечка:**
- `8616446490:AAEaSLYw4F5TMrUJj23KcaCWCsQxylhudEk` (Telegram)
- `sk-or-v1-***REDACTED***` (OpenRouter)
- `8546968865:AAGRp4pDUkdjt16XqRlX-w-b1hRrJAgVbD8` (Telegram)
- `sk-or-v1-***REDACTED***` (OpenRouter)
- `8735680899:AAFOQfjfsM2MVuB1sxDUJ-ZXExo9Rm-jDlY` (Telegram)

**Действия:**
1. ✅ Токены больше не активны (legacy проект)
2. ⏳ Требуется BFG Repo-Cleaner для очистки git history
3. ✅ Документы TRANSITION.md и QWEN.md очищены от токена Protocolstandbot

**Статус:** В работе
**Ответственный:** КотОлизатОр