#!/usr/bin/env python3
"""
FedLab Semantic Parser — Topic Classifier
"""
import re
from typing import List, Tuple
from dataclasses import dataclass

@dataclass
class Classification:
    category: str
    confidence: float
    tags: List[str]

class TopicClassifier:
    """Классификатор тем документов"""
    
    # Ключевые слова для каждой категории
    KEYWORDS = {
        "ГОСТ": [
            "гост", "р ост", "технический регламент", "стандарт", 
            "tr cu", "госстандарт", "потребительский", "промышленный"
        ],
        "ПЗИ/ПБ": [
            "пзи", "пожарная безопасность", "противопожар", "пожарный",
            "постановление", "федеральный закон", "фз", "рд", "свод правил"
        ],
        "PCR": [
            "pcr", "полимеразная цепная реакция", "рт-pcr", "qpcr", 
            "реальное время", "днаковая диагностика", "генная инженерия"
        ],
        "микробиология": [
            "микроб", "бактериолог", "вирусолог", "прокладка", 
            "посев", "аутопси", "антитела", "иммун"
        ],
        "безопасность": [
            "безопасность", "охрана труда", "охрана здоровья",
            "biohazard", "биологический риск", "инфекционный", 
            "передовка", "дезинфекция", "стерилизация"
        ]
    }
    
    # Роли для контента
    ROLE_KEYWORDS = {
        "заведующий КДЛ": ["заведующий", "руководитель", "директор", "командировка", "лицензия"],
        "лаборант": ["лаборант", "технолог", "оператор", "исследование"],
        "врач": ["врач", "диагностика", "нозология", "терапевт"]
    }
    
    def classify(self, text: str, title: str = "") -> Classification:
        """Классифицирует документ по темам"""
        full_text = f"{title} {text}".lower()
        
        scores = {}
        for category, keywords in self.KEYWORDS.items():
            score = sum(1 for kw in keywords if re.search(rf'\b{kw}\b', full_text, re.IGNORECASE))
            scores[category] = score
        
        # Определяем категорию с максимальным счётом
        best_category = max(scores, key=scores.get)
        confidence = scores[best_category] / max(sum(scores.values()), 1)
        
        # Если нет совпадений - ставим "общие"
        if scores[best_category] == 0:
            best_category = "общие"
            confidence = 0.1
        
        # Извлекаем теги
        tags = [cat for cat, sc in scores.items() if sc > 0]
        
        return Classification(
            category=best_category,
            confidence=min(confidence, 1.0),
            tags=tags
        )
    
    def classify_role(self, text: str) -> str:
        """Определяет роль аудитории контента"""
        full_text = text.lower()
        
        scores = {}
        for role, keywords in self.ROLE_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in full_text)
            scores[role] = score
        
        if not scores or max(scores.values()) == 0:
            return "все"
        
        return max(scores, key=scores.get)


# Префикс для категорий
CATEGORY_PREFIXES = {
    "ГОСТ": "[ГОСТ]",
    "ПЗИ/ПБ": "[ПБ]",
    "PCR": "[PCR]",
    "микробиология": "[Микроб]",
    "безопасность": "[Безопасность]"
}


if __name__ == "__main__":
    clf = TopicClassifier()
    test_texts = [
        "ГОСТ Р 52764-2007 для микробиологического анализа крови",
        "Пожарная безопасность лабораторий ПЗИ требования",
        "PCR диагностика коронавируса методика",
        "Посев на антисептик в бактериологической лаборатории"
    ]
    
    for text in test_texts:
        result = clf.classify(text)
        print(f"{text[:50]}... -> {result.category} ({result.confidence:.2f})")