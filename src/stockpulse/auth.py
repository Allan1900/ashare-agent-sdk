"""API Key authentication + usage tracking."""

import os
import sqlite3
import secrets
from datetime import date
from pathlib import Path
from fastapi import Request, HTTPException


def _db_path() -> str:
    env = os.environ.get("STOCKPULSE_KEYS_DB")
    if env:
        return env
    return str(Path.home() / ".stockpulse" / "keys.db")


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
        return {"key": "", "tier": "anonymous", "remaining": 0}

    valid, tier, remaining = verify_key(key)
    if not valid:
        raise HTTPException(status_code=401, detail="Invalid API key")
    if remaining <= 0:
        raise HTTPException(
            status_code=429,
            detail=f"Daily limit reached ({tier} tier)"
        )

    record_usage(key)
    return {"key": key, "tier": tier, "remaining": remaining - 1}


def list_keys() -> list:
    """List all API keys (for admin)."""
    conn = _get_conn()
    try:
        rows = conn.execute(
            "SELECT key_id, tier, daily_limit, used_today, last_used_date, "
            "created_at, label FROM api_keys ORDER BY created_at DESC"
        ).fetchall()
        return [
            {
                "key_id": r[0], "tier": r[1], "daily_limit": r[2],
                "used_today": r[3], "last_used_date": r[4],
                "created_at": r[5], "label": r[6],
            }
            for r in rows
        ]
    finally:
        conn.close()
