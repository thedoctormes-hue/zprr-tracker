---
name: LLM Router Capability Declaration
description: Инверсия зависимостей в роутере через декларацию возможностей моделей
type: concept
---

## Архитектура

Роутер описывает задачи через требования, модели декларируют возможности:

```
{
  "task_requirements": {
    "latency": "low" | "medium" | "high",
    "cost": "budget" | "balanced" | "premium",
    "modality": "text" | "vision" | "multimodal",
    "reasoning_depth": 1-5,
    "context_length": 8k-200k
  }
}
```

## Capability Declaration (модель)

```json
{
  "id": "openrouter:anthropic/claude-sonnet-4",
  "capabilities": {
    "modality": ["text"],
    "vision": false,
    "reasoning_depth": 4,
    "context_length": 200000,
    "latency_profile": "medium",
    "cost_per_1k": 0.003,
    "strengths": ["coding", "long-context", "tool-use"]
  }
}
```

## Преимущества
- Новые модели автоматически подхватываются
- Нет хрупкого ручного маппинга
- Декларативная миграция между провайдерами