# API Reference

## OpenAI-compatible Endpoints

### POST /v1/chat/completions

OpenAI-compatible chat completion endpoint. Send natural language queries about A-share financial data.

**Request:**
```json
{
  "model": "ashare-data",
  "messages": [
    {"role": "user", "content": "宁德时代最近5个交易日资金流向如何？"}
  ],
  "temperature": 0.1
}
```

**Response:**
```json
{
  "id": "chatcmpl-ashare-abc123",
  "object": "chat.completion",
  "model": "ashare-data",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "trade_date  buy_sm_vol  ...  net_mf_amount\n..."
      },
      "finish_reason": "stop"
    }
  ]
}
```

**Authentication:** Bearer token in Authorization header, or x-api-key header.

### GET /v1/models

List available models.

### GET /health

Health check endpoint.

---

## Supported Query Types

| Natural Language Pattern | Query Type | Example |
|-------------------------|------------|---------|
| "行情" "收盘" "涨跌" | daily | "贵州茅台最近10个交易日收盘价" |
| "资金流向" "主力" "净流入" | moneyflow | "宁德时代今日资金流向" |
| "财务" "营收" "利润" "ROE" | financial | "比亚迪2025年财务数据" |
| "行业" "板块" | industry | "今日行业涨跌排行" |
| "北向" "沪深股通" | hsgt | "北向资金最近10天" |
| "龙虎榜" | top_list | "龙虎榜 20260724" |
| CPI/PPI/PMI/GDP/M2 | macro | "最新CPI数据" |
| "筛选" "PE<" "PB<" "ROE>" | screen | "筛选 PE<20 且 ROE>15% 的股票" |
| "搜索" "查找" | search | "搜索新能源汽车股票" |

---

## MCP Protocol Endpoints

### GET /mcp/v1/tools/list

List all available tools.

### POST /mcp/v1/tools/call

Call a specific tool.

**Available Tools:** query_daily, query_moneyflow, query_financial, query_industry, query_hsgt, query_hsgt_top, query_top_list, search_stocks, screen_stocks
