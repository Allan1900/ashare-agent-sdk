"""StockPulse — AI Agent-native A-share financial analysis engine."""
from .config import Settings, get_settings
from .engine import (
    query, query_daily, query_daily_basic, query_moneyflow,
    query_financial, query_industry_performance,
    query_hsgt, query_hsgt_top, query_top_list, query_macro,
    search_stocks, screen_stocks, name_to_code,
)
from . import indicators

__version__ = "0.2.0"


class StockPulse:
    """High-level client for AI agents."""

    def __init__(self, api_key: str = ""):
        self.api_key = api_key

    def query(self, text: str) -> str:
        from .utils import detect_query_type, extract_code, extract_days, fmt_df
        from .server import _resolve_code

        code = _resolve_code(text)
        qtype = detect_query_type(text)
        days = extract_days(text)

        # 技术指标检测
        if any(kw in text.lower() for kw in ["macd", "rsi", "kdj", "金叉", "死叉", "超买", "超卖"]):
            if not code:
                return "请提供股票代码或名称"
            ind = indicators.get_indicators(code, days * 2)
            if isinstance(ind, dict) and "error" in ind:
                return ind["error"]
            parts = []
            for name in ["ma", "macd", "rsi", "kdj", "boll"]:
                if name in ind and ind[name] is not None and not ind[name].empty:
                    parts.append(f"── {name.upper()} ──\n" + fmt_df(ind[name].tail(10)))
            return "\n\n".join(parts) if parts else "无数据"

        if qtype == "daily" and code:
            return fmt_df(query_daily(code, days))
        elif qtype == "moneyflow" and code:
            return fmt_df(query_moneyflow(code, days))
        ...