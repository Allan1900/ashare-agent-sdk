---
layout: default
---

# 🏦 ashare-agent

**让 AI Agent（Claude Code / Cursor / Codex / OpenClaw）用自然语言查 A 股数据。**

```bash
pip install ashare-agent
ashare-agent query "宁德时代最近5个交易日行情"
```

---

## 快速上手

### 使用 CLI

```bash
ashare-agent query "宁德时代最近5个交易日行情"
ashare-agent query "贵州茅台资金流向"
ashare-agent query "今日行业涨跌排行"
ashare-agent query "北向资金最近5天"
ashare-agent query "比亚迪财务数据"
```

### 启动 API 服务器（OpenAI 兼容）

```bash
ashare-agent serve
# → http://localhost:8900
# → /v1/chat/completions
```

### 启动 MCP 服务器（Claude Code / Cursor）

```bash
ashare-agent mcp
# → http://localhost:8901/mcp/v1
```

---

## 快速跳转

| 链接 | 说明 |
|------|------|
| [📖 快速开始](getting-started.md) | 安装 & 配置 |
| [📚 API 参考](api-reference.md) | 所有端点说明 |
| [🔗 MCP 集成](mcp-integration.md) | Claude Code / Cursor 配置 |
| [🤖 Agent 示例](agent-examples.md) | 使用场景 |
| [📝 介绍文章](blog/introduction.md) | 《让 Claude Code 直接查 A 股数据》 |
| [🐙 GitHub](https://github.com/Allan1900/ashare-agent-sdk) | 源代码 |

---

## 支持的数据

| 分类 | 覆盖范围 | 行数 |
|------|---------|------|
| 日线行情 | 5529 只股票，2015~至今 | 800万+ |
| 资金流向 | 主力/散户净流入 | 890万+ |
| 财务指标 | EPS/ROE/营收/资本公积 | 22万+ |
| 行业排行 | 78 个行业实时涨跌 | — |
| 北向资金 | 沪深股通每日汇总 | 近 2 年 |
| 龙虎榜 | 每日上榜明细 | 16万+ |
| 宏观数据 | CPI/PPI/PMI/GDP/M2/Shibor/LPR | 20 年 |