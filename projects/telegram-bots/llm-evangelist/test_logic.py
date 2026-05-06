#!/usr/bin/env python3
"""Тест логики LLMevangelist без Telegram"""

import asyncio
import sys
from pathlib import Path

# Добавляем путь к проекту
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from dotenv import load_dotenv
load_dotenv()

# Импортируем функции из main.py
from main import (
    fetch_openrouter_models,
    fetch_model_response,
    format_models_list,
    format_top_models,
    scan_laboratory,
    analyze_self,
)


async def test_openrouter():
    """Тест подключения к OpenRouter"""
    print("🧪 Тест 1: Подключение к OpenRouter API...")
    models, pricing = await fetch_openrouter_models()
    if models:
        print(f"✅ Успех! Получено моделей: {len(models)}")
        for m in models[:3]:
            print(f"  • {m['id']}")
        return True
    else:
        print("❌ Ошибка подключения")
        return False


async def test_scan():
    """Тест сканера проектов"""
    print("\n🧪 Тест 2: Сканирование проектов...")
    try:
        projects = scan_laboratory()
        print(f"✅ Успех! Найдено проектов: {len(projects)}")
        for p in projects[:5]:
            models = ', '.join(p.get('models_used', [])[:2])
            print(f"  • {p['path']}: {models}")
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


async def test_analyze():
    """Тест самоанализа"""
    print("\n🧪 Тест 3: Самоанализ...")
    try:
        result = analyze_self()
        print(f"✅ Успех! Проект: {result.get('project')}")
        print(f"  • Модели: {', '.join(result.get('uses_models', []))}")
        print(f"  • Рекомендаций: {len(result.get('recommendation', []))}")
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


async def test_report():
    """Тест генерации отчёта"""
    print("\n🧪 Тест 4: Генерация отчёта...")
    try:
        models, _ = await fetch_openrouter_models()
        if not models:
            print("❌ Нет моделей для отчёта")
            return False
        
        report = format_top_models(models)
        print("✅ Отчёт сгенерирован")
        # Показываем только первые 300 символов
        preview = report[:300]
        if len(report) > 300:
            preview += "..."
        print(preview)
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


async def test_compare():
    """Тест сравнения моделей"""
    print("\n🧪 Тест 5: Сравнение моделей...")
    try:
        models, _ = await fetch_openrouter_models()
        free_models = [m["id"] for m in models if ":free" in m.get("id", "")]
        
        if not free_models:
            print("❌ Нет FREE моделей")
            return False
        
        test_prompt = "What is 2+2?"
        print(f"  • Промпт: {test_prompt}")
        print(f"  • Модель: {free_models[0]}")
        
        response = await fetch_model_response(free_models[0], test_prompt)
        preview = response[:100]
        if len(response) > 100:
            preview += "..."
        print(f"✅ Ответ получен: {preview}")
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


async def main():
    """Запуск всех тестов"""
    print("🚀 LLMevangelist - Проверка логики\n")
    print("=" * 50)
    
    results = []
    
    # Тест 1: OpenRouter
    r1 = await test_openrouter()
    results.append(("OpenRouter API", r1))
    
    # Тест 2: Scanner
    r2 = await test_scan()
    results.append(("Scanner", r2))
    
    # Тест 3: Analyzer
    r3 = await test_analyze()
    results.append(("Analyzer", r3))
    
    # Тест 4: Report
    r4 = await test_report()
    results.append(("Report", r4))
    
    # Тест 5: Compare
    r5 = await test_compare()
    results.append(("Compare", r5))
    
    # Итоги
    print("\n" + "=" * 50)
    print("📊 ИТОГИ ТЕСТИРОВАНИЯ:\n")
    
    passed = 0
    for name, result in results:
        status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
        print(f"{status} - {name}")
        if result:
            passed += 1
    
    print(f"\nВсего: {passed}/{len(results)} тестов пройдено")
    
    if passed == len(results):
        print("\n🎉 Все тесты пройдены! Логика работает корректно.")
        return 0
    else:
        print("\n⚠️ Есть проблемы в логике!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
