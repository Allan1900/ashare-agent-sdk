#!/usr/bin/env python3
"""Generate all source files for ashare-agent-sdk.
Run with: python3 _generate.py
"""
import os, shutil

BASE = os.path.dirname(os.path.abspath(__file__))

def write(path, content):
    full = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w') as f:
        f.write(content)
    print(f"  ✓ {path}")

# ── config.py ──────────────────────────────────────
CONFIG_PY = '''"""Configuration — YAML + env vars"""

import os
import yaml
from pathlib import Path
from typing import Optional


CONFIG_PATHS = [
    Path("config.yaml"),
    Path.home() / ".ashare-agent" / "config.yaml",
]


class Settings:
    """Settings loaded from YAML then overridden by env vars."""

    def __init__(self):
        self._data = {
            "host": "localhost",
            "port": 8900,
            "log_level": "info",
            "pg_uri": None,  # resolved lazily
        }
        self._loaded = None
        self._load_file()
        self._apply_env()
        # resolve pg_uri after all overrides
        if self._data["pg_uri"] is None:
            self._data["pg_uri"] = self._resolve_pg_uri()

    @staticmethod
    def _resolve_pg_uri() -> str:
        uri = os.environ.get("ASHARE_AGENT_PG_URI")
        if uri:
            return uri
        user = os.environ.get("USER", "zrall")
        host = os.environ.get("PG_HOST", "localhost")
        return f"postgresql://{user}@{host}/ashare?options=-c%20search_path=ashare,public"

    def _load_file(self):
        for p in CONFIG_PATHS:
            if p.exists():
                with open(p) as f:
                    cfg = yaml.safe_load(f) or {}
                self._loaded = p
                for k in ("pg_uri", "host", "port", "log_level"):
                    if k in cfg:
                        self._data[k] = str(cfg[k]) if k in ("host", "pg_uri", "log_level") and k in cfg else cfg[k]
                break

    def _apply_env(self):
        mapping = {
            "pg_uri": "ASHARE_AGENT_PG_URI",
            "host": "ASHARE_AGENT_HOST",
            "port": "ASHARE_AGENT_PORT",
            "log_level": "ASHARE_AGENT_LOG_LEVEL",
        }
        for key, env_name in mapping.items():
            val = os.environ.get(env_name)
            if val is not None:
                self._data[key] = val

    @property
    def pg_uri(self) -> str:
        return self._data.get("pg_uri") or self._resolve_pg_uri()

    @property
    def host(self) -> str:
        return self._data.get("host", "localhost")

    @property
    def port(self) -> int:
        return int(self._data.get("port", 8900))

    @property
    def log_level(self) -> str:
        return self._data.get("log_level", "info")

    def loaded_from(self) -> Optional[str]:
        return str(self._loaded) if self._loaded else None


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
'''

# ── engine.py ──────────────────────────────────────
ENGINE_PY = '''"""PG query engine — wraps ashare database queries."""

import pandas as pd
from sqlalchemy import create_engine, text
from .config import get_settings


_engine = None


def get_engine():
    global _engine
    if _engine is None:
        uri = get_settings().pg_uri
        _engine = create_engine(uri)
    return _engine


def query(sql: str, params: list = None) -> pd.DataFrame:
    """Execute SQL query, return DataFrame."""
    conn = get_engine().raw_connection()
    try:
        return pd.read_sql(sql, conn, params=params or [])
    finally:
        conn.close()


def query_daily(code: str, days: int = 20) -> pd.DataFrame:
    """Query daily quotes for a stock."""
    return query(
        "SELECT trade_date, open, high, low, close, vol, amount "
        "FROM daily WHERE ts_code=? ORDER BY trade_date DESC LIMIT ?",
        [code, days]
    )


def query_daily_basic(code: str, days: int = 20) -> pd.DataFrame:
    """Query daily basic indicators (PE, PB, etc.)."""
    return query(
        "SELECT trade_date, pe_ttm, pb, ps_ttm, total_mv, float_mv, dv_ratio, turnover_rate "
        "FROM daily_basic WHERE ts_code=? ORDER BY trade_date DESC LIMIT ?",
        [code, days]
    )


def query_moneyflow(code: str, days: int = 20) -> pd.DataFrame:
    """Query money flow for a stock."""
    return query(
        "SELECT trade_date, buy_sm_vol, sell_sm_vol, buy_md_vol, sell_md_vol, "
        "buy_lg_vol, sell_lg_vol, buy_elg_vol, sell_elg_vol, "
        "net_mf_vol, net_mf_amount "
        "FROM moneyflow WHERE ts_code=? ORDER BY trade_date DESC LIMIT ?",
        [code, days]
    )


def query_financial(code: str, limit: int = 8) -> pd.DataFrame:
    """Query financial indicators."""
    return query(
        "SELECT end_date, revenue, net_profit, roe, roe_diluted, "
        "eps, total_assets, total_liab, total_equity "
        "FROM fina_indicator WHERE ts_code=? ORDER BY end_date DESC LIMIT ?",
        [code, limit]
    )


def query_industry_performance(trade_date: str = None, top_n: int = 15) -> pd.DataFrame:
    """Query industry ranking for a given date."""
    if trade_date:
        return query(
            "SELECT industry, stock_count, avg_change FROM industry_performance "
            "WHERE trade_date=? ORDER BY avg_change DESC LIMIT ?",
            [trade_date, top_n]
        )
    return query(
        "SELECT industry, stock_count, avg_change FROM industry_performance "
        "ORDER BY trade_date DESC, avg_change DESC LIMIT ?",
        [top_n]
    )


def query_hsgt(days: int = 10) -> pd.DataFrame:
    """Query north-bound money flow summary."""
    return query(
        "SELECT trade_date, north_money_s, south_money_s, north_money, south_money "
        "FROM hsgt_moneyflow ORDER BY trade_date DESC LIMIT ?",
        [days]
    )


def query_hsgt_top(days: int = 10) -> pd.DataFrame:
    """Query top 10 north-bound stocks."""
    return query(
        "SELECT trade_date, ts_code, name, close, change_pct, amount "
        "FROM hsgt_top10 ORDER BY trade_date DESC, amount DESC LIMIT ?",
        [days * 10]
    )


def query_top_list(trade_date: str) -> pd.DataFrame:
    """Query dragon and tiger list for a date."""
    return query(
        "SELECT ts_code, name, close, change_pct, amount, net_amount, buy_amount, sell_amount "
        "FROM top_list WHERE trade_date=? ORDER BY net_amount DESC",
        [trade_date]
    )


def query_macro(indicator: str, limit: int = 120) -> pd.DataFrame:
    """Query macro-economic data."""
    table_map = {
        "cpi": "cn_cpi", "ppi": "cn_ppi", "pmi": "cn_pmi",
        "gdp": "cn_gdp", "m2": "cn_m2", "shibor": "shibor",
        "lpr": "shibor_lpr", "us_treasury": "us_treasury_yield",
    }
    table = table_map.get(indicator)
    if not table:
        return pd.DataFrame()
    return query(
        f"SELECT * FROM {table} ORDER BY date DESC LIMIT ?",
        [limit]
    )


def search_stocks(keyword: str, limit: int = 20) -> pd.DataFrame:
    """Search stocks by code or name."""
    return query(
        "SELECT ts_code, symbol, name, industry, area, market, list_date "
        "FROM stock_basic WHERE ts_code ILIKE ? OR name ILIKE ? LIMIT ?",
        [f"%{keyword}%", f"%{keyword}%", limit]
    )


def screen_stocks(pe_max: float = None, pb_max: float = None,
                  roe_min: float = None, industry: str = None,
                  limit: int = 50) -> pd.DataFrame:
    """Screen stocks by criteria."""
    conditions = []
    params = []
    if pe_max is not None:
        conditions.append("pe_ttm <= ?")
        params.append(pe_max)
    if pb_max is not None:
        conditions.append("pb <= ?")
        params.append(pb_max)
    if roe_min is not None:
        conditions.append("roe >= ?")
        params.append(roe_min)
    if industry:
        conditions.append("b.industry = ?")
        params.append(industry)

    where = " AND ".join(conditions) if conditions else "1=1"
    sql = f"""
        SELECT b.ts_code, b.name, b.industry, b.area,
               d.pe_ttm, d.pb, d.total_mv, d.turnover_rate
        FROM stock_basic b
        JOIN LATERAL (
            SELECT pe_ttm, pb, total_mv, turnover_rate
            FROM daily_basic WHERE ts_code = b.ts_code
            ORDER BY trade_date DESC LIMIT 1
        ) d ON true
        WHERE {where}
        ORDER BY d.total_mv DESC NULLS LAST
        LIMIT ?
    """
    return query(sql, params + [limit])
'''

# ── auth.py ─────────────────────────────────────────
AUTH_PY = '''"""API Key authentication + usage tracking."""

import os
import sqlite3
import hashlib
import secrets
from datetime import date
from pathlib import Path
from functools import wraps
from fastapi import Request, HTTPException


def _db_path() -> str:
    env = os.environ.get("ASHARE_AGENT_KEYS_DB")
    if env:
        return env
    return str(Path.home() / ".ashare-agent" / "keys.db")


def _get_conn():
    path = _db_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS api_keys (
            key_id TEXT PRIMARY KEY,
            tier TEXT NOT NULL DEFAULT 'free',
            daily_limit INTEGER NOT NULL DEFAULT 100,
            used_today INTEGER NOT NULL DEFAULT 0,
            last_used_date TEXT,
            created_at TEXT NOT NULL,
            label TEXT
        )
    """)
    conn.commit()
    return conn


def generate_key(tier: str = "free", daily_limit: int = 100,
                 label: str = "") -> str:
    """Generate a new API key."""
    key_id = "ashare_" + secrets.token_hex(16)
    conn = _get_conn()
    try:
        conn.execute(
            "INSERT INTO api_keys (key_id, tier, daily_limit, created_at, label) "
            "VALUES (?, ?, ?, date('now'), ?)",
            (key_id, tier, daily_limit, label)
        )
        conn.commit()
    finally:
        conn.close()
    return key_id


def verify_key(key_id: str) -> tuple:
    """Verify a key, return (valid: bool, tier: str, remaining: int)."""
    conn = _get_conn()
    try:
        row = conn.execute(
            "SELECT tier, daily_limit, used_today, last_used_date "
            "FROM api_keys WHERE key_id=?", (key_id,)
        ).fetchone()
        if not row:
            return False, "", 0

        tier, daily_limit, used_today, last_used = row
        today = date.today().isoformat()

        # reset counter if new day
        if last_used != today:
            used_today = 0
            conn.execute(
                "UPDATE api_keys SET used_today=0, last_used_date=? WHERE key_id=?",
                (today, key_id)
            )
            conn.commit()

        remaining = daily_limit - used_today
        return True, tier, remaining
    finally:
        conn.close()


def record_usage(key_id: str, count: int = 1):
    """Record API usage for a key."""
    conn = _get_conn()
    try:
        today = date.today().isoformat()
        conn.execute(
            "UPDATE api_keys SET used_today = used_today + ?, "
            "last_used_date = ? WHERE key_id = ?",
            (count, today, key_id)
        )
        conn.commit()
    finally:
        conn.close()


async def require_auth(request: Request):
    """FastAPI dependency — extract and verify API key."""
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        key = auth[7:]
    else:
        key = request.headers.get("x-api-key", "")

    if not key:
        return None  # will be allowed but tracked as anonymous

    valid, tier, remaining = verify_key(key)
    if not valid:
        raise HTTPException(status_code=401, detail="Invalid API key")
    if remaining <= 0:
        raise HTTPException(status_code=429,
                            detail=f"Daily limit reached ({tier} tier)")

    record_usage(key)
    return {"key": key, "tier": tier, "remaining": remaining - 1}
'''

# ── __init__.py ─────────────────────────────────────
INIT_PY = '''"""ashare-agent — OpenAI-compatible API + MCP + CLI for A-share data."""

from .config import Settings, get_settings
from .engine import (
    query, query_daily, query_daily_basic, query_moneyflow,
    query_financial, query_industry_performance,
    query_hsgt, query_hsgt_top, query_top_list, query_macro,
    search_stocks, screen_stocks,
)

__version__ = "0.1.0"
'''

# ── utils.py ────────────────────────────────────────
UTILS_PY = '''"""Utility functions."""

import re


def extract_stock_code(text: str) -> str | None:
    """Extract stock code from natural language text."""
    # Try explicit code: 000001.SZ, 600000.SH, 000001, 600000
    m = re.search(r'\\b(\\d{6})\\.(SZ|SH)\\b', text, re.I)
    if m:
        return m.group(0).upper()

    m = re.search(r'\\b(\\d{6})\\b', text)
    if m:
        code = m.group(1)
        prefix = code[0]
        suffix = "SZ" if prefix in ("0", "2", "3") else "SH"
        return f"{code}.{suffix}"

    return None


def format_dataframe(df, max_rows: int = 20) -> str:
    """Format DataFrame as readable text for LLM consumption."""
    if df is None or df.empty:
        return "无数据"

    result = df.head(max_rows).to_string(index=False)
    total = len(df)
    if total > max_rows:
        result += f"\\n... 共 {total} 行，仅显示前 {max_rows} 行"
    return result


def detect_query_type(text: str) -> str:
    """Detect the type of financial query from natural language."""
    t = text.lower()

    if any(kw in t for kw in ("北向", "hsgt", "沪深股通")):
        return "hsgt"
    if any(kw in t for kw in ("龙虎榜", "上榜")):
        return "top_list"
    if any(kw in t for kw in ("资金流向", "主力", "净流入", "净流出", "资金")):
        return "moneyflow"
    if any(kw in t for kw in ("财务", "营收", "利润", "roe", "eps", "净利润", "收入")):
        return "financial"
    if any(kw in t for kw in ("行业", "板块", "涨跌排行")):
        return "industry"
    if any(kw in t for kw in ("cpi", "ppi", "pmi", "gdp", "m2", "shibor", "lpr", "宏观")):
        return "macro"
    if any(kw in t for kw in ("筛选", "pe<", "pb<", "roe>", "选股")):
        return "screen"
    if any(kw in t for kw in ("搜索", "查找", "找股票")):
        return "search"

    return "daily"  # default to daily quote


def extract_days(text: str) -> int:
    """Extract number of days from text."""
    m = re.search(r'(\\d+)\\s*[个天]', text)
    if m:
        n = int(m.group(1))
        return min(n, 120)  # cap at 120
    return 20  # default


def extract_trade_date(text: str) -> str | None:
    """Extract trade date YYYYMMDD from text."""
    m = re.search(r'\\b(20\\d{2}[01]\\d[0-3]\\d)\\b', text)
    return m.group(1) if m else None
'''

# ── Write all files ─────────────────────────────────
print("Generating ashare-agent-sdk source files...")
write("src/ashare_agent/__init__.py", INIT_PY)
write("src/ashare_agent/config.py", CONFIG_PY)
write("src/ashare_agent/engine.py", ENGINE_PY)
write("src/ashare_agent/auth.py", AUTH_PY)
write("src/ashare_agent/utils.py", UTILS_PY)
print("\\nDone — 5 files generated.")