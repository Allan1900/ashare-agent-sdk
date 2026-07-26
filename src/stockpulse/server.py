""""OpenAI-compatible FastAPI server with indicator support.""

import secrets
import re
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from .config import get_settings
from .auth import require_auth
from .engine import (
    query_daily, query_daily_basic, query_moneyflow,
    query_financial, query_industry_performance,
    query_hsgt, query_hsgt_top, query_top_list, query_macro,
    search_stocks, screen_stocks, name_to_code,
)
from . import indicators
from .utils import (
    extract_code, detect_query_type, extract_days,
    extract_trade_date, fmt_df,
)

app = FastAPI(title="stockpulse API", version="0.2.0",
              description="AI Agent-native A-share financial analysis engine")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)


class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str = "stockpulse-data"
    messages: list[ChatMessage]
    temperature: float = 0.1

class ChatChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str = "stop"

class ChatResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    model: str = "stockpulse-data"
    choices: list[ChatChoice]


def _resolve_code(text: str) -> str | None:
    code = extract_code(text)
    if code:
        return code
    for suffix in ["行情", "资金流向", "资金", "财务", "macd", "rsi", "kdj",
                    "均线", "金叉", "死叉", "股价", "数据", "最近", "今日", "今天"]:
        if suffix in text:
            parts = text.split(suffix)[0].strip()
            if parts:
                code = name_to_code(parts)
                if code:
                    return code
    return None


def _route_query(text: str) -> str:
    t = text.lower()
    days = extract_days(text)
    code = _resolve_code(text)

    try:
        # ── Indicator queries ────────────────────────
        if any(kw in t for kw in ["macd", "dif", "dea"]):
            if not code:
                return "请提供股票代码或名称"
            df = query_daily(code, max(days * 2, 120))
            if df.empty:
                return f"无数据: {code}"
            r = indicators.calc_macd(df.sort_values("trade_date"))
            return fmt_df(r.tail(min(days * 2, 30)))

        if any(kw in t for kw in ["rsi", "超买", "超卖"]):
            if not code:
                return "请提供股票代码或名称"
            df = query_daily(code, max(days * 2, 60))
            if df.empty:
                return f"无数据: {code}"
            r = indicators.calc_rsi(df.sort_values("trade_date"))
            return fmt_df(r.tail(min(days * 2, 30)))

        if any(kw in t for kw in ["kdj", "随机指标"]):
            if not code:
                return "请提供股票代码或名称"
            df = query_daily(code, max(days * 2, 60))
            if df.empty:
                return f"无数据: {code}"
            r = indicators.calc_kdj(df.sort_values("trade_date"))
            return fmt_df(r.tail(min(days * 2, 30)))

        if any(kw in t for kw in ["boll", "布林", "布林带", "bo ll"]):
            if not code:
                return "请提供股票代码或名称"
            df = query_daily(code, max(days * 2, 60))
            if df.empty:
                return f"无数据: {code}"
            r = indicators.calc_boll(df.sort_values("trade_date"))
            return fmt_df(r.tail(min(days * 2, 30)))

        if "金叉" in t:
            if not code:
                return "请提供股票代码或名称"
            sig = indicators.check_golden_cross(code)
            return sig or "无金叉信号"

        if "死叉" in t:
            if not code:
                return "请提供股票代码或名称"
            sig = indicators.check_death_cross(code)
            return sig or "无死叉信号"

        # ── Data queries ────────────────────────────
        query_type = detect_query_type(text)
        trade_date = extract_trade_date(text)

        if query_type == "daily":
            if code:
                return fmt_df(query_daily(code, days))
            return "请提供股票代码或名称"

        elif query_type == "moneyflow":
            if code:
                return fmt_df(query_moneyflow(code, days))
            return "请提供股票代码或名称"

        elif query_type == "financial":
            if code:
                return fmt_df(query_financial(code))
            return "请提供股票代码或名称"

        elif query_type == "industry":
            return fmt_df(query_industry_performance())

        elif query_type == "hsgt":
            return fmt_df(query_hsgt(days))

        elif query_type == "top_list":
            if trade_date:
                return fmt_df(query_top_list(trade_date))
            return "请提供日期，例如：龙虎榜 20260724"

        elif query_type == "macro":
            for kw in ["cpi", "ppi", "pmi", "gdp", "m2", "shibor", "lpr"]:
                if kw in t:
                    return fmt_df(query_macro(kw))
            return "支持的宏观指标: cpi, ppi, pmi, gdp, m2, shibor, lpr"

        elif query_type == "screen":
            pe_max = None; pb_max = None; roe_min = None
            m = re.search(r"pe<\s*(\d+)", t)
            if m: pe_max = float(m.group(1))
            m = re.search(r"pb<\s*(\d+)", t)
            if m: pb_max = float(m.group(1))
            m = re.search(r"roe>\s*(\d+)", t)
            if m: roe_min = float(m.group(1))
            return fmt_df(screen_stocks(pe_max=pe_max, pb_max=pb_max, roe_min=roe_min))

        elif query_type == "search":
            for kw in ["搜索", "查找", "找股票"]:
                if kw in text:
                    keyword = text.split(kw)[-1].strip()
                    if keyword:
                        return fmt_df(search_stocks(keyword))
            return "请提供搜索关键词"

        return "\n".join([
            "无法识别的查询，试试：",
            "  宁德时代MACD指标",
            "  贵州茅台RSI是否超买",
            "  宁德时代KDJ",
            "  比亚迪布林带",
            "  贵州茅台金叉/死叉",
            "  宁德时代最近5个交易日行情",
            "  贵州茅台资金流向",
            "  今日行业涨跌排行",
            "  北向资金最近10天",
            "  筛选 PE<20 的股票",
        ])

    except Exception as e:
        return f"查询出错: {e}"


@app.get("/health")
def health():
    return {"status": "ok", "service": "stockpulse", "version": "0.2.0"}


@app.post("/v1/chat/completions", response_model=ChatResponse)
async def chat_completions(
    request: ChatRequest,
    auth_info: dict = Depends(require_auth),
):
    if not request.messages:
        raise HTTPException(status_code=400, detail="messages is required")
    last_msg = request.messages[-1].content
    result = _route_query(last_msg)
    return ChatResponse(
        id=f"chatcmpl-stockpulse-{secrets.token_hex(8)}",
        model=request.model,
        choices=[ChatChoice(index=0, message=ChatMessage(role="assistant", content=result))],
    )


@app.get("/v1/models")
def list_models():
    return {
        "object": "list",
        "data": [{"id": "stockpulse-data", "object": "model",
                   "created": 1710000000, "owned_by": "stockpulse"}],
    }


def run_server():
    settings = get_settings()
    print(f"stockpulse API server starting...")
    print(f"  Listen: http://{settings.host}:{settings.port}")
    print(f"  Docs:   http://{settings.host}:{settings.port}/docs")
    print(f"  Health: http://{settings.host}:{settings.port}/health")
    uvicorn.run(app, host=settings.host, port=settings.port,
                log_level=settings.log_level)


if __name__ == "__main__":
    run_server()