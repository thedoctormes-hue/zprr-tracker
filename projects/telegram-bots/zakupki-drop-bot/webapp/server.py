"""
Zakupki Drop Bot WebApp API
FastAPI backend for government contract analysis
"""
import os
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Zakupki Drop Bot WebApp")

BASE_DIR = Path(__file__).parent.resolve()
STATIC_DIR = BASE_DIR / "static"

app.mount("/static", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

class AnalysisRequest(BaseModel):
    subject: str
    price: float
    region: str = ""

class ContractResponse(BaseModel):
    reg_number: str
    subject: str
    price: float
    profit_potential: float
    recommendation: str


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve main page"""
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return index_path.read_text()
    return "<h1>Zakupki Drop Bot WebApp</h1><p>Coming soon...</p>"


@app.post("/api/analyze")
async def analyze_contract(request: AnalysisRequest, req: Request = None):
    """Analyze government contract for drop-shipping potential"""
    try:
        # Импортируем анализатор
        import sys
        sys.path.insert(0, str(BASE_DIR.parent))
        from price_analyzer import PriceAnalyzer

        analyzer = PriceAnalyzer()
        result = analyzer.analyze_contract(request.subject, request.price, request.region)

        return {
            "subject": result.contract_subject,
            "gov_price": result.gov_price,
            "best_margin": result.best_margin,
            "recommendation": result.recommendation,
            "matches": [
                {
                    "source": m.source,
                    "market_price": m.market_price,
                    "profit_potential": m.profit_potential
                }
                for m in result.matches[:3]
            ]
        }
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/contracts/profitable")
async def get_profitable_contracts(limit: int = 20):
    """Get contracts sorted by profit potential"""
    try:
        import sys
        sys.path.insert(0, str(BASE_DIR.parent))
        from zakupki_database import get_profitable_contracts

        contracts = get_profitable_contracts(limit=limit)
        return [
            {
                "subject": c.subject,
                "price": c.price,
                "region": c.region
            }
            for c in contracts
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)