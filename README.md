# 🫀 StockPulse

**让 AI Agent 做 A 股分析——不仅仅是查数据。**

不只是查行情，而是让 Agent 帮你分析资金流向、判断北向资金态度、解读财务趋势、交叉验证信号。

```python
from stockpulse import StockPulse

pulse = StockPulse()
pulse.query("宁德时代最近资金流向怎么样？北向资金怎么看？")
```

---

## ✨ 不仅仅是 MCP 服务器——是 AI 金融分析引擎

| 能力 | StockPulse | 其他 A 股 MCP |
|------|-----------|-------------|
| 🧠 **北向资金分析** | ✅ **独家** | ❌ 全部没有 |
| 📋 **龙虎榜追踪** | ✅ **独家** | ❌ 全部没有 |
| 🌐 **宏观数据联动** | ✅ CPI/PMI/M2/Shibor/LPR | ❌ 全部没有 |
| 🔌 **OpenAI 协议直连** | ✅ **独家** — Claude Code/Codex 直接调 | ❌ 仅 MCP 协议 |
| 🏗 **自建数据仓库** | ✅ **3400 万行** — 查询快、稳定 | ❌ 每次实时爬取 |
| 🔀 **多维交叉分析** | ✅ 资金+北向+财务+宏观 联合判断 | ❌ 单点查询 |
| ⚡ **实时行情** | — | ✅ 更快 |
| 🚀 **秒级部署** | — | ✅ 更简单 |

---

## 📊 覆盖数据

| 分类 | 内容 | 行数 | 独家 |
|------|------|------|------|
| 📈 日线行情 | 开高低收量额 | 800万+ | |
| 💰 资金流向 | 主力/散户/超大单净流入 | 890万+ | |
| 📊 财务指标 | EPS/ROE/ROA/营收/资本公积 | 22万+ | |
| 🏭 行业排行 | 78个行业实时涨跌均值 | 实时计算 | |
| 🇭🇰 **北向资金** | **沪深股通每日汇总** | **近2年** | ✅ **唯一** |
| 📋 **龙虎榜** | **每日上榜明细** | **16万+** | ✅ **唯一** |
| 🌐 **宏观数据** | **CPI/PPI/PMI/GDP/M2/Shibor/LPR** | **20年** | ✅ **唯一** |
| 🔍 **智能选股** | PE/PB/ROE/行业 多维筛选 | 实时计算 | |

---

## 🚀 快速开始

### 安装

```bash
pip install stockpulse
```

### 配置

```bash
# 使用自建数据库
export STOCKPULSE_PG_URI="postgresql://user@host/db?options=-c%20search_path=ashare,public"

# 或使用托管 API（无需自建数据库）
export STOCKPULSE_API_KEY="your_key"
```

### 启动

```bash
# API 服务器（OpenAI 兼容）
stockpulse serve

# MCP 服务器（Claude Code / Cursor）
stockpulse mcp
```

### 查询

```bash
stockpulse query "宁德时代最近5个交易日行情"
stockpulse query "今日行业涨跌排行"
stockpulse query "北向资金最近10天流向分析"
```

---

## 🔗 MCP 集成（Claude Code / Cursor）

```json
{
  "mcpServers": {
    "stockpulse": {
      "type": "http",
      "url": "http://localhost:8901/mcp/v1"
    }
  }
}
```

配置后直接在对话里问：

> "帮我查一下宁德时代的资金流向，结合北向资金最近5天的数据，做一个综合判断"

---

## 🏗 架构

```
用户（自然语言）
    ↓
意图识别 → 判断是查行情/资金/北向/财务/宏观...
    ↓
查询引擎 → PostgreSQL 3400 万行 → 毫秒级返回
    ↓
分析层 → 交叉验证 + 趋势判断
    ↓
Agent 友好输出 → 表格 + 文字结论
```

---

## 📖 文档
\n## 🐳 Docker\n\n```bash\n# 一键启动（API + PostgreSQL）\ndocker compose up -d\n\n# 仅启动 API（使用外部 PG）\ndocker run -p 8900:8900 \\\n  -e STOCKPULSE_PG_URI="postgresql://user@host/db?options=-c%20search_path=ashare,public" \\\n  ghcr.io/Allan1900/stockpulse:latest\n```\n\n| 端口 | 服务 |\n|------|------|\n| 8900 | OpenAI 兼容 API |\n| 8901 | MCP 协议服务器 |\n

| 链接 | 说明 |
|------|------|
| [快速开始](docs/getting-started.md) | 安装 & 配置 |
| [API 参考](docs/api-reference.md) | 所有端点 |
| [MCP 集成](docs/mcp-integration.md) | Claude Code/Cursor |
| [Agent 示例](docs/agent-examples.md) | 使用场景 |
| [介绍文章](docs/blog/introduction.md) | 完整背景 |

---

## 🔑 开源与付费

| | 自部署（免费） | 托管 API（付费） |
|--|--------------|----------------|
| 费用 | MIT 开源 | 免费层 100次/天 |
| 数据库 | 自己维护 | 我们维护，每日更新 |
| 运维 | 自己管 | 零运维 |

---

## 📜 许可证

MIT