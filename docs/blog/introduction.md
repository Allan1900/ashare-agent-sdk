# 让 Claude Code 直接查 A 股数据——我开源了一个 Agent SDK

> 5 分钟让你的 AI 编程助手拥有查询 A 股行情、资金流向、财务数据的能力

---

## 痛点

你有没有遇到过这种情况：

在用 Claude Code 写量化策略的时候，想查一只股票的行情数据，必须：

1. 切到终端，敲 `python3 -c "import tushare as ts; ..."` 
2. 或者打开浏览器去东方财富搜
3. 把数据手动复制回来

Agent 的优势在于**连续推理**，但每次查数据就要打断一次，推理链就断了。

如果能直接在对话里说一句：

> "宁德时代最近5个交易日资金流向怎么样？"

Agent 就自己把数据查回来、分析完、给出结论——这才是 Agent 该有的工作方式。

所以我做了一个开源工具。

---

## 项目简介

**[ashare-agent](https://github.com/Allan1900/ashare-agent-sdk)** 是一个让 AI Agent 用自然语言查询 A 股数据的工具。它提供三样东西：

1. **OpenAI 兼容 API** — Claude Code / Cursor / Codex / OpenClaw 都能直接调
2. **MCP 协议服务器** — 任何支持 MCP 的 Agent 即插即用
3. **CLI 命令行** — 终端直接查

背后的数据源是 A 股全市场数据库，覆盖：

| 数据 | 覆盖范围 | 行数 |
|------|---------|------|
| 📈 日线行情 | 2015 ~ 至今，5529 只股票 | 800万+ |
| 💰 资金流向 | 主力/散户净流入 | 890万+ |
| 📊 财务指标 | ROE/EPS/营收/资本公积 | 22万+ |
| 🏭 行业排行 | 实时行业涨跌 | 实时计算 |
| 🇭🇰 北向资金 | 沪深股通每日汇总 | 近2年 |
| 📋 龙虎榜 | 每日上榜明细 | 16万+ |

---

## 5 分钟上手

### 1. 安装

```bash
pip install ashare-agent
```

### 2. 配置数据库连接

工具需要连接一个 PostgreSQL 数据库（里面装有 A 股数据）。如果你有自己的数据库：

```bash
export ASHARE_AGENT_PG_URI="postgresql://user@host/db?options=-c%20search_path=ashare,public"
```

> 💡 **没有数据库？** 下文提供了托管服务选项，可以直接用，不用自己搭。

### 3. 启动服务

```bash
# 启动 API 服务器
ashare-agent serve

# 或者启动 MCP 服务器（给 Claude Code / Cursor 用）
ashare-agent mcp
```

### 4. 开始查询

**方式一：CLI 直接查**

```bash
ashare-agent query "宁德时代最近5个交易日行情"
```

输出：

```
trade_date   open   high    low  close       vol     amount
20260724 383.18 390.86 382.65 383.01 254542.23  9822804.0
20260723 373.00 386.00 366.01 385.99 359409.28 13610469.0
20260722 382.85 385.00 369.87 372.26 311937.62 11690411.0
```

**方式二：MCP 协议（推荐 — Claude Code / Cursor）**

在 `claude_desktop_config.json` 中添加：

```json
{
  "mcpServers": {
    "ashare": {
      "type": "http",
      "url": "http://localhost:8901/mcp/v1"
    }
  }
}
```

然后直接在 Claude Code 里问：

> "帮我查一下贵州茅台最近资金流向，然后分析一下主力是否在出货"

Agent 会自动调用工具查数据，然后基于数据做分析。

**方式三：curl / 任何 HTTP 客户端**

```bash
curl http://localhost:8900/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"今日行业涨跌排行"}]}'
```

---

## 真实运行效果

以下是用自然语言查询的真实返回数据：

### 查询行情

```
用户: 宁德时代最近3个交易日行情
Agent: trade_date   open   high    low  close       vol     amount
       20260724 383.18 390.86 382.65 383.01 254542.23  9822804.0
       20260723 373.00 386.00 366.01 385.99 359409.28 13610469.0
       20260722 382.85 385.00 369.87 372.26 311937.62 11690411.0
```

### 查询资金流向

```
用户: 贵州茅台资金流向
Agent: trade_date  buy_sm_vol  sell_sm_vol  buy_md_vol  sell_md_vol ...
       20260724        15.0         12.0     19239.0      19769.0
```

### 查询行业排行

```
用户: 今日行业涨跌排行
Agent: industry  stock_count  avg_change
       摩托车           12        0.19
       半导体          194       -0.09
        银行           42       -0.24
```

### 查询财务数据

```
用户: 比亚迪财务数据
Agent: end_date    eps  diluted_eps     roe  weighted_roe
       20260331  0.448        0.448  1.6464          1.65
       20251231  3.580        3.580 15.1180         15.31
       20241231 13.840       13.840 24.8437         26.05
```

### 查询北向资金

```
用户: 北向资金最近5天
Agent: trade_date  north_money  south_money
       20260724    283837.28     54852.56
       20260723    307549.79     54867.74
```

---

## 两种使用方式

### 方式 A：自部署（开源免费）

适合有技术能力、有自己的数据源的团队。

- 安装 Python 包，配置自己的 PostgreSQL
- 数据自己维护，服务自己管
- 完全免费，MIT 协议

### 方式 B：托管 API（付费）

适合不想自己搭数据 Pipeline 的个人和团队。

- 不用装数据库，直接调 API
- 数据实时更新，零运维
- 免费层 100 次/天，开发者版 ¥99/月

> ⚠️ **安全说明**：自部署版本默认绑定 localhost:8900，仅限本地访问。如需对外提供服务，请自行配置反向代理和 HTTPS。

---

## 技术架构

整个工具由四层组成：

```
用户输入（自然语言）
      ↓
意图识别层 — 判断是查行情/资金/财务/行业...
      ↓
查询路由层 — 转换为 SQL，调用 PostgreSQL
      ↓
结果格式化层 — 表格文本输出，Agent 可直接消费
```

- **协议层**：OpenAI `/v1/chat/completions` + MCP `tools/list` / `tools/call`
- **查询引擎**：SQLAlchemy + psycopg2，直连 PostgreSQL
- **名称解析**：内置 5529 只 A 股名称 → ts_code 映射，**宁德时代 → 300750.SZ，贵州茅台 → 600519.SH**
- **鉴权**：API Key 分级限流，免费 100次/天，开发者 5000次/天

---

## 为什么做这个

过去半年我一直在维护一个 A 股全市场数据库——每天自动拉取日线、资金流向、财务数据、北向资金、龙虎榜等 20+ 个接口，处理 schema 漂移、断点续传、限流调度、分区表优化……这套 Pipeline 跑了半年，积累了 3400万行数据。

但我发现，数据躺在数据库里，用起来还是很麻烦——每次都要写 SQL、写 Python 脚本。直到 AI Agent 成熟了，我才意识到：**Agent 才是最好的数据查询接口**。

所以我把数据 Pipeline 和 Agent 之间的一层封装开源了。希望这套工具能让更多人用上 AI + 金融数据的组合能力。

---

## 链接

- GitHub: [https://github.com/Allan1900/ashare-agent-sdk](https://github.com/Allan1900/ashare-agent-sdk)
- 文档：`docs/getting-started.md`
- MCP 集成：`docs/mcp-integration.md`

---

*如果你有想法或建议，欢迎在 GitHub 提 Issue。*