---
name: ashare-stock-query
description: "Use when the user asks about A-share (Chinese stock market) data — daily quotes, money flow, financials, industry rankings, north-bound capital, top list, or macro indicators."
version: 1.0.0
author: ALLAN
license: MIT
metadata:
  hermes:
    tags: [financial, a-share, stock-data, agent-tool]
    related_skills: [ashare-financial-analysis]
---

# ashare-stock-query

让 Hermes Agent 具备查询 A 股数据的能力。

## 配置

确保 `ashare-agent` 包已安装，且 PostgreSQL 数据库可用：

```bash
pip install ashare-agent
export ASHARE_AGENT_PG_URI="postgresql://user@host/db?options=-c%20search_path=ashare,public"
```

## 使用方式

在对话中直接提问，Agent 会自动路由到对应查询：

| 你想问 | Agent 会执行 |
|--------|-------------|
| "宁德时代最近5个交易日行情" | `query_daily("300750.SZ", 5)` |
| "贵州茅台资金流向" | `query_moneyflow("600519.SH", 20)` |
| "比亚迪2025年财务数据" | `query_financial("002594.SZ")` |
| "今日行业涨跌排行" | `query_industry_performance()` |
| "北向资金最近10天" | `query_hsgt(10)` |
| "龙虎榜 20260724" | `query_top_list("20260724")` |
| "最新CPI数据" | `query_macro("cpi")` |
| "筛选PE<20的股票" | `screen_stocks(pe_max=20)` |
| "搜索新能源汽车股票" | `search_stocks("新能源汽车")` |

## 实现

使用 `ashare_agent.engine` 模块中的函数直接查询 PostgreSQL 数据库：

```python
from ashare_agent.engine import query_daily, query_moneyflow
from ashare_agent.utils import fmt_df

df = query_daily("300750.SZ", 10)
result = fmt_df(df)
```

## 注意事项

- 数据库搜索路径为 `ashare` schema
- 数据覆盖：日线 2015~今，财务 2008~今
- 如果 Agent 没有安装 ashare-agent 包，可以用 `pip install` 安装
