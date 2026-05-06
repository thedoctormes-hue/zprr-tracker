---
name: Solidity Security Auditor Insights
description: Multi-agent security audit pipeline для DeFi контрактов в OpenClawBox
type: project
---

# Solidity CoT Auditor Integration

## Архитектура 4-х агентов:
1. **Explainer** — фильтрует false positives, объясняет уязвимости
2. **ExploitWriter** — генерирует PoC эксплойты
3. **Fixer** — unified diff с исправлениями
4. **Judge** — валидирует цепочку

## Интеграция в AntColony:
- OpenClawBox → DeFi pre-audit
- Security-as-a-Service продукт
- Investor security reports

## Источник:
https://github.com/butthtio/solidity-cot-auditor