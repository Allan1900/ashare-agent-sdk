# MCP Integration Guide

## What is MCP?

MCP (Model Context Protocol) is a standard protocol that allows AI agents (Claude Code, Cursor, etc.) to call external tools directly.

## Configuration

### Claude Code

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ashare": {
      "type": "http",
      "url": "http://localhost:8901/mcp/v1",
      "headers": {
        "x-api-key": "your_api_key_here"
      }
    }
  }
}
```

### Cursor

In Cursor settings > MCP Servers > Add Server:
- Name: `ashare`
- Type: `HTTP`
- URL: `http://localhost:8901/mcp/v1`
- Headers: `{"x-api-key": "your_api_key_here"}`

## Usage Examples

Once connected, just type in natural language:

- "查一下宁德时代的资金流向"
- "今天哪个行业涨得最好？"
- "北向资金最近买了哪些股票？"
- "帮我筛选PE小于20的股票"
