#!/usr/bin/env python3
"""
Price Analyzer — сравнение НМЦК госзакупок с рыночными ценами
"""
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# Market sources for price comparison
MARKET_SOURCES = {
    "wildberries": "https://www.wildberries.ru",
    "ozon": "https://www.ozon.ru", 
    "yandex_market": "https://market.yandex.ru",
    "aliexpress": "https://www.aliexpress.com"
}

@dataclass
class PriceMatch:
    """Сопоставление цены"""
    source: str
    product_name: str
    market_price: float
    gov_price: float
    profit_potential: float  # в процентах
    url: str
    drop_shipping_score: float  # 0-1

@dataclass
class AnalysisResult:
    """Результат анализа контракта"""
    contract_subject: str
    gov_price: float
    matches: List[PriceMatch]
    best_margin: float
    recommendation: str


class PriceAnalyzer:
    """Анализатор цен для дропшипинга"""

    def __init__(self):
        self.min_profit_threshold = float(os.getenv("MIN_PROFIT_THRESHOLD", "25.0"))
        self.min_contract_price = float(os.getenv("MIN_CONTRACT_PRICE", "10000.0"))

    def calculate_profit_potential(self, gov_price: float, market_price: float) -> float:
        """Расчёт потенциальной прибыли в процентах"""
        if market_price <= 0:
            return 0.0
        return ((gov_price - market_price) / market_price) * 100

    def calculate_drop_shipping_score(self, profit_potential: float, volume: int = 1) -> float:
        """Оценка потенциала дропшипинга (0-1)"""
        # Базовый скор: прибыльность + объём
        base_score = min(profit_potential / 50.0, 1.0)  # макс 50% = score 1.0
        volume_boost = min(volume / 100.0, 0.2)  # до 20% за объём
        return round(min(base_score + volume_boost, 1.0), 2)

    def analyze_contract(
        self, 
        subject: str, 
        gov_price: float, 
        region: str = ""
    ) -> AnalysisResult:
        """Анализ контракта на прибыльность"""
        matches = []
        
        # TODO: Интеграция с API маркетплейсов
        # Пока используем заглушку
        mock_matches = self._mock_market_search(subject, gov_price)
        
        for match in mock_matches:
            profit = self.calculate_profit_potential(gov_price, match["price"])
            if profit >= self.min_profit_threshold:
                score = self.calculate_drop_shipping_score(profit)
                matches.append(PriceMatch(
                    source=match["source"],
                    product_name=match["name"],
                    market_price=match["price"],
                    gov_price=gov_price,
                    profit_potential=profit,
                    url=match["url"],
                    drop_shipping_score=score
                ))

        best_margin = max((m.profit_potential for m in matches), default=0.0)
        
        recommendation = self._generate_recommendation(best_margin, len(matches))
        
        return AnalysisResult(
            contract_subject=subject,
            gov_price=gov_price,
            matches=sorted(matches, key=lambda x: x.profit_potential, reverse=True)[:5],
            best_margin=best_margin,
            recommendation=recommendation
        )

    def _mock_market_search(self, subject: str, gov_price: float) -> List[Dict]:
        """Заглушка для поиска в маркетплейсах"""
        # TODO: Реальная интеграция через API или парсинг
        import hashlib
        
        # Детерминированный "случайный" ценник для демо
        seed = int(hashlib.md5(subject.encode()).hexdigest()[:8], 16)
        base_price = gov_price * (0.6 + (seed % 40) / 100)  # 60-100% от гос цены
        
        return [
            {
                "source": "wildberries",
                "name": f"{subject[:30]}...",
                "price": round(base_price * 0.95, 2),
                "url": f"https://wildberries.ru/catalog/{seed}"
            },
            {
                "source": "ozon",
                "name": f"Оригинал: {subject[:25]}",
                "price": round(base_price * 1.05, 2),
                "url": f"https://ozon.ru/product/{seed}"
            },
        ]

    def _generate_recommendation(self, margin: float, matches_count: int) -> str:
        """Генерация рекомендации"""
        if margin >= 50 and matches_count >= 2:
            return "🔥 ОТЛИЧНАЯ возможность! Высокая прибыль и несколько поставщиков"
        elif margin >= 35:
            return "✅ Хорошая сделка — проверить поставщиков"
        elif margin >= 25:
            return "⚠️ Умеренная прибыль — требует внимательной проверки"
        else:
            return "❌ Низкая прибыль — ищите другие контракты"


def format_signal(result: AnalysisResult) -> str:
    """Форматирование сигнала для Telegram"""
    lines = [
        f"📊 <b>{result.contract_subject[:50]}</b>",
        f"💰 Гос цена: {result.gov_price:,.0f} ₽",
        "",
    ]
    
    for match in result.matches[:3]:
        lines.append(
            f"🛒 {match.source}: {match.market_price:,.0f} ₽ "
            f"({match.profit_potential:.1f}% выгода)"
        )
    
    lines.extend([
        "",
        f"📈 Лучшая наценка: {result.best_margin:.1f}%",
        f"{result.recommendation}",
    ])
    
    return "\n".join(lines)


if __name__ == "__main__":
    # Тестовый запуск
    analyzer = PriceAnalyzer()
    result = analyzer.analyze_contract("Медицинские маски 3 слоя", 150000.0, "77")
    print(format_signal(result))