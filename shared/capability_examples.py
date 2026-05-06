"""
Примеры регистрации навыков для агентов лаборатории.
"""


def create_vpn_infrastructure_profile():
    """Создаёт профиль VPN-инфраструктурного агента."""
    from capability_registry import AgentProfile, AgentCapability, ExpertiseLevel
    
    return AgentProfile(
        agent_name="vpn-infrastructure-agent",
        version="1.0.0",
        description="Эксперт по VLESS/REALITY/xhttp, VPN туннелирование, DPI обход",
        capabilities=[
            AgentCapability(
                skill="vpn",
                tags=["vless", "reality", "xhttp", "dpi-bypass"],
                expertise=ExpertiseLevel.EXPERT,
                confidence=0.95
            ),
            AgentCapability(
                skill="server-management",
                tags=["warsaw", "florida", "60k-scaling"],
                expertise=ExpertiseLevel.ADVANCED,
                confidence=0.90
            ),
        ]
    )


def create_tester_profile():
    """Создаёт профиль тестировщика."""
    from capability_registry import AgentProfile, AgentCapability, ExpertiseLevel
    
    return AgentProfile(
        agent_name="tester",
        version="1.0.0",
        description="Тестировщик Telegram-ботов и Python-кода",
        capabilities=[
            AgentCapability(
                skill="testing",
                tags=["pytest", "telegram-bots", "python"],
                expertise=ExpertiseLevel.ADVANCED,
                confidence=0.85
            ),
            AgentCapability(
                skill="debugging",
                tags=["python", "telegram", "async"],
                expertise=ExpertiseLevel.INTERMEDIATE,
                confidence=0.75
            ),
        ]
    )


def create_deploy_bot_profile():
    """Создаёт профиль деплой-бота."""
    from capability_registry import AgentProfile, AgentCapability, ExpertiseLevel
    
    return AgentProfile(
        agent_name="deploy-bot",
        version="1.0.0",
        description="Автоматизирует деплой проектов лаборатории",
        capabilities=[
            AgentCapability(
                skill="deployment",
                tags=["systemd", "fastapi", "react", "nginx"],
                expertise=ExpertiseLevel.EXPERT,
                confidence=0.92
            ),
            AgentCapability(
                skill="ci-cd",
                tags=["github-actions", "docker"],
                expertise=ExpertiseLevel.ADVANCED,
                confidence=0.80
            ),
        ]
    )


if __name__ == "__main__":
    import sys
    sys.path.insert(0, __file__.rsplit('/', 1)[0])
    from capability_registry import registry
    
    # Регистрация всех агентов
    registry.register(create_vpn_infrastructure_profile())
    registry.register(create_tester_profile())
    registry.register(create_deploy_bot_profile())

    # Примеры поиска
    print("=== Примеры поиска агентов ===")
    for skill in ["vpn", "testing", "deployment", "nonexistent"]:
        best = registry.find_agent(skill)
        if best:
            print(f"Skill '{skill}': {best.agent_name} (confidence: {best.get_skill_confidence(skill):.2f})")
        else:
            print(f"Skill '{skill}': не найден")