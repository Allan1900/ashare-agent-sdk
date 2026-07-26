"""Technical indicators for A-share stock analysis.

Calculates MA, MACD, RSI, KDJ, BOLL from daily OHLCV data.
"""

import pandas as pd
import numpy as np
from .engine import query_daily


# ── Moving Average ─────────────────────────────────

def calc_ma(df: pd.DataFrame, periods: list[int] | None = None) -> pd.DataFrame:
    """Calculate Simple Moving Averages for given periods."""
    if df is None or df.empty:
        return df
    periods = periods or [5, 10, 20, 60]
    result = df[["trade_date", "close"]].copy()
    for p in periods:
        result[f"ma{p}"] = df["close"].rolling(window=p).mean()
    return result


# ── MACD ───────────────────────────────────────────

def calc_macd(df: pd.DataFrame,
              fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """Calculate MACD: DIF, DEA, MACD histogram."""
    if df is None or df.empty:
        return df
    close = df["close"]
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    dif = ema_fast - ema_slow
    dea = dif.ewm(span=signal, adjust=False).mean()
    macd_hist = 2 * (dif - dea)

    return pd.DataFrame({
        "trade_date": df["trade_date"],
        "dif": dif,
        "dea": dea,
        "macd_hist": macd_hist,
    })


# ── RSI ───────────────────────────────────────────

def calc_rsi(df: pd.DataFrame, periods: list[int] | None = None) -> pd.DataFrame:
    """Calculate RSI for given periods."""
    if df is None or df.empty:
        return df
    periods = periods or [6, 12, 24]
    close = df["close"]
    delta = close.diff()

    result = pd.DataFrame({"trade_date": df["trade_date"]})
    for p in periods:
        gain = delta.where(delta > 0, 0).rolling(window=p).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=p).mean()
        rs = gain / loss.replace(0, np.nan)
        result[f"rsi{p}"] = 100 - (100 / (1 + rs))
    return result


# ── KDJ ────────────────────────────────────────────

def calc_kdj(df: pd.DataFrame,
             n: int = 9, m1: int = 3, m2: int = 3) -> pd.DataFrame:
    """Calculate KDJ (Stochastic Oscillator)."""
    if df is None or df.empty:
        return df

    low_n = df["low"].rolling(window=n).min()
    high_n = df["high"].rolling(window=n).max()
    rsv = ((df["close"] - low_n) / (high_n - low_n).replace(0, np.nan)) * 100

    k = rsv.ewm(com=m1 - 1, adjust=False).mean()
    d = k.ewm(com=m2 - 1, adjust=False).mean()
    j = 3 * k - 2 * d

    return pd.DataFrame({
        "trade_date": df["trade_date"],
        "k": k, "d": d, "j": j,
    })


# ── BOLL (Bollinger Bands) ─────────────────────────

def calc_boll(df: pd.DataFrame,
              period: int = 20, std_mult: float = 2.0) -> pd.DataFrame:
    """Calculate Bollinger Bands."""
    if df is None or df.empty:
        return df

    middle = df["close"].rolling(window=period).mean()
    std = df["close"].rolling(window=period).std()
    upper = middle + std_mult * std
    lower = middle - std_mult * std

    return pd.DataFrame({
        "trade_date": df["trade_date"],
        "boll_upper": upper,
        "boll_middle": middle,
        "boll_lower": lower,
    })


# ── All-in-one ──────────────────────────────────────

def calc_all(df: pd.DataFrame) -> dict:
    """Calculate all indicators, return dict of DataFrames."""
    return {
        "ma": calc_ma(df),
        "macd": calc_macd(df),
        "rsi": calc_rsi(df),
        "kdj": calc_kdj(df),
        "boll": calc_boll(df),
    }


# ── Query helpers (from PG) ────────────────────────

def get_indicators(code: str, days: int = 120) -> dict:
    """Fetch daily data from PG and calculate all indicators."""
    df = query_daily(code, days)
    if df is None or df.empty:
        return {"error": f"无数据: {code}"}
    df = df.sort_values("trade_date")
    return calc_all(df)


# ── Signal helpers ──────────────────────────────────

def check_golden_cross(code: str) -> str | None:
    """Check if MA5 just crossed above MA10 (golden cross)."""
    df = query_daily(code, 30)
    if df is None or df.empty:
        return None
    df = df.sort_values("trade_date")
    ma5 = df["close"].rolling(5).mean()
    ma10 = df["close"].rolling(10).mean()
    if len(ma5) < 2:
        return None
    prev = ma5.iloc[-2] <= ma10.iloc[-2]
    curr = ma5.iloc[-1] > ma10.iloc[-1]
    if prev and curr:
        return f"MA5金叉MA10 ({df['trade_date'].iloc[-1]})"
    return None


def check_death_cross(code: str) -> str | None:
    """Check if MA5 just crossed below MA10 (death cross)."""
    df = query_daily(code, 30)
    if df is None or df.empty:
        return None
    df = df.sort_values("trade_date")
    ma5 = df["close"].rolling(5).mean()
    ma10 = df["close"].rolling(10).mean()
    if len(ma5) < 2:
        return None
    prev = ma5.iloc[-2] >= ma10.iloc[-2]
    curr = ma5.iloc[-1] < ma10.iloc[-1]
    if prev and curr:
        return f"MA5死叉MA10 ({df['trade_date'].iloc[-1]})"
    return None


def check_rsi_signal(code: str) -> str | None:
    """Check RSI overbought/oversold signals."""
    rsi = calc_rsi(query_daily(code, 30))
    if rsi is None or rsi.empty:
        return None
    val = rsi["rsi12"].iloc[-1] if "rsi12" in rsi.columns else None
    if val is None or pd.isna(val):
        return None
    date = rsi["trade_date"].iloc[-1]
    if val > 80:
        return f"RSI超买 ({val:.1f}, {date})"
    if val < 20:
        return f"RSI超卖 ({val:.1f}, {date})"
    return None