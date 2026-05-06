#!/usr/bin/env python3
"""
FedLab Semantic Parser — Main Parser
Парсит fedlab.ru и сохраняет в векторную БД
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
from typing import List, Optional
from dataclasses import dataclass, asdict
import json
import time
from datetime import datetime

from embeddings import EmbeddingsEngine, chunk_text
from vector_db import VectorDB, Document
from classifier import TopicClassifier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "https://fedlab.ru"

@dataclass
class ParsedContent:
    """Результат парсинга"""
    title: str
    content: str
    url: str
    doc_type: str
    published_at: Optional[str] = None

class FedLabSmartParser:
    """Умный парсер fedlab.ru с семантической обработкой"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.embeddings = EmbeddingsEngine()
        self.vdb = VectorDB()
        self.classifier = TopicClassifier()
        self.processed_urls = set()
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={"User-Agent": "Mozilla/5.0 (compatible; FedLabBot/1.0)"}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch(self, url: str) -> Optional[str]:
        """Загружает страницу"""
        try:
            async with self.session.get(url, timeout=30) as response:
                if response.status == 200:
                    return await response.text()
        except Exception as e:
            logger.error(f"Fetch error {url}: {e}")
        return None
    
    async def parse_news(self) -> List[ParsedContent]:
        """Парсит новости"""
        logger.info("Parsing news...")
        results = []
        
        html = await self.fetch(f"{BASE_URL}/news")
        if not html:
            return results
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Ищем ссылки на новости
        for link in soup.find_all('a', href=True):
            href = link['href']
            if '/news/' in href and href not in self.processed_urls:
                url = urljoin(BASE_URL, href)
                content = await self.fetch(url)
                if content:
                    parsed = self._extract_content(content, url, 'news')
                    if parsed:
                        results.append(parsed)
                        self.processed_urls.add(href)
        
        return results
    
    async def parse_documents(self) -> List[ParsedContent]:
        """Парсит документы"""
        logger.info("Parsing documents...")
        results = []
        
        # Документы могут быть в разделе /documents или /library
        paths = ['/documents', '/library', '/docs']
        
        for path in paths:
            html = await self.fetch(f"{BASE_URL}{path}")
            if not html:
                continue
            
            soup = BeautifulSoup(html, 'html.parser')
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                if any(x in href for x in ['.pdf', '.doc', '.docx']) or '/doc/' in href:
                    url = urljoin(BASE_URL, href)
                    parsed = self._extract_content(await self.fetch(url), url, 'document')
                    if parsed:
                        results.append(parsed)
        
        return results
    
    async def parse_events(self) -> List[ParsedContent]:
        """Парсит мероприятия"""
        logger.info("Parsing events...")
        results = []
        
        html = await self.fetch(f"{BASE_URL}/events")
        if not html:
            html = await self.fetch(f"{BASE_URL}/calendar")
        
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            
            for item in soup.find_all(['article', 'div', 'li'], class_=lambda x: x and 'event' in x.lower()):
                title = item.find(['h1', 'h2', 'h3', 'h4'])
                if title:
                    content = item.get_text(strip=True)
                    url = item.find('a')['href'] if item.find('a') else ""
                    results.append(ParsedContent(
                        title=title.get_text(strip=True),
                        content=content,
                        url=urljoin(BASE_URL, url),
                        doc_type='event'
                    ))
        
        return results
    
    def _extract_content(self, html: str, url: str, doc_type: str) -> Optional[ParsedContent]:
        """Извлекает основной контент со страницы"""
        if not html:
            return None
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Удаляем ненужные элементы
        for elem in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            elem.decompose()
        
        # Извлекаем заголовок
        title = soup.find('h1') or soup.find('title') or soup.find('meta', {'property': 'og:title'})
        title_text = title.get_text(strip=True) if title else "Без названия"
        
        # Извлекаем основной контент
        content_div = soup.find('article') or soup.find('main') or soup.find('div', class_='content')
        if content_div:
            content = content_div.get_text(strip=True)
        else:
            content = soup.get_text(separator='\n', strip=True)
        
        return ParsedContent(
            title=title_text,
            content=content[:5000],  # Обрезаем длинные тексты
            url=url,
            doc_type=doc_type
        )
    
    async def process_and_store(self, content: ParsedContent):
        """Обрабатывает и сохраняет документ в векторную БД"""
        # Классифицируем
        classification = self.classifier.classify(content.content, content.title)
        role = self.classifier.classify_role(content.content)
        
        # Разбиваем на чанки и создаём embeddings
        chunks = chunk_text(content.content)
        embeddings = self.embeddings.encode(chunks)
        
        # Сохраняем каждый чанк
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            doc = Document(
                id=f"{hash(content.url)}_{i}",
                content=chunk,
                title=content.title,
                url=content.url,
                doc_type=content.doc_type,
                category=classification.category,
                role=role,
                version=1,
                timestamp=datetime.now().isoformat()
            )
            self.vdb.upsert_document(doc, emb)
        
        logger.info(f"Stored: {content.title[:50]}... -> {classification.category}")
    
    async def run_full_parse(self):
        """Запускает полный парсинг"""
        start = time.time()
        
        content = []
        content.extend(await self.parse_news())
        content.extend(await self.parse_documents())
        content.extend(await self.parse_events())
        
        for item in content:
            await self.process_and_store(item)
        
        elapsed = time.time() - start
        logger.info(f"Parsed {len(content)} items in {elapsed:.2f}s")
        return len(content)


async def main():
    async with FedLabSmartParser() as parser:
        count = await parser.run_full_parse()
        print(f"✅ Parsed {count} documents")


if __name__ == "__main__":
    asyncio.run(main())