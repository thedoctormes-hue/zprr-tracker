#!/usr/bin/env python3
"""
FedLab Smart Search - простая версия без внешней БД
"""
import json, re
from pathlib import Path
from sentence_transformers import SentenceTransformer
import numpy as np

class FedLabSearch:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.documents = []
        self.embeddings = []
    
    def load_events(self, json_path: str):
        data = json.loads(Path(json_path).read_text())
        for item in data:
            text = f"{item.get('title', '')} {item.get('location', '')}"
            if text.strip():
                self.documents.append(item)
                self.embeddings.append(self.model.encode(text))
        self.embeddings = np.array(self.embeddings)
    
    def search(self, query: str, limit: int = 10):
        query_vec = self.model.encode(query)
        scores = np.dot(self.embeddings, query_vec) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_vec)
        )
        top_idx = np.argsort(scores)[-limit:][::-1]
        
        results = []
        for idx in top_idx:
            results.append({
                'score': float(scores[idx]),
                'title': self.documents[idx]['title'],
                'location': self.documents[idx]['location'],
                'month': self.documents[idx]['month']
            })
        return results

if __name__ == "__main__":
    s = FedLabSearch()
    s.load_events('/root/LabDoctorM/fedlab_events.json')
    
    # Тестовый поиск
    results = s.search("КЛФ Санкт-Петербург июнь")
    print(json.dumps(results, ensure_ascii=False, indent=2))