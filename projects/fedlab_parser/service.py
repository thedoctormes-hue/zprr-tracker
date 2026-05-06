#!/usr/bin/env python3
"""
FedLab Semantic Parser — Service Runner
"""
import asyncio
import logging
from fedlab_smart_parser import FedLabSmartParser

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_scheduler():
    """Планировщик для периодического парсинга"""
    parser = FedLabSmartParser()
    
    while True:
        try:
            logger.info("Starting scheduled parse...")
            count = await parser.run_full_parse()
            logger.info(f"Parsed {count} documents")
        except Exception as e:
            logger.error(f"Parse error: {e}")
        
        # Ждём 1 час перед следующим запуском
        await asyncio.sleep(3600)


def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "schedule":
        asyncio.run(run_scheduler())
    elif len(sys.argv) > 1 and sys.argv[1] == "once":
        asyncio.run(run_once())
    else:
        print("Usage: python service.py [schedule|once]")
        print("  schedule - Run parser periodically")
        print("  once     - Run parser once")
        sys.exit(1)


async def run_once():
    """Run parser once"""
    async with FedLabSmartParser() as parser:
        count = await parser.run_full_parse()
        print(f"✅ Parsed {count} documents")


if __name__ == "__main__":
    main()