# Agent Usage Examples

## Example 1: Claude Code

```bash
# In Claude Code terminal:
ashare-agent query "宁德时代最近5个交易日行情"
```

## Example 2: Cursor with MCP

```bash
# Start MCP server
ashare-agent mcp

# In Cursor composer, type:
# "查一下贵州茅台的PE和PB"
```

## Example 3: Python SDK

```python
from ashare_agent.engine import query_daily, query_moneyflow

# Get daily quotes
df = query_daily("000001.SZ", days=10)
print(df)

# Get money flow
df = query_moneyflow("300750.SZ", days=5)
print(df)
```

## Example 4: curl

```bash
curl -s http://localhost:8900/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_KEY" \
  -d '{"messages":[{"role":"user","content":"今日行业涨跌排行"}]}' | \
  jq .
```
