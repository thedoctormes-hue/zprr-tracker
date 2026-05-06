---
name: Router Autorater Feedback Loop
description: Автономный feedback через LLM-судью без human-in-the-loop
type: concept
---

## Паттерн 2025 года

```
Agent₁ → [output] → Autorater LLM → [quality_score] → Agent₂
   ↓                                        ↓
Router знает: был ли успех?        Self-correction signal
```

## Цикл обратной связи

1. **Авторater** — отдельная LLM (компактная, 7-8B) оценивает каждый output:
   - correctness score (0-1)
   - completion status (complete/partial/fail)
   - actionable feedback

2. **Сигнал к следующему агенту**:
   - Если score < 0.7 → reroute с изменёнными установками
   - Если score > 0.9 → усилить reward для выбранной модели

3. **Замкнутый цикл**:
   - Agent N+1 сигнализирует о качестве работы Agent N
   - Router обновляет статистику UCB без участия человека

## Автокоррекция

```python
if feedback.quality < 0.7:
    router.adjust_preferences(
        model_id=previous_model,
        task_type=feedback.task_type,
        penalty=0.1
    )
    reroute_with_fallback()
```