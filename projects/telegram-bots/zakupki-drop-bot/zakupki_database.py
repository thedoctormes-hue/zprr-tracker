#!/usr/bin/env python3
"""
Zakupki Database — PostgreSQL with SQLite fallback для контрактов госзакупок
"""
import os
from typing import Optional, List
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "")

# Fallback to SQLite if PostgreSQL not configured
USE_SQLITE = not DATABASE_URL

if not USE_SQLITE:
    import psycopg2
    from psycopg2.extras import RealDictCursor

    @contextmanager
    def get_db():
        """Get PostgreSQL connection."""
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        try:
            yield conn
        finally:
            conn.close()
else:
    import sqlite3

    @contextmanager
    def get_db():
        """Get SQLite connection."""
        db_path = Path(__file__).parent / "zakupki.db"
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()


@dataclass
class Contract:
    """Контракт госзакупки"""
    reg_number: str
    subject: str
    price: float
    currency: str = "RUB"
    customer: str = ""
    supplier: str = ""
    region: str = ""
    publish_date: Optional[datetime] = None
    contract_url: str = ""


def init_db():
    """Initialize database schema for contracts."""
    with get_db() as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS contracts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reg_number TEXT UNIQUE NOT NULL,
                subject TEXT,
                price REAL,
                currency TEXT DEFAULT 'RUB',
                customer TEXT,
                supplier TEXT,
                region TEXT,
                publish_date TIMESTAMP,
                contract_url TEXT,
                parsed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                profit_margin REAL DEFAULT 0,
                drop_shipping_score REAL DEFAULT 0
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS price_comparisons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contract_id INTEGER,
                market_price REAL,
                supplier_name TEXT,
                url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (contract_id) REFERENCES contracts(id)
            )
        ''')
        c.execute('''
            CREATE INDEX IF NOT EXISTS idx_contracts_region ON contracts(region)
        ''')
        c.execute('''
            CREATE INDEX IF NOT EXISTS idx_contracts_price ON contracts(price)
        ''')
        c.execute('''
            CREATE INDEX IF NOT EXISTS idx_contracts_date ON contracts(publish_date)
        ''')
        conn.commit()


def save_contract(contract: Contract) -> int:
    """Save contract to database. Returns ID."""
    with get_db() as conn:
        c = conn.cursor()
        if USE_SQLITE:
            c.execute('''
                INSERT OR REPLACE INTO contracts
                (reg_number, subject, price, currency, customer, supplier, region, publish_date, contract_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                contract.reg_number, contract.subject, contract.price, contract.currency,
                contract.customer, contract.supplier, contract.region, contract.publish_date,
                contract.contract_url
            ))
        else:
            c.execute('''
                INSERT INTO contracts
                (reg_number, subject, price, currency, customer, supplier, region, publish_date, contract_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (reg_number) DO UPDATE SET
                    subject = EXCLUDED.subject,
                    price = EXCLUDED.price,
                    customer = EXCLUDED.customer,
                    supplier = EXCLUDED.supplier
            ''', (
                contract.reg_number, contract.subject, contract.price, contract.currency,
                contract.customer, contract.supplier, contract.region, contract.publish_date,
                contract.contract_url
            ))
        conn.commit()
        
        if USE_SQLITE:
            c.execute("SELECT last_insert_rowid()")
        else:
            c.execute("SELECT currval(pg_get_serial_sequence('contracts', 'id'))")
        return c.fetchone()[0]


def get_contracts_by_region(region: str, limit: int = 100) -> List[Contract]:
    """Get contracts by region."""
    with get_db() as conn:
        c = conn.cursor()
        if USE_SQLITE:
            c.execute('''
                SELECT * FROM contracts WHERE region = ? ORDER BY publish_date DESC LIMIT ?
            ''', (region, limit))
        else:
            c.execute('''
                SELECT * FROM contracts WHERE region = %s ORDER BY publish_date DESC LIMIT %s
            ''', (region, limit))
        
        return [Contract(**dict(row)) for row in c.fetchall()]


def get_profitable_contracts(min_margin: float = 0.25, limit: int = 50) -> List[Contract]:
    """Get contracts with high drop-shipping potential."""
    with get_db() as conn:
        c = conn.cursor()
        # For now, return by price - actual margin calculated elsewhere
        if USE_SQLITE:
            c.execute('''
                SELECT * FROM contracts 
                WHERE price > 10000 
                ORDER BY publish_date DESC 
                LIMIT ?
            ''', (limit,))
        else:
            c.execute('''
                SELECT * FROM contracts 
                WHERE price > 10000 
                ORDER BY publish_date DESC 
                LIMIT %s
            ''', (limit,))
        
        return [Contract(**dict(row)) for row in c.fetchall()]


# Initialize on import
init_db()