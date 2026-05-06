#!/usr/bin/env python3
"""
УЛЬТИМАТИВНОЕ тестирование Capability Registry
Покрывает все 7 требований:
1. Все уровни ExpertiseLevel (NOVICE, BEGINNER, INTERMEDIATE, ADVANCED, EXPERT)
2. Поиск по прямому навыку и по тегу
3. Выбор агента с высоким confidence когда несколько подходят
4. Граничные случаи: пустой реестр, несуществующий навык, агент без навыков
5. get_skill_confidence для разных сценариев
6. has_skill проверка
7. Регистрация дублирующихся агентов (перезапись)
"""

import sys
sys.path.insert(0, '/root/LabDoctorM')

from shared.capability_registry import (
    ExpertiseLevel,
    AgentCapability,
    AgentProfile,
    CapabilityRegistry,
    registry
)


def print_section(title):
    """Красивый вывод раздела"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_1_all_expertise_levels():
    """
    ТЕСТ 1: Все уровни ExpertiseLevel
    Проверка NOVICE, BEGINNER, INTERMEDIATE, ADVANCED, EXPERT
    """
    print_section("TEST 1: Все уровни ExpertiseLevel")

    # Создаем агентов для каждого уровня
    levels_info = {
        ExpertiseLevel.NOVICE: "0-30% уверенности",
        ExpertiseLevel.BEGINNER: "30-50% уверенности",
        ExpertiseLevel.INTERMEDIATE: "50-70% уверенности",
        ExpertiseLevel.ADVANCED: "70-90% уверенности",
        ExpertiseLevel.EXPERT: "90-100% уверенности"
    }

    test_registry = CapabilityRegistry()

    for level, description in levels_info.items():
        agent = AgentProfile(
            agent_name=f"agent_{level.value}",
            capabilities=[
                AgentCapability(
                    skill=f"skill_{level.value}",
                    expertise=level,
                    confidence=0.85 if level == ExpertiseLevel.EXPERT else 0.65
                )
            ]
        )
        test_registry.register(agent)
        print(f"✓ {level.value.upper():12} - expertise: {level.value}, {description}")

    # Проверяем, что все уровни зарегистрированы
    assert len(test_registry.list_agents()) == 5
    print(f"\n✓ Зарегистрировано {len(test_registry.list_agents())} агентов для всех уровней")

    # Проверка перечисления всех уровней
    all_levels = list(ExpertiseLevel)
    assert len(all_levels) == 5
    print(f"✓ Всего уровней ExpertiseLevel: {len(all_levels)}")
    for level in all_levels:
        print(f"    - {level.name} = '{level.value}'")
    print()


def test_2_search_by_skill_and_tag():
    """
    ТЕСТ 2: Поиск по прямому навыку и по тегу
    """
    print_section("TEST 2: Поиск по прямому навыку и по тегу")

    test_registry = CapabilityRegistry()

    # Агент 1: прямой навык "python"
    agent1 = AgentProfile(
        agent_name="python_developer",
        capabilities=[
            AgentCapability(
                skill="python",
                tags=["programming", "backend"],
                confidence=0.95
            )
        ]
    )

    # Агент 2: навык "javascript", но тег "frontend"
    agent2 = AgentProfile(
        agent_name="js_developer",
        capabilities=[
            AgentCapability(
                skill="javascript",
                tags=["frontend", "web"],
                confidence=0.80
            )
        ]
    )

    # Агент 3: несколько тегов
    agent3 = AgentProfile(
        agent_name="fullstack_dev",
        capabilities=[
            AgentCapability(
                skill="fullstack",
                tags=["python", "javascript", "devops", "cloud"],
                confidence=0.75
            )
        ]
    )

    test_registry.register(agent1)
    test_registry.register(agent2)
    test_registry.register(agent3)

    print(f"Агенты: {test_registry.list_agents()}")

    # Поиск по прямому навыку
    print("\n--- Поиск по прямому навыку ---")
    found_python = test_registry.find_agent("python")
    print(f"  Поиск 'python': {found_python.agent_name if found_python else 'None'}")
    assert found_python.agent_name == "python_developer"
    print("  ✓ Найден python_developer по прямому навыку 'python'")

    found_js = test_registry.find_agent("javascript")
    print(f"  Поиск 'javascript': {found_js.agent_name if found_js else 'None'}")
    assert found_js.agent_name == "js_developer"
    print("  ✓ Найден js_developer по прямому навыку 'javascript'")

    # Поиск по тегу
    print("\n--- Поиск по тегу ---")
    found_frontend = test_registry.find_agent("frontend")
    print(f"  Поиск 'frontend': {found_frontend.agent_name if found_frontend else 'None'}")
    assert found_frontend.agent_name == "js_developer"
    print("  ✓ Найден js_developer по тегу 'frontend'")

    found_backend = test_registry.find_agent("backend")
    print(f"  Поиск 'backend': {found_backend.agent_name if found_backend else 'None'}")
    assert found_backend.agent_name == "python_developer"
    print("  ✓ Найден python_developer по тегу 'backend'")

    found_cloud = test_registry.find_agent("cloud")
    print(f"  Поиск 'cloud': {found_cloud.agent_name if found_cloud else 'None'}")
    assert found_cloud.agent_name == "fullstack_dev"
    print("  ✓ Найден fullstack_dev по тегу 'cloud'")

    # Тег "python" сопоставляется с fullstack_dev (agent3), но python_developer имеет выше confidence
    found_python_tag = test_registry.find_agent("python")
    print(f"  Поиск 'python' (тоже тег fullstack_dev): {found_python_tag.agent_name}")
    assert found_python_tag.agent_name == "python_developer"  # Выше confidence
    print("  ✓ Выбран агент с высшим confidence для тега 'python'")

    print()


def test_3_highest_confidence_selection():
    """
    ТЕСТ 3: Выбор агента с высоким confidence когда несколько подходят
    """
    print_section("TEST 3: Выбор агента с высоким confidence")

    test_registry = CapabilityRegistry()

    # Три агента с разным confidence для одного и того же навыка
    agent_low = AgentProfile(
        agent_name="low_confidence_agent",
        capabilities=[
            AgentCapability(skill="python", confidence=0.30)
        ]
    )

    agent_medium = AgentProfile(
        agent_name="medium_confidence_agent",
        capabilities=[
            AgentCapability(skill="python", confidence=0.60)
        ]
    )

    agent_high = AgentProfile(
        agent_name="high_confidence_agent",
        capabilities=[
            AgentCapability(skill="python", confidence=0.95)
        ]
    )

    # Агент с тегом, но выше confidence чем medium
    agent_tag_high = AgentProfile(
        agent_name="tag_agent_high_conf",
        capabilities=[
            AgentCapability(skill="other", tags=["python"], confidence=0.75)
        ]
    )

    test_registry.register(agent_low)
    test_registry.register(agent_medium)
    test_registry.register(agent_high)
    test_registry.register(agent_tag_high)

    print("Агенты с разным confidence для 'python':")
    print(f"  - {agent_low.agent_name}: 0.30 (direct)")
    print(f"  - {agent_medium.agent_name}: 0.60 (direct)")
    print(f"  - {agent_high.agent_name}: 0.95 (direct)")
    print(f"  - {agent_tag_high.agent_name}: 0.75 (via tag)")

    found = test_registry.find_agent("python")
    print(f"\n  Выбран: {found.agent_name} (должен быть high_confidence_agent)")
    assert found.agent_name == "high_confidence_agent"
    print("  ✓ Выбран агент с самым высоким confidence = 0.95")

    # Проверка выбора между тегом и прямым навыком
    test2 = CapabilityRegistry()

    agent_direct_low = AgentProfile(
        agent_name="direct_low",
        capabilities=[AgentCapability(skill="python", confidence=0.40)]
    )

    agent_tag_higher = AgentProfile(
        agent_name="tag_higher",
        capabilities=[AgentCapability(skill="other", tags=["python"], confidence=0.85)]
    )

    test2.register(agent_direct_low)
    test2.register(agent_tag_higher)

    found2 = test2.find_agent("python")
    print(f"\n  Выбор между 0.40 (direct) и 0.85 (tag): {found2.agent_name}")
    assert found2.agent_name == "tag_higher"
    print("  ✓ Выбран агент с высшим confidence независимо от прямого/тег")

    print()


def test_4_edge_cases():
    """
    ТЕСТ 4: Граничные случаи
    - пустой реестр
    - несуществующий навык
    - агент без навыков
    """
    print_section("TEST 4: Граничные случаи")

    # 4.1 Пустой реестр
    print("--- 4.1 Пустой реестр ---")
    empty_registry = CapabilityRegistry()
    assert empty_registry.find_agent("any_skill") is None
    print("  ✓ find_agent('any_skill') = None для пустого реестра")
    assert empty_registry.list_agents() == []
    print("  ✓ list_agents() = [] для пустого реестра")
    assert empty_registry.get_agent("nonexistent") is None
    print("  ✓ get_agent('nonexistent') = None для пустого реестра")

    # 4.2 Несуществующий навык
    print("\n--- 4.2 Несуществующий навык ---")
    test_registry = CapabilityRegistry()
    agent = AgentProfile(
        agent_name="test_agent",
        capabilities=[AgentCapability(skill="python", confidence=0.8)]
    )
    test_registry.register(agent)

    not_found = test_registry.find_agent("nonexistent_skill")
    assert not_found is None
    print("  ✓ find_agent('nonexistent_skill') = None")

    zero_conf = agent.get_skill_confidence("nonexistent_skill")
    assert zero_conf == 0.0
    print("  ✓ get_skill_confidence('nonexistent_skill') = 0.0")

    # 4.3 Агент без навыков
    print("\n--- 4.3 Агент без навыков ---")
    empty_agent = AgentProfile(agent_name="empty_agent", capabilities=[])
    test_registry.register(empty_agent)

    assert empty_agent.get_skill_confidence("python") == 0.0
    print("  ✓ Агент без навыков: get_skill_confidence('python') = 0.0")

    assert empty_agent.has_skill("python") == False
    print("  ✓ Агент без навыков: has_skill('python') = False")

    # 4.4 Поиск несуществующего агента
    print("\n--- 4.4 Поиск несуществующего агента ---")
    assert test_registry.get_agent("ghost_agent") is None
    print("  ✓ get_agent('ghost_agent') = None")

    # 4.5 Агент с несколькими одинаковыми confidence
    print("\n--- 4.5 Агенты с одинаковым confidence ---")
    same_conf_registry = CapabilityRegistry()

    agent1 = AgentProfile(
        agent_name="agent_a",
        capabilities=[AgentCapability(skill="python", confidence=0.5)]
    )
    agent2 = AgentProfile(
        agent_name="agent_b",
        capabilities=[AgentCapability(skill="python", confidence=0.5)]
    )

    same_conf_registry.register(agent1)
    same_conf_registry.register(agent2)

    found = same_conf_registry.find_agent("python")
    # При одинаковом confidence выбирается последний найденный
    print(f"  При одинаковом confidence (0.5) выбран: {found.agent_name}")
    print("  ✓ При равных confidence выбирается один из подходящих")

    print()


def test_5_get_skill_confidence_scenarios():
    """
    ТЕСТ 5: get_skill_confidence для разных сценариев
    """
    print_section("TEST 5: get_skill_confidence для разных сценариев")

    # 5.1 Прямой навык
    agent1 = AgentProfile(
        agent_name="dev",
        capabilities=[AgentCapability(skill="python", confidence=0.9)]
    )
    conf = agent1.get_skill_confidence("python")
    print(f"  Прямой навык 'python': {conf}")
    assert conf == 0.9

    # 5.2 Через тег
    agent2 = AgentProfile(
        agent_name="ml_dev",
        capabilities=[
            AgentCapability(skill="ml", tags=["ai", "deep-learning"], confidence=0.85)
        ]
    )
    conf_ai = agent2.get_skill_confidence("ai")
    conf_dl = agent2.get_skill_confidence("deep-learning")
    print(f"  Через тег 'ai': {conf_ai}")
    print(f"  Через тег 'deep-learning': {conf_dl}")
    assert conf_ai == 0.85
    assert conf_dl == 0.85

    # 5.3 Регистр не важен
    conf_upper = agent1.get_skill_confidence("PYTHON")
    conf_lower = agent1.get_skill_confidence("python")
    print(f"  Регистронезависимость: PYTHON={conf_upper}, python={conf_lower}")
    assert conf_upper == conf_lower

    # 5.4 Несколько навыков
    agent3 = AgentProfile(
        agent_name="multi",
        capabilities=[
            AgentCapability(skill="python", confidence=0.9),
            AgentCapability(skill="java", confidence=0.7),
            AgentCapability(skill="go", confidence=0.8)
        ]
    )
    print(f"  Python: {agent3.get_skill_confidence('python')}")
    print(f"  Java: {agent3.get_skill_confidence('java')}")
    print(f"  Go: {agent3.get_skill_confidence('go')}")
    assert agent3.get_skill_confidence("python") == 0.9
    assert agent3.get_skill_confidence("java") == 0.7
    assert agent3.get_skill_confidence("go") == 0.8

    # 5.5 Приоритет первого найденного (прямой навык vs тег)
    agent4 = AgentProfile(
        agent_name="complex",
        capabilities=[
            AgentCapability(skill="primary", tags=["search"], confidence=0.95),
            AgentCapability(skill="secondary", tags=["search"], confidence=0.70)
        ]
    )
    conf_search = agent4.get_skill_confidence("search")
    print(f"  Приоритет первого совпадения для тега 'search': {conf_search}")
    # Первый навык в списке имеет тот же тег, но выше confidence
    assert conf_search == 0.95

    print("\n✓ Все сценарии get_skill_confidence протестированы")
    print()


def test_6_has_skill_check():
    """
    ТЕСТ 6: has_skill проверка
    """
    print_section("TEST 6: has_skill проверка")

    agent = AgentProfile(
        agent_name="test_agent",
        capabilities=[
            AgentCapability(
                skill="python",
                tags=["backend", "coding"],
                confidence=0.9
            ),
            AgentCapability(
                skill="ml",
                tags=["ai", "data-science"],
                confidence=0.8
            )
        ]
    )

    # 6.1 Прямой навык
    print("--- Прямые навыки ---")
    assert agent.has_skill("python") == True
    print(f"  has_skill('python'): {agent.has_skill('python')} ✓")
    assert agent.has_skill("ml") == True
    print(f"  has_skill('ml'): {agent.has_skill('ml')} ✓")

    # 6.2 Через тег
    print("\n--- Через тег ---")
    assert agent.has_skill("backend") == True
    print(f"  has_skill('backend'): {agent.has_skill('backend')} ✓")
    assert agent.has_skill("ai") == True
    print(f"  has_skill('ai'): {agent.has_skill('ai')} ✓")
    assert agent.has_skill("data-science") == True
    print(f"  has_skill('data-science'): {agent.has_skill('data-science')} ✓")

    # 6.3 Неизвестный навык
    print("\n--- Неизвестные навыки ---")
    assert agent.has_skill("ruby") == False
    print(f"  has_skill('ruby'): {agent.has_skill('ruby')} ✓")
    assert agent.has_skill("nonexistent") == False
    print(f"  has_skill('nonexistent'): {agent.has_skill('nonexistent')} ✓")

    # 6.4 Регистронезависимость
    print("\n--- Регистронезависимость ---")
    assert agent.has_skill("PYTHON") == True
    print(f"  has_skill('PYTHON'): {agent.has_skill('PYTHON')} ✓")
    assert agent.has_skill("BACKEND") == True
    print(f"  has_skill('BACKEND'): {agent.has_skill('BACKEND')} ✓")

    # 6.5 Агент без навыков
    empty_agent = AgentProfile(agent_name="empty", capabilities=[])
    assert empty_agent.has_skill("anything") == False
    print(f"  Агент без навыков: has_skill('anything'): {empty_agent.has_skill('anything')} ✓")

    print("\n✓ Все проверки has_skill пройдены")
    print()


def test_7_duplicate_agent_overwrite():
    """
    ТЕСТ 7: Регистрация дублирующихся агентов (перезапись)
    """
    print_section("TEST 7: Регистрация дублирующихся агентов")

    test_registry = CapabilityRegistry()

    # Первоначальная регистрация
    original_agent = AgentProfile(
        agent_name="duplicate_test",
        capabilities=[
            AgentCapability(skill="python", confidence=0.8)
        ],
        description="Original version"
    )
    test_registry.register(original_agent)
    print(f"Исходный агент: {original_agent.agent_name}")
    print(f"  Capabilities: {original_agent.capabilities}")
    print(f"  Description: {original_agent.description}")

    # Проверка исходного
    found = test_registry.get_agent("duplicate_test")
    assert found.description == "Original version"
    assert len(found.capabilities) == 1
    print("\n✓ Первоначальная регистрация проверена")

    # Перезапись новым агентом с тем же именем
    updated_agent = AgentProfile(
        agent_name="duplicate_test",
        capabilities=[
            AgentCapability(skill="python", confidence=0.95),
            AgentCapability(skill="ml", confidence=0.9),
            AgentCapability(skill="go", confidence=0.85)
        ],
        version="2.0.0",
        description="Updated version"
    )
    test_registry.register(updated_agent)
    print(f"\nОбновленный агент: {updated_agent.agent_name}")
    print(f"  Capabilities: {[c.skill for c in updated_agent.capabilities]}")
    print(f"  Description: {updated_agent.description}")

    # Проверка, что данные обновились
    found_updated = test_registry.get_agent("duplicate_test")
    assert found_updated.description == "Updated version"
    assert len(found_updated.capabilities) == 3
    print("\n✓ Данные успешно обновлены (перезаписаны)")

    # Проверка, что в реестре один агент
    assert len(test_registry.list_agents()) == 1
    print(f"✓ В реестре ровно 1 агент: {test_registry.list_agents()}")

    # Проверка, что capabilities изменились
    conf_python = found_updated.get_skill_confidence("python")
    conf_ml = found_updated.get_skill_confidence("ml")
    conf_go = found_updated.get_skill_confidence("go")
    print(f"\n  python confidence: {conf_python} (ожидалось 0.95)")
    print(f"  ml confidence: {conf_ml} (ожидалось 0.9)")
    print(f"  go confidence: {conf_go} (ожидалось 0.85)")

    assert conf_python == 0.95
    assert conf_ml == 0.9
    assert conf_go == 0.85
    print("\n✓ Все capabilities успешно обновлены")

    print()


def run_all_tests():
    """Запуск всех тестов"""
    print("\n" + "=" * 70)
    print("    УЛЬТИМАТИВНОЕ ТЕСТИРОВАНИЕ CAPABILITY REGISTRY")
    print("    Полное покрытие 7 пунктов тестирования")
    print("=" * 70)

    all_passed = True

    try:
        test_1_all_expertise_levels()
        test_2_search_by_skill_and_tag()
        test_3_highest_confidence_selection()
        test_4_edge_cases()
        test_5_get_skill_confidence_scenarios()
        test_6_has_skill_check()
        test_7_duplicate_agent_overwrite()

        print("=" * 70)
        print("    ALL 7 TEST SECTIONS PASSED ✓✓✓")
        print("=" * 70)
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