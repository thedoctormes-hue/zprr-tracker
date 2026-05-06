#!/usr/bin/env python3
"""
FedLab Simple Search - TF-IDF без ML моделей
"""
import json, re
from pathlib import Path
from collections import Counter
import math

class SimpleSearch:
    def __init__(self):
        self.documents = []
        self.corpus = []
    
    def load_events(self, json_path: str):
        data = json.loads(Path(json_path).read_text())
        for item in data:
            text = f"{item.get('title', '')} {item.get('location', '')}"
            if text.strip():
                self.documents.append(item)
                self.corpus.append(text.lower())
    
    def tokenize(self, text):
        return re.findall(r'[а-яёa-z]+', text.lower())
    
    def search(self, query: str, limit: int = 10):
        query_words = Counter(self.tokenize(query))
        scores = []
        
        for i, doc_text in enumerate(self.corpus):
            doc_words = Counter(self.tokenize(doc_text))
            
            # TF-IDF простая реализация
            score = sum((doc_words.get(w, 0) * qf) for w, qf in query_words.items())
            
            # Бонус за точное совпадение месяца
            query_month = query_words.get('май', 0) * 5 or query_words.get('июнь', 0) * 5 or 0
            doc_month = doc_words.get('май', 0) * 5 or doc_words.get('июнь', 0) * 5 or 0
            score += min(query_month, doc_month)
            
            scores.append((score, i))
        
        scores.sort(reverse=True)
        results = []
        for score, idx in scores[:limit]:
            if score > 0:
                results.append({
                    'score': score,
                    'title': self.documents[idx]['title'],
                    'location': self.documents[idx]['location'],
                    'month': self.documents[idx]['month']
                })
        return results

if __name__ == "__main__":
    s = SimpleSearch()
    s.load_events('/root/LabDoctorM/fedlab_events.json')
    
    # Тесты поиска
    queries = [
        "КЛФ Санкт-Петербург",
        "форум июнь",
        "РКЛМ Москва"
    ]
    
    for q in queries:
        print(f"\n🔍 '{q}':")
        for r in s.search(q):
            print(f"  - {r['title']} ({r['location']}, {r['month']})")