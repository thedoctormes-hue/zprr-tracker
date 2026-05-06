#!/usr/bin/env python3
"""
FedLab Semantic Parser — Vector DB Module (Qdrant)
"""
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, Filter, FieldCondition, MatchValue
import numpy as np
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import uuid
import logging

logger = logging.getLogger(__name__)

@dataclass
class Document:
    """Документ с метаданными"""
    id: str
    content: str
    title: str
    url: str
    doc_type: str  # news, document, event
    category: str  # ГОСТ, ПЗИ/ПБ, PCR, микробиология, безопасность
    role: str  # заведующий КДЛ, лаборант, все
    version: int
    timestamp: str

class VectorDB:
    """Qdrant векторная база данных"""
    
    def __init__(self, host: str = "localhost", port: int = 6333, collection_name: str = "fedlab_documents"):
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = collection_name
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Создаёт коллекцию если не существует"""
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)
        
        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=384,  # Размер embeddings модели MiniLM
                    distance=Distance.COSINE
                )
            )
            # Создаём индексы для фильтрации
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="category",
                field_schema=models.KeywordIndexType()
            )
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="doc_type",
                field_schema=models.KeywordIndexType()
            )
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="role",
                field_schema=models.KeywordIndexType()
            )
            logger.info(f"Created collection: {self.collection_name}")
    
    def upsert_document(self, doc: Document, embedding: np.ndarray):
        """Добавляет или обновляет документ"""
        point_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{doc.url}_{doc.version}"))
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=[models.PointStruct(
                id=point_id,
                vector=embedding.tolist(),
                payload={
                    "id": doc.id,
                    "title": doc.title,
                    "content": doc.content[:1000],  # Обрезаем для хранения
                    "url": doc.url,
                    "doc_type": doc.doc_type,
                    "category": doc.category,
                    "role": doc.role,
                    "version": doc.version,
                    "timestamp": doc.timestamp
                }
            )]
        )
    
    def search(
        self, 
        query_embedding: np.ndarray, 
        limit: int = 10,
        category: Optional[str] = None,
        doc_type: Optional[str] = None,
        role: Optional[str] = None,
        score_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Семантический поиск с фильтрами"""
        filters = []
        
        if category:
            filters.append(FieldCondition(key="category", match=MatchValue(value=category)))
        if doc_type:
            filters.append(FieldCondition(key="doc_type", match=MatchValue(value=doc_type)))
        if role:
            filters.append(FieldCondition(key="role", match=MatchValue(value=role)))
        
        query_filter = Filter(must=filters) if filters else None
        
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding.tolist(),
            query_filter=query_filter,
            limit=limit,
            score_threshold=score_threshold
        )
        
        return [
            {
                "id": r.payload["id"],
                "title": r.payload["title"],
                "content": r.payload["content"],
                "url": r.payload["url"],
                "score": r.score,
                "category": r.payload["category"],
                "doc_type": r.payload["doc_type"],
                "role": r.payload["role"]
            }
            for r in results
        ]
    
    def get_document(self, doc_id: str) -> Optional[Dict]:
        """Получить документ по ID"""
        # Используем scroll для поиска
        results = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=Filter(
                must=[FieldCondition(key="id", match=MatchValue(value=doc_id))]
            ),
            limit=1
        )
        if results[0]:
            return results[0][0].payload
        return None
    
    def get_categories(self) -> List[str]:
        """Получить список категорий"""
        return ["ГОСТ", "ПЗИ/ПБ", "PCR", "микробиология", "безопасность"]
    
    def get_doc_types(self) -> List[str]:
        """Получить типы документов"""
        return ["news", "document", "event"]


if __name__ == "__main__":
    # Test
    vdb = VectorDB()
    print(f"Collection ready: {vdb.collection_name}")
    print(f"Categories: {vdb.get_categories()}")