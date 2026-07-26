"""Utility functions — stock code extraction, query type detection, formatting."""

import re


def extract_code(text: str) -> str | None:
    """Extract stock code (e.g. 000001.SZ, 600000.SH) from natural language."""
    m = re.search(r"\b(\d{6})\.(SZ|SH)\b", text, re.IGNORECASE)
    if m:
        return m.group(0).upper()

    m = re.search(r"\b(\d{6})\b", text)
    if m:
        code = m.group(1)
        suffix = "SZ" if code[0] in ("0", "2", "3") else "SH"
        return f"{code}.{suffix}"

    return None


def detect_query_type(text: str) -> str:
    """Detect financial query type from natural language."""
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

    return "daily"


def extract_days(text: str) -> int:
    """Extract number of days from text, default 20."""
    m = re.search(r"(\d+)\s*[个天]", text)
    if m:
        return min(int(m.group(1)), 120)
    return 20


def extract_trade_date(text: str) -> str | None:
    """Extract trade date YYYYMMDD from text."""
    m = re.search(r"\b(20\d{2}[01]\d[0-3]\d)\b", text)
    return m.group(1) if m else None


def fmt_df(df, max_rows: int = 20) -> str:
    """Format DataFrame as readable text for LLM consumption."""
    if df is None or df.empty:
        return "无数据"

    result = df.head(max_rows).to_string(index=False)
    total = len(df)
    if total > max_rows:
        result += f"\n... 共 {total} 行，仅显示前 {max_rows} 行"
    return result
