# 🔄 Sub-agent patterns: planner → coder → verifier

## Паттерн 1: Sequential Handoff

**Архитектура:**
```
Router (главный агент)
  → 📋 Planner (планирует, создаёт todo)
  → 💻 Coder (реализует)
  → ✅ Verifier (проверяет тесты/линт)
  → 🔄 Router (фидбек)
```

**Когда использовать:**
• Сложные задачи > 100 строк кода
• Требуются тесты и валидация
• Много файлов для изменения

**Пример:**
```
User: "Добавить endpoint /rerank в Protocol"
→ Planner: 1) прочитать router, 2) добавить schema, 3) ...
→ Coder: пишет код по плану
→ Verifier: pytest + ruff check
```

---

## Паттерн 2: Parallel Workers

**Архитектура:**
```
Router
  ├── 💻 Coder A (фронтенд)
  ├── 💻 Coder B (бэкенд)
  └── 🧪 Tester (параллельно тестирует)
```

**Когда использовать:**
• Независимые компоненты
• UI + API одновременно

---

## Паттерн 3: Specialist Chain

**Архитектура:**
```
User → Context-Agent → Skill-Architect → Deploy-Bot
```

**Когда использовать:**
• Требуется экспертиза
• skill-architect для SKILL.md
• deploy-bot для деплоя

---

## Qwen Code как Orchestrator

**Настройка в settings.json:**
```json
{
  "subAgentMode": "sequential",
  "maxConcurrent": 2,
  "defaultChain": ["planner", "coder", "verifier"]
}
```

**Router prompts:**
```
PLAN: создай план задач
CODE: реализуй по плану
VERIFY: проверь тесты
```

---

## Лимиты

• Context reset каждые 5 шагов
• Максимум 2 агента в parallel mode
• Planner + Coder + Verifier — золотой стандарт

---

*Документ создан: 2026-05-04*