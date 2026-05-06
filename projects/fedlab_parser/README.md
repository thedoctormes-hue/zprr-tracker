# FedLab Parser

Умный поиск мероприятий Российской Федерации Лабораторной Медицины.

## Стек
- Python 3.10
- FastAPI + UVicorn
- BeautifulSoup4
- TF-IDF поиск (без ML зависимостей)

## Быстрый старт

```bash
cd /root/LabDoctorM/projects/fedlab_parser

# Запуск API
python3 api.py

# Поиск мероприятий
curl -X POST http://127.0.0.1:9999/search \
  -H "Content-Type: application/json" \
  -d '{"query": "КЛФ Санкт-Петербург"}'
```

## Мероприятия 2026 (9 штук)
- ЛАБНЕКС (Онлайн) — март
- Приволжский форум (Уфа) — апрель  
- КЛФ, Уральский форум — июнь
- МЕД&ТЕХ, РДС, РКЛМ — октябрь
- Южный форум — ноябрь
- Конференция ВМА — декабрь

## API Endpoints

POST /search — поиск по мероприятиям
GET /events — список всех мероприятий