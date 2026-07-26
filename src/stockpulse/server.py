"""OpenAI-compatible FastAPI server."""

import secrets
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .config import get_settings
from .auth import require_auth
from .engine import (
    query_daily, query_daily_basic, query_moneyflow,
    query_financial, query_industry_performance,
    query_hsgt, query_hsgt_top, query_top_list, query_macro,
    search_stocks, screen_stocks, name_to_code,
)
from .utils import (
    extract_code, detect_query_type, extract_days,
    extract_trade_date, fmt_df,
)
import uvicorn

app = FastAPI(title="stockpulse API", version="0.1.0",
              description="AI Agent-native A-share financial data API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str = "ashare-data"
    messages: list[ChatMessage]
    temperature: float = 0.1

class ChatChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str = "stop"

class ChatResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    model: str = "ashare-data"
    choices: list[ChatChoice]


def _resolve_code(text: str) -> str | None:
    """Resolve stock code from text: try explicit code, then name lookup."""
    code = extract_code(text)
    if code:
        return code
    # Try name lookup — extract the stock name from the query
    # Common patterns: "宁德时代..." or "...宁德时代..."
    for suffix in ["行情", "资金流向", "财务", "股价", "数据", "最近", "今日", "今天"]:
        if suffix in text:
            parts = text.split(suffix)[0].strip()
            if parts:
                code = name_to_code(parts)
                if code:
                    return code
    return None


def _route_query(text: str) -> str:
    """Parse natural language, execute query, return formatted result."""
    query_type = detect_query_type(text)
    days = extract_days(text)
    trade_date = extract_trade_date(text)
    code = _resolve_code(text)

    try:
        if query_type == "daily":
            if code:
                df = query_daily(code, days)
                return fmt_df(df)
            return "请提供股票代码或名称，例如：查询宁德时代最近5个交易日行情"

        elif query_type == "moneyflow":
            if code:
                df = query_moneyflow(code, days)
                return fmt_df(df)
            return "请提供股票代码或名称"

        elif query_type == "financial":
            if code:
                df = query_financial(code)
                return fmt_df(df)
            return "请提供股票代码或名称"

        elif query_type == "industry":
            df = query_industry_performance()
            return fmt_df(df)

        elif query_type == "hsgt":
            df = query_hsgt(days)
            return fmt_df(df)

        elif query_type == "top_list":
            if trade_date:
                df = query_top_list(trade_date)
                return fmt_df(df)
            return "请提供日期，例如：龙虎榜 20260724"

        elif query_type == "macro":
            for kw in ["cpi", "ppi", "pmi", "gdp", "m2", "shibor", "lpr"]:
                if kw in text.lower():
                    df = query_macro(kw)
                    return fmt_df(df)
            return "支持的宏观指标: cpi, ppi, pmi, gdp, m2, shibor, lpr"

        elif query_type == "screen":
            import re
            pe_max = None; pb_max = None; roe_min = None
            m = re.search(r"pe<\s*(\d+)", text.lower())
            if m: pe_max = float(m.group(1))
            m = re.search(r"pb<\s*(\d+)", text.lower())
            if m: pb_max = float(m.group(1))
            m = re.search(r"roe>\s*(\d+)", text.lower())
            if m: roe_min = float(m.group(1))
            df = screen_stocks(pe_max=pe_max, pb_max=pb_max, roe_min=roe_min)
            return fmt_df(df)

        elif query_type == "search":
            for kw in ["搜索", "查找", "找股票"]:
                if kw in text:
                    keyword = text.split(kw)[-1].strip()
                    if keyword:
                        df = search_stocks(keyword)
                        return fmt_df(df)
            return "请提供搜索关键词"

        return "无法识别的查询。试试：\n- 宁德时代最近5个交易日行情\n- 贵州茅台资金流向\n- 今日行业涨跌排行\n- 北向资金最近10天\n- 筛选 PE<20 的股票"

    except Exception as e:
        return f"查询出错: {e}"


@app.get("/health")
def health():
    return {"status": "ok", "service": "stockpulse", "version": "0.1.0"}


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
        id=f"chatcmpl-ashare-{secrets.token_hex(8)}",
        model=request.model,
        choices=[
            ChatChoice(
                index=0,
                message=ChatMessage(role="assistant", content=result),
            )
        ],
    )


@app.get("/v1/models")
def list_models():
    return {
        "object": "list",
        "data": [
            {
                "id": "ashare-data",
                "object": "model",
                "created": 1710000000,
                "owned_by": "stockpulse",
            }
        ],
    }


def run_server():
    settings = get_settings()
    print(f"stockpulse API server starting...")
    print(f"  Listen: http://{settings.host}:{settings.port}")
    print(f"  Docs:  http://{settings.host}:{settings.port}/docs")
    print(f"  Health: http://{settings.host}:{settings.port}/health")
    uvicorn.run(app, host=settings.host, port=settings.port,
                log_level=settings.log_level)


if __name__ == "__main__":
    run_server()