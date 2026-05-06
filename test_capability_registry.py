#!/usr/bin/env python3
"""Тестирование Capability Registry"""

import sys
sys.path.insert(0, '/root/LabDoctorM')

from shared.capability_registry import (
    ExpertiseLevel,
    AgentCapability,
    AgentProfile,
    CapabilityRegistry,
    registry
)

def test_import():
    """Тест 1: Проверка импорта модулей"""
    print("=" * 60)
    print("TEST 1: Импорт модулей")
    print("=" * 60)
    
    assert ExpertiseLevel.EXPERT is not None
    assert AgentCapability is not None
    assert AgentProfile is not None
    assert CapabilityRegistry is not None
    assert registry is not None
    
    print("✓ Все модули импортированы успешно")
    print(f"  - ExpertiseLevel: {len([e for e in ExpertiseLevel])} уровней")
    print(f"  - AgentCapability: {AgentCapability.__name__}")
    print(f"  - AgentProfile: {AgentProfile.__name__}")
    print(f"  - CapabilityRegistry: {CapabilityRegistry.__name__}")
    print()


def test_skill_search():
    """Тест 2: Поиск агента по навыку"""
    print("=" * 60)
    print("TEST 2: Поиск агента по навыку")
    print("=" * 60)
    
    # Создаем тестовый реестр
    test_registry = CapabilityRegistry()
    
    # Агент 1: специалист по Python с высокой уверенностью
    agent1 = AgentProfile(
        agent_name="python_coder",
        capabilities=[
            AgentCapability(
                skill="python",
                tags=["coding", "backend"],
                expertise=ExpertiseLevel.EXPERT,
                confidence=0.95
            )
        ]
    )
    
    # Агент 2: специалист по JavaScript средней уверенностью
    agent2 = AgentProfile(
        agent_name="js_coder",
        capabilities=[
            AgentCapability(
                skill="javascript",
                tags=["coding", "frontend"],
                expertise=ExpertiseLevel.INTERMEDIATE,
                confidence=0.70
            )
        ]
    )
    
    # Агент 3: универсален, но с низкой уверенностью в Python
    agent3 = AgentProfile(
        agent_name="generalist",
        capabilities=[
            AgentCapability(
                skill="general",
                tags=["python", "coding"],
                expertise=ExpertiseLevel.NOVICE,
                confidence=0.30
            )
        ]
    )
    
    # Регистрация
    test_registry.register(agent1)
    test_registry.register(agent2)
    test_registry.register(agent3)
    
    print(f"Зарегистрировано агентов: {len(test_registry.list_agents())}")
    
    # Поиск по прямому навыку
    found = test_registry.find_agent("python")
    print(f"\nПоиск 'python': найден {found.agent_name if found else 'None'}")
    assert found is not None
    assert found.agent_name == "python_coder", f"Ожидался python_coder, получил {found.agent_name}"
    print("✓ Найден правильный агент для прямого навыка")
    
    # Поиск по тегу
    found_tag = test_registry.find_agent("coding")
    print(f"Поиск 'coding': найден {found_tag.agent_name if found_tag else 'None'}")
    assert found_tag is not None
    assert found_tag.agent_name == "python_coder"  # У него выше confidence
    print("✓ Найден правильный агент по тегу (с высшим confidence)")
    
    # Поиск агента с худшей уверенностью
    found_js = test_registry.find_agent("javascript")
    print(f"Поиск 'javascript': найден {found_js.agent_name if found_js else 'None'}")
    assert found_js is not None
    assert found_js.agent_name == "js_coder"
    print("✓ Найден правильный агент для JavaScript")
    print()


def test_confidence_calculation():
    """Тест 3: Вычисление confidence"""
    print("=" * 60)
    print("TEST 3: Вычисление confidence")
    print("=" * 60)
    
    test_registry = CapabilityRegistry()
    
    agent = AgentProfile(
        agent_name="multi_skill_agent",
        capabilities=[
            AgentCapability(skill="python", confidence=0.9),
            AgentCapability(skill="ml", confidence=0.75, tags=["ai", "machine-learning"]),
            AgentCapability(skill="data-analysis", confidence=0.5)
        ]
    )
    
    test_registry.register(agent)
    
    # Проверка confidence для разных навыков
    assert agent.get_skill_confidence("python") == 0.9
    print(f"  python: {agent.get_skill_confidence('python')}")
    
    assert agent.get_skill_confidence("ml") == 0.75
    print(f"  ml: {agent.get_skill_confidence('ml')}")
    
    # Поиск по тегу - должен вернуть confidence основного навыка
    assert agent.get_skill_confidence("ai") == 0.75
    print(f"  ai (по тегу): {agent.get_skill_confidence('ai')}")
    
    assert agent.get_skill_confidence("machine-learning") == 0.75
    print(f"  machine-learning (по тегу): {agent.get_skill_confidence('machine-learning')}")
    
    assert agent.get_skill_confidence("data-analysis") == 0.5
    print(f"  data-analysis: {agent.get_skill_confidence('data-analysis')}")
    
    print("✓ Confidence рассчитывается корректно")
    print()


def test_edge_cases():
    """Тест 4: Edge cases"""
    print("=" * 60)
    print("TEST 4: Edge cases (пустой реестр, несуществующий навык)")
    print("=" * 60)
    
    # Пустой реестр
    empty_registry = CapabilityRegistry()
    assert empty_registry.find_agent("any_skill") is None
    print("✓ Пустой реестр возвращает None")
    
    assert empty_registry.list_agents() == []
    print("✓ Пустой реестр возвращает пустой список агентов")
    
    # Несуществующий навык в заполненном реестре
    test_registry = CapabilityRegistry()
    agent = AgentProfile(
        agent_name="test_agent",
        capabilities=[AgentCapability(skill="python", confidence=0.8)]
    )
    test_registry.register(agent)
    
    not_found = test_registry.find_agent("nonexistent_skill")
    assert not_found is None
    print("✓ Несуществующий навык возвращает None")
    
    zero_conf = agent.get_skill_confidence("nonexistent_skill")
    assert zero_conf == 0.0
    print("✓ Confidence для несуществующего навыка = 0.0")
    
    # Регистрация агента с пустыми навыками
    empty_agent = AgentProfile(agent_name="empty_agent", capabilities=[])
    test_registry.register(empty_agent)
    
    assert empty_agent.get_skill_confidence("python") == 0.0
    print("✓ Агент без навыков возвращает 0.0 confidence")
    
    # Поиск несуществующего агента
    assert test_registry.get_agent("ghost_agent") is None
    print("✓ Поиск несуществующего агента возвращает None")
    
    print()


def run_all_tests():
    """Запуск всех тестов"""
    print("\n" + "=" * 60)
    print("TESTING CAPABILITY REGISTRY")
    print("=" * 60 + "\n")
    
    try:
        test_import()
        test_skill_search()
        test_confidence_calculation()
        test_edge_cases()
        
        print("=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        return True
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)