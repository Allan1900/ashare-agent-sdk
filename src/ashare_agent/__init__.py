"""ashare-agent — OpenAI-compatible API + MCP + CLI for A-share data."""

from .config import Settings, get_settings
from .engine import (
    query, query_daily, query_daily_basic, query_moneyflow,
    query_financial, query_industry_performance,
    query_hsgt, query_hsgt_top, query_top_list, query_macro,
    search_stocks, screen_stocks,
)

__version__ = "0.1.0"
