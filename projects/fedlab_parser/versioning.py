#!/usr/bin/env python3
"""
FedLab Semantic Parser — Document Versioning
Система версонирования документов
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
import hashlib
import json

@dataclass
class DocumentVersion:
    """Версия документа"""
    version: int
    content_hash: str
    timestamp: str
    changes: List[str] = field(default_factory=list)
    
    def to_dict(self):
        return asdict(self)


@dataclass 
class DocumentHistory:
    """История версий документа"""
    doc_id: str
    url: str
    versions: List[DocumentVersion] = field(default_factory=list)
    
    def add_version(self, content: str, changes: List[str] = None) -> DocumentVersion:
        """Добавляет новую версию"""
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        
        # Проверяем, изменился ли контент
        latest = self.get_latest_version()
        if latest and latest.content_hash == content_hash:
            return latest
        
        version = DocumentVersion(
            version=len(self.versions) + 1,
            content_hash=content_hash,
            timestamp=datetime.now().isoformat(),
            changes=changes or ["updated"]
        )
        self.versions.append(version)
        return version
    
    def get_latest_version(self) -> Optional[DocumentVersion]:
        if not self.versions:
            return None
        return self.versions[-1]
    
    def get_version(self, version: int) -> Optional[DocumentVersion]:
        for v in self.versions:
            if v.version == version:
                return v
        return None
    
    def to_dict(self):
        return {
            "doc_id": self.doc_id,
            "url": self.url,
            "versions": [v.to_dict() for v in self.versions]
        }


class VersionManager:
    """Менеджер версий документов"""
    
    def __init__(self):
        self.histories: Dict[str, DocumentHistory] = {}
    
    def get_or_create_history(self, doc_id: str, url: str) -> DocumentHistory:
        """Получить или создать историю"""
        if doc_id not in self.histories:
            self.histories[doc_id] = DocumentHistory(doc_id=doc_id, url=url)
        return self.histories[doc_id]
    
    def check_and_add_version(
        self, 
        doc_id: str, 
        url: str, 
        content: str,
        changes: List[str] = None
    ) -> DocumentVersion:
        """Проверяет и добавляет версию если контент изменился"""
        history = self.get_or_create_history(doc_id, url)
        return history.add_version(content, changes)
    
    def get_history(self, doc_id: str) -> Optional[DocumentHistory]:
        return self.histories.get(doc_id)
    
    def get_all_histories(self) -> List[Dict[str, Any]]:
        return [h.to_dict() for h in self.histories.values()]


# Глобальный менеджер версий
version_manager = VersionManager()


if __name__ == "__main__":
    vm = VersionManager()
    
    # Тест
    v1 = vm.check_and_add_version("doc1", "https://example.com/doc1", "Initial content")
    print(f"Version 1: {v1.version} - {v1.content_hash}")
    
    v2 = vm.check_and_add_version("doc1", "https://example.com/doc1", "Updated content", ["minor fix"])
    print(f"Version 2: {v2.version} - {v2.content_hash}")
    
    v3 = vm.check_and_add_version("doc1", "https://example.com/doc1", "Updated content")  # Тот же контент
    print(f"Version 3 (same): {v3.version} - {v3.content_hash}")  # Должна быть v2