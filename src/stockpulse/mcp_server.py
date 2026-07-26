"""MCP protocol server — exposes finance tools via Model Context Protocol.

Allows Claude Code, Cursor, and any MCP-compatible agent to call A-share data
functions directly.
"""

import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .auth import require_auth
from .engine import (
    query_daily, query_daily_basic, query_moneyflow,
    query_financial, query_industry_performance,
    query_hsgt, query_hsgt_top, query_top_list, query_macro,
    search_stocks, screen_stocks,
)
from .utils import fmt_df

mcp_app = FastAPI(title="stockpulse MCP Server", version="0.1.0")

mcp_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── MCP protocol endpoints ─────────────────────────

# Tool definitions
TOOLS = [
    {
        "name": "query_daily",
        "description": "查询股票日线行情（开高低收量额）",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "股票代码 000001.SZ"},
                "days": {"type": "integer", "description": "最近N个交易日，默认20"},
            },
        },
    },
    {
        "name": "query_moneyflow",
        "description": "查询个股资金流向（主力/散户净流入）",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "股票代码"},
                "days": {"type": "integer", "description": "最近N天"},
            },
        },
    },
    {
        "name": "query_financial",
        "description": "查询财务数据（营收/利润/ROE/EPS）",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "股票代码"},
            },
        },
    },
    {
        "name": "query_industry",
        "description": "查询行业涨跌排行",
        "inputSchema": {
            "type": "object",
            "properties": {
                "top_n": {"type": "integer", "description": "前N个行业"},
            },
        },
    },
    {
        "name": "query_hsgt",
        "description": "查询北向资金（沪深股通）每日汇总",
        "inputSchema": {
            "type": "object",
            "properties": {
                "days": {"type": "integer", "description": "最近N天"},
            },
        },
    },
    {
        "name": "query_hsgt_top",
        "description": "查询北向资金十大活跃股",
        "inputSchema": {
            "type": "object",
            "properties": {
                "days": {"type": "integer", "description": "最近N天"},
            },
        },
    },
    {
        "name": "query_top_list",
        "description": "查询龙虎榜数据",
        "inputSchema": {
            "type": "object",
            "properties": {
                "trade_date": {"type": "string", "description": "日期 YYYYMMDD"},
            },
            "required": ["trade_date"],
        },
    },
    {
        "name": "search_stocks",
        "description": "搜索股票代码或名称",
        "inputSchema": {
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "关键词"},
            },
            "required": ["keyword"],
        },
    },
    {
        "name": "screen_stocks",
        "description": "筛选股票（PE/PB/ROE/行业）",
        "inputSchema": {
            "type": "object",
            "properties": {
                "pe_max": {"type": "number", "description": "最大PE"},
                "pb_max": {"type": "number", "description": "最大PB"},
                "roe_min": {"type": "number", "description": "最小ROE"},
                "industry": {"type": "string", "description": "行业名称"},
            },
        },
    },
]


@mcp_app.get("/mcp/v1/tools/list")
def list_tools(auth_info: dict = Depends(require_auth)):
    return {"tools": TOOLS}


@mcp_app.post("/mcp/v1/tools/call")
def call_tool(request: dict, auth_info: dict = Depends(require_auth)):
    name = request.get("tool", request.get("name", ""))
    args = request.get("arguments", request.get("args", {}))

    try:
        if name == "query_daily":
            df = query_daily(args.get("code", ""), args.get("days", 20))
            return {"result": fmt_df(df)}

        elif name == "query_moneyflow":
            df = query_moneyflow(args.get("code", ""), args.get("days", 20))
            return {"result": fmt_df(df)}

        elif name == "query_financial":
            df = query_financial(args.get("code", ""))
            return {"result": fmt_df(df)}

        elif name == "query_industry":
            df = query_industry_performance(args.get("top_n", 15))
            return {"result": fmt_df(df)}

        elif name == "query_hsgt":
            df = query_hsgt(args.get("days", 10))
            return {"result": fmt_df(df)}

        elif name == "query_hsgt_top":
            df = query_hsgt_top(args.get("days", 5))
            return {"result": fmt_df(df)}

        elif name == "query_top_list":
            df = query_top_list(args.get("trade_date", ""))
            return {"result": fmt_df(df)}

        elif name == "search_stocks":
            df = search_stocks(args.get("keyword", ""))
            return {"result": fmt_df(df)}

        elif name == "screen_stocks":
            df = screen_stocks(
                pe_max=args.get("pe_max"),
                pb_max=args.get("pb_max"),
                roe_min=args.get("roe_min"),
                industry=args.get("industry"),
            )
            return {"result": fmt_df(df)}

        else:
            tool_names = [t["name"] for t in TOOLS]
            return {"error": f"Unknown tool: {name}. Available: {', '.join(tool_names)}"}

    except Exception as e:
        return {"error": f"Tool execution failed: {e}"}


def run_mcp_server():
    from .config import get_settings
    settings = get_settings()
    mcp_port = settings.port + 1  # default 8901
    print(f"stockpulse MCP server starting on :{mcp_port}")
    uvicorn.run(mcp_app, host=settings.host, port=mcp_port,
                log_level=settings.log_level)
