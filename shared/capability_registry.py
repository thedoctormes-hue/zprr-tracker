"""
Capability Registry — централизованный реестр навыков агентов.

Позволяет динамически определять, какой агент подходит для задачи.
"""

from typing import List, Dict, Any, Optional
try:
    from pydantic import BaseModel, Field
except ImportError:
    from pydantic.v1 import BaseModel, Field
from enum import Enum


class ExpertiseLevel(str, Enum):
    """Уровень экспертизы агента."""
    NOVICE = "novice"      # 0-30% уверенности
    BEGINNER = "beginner"  # 30-50%
    INTERMEDIATE = "intermediate"  # 50-70%
    ADVANCED = "advanced"  # 70-90%
    EXPERT = "expert"      # 90-100%


class AgentCapability(BaseModel):
    """Навык агента."""
    skill: str
    tags: List[str] = Field(default_factory=list)
    expertise: ExpertiseLevel = ExpertiseLevel.INTERMEDIATE
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class AgentProfile(BaseModel):
    """Профиль агента с набором навыков."""
    agent_name: str
    capabilities: List[AgentCapability] = Field(default_factory=list)
    version: str = "1.0.0"
    description: Optional[str] = None

    def has_skill(self, skill: str) -> bool:
        """Проверяет, есть ли у агента нужный навык."""
        skill_lower = skill.lower()
        for cap in self.capabilities:
            if cap.skill.lower() == skill_lower:
                return True
            for tag in cap.tags:
                if tag.lower() == skill_lower:
                    return True
        return False

    def get_skill_confidence(self, skill: str) -> float:
        """Возвращает confidence для конкретного навыка."""
        skill_lower = skill.lower()
        for cap in self.capabilities:
            if cap.skill.lower() == skill_lower:
                return cap.confidence
            for tag in cap.tags:
                if tag.lower() == skill_lower:
                    return cap.confidence
        return 0.0


# Глобальный реестр
class CapabilityRegistry:
    """Централизованный реестр агентов и их навыков."""

    def __init__(self):
        self._agents: Dict[str, AgentProfile] = {}

    def register(self, profile: AgentProfile) -> None:
        """Регистрация агента в реестре."""
        self._agents[profile.agent_name] = profile

    def find_agent(self, required_skill: str) -> Optional[AgentProfile]:
        """Находит агента с нужным навыком (самый высокий confidence)."""
        best_agent = None
        best_confidence = 0.0

        for agent in self._agents.values():
            confidence = agent.get_skill_confidence(required_skill)
            if confidence > best_confidence:
                best_confidence = confidence
                best_agent = agent

        return best_agent

    def list_agents(self) -> List[str]:
        """Список всех зарегистрированных агентов."""
        return list(self._agents.keys())

    def get_agent(self, name: str) -> Optional[AgentProfile]:
        """Получить профиль агента по имени."""
        return self._agents.get(name)


# Глобальный экземпляр
registry = CapabilityRegistry()