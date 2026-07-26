"""MCP protocol server — data + indicators + report tools."""

import json
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .auth import require_auth
from .engine import (
    query_daily, query_daily_basic, query_moneyflow,
    query_financial, query_industry_performance,
    query_hsgt, query_hsgt_top, query_top_list, query_macro,
    search_stocks, screen_stocks,
)
from . import indicators
from .utils import fmt_df

mcp_app = FastAPI(title="stockpulse MCP Server", version="0.3.0")
mcp_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# ── Tool definitions ─────────────────────────────

TOOLS = [
    {"name": "query_daily", "description": "查询股票日线行情",
     "inputSchema": {"type": "object", "properties": {
         "code": {"type": "string"}, "days": {"type": "integer"}}}},
    {"name": "query_moneyflow", "description": "查询个股资金流向",
     "inputSchema": {"type": "object", "properties": {
         "code": {"type": "string"}, "days": {"type": "integer"}}}},
    {"name": "query_financial", "description": "查询财务数据",
     "inputSchema": {"type": "object", "properties": {
         "code": {"type": "string"}}}},
    {"name": "query_industry", "description": "查询行业涨跌排行",
     "inputSchema": {"type": "object", "properties": {
         "top_n": {"type": "integer"}}}},
    {"name": "query_hsgt", "description": "查询北向资金汇总",
     "inputSchema": {"type": "object", "properties": {
         "days": {"type": "integer"}}}},
    {"name": "query_hsgt_top", "description": "北向资金十大活跃股",
     "inputSchema": {"type": "object", "properties": {
         "days": {"type": "integer"}}}},
    {"name": "query_top_list", "description": "查询龙虎榜",
     "inputSchema": {"type": "object", "properties": {
         "trade_date": {"type": "string"}}, "required": ["trade_date"]}},
    {"name": "search_stocks", "description": "搜索股票",
     "inputSchema": {"type": "object", "properties": {
         "keyword": {"type": "string"}}, "required": ["keyword"]}},
    {"name": "screen_stocks", "description": "筛选股票(PE/PB/ROE)",
     "inputSchema": {"type": "object", "properties": {
         "pe_max": {"type": "number"}, "pb_max": {"type": "number"},
         "roe_min": {"type": "number"}, "industry": {"type": "string"}}}},
    # ── Indicators ──
    {"name": "get_ma", "description": "移动平均线(MA5/10/20/60)",
     "inputSchema": {"type": "object", "properties": {
         "code": {"type": "string"}, "days": {"type": "integer"}}}},
    {"name": "get_macd", "description": "MACD(DIF/DEA/柱)",
     "inputSchema": {"type": "object", "properties": {
         "code": {"type": "string"}, "days": {"type": "integer"}}}},
    {"name": "get_rsi", "description": "RSI相对强弱指标(6/12/24)",
     "inputSchema": {"type": "object", "properties": {
         "code": {"type": "string"}, "days": {"type": "integer"}}}},
    {"name": "get_kdj", "description": "KDJ随机指标",
     "inputSchema": {"type": "object", "properties": {
         "code": {"type": "string"}, "days": {"type": "integer"}}}},
    {"name": "get_boll", "description": "布林带(BOLL)",
     "inputSchema": {"type": "object", "properties": {
         "code": {"type": "string"}, "days": {"type": "integer"}}}},
    {"name": "get_golden_cross", "description": "检测MA5金叉MA10",
     "inputSchema": {"type": "object", "properties": {
         "code": {"type": "string"}}}},
    {"name": "get_death_cross", "description": "检测MA5死叉MA10",
     "inputSchema": {"type": "object", "properties": {
         "code": {"type": "string"}}}},
    {"name": "get_rsi_signal", "description": "检测RSI超买超卖",
     "inputSchema": {"type": "object", "properties": {
         "code": {"type": "string"}}}},
    # ── Report ──
    {"name": "get_report", "description": "生成完整AI分析报告(行情+资金+财务+46指标+综合研判)",
     "inputSchema": {"type": "object", "properties": {
         "code": {"type": "string", "description": "股票代码或名称"}},
         "required": ["code"]}},
]


@mcp_app.get("/mcp/v1/tools/list")
def list_tools(auth_info: dict = Depends(require_auth)):
    return {"tools": TOOLS}


@mcp_app.post("/mcp/v1/tools/call")
def call_tool(request: dict, auth_info: dict = Depends(require_auth)):
    name = request.get("tool", request.get("name", ""))
    args = request.get("arguments", request.get("args", {}))

    try:
        # ── Data ──
        if name == "query_daily":
            return {"result": fmt_df(query_daily(args.get("code",""), args.get("days",20)))}
        elif name == "query_moneyflow":
            return {"result": fmt_df(query_moneyflow(args.get("code",""), args.get("days",20)))}
        elif name == "query_financial":
            return {"result": fmt_df(query_financial(args.get("code","")))}
        elif name == "query_industry":
            return {"result": fmt_df(query_industry_performance(args.get("top_n",15)))}
        elif name == "query_hsgt":
            return {"result": fmt_df(query_hsgt(args.get("days",10)))}
        elif name == "query_hsgt_top":
            return {"result": fmt_df(query_hsgt_top(args.get("days",5)))}
        elif name == "query_top_list":
            return {"result": fmt_df(query_top_list(args.get("trade_date","")))}
        elif name == "search_stocks":
            return {"result": fmt_df(search_stocks(args.get("keyword","")))}
        elif name == "screen_stocks":
            return {"result": fmt_df(screen_stocks(
                pe_max=args.get("pe_max"), pb_max=args.get("pb_max"),
                roe_min=args.get("roe_min"), industry=args.get("industry")))}

        # ── Indicators ──
        elif name == "get_ma":
            df = query_daily(args.get("code",""), args.get("days",60))
            return {"result": "无数据" if df.empty else fmt_df(indicators.calc_ma(df.sort_values("trade_date")).tail(20))}
        elif name == "get_macd":
            df = query_daily(args.get("code",""), args.get("days",120))
            return {"result": "无数据" if df.empty else fmt_df(indicators.calc_macd(df.sort_values("trade_date")).tail(20))}
        elif name == "get_rsi":
            df = query_daily(args.get("code",""), args.get("days",60))
            return {"result": "无数据" if df.empty else fmt_df(indicators.calc_rsi(df.sort_values("trade_date")).tail(20))}
        elif name == "get_kdj":
            df = query_daily(args.get("code",""), args.get("days",60))
            return {"result": "无数据" if df.empty else fmt_df(indicators.calc_kdj(df.sort_values("trade_date")).tail(20))}
        elif name == "get_boll":
            df = query_daily(args.get("code",""), args.get("days",60))
            return {"result": "无数据" if df.empty else fmt_df(indicators.calc_boll(df.sort_values("trade_date")).tail(20))}
        elif name == "get_golden_cross":
            sig = indicators.check_golden_cross(args.get("code",""))
            return {"result": sig or "无金叉信号"}
        elif name == "get_death_cross":
            sig = indicators.check_death_cross(args.get("code",""))
            return {"result": sig or "无死叉信号"}
        elif name == "get_rsi_signal":
            sig = indicators.check_rsi_signal(args.get("code",""))
            return {"result": sig or "无RSI超买超卖信号"}

        # ── Report ──
        elif name == "get_report":
            from .report import analyze
            return {"result": analyze(args.get("code", ""))}

        else:
            names = [t["name"] for t in TOOLS]
            return {"error": f"未知工具: {name}"}
    except Exception as e:
        return {"error": f"执行失败: {e}"}


def run_mcp_server():
    from .config import get_settings
    settings = get_settings()
    mcp_port = settings.port + 1
    print(f"stockpulse MCP server starting on :{mcp_port}")
    uvicorn.run(mcp_app, host=settings.host, port=mcp_port,
                log_level=settings.log_level)