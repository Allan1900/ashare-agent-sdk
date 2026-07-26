"""StockPulse — 让 AI Agent 做 A 股分析。北向资金/龙虎榜/宏观/行情/财务，OpenAI 兼容 API + MCP + CLI。"""

from .config import Settings, get_settings
from .engine import (
    query, query_daily, query_daily_basic, query_moneyflow,
    query_financial, query_industry_performance,
    query_hsgt, query_hsgt_top, query_top_list, query_macro,
    search_stocks, screen_stocks, name_to_code,
)

__version__ = "0.1.0"


class StockPulse:
    """StockPulse client — high-level interface for AI agents."""

    def __init__(self, api_key: str = ""):
        self.api_key = api_key

    def query(self, text: str) -> str:
        """Query A-share data using natural language."""
        from .utils import detect_query_type, extract_code, extract_days, fmt_df
        from .server import _resolve_code

        code = _resolve_code(text)
        qtype = detect_query_type(text)
        days = extract_days(text)

        if qtype == "daily" and code:
            return fmt_df(query_daily(code, days))
        elif qtype == "moneyflow" and code:
            return fmt_df(query_moneyflow(code, days))
        elif qtype == "financial" and code:
            return fmt_df(query_financial(code))
        elif qtype == "industry":
            return fmt_df(query_industry_performance())
        elif qtype == "hsgt":
            return fmt_df(query_hsgt(days))
        elif qtype == "top_list":
            from .utils import extract_trade_date
            td = extract_trade_date(text)
            if td:
                return fmt_df(query_top_list(td))
        elif qtype == "macro":
            for kw in ["cpi", "ppi", "pmi", "gdp", "m2", "shibor", "lpr"]:
                if kw in text.lower():
                    return fmt_df(query_macro(kw))
        elif qtype == "screen":
            from .utils import fmt_df
            import re
            pe_max = None; pb_max = None; roe_min = None
            m = re.search(r"pe<\s*(\d+)", text.lower())
            if m: pe_max = float(m.group(1))
            m = re.search(r"pb<\s*(\d+)", text.lower())
            if m: pb_max = float(m.group(1))
            m = re.search(r"roe>\s*(\d+)", text.lower())
            if m: roe_min = float(m.group(1))
            return fmt_df(screen_stocks(pe_max=pe_max, pb_max=pb_max, roe_min=roe_min))
        elif qtype == "search":
            for kw in ["搜索", "查找", "找股票"]:
                if kw in text:
                    keyword = text.split(kw)[-1].strip()
                    if keyword:
                        return fmt_df(search_stocks(keyword))

        return "无法识别的查询。试试：查行情、查资金、查北向、查财务、查行业、筛选"