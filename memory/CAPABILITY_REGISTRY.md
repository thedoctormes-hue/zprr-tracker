---
name: Capability Registry Pattern
description: Паттерн декларирования навыков агентов для динамического роутинга
type: reference
---

# Capability Registry Pattern

## Зачем

Централизованный реестр навыков позволяет:
- Динамически выбирать подходящего агента для задачи
- Устранять хрупкость ручного маппинга
- Автоматически находить cover в случае недоступности агента

## Структура

```python
{
    skill: str,           # основной навык
    tags: List[str],      # дополнительные теги
    expertise: Enum,      # уровень: novice/expert
    confidence: float     # 0.0-1.0
}
```

## Как использовать

1. **Регистрация агента:**
```python
profile = AgentProfile(
    agent_name="vpn-infrastructure-agent",
    capabilities=[
        AgentCapability(
            skill="vpn",
            tags=["vless", "reality", "dpi-bypass"],
            expertise=ExpertiseLevel.EXPERT,
            confidence=0.95
        )
    ]
)
registry.register(profile)
```

2. **Поиск подходящего агента:**
```python
best = registry.find_agent("vpn")
if best:
    print(f"Найден: {best.agent_name}")
```

## Интеграция с Router

Роутер описывает задачи через требования:
- `required_skill`: какой навык нужен
- `min_confidence`: минимальный порог

Агенты декларируют возможности сами — новые модели на OpenRouter подхватываются автоматически.