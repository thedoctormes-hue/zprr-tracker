"""Notion webhook integration for stenographer bot."""
import os
import logging
import httpx
from typing import Optional

logger = logging.getLogger(__name__)

NOTION_WEBHOOK_URL = os.getenv("NOTION_WEBHOOK_URL", "")

async def send_to_notion(summary_text: str, clean_text: str, timestamp: str) -> Optional[bool]:
    """Send protocol summary to Notion via webhook."""
    if not NOTION_WEBHOOK_URL:
        logger.debug("NOTION_WEBHOOK_URL not configured, skipping webhook")
        return None

    payload = {
        "timestamp": timestamp,
        "summary": summary_text[:1000],  # Limit for webhook
        "source": "stenographerobot"
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(NOTION_WEBHOOK_URL, json=payload)
            r.raise_for_status()
            logger.info(f"✅ Webhook sent to Notion: {r.status_code}")
            return True
    except Exception as e:
        logger.warning(f"⚠️ Webhook failed: {e}")
        return False