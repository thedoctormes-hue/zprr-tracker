#!/usr/bin/env python3
"""
zakupki.gov.ru Parser — Enterprise Safe Pattern (без токенов в коде)

Endpoints:
- GET /epz/order/extPrintForm/order/view/orderView.html?regNumber={id} — детали заказа
- GET /epz/order/search/orderSearch.html — поиск заказов
- GET /epz/contract/contractSearch.html — поиск контрактов

Usage:
    python zakupki_parser.py --mode contracts --region 77 --days 7
"""
import os
import sys
import json
import time
import asyncio
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv
import aiohttp
from pydantic import BaseModel

load_dotenv()

# Configuration from environment
BASE_URL = "https://zakupki.gov.ru"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}
REQUEST_DELAY = float(os.getenv("ZAKUPKI_DELAY", "2.0"))
MAX_RETRIES = 3


class Contract(BaseModel):
    """Модель контракта госзакупки"""
    reg_number: str
    subject: str
    price: float
    currency: str = "RUB"
    customer: str
    supplier: str
    region: str
    publish_date: datetime
    contract_url: str


class ZakupkiParser:
    """Парсер госзакупок zakupki.gov.ru"""

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.output_dir = Path(os.getenv("ZAKUPKI_OUTPUT", "./output/zakupki"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=HEADERS)
        return self

    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()

    async def fetch(self, url: str) -> Optional[str]:
        """Fetch with retry and delay"""
        for attempt in range(MAX_RETRIES):
            try:
                await asyncio.sleep(REQUEST_DELAY)
                async with self.session.get(url, timeout=30) as response:
                    if response.status == 200:
                        return await response.text()
                    elif response.status == 429:
                        await asyncio.sleep(10 * (attempt + 1))
            except Exception as e:
                print(f"⚠️ Attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(5 * (attempt + 1))
        return None

    async def parse_contracts(self, page: int = 1, region: str = "") -> List[Dict]:
        """Парсит контракты с сайта"""
        contracts = []
        url = f"{BASE_URL}/epz/contract/search/contractSearch.html"

        params = {
            "pageNumber": page,
            "recordsPerPage": 10,
        }
        if region:
            params["region"] = region

        html = await self.fetch(f"{url}?{('&'.join(f'{k}={v}' for k, v in params.items()))}")
        if not html:
            return contracts

        # TODO: реальный парсинг через BeautifulSoup
        # Для MVP сохраняем сырые HTML для последующей обработки
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"contracts_page{page}_{timestamp}.html"
        output_file.write_text(html)
        print(f"💾 Saved: {output_file}")

        return contracts

    async def parse_contract_details(self, reg_number: str) -> Optional[Contract]:
        """Парсит детали конкретного контракта"""
        url = f"{BASE_URL}/epz/contract/contractDetails.html?regNumber={reg_number}"
        html = await self.fetch(url)
        if not html:
            return None

        # TODO: извлечение данных через BeautifulSoup/BeautifulSoup4
        return None

    async def run(self, mode: str, **kwargs):
        """Главный entry point"""
        if mode == "contracts":
            page = kwargs.get("page", 1)
            region = kwargs.get("region", "")
            contracts = await self.parse_contracts(page=page, region=region)
            print(f"📊 Found {len(contracts)} contracts")

        elif mode == "html":
            # Скачивание HTML для последующего парсинга
            pages = kwargs.get("pages", 5)
            for p in range(1, pages + 1):
                await self.parse_contracts(page=p)


def main():
    parser = argparse.ArgumentParser(description="zakupki.gov.ru Parser")
    parser.add_argument("--mode", choices=["contracts", "html"], default="contracts")
    parser.add_argument("--page", type=int, default=1)
    parser.add_argument("--region", type=str, default="", help="Region code (e.g. 77 for Moscow)")
    parser.add_argument("--pages", type=int, default=5, help="Number of pages for HTML mode")

    args = parser.parse_args()

    async def run_async():
        async with ZakupkiParser() as zp:
            await zp.run(args.mode, page=args.page, region=args.region, pages=args.pages)

    asyncio.run(run_async())


if __name__ == "__main__":
    main()