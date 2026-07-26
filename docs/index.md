---
layout: default
---

# 🫀 StockPulse

**让 AI Agent 做 A 股分析——不仅仅是查数据。**

北向资金 / 龙虎榜 / 宏观数据 / 行情 / 财务 — OpenAI 兼容 API + MCP 协议 + CLI。

```bash
pip install stockpulse
stockpulse query "宁德时代最近5个交易日行情"
```

---

## 快速上手

### CLI

```bash
stockpulse query "宁德时代最近5个交易日行情"
stockpulse query "贵州茅台资金流向"
stockpulse query "今日行业涨跌排行"
stockpulse query "北向资金最近5天"
stockpulse query "比亚迪财务数据"
```

### API 服务器（OpenAI 兼容）

```bash
stockpulse serve
# → http://localhost:8900
# → /v1/chat/completions
```

### MCP 服务器（Claude Code / Cursor）

```bash
stockpulse mcp
# → http://localhost:8901/mcp/v1
```

---

## 文档

| 链接 | 说明 |
|------|------|
| [📖 快速开始](getting-started.md) | 安装 & 配置 |
| [📚 API 参考](api-reference.md) | 所有端点 |
| [🔗 MCP 集成](mcp-integration.md) | Claude Code / Cursor 配置 |
| [🤖 Agent 示例](agent-examples.md) | 使用场景 |
| [📝 介绍文章](blog/introduction.md) | 《让 Claude Code 直接查 A 股数据》 |
| [🐙 GitHub](https://github.com/Allan1900/stockpulse) | 源代码 |

---

## 独家数据

| 分类 | 覆盖范围 | 行数 |
|------|---------|------|
| 📈 日线行情 | 5529 只股票，2015~至今 | 800万+ |
| 💰 资金流向 | 主力/散户净流入 | 890万+ |
| 📊 财务指标 | EPS/ROE/营收/资本公积 | 22万+ |
| 🏭 行业排行 | 78 个行业实时涨跌 | — |
| 🇭🇰 **北向资金** | 沪深股通每日汇总 | **独家** |
| 📋 **龙虎榜** | 每日上榜明细 | **独家** |
| 🌐 **宏观数据** | CPI/PPI/PMI/GDP/M2/Shibor/LPR | **独家** |