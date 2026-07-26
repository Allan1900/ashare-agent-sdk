# 我开源了一个金融数据 Agent SDK，Claude Code 可以直接查 A 股了

> 5 分钟让你的 AI 编程助手拥有查询行情、资金流向、财务数据的能力。全部自然语言操作，零代码切换。

---

## 为什么你需要这个

如果你用过 Claude Code、Cursor 或者 Codex 写代码，你一定遇到过这个场景：

你在写一个量化策略，需要查贵州茅台最近 5 天的资金流向。你的流程是这样的：

1. 停下手中的代码
2. 打开浏览器 / 切到终端
3. 敲一行 Python 调用 Tushare
4. 把结果复制回来
5. 继续写策略

每次查数据，推理链就断了。

Agent 的优势是连续推理。如果 Agent 自己就能查数据，你的工作流应该是这样的：

```
你：贵州茅台最近资金流向怎么样？主力在出货吗？
Agent：查数据 → 分析 → 回答
你：那结合这两天北向资金的情况，给我一个判断
Agent：查更多数据 → 交叉分析 → 给结论
```

**一个对话完成所有事情，不需要切窗口。**

所以我做了一个开源工具。

---

## 这个工具是什么

[stockpulse](https://github.com/Allan1900/stockpulse-sdk) 是一个让 AI Agent 用自然语言查询 A 股数据的工具。

你告诉 Agent "宁德时代最近 5 个交易日行情"，它自己去数据库查，然后把结果返回给你。

### 三种使用方式

| 方式 | 适合谁 | 一句话 |
|------|--------|--------|
| **CLI 命令行** | 终端用户 | `stockpulse query "宁德时代行情"` |
| **MCP 协议** | Claude Code / Cursor / OpenClaw 用户 | 在对话里直接问 |
| **OpenAI API** | 任何 HTTP 客户端 | POST `/v1/chat/completions` |

### 支持的数据

| 分类 | 内容 | 覆盖范围 |
|------|------|---------|
| 日线行情 | open, high, low, close, vol, amount | 5529 只股票，2015~至今 |
| 资金流向 | 主力/散户/超大单净流入 | 890万+ 条记录 |
| 财务指标 | EPS, ROE, ROA, 每股营收, 资本公积 | 22万+ 条记录 |
| 行业排行 | 实时计算各行业涨跌均值 | 78 个行业 |
| 北向资金 | 沪深股通每日汇总 | 近 2 年 |
| 龙虎榜 | 每日上榜明细 | 16万+ 条 |
| 宏观数据 | CPI, PPI, PMI, GDP, M2, Shibor, LPR | 20 年 |

---

## 上手：5 分钟

### 安装

```bash
pip install stockpulse
```

### 配置数据库

工具需要一个装有 A 股数据的 PostgreSQL。你有两个选择：

**自己搭（开源免费）：**
自己维护数据库，自己管理数据更新。

**用托管服务（付费）：**
不用搭建，直接拿 API Key 就能用。免费层每天 100 次。

```bash
# 配置自己的数据库连接
export ASHARE_AGENT_PG_URI="postgresql://user@host/db?options=-c%20search_path=ashare,public"
```

### 启动

```bash
# 方式一：API 服务器
stockpulse serve

# 方式二：MCP 服务器（推荐给 Claude Code / Cursor）
stockpulse mcp
```

### 查询

```bash
# CLI 直接查
stockpulse query "宁德时代最近3个交易日行情"

# curl 查
curl http://localhost:8900/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"今日行业涨跌排行"}]}'
```

---

## 效果演示

以下全是真实查询结果，不是 Demo 数据。

### 📈 查行情

```
你：宁德时代最近3个交易日行情

  trade_date   open   high    low  close       vol     amount
  20260724 383.18 390.86 382.65 383.01 254542.23  9822804.0
  20260723 373.00 386.00 366.01 385.99 359409.28 13610469.0
  20260722 382.85 385.00 369.87 372.26 311937.62 11690411.0
```

### 💰 查资金流向

```
你：贵州茅台资金流向

  trade_date  buy_sm_vol  sell_sm_vol  buy_md_vol  ...  net_mf_amount
  20260724        15.0         12.0     19239.0    ...    -172368.0
```

### 🏭 查行业排行

```
你：今日行业涨跌排行

  industry    stock_count  avg_change
  摩托车             12        0.19
  半导体            194       -0.09
  银行              42       -0.24
  船舶              11       -0.44
```

### 📊 查财务数据

```
你：比亚迪财务数据

  end_date    eps  diluted_eps     roe  weighted_roe
  20260331  0.448        0.448  1.6464          1.65
  20251231  3.580        3.580 15.1180         15.31
  20241231 13.840       13.840 24.8437         26.05
```

### 🇭🇰 查北向资金

```
你：北向资金最近5天

  trade_date  north_money  south_money
  20260724    283837.28     54852.56
  20260723    307549.79     54867.74
  20260722    375048.34     54910.00
```

---

## 在 Claude Code 中配置（MCP 协议）

这是最推荐的用法——在对话中直接用自然语言查数据。

**第一步：** 启动 MCP 服务器

```bash
stockpulse mcp
```

服务器运行在 `http://localhost:8901`。

**第二步：** 配置 Claude Code

编辑 `claude_desktop_config.json`：

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

**第三步：** 开始使用

在 Claude Code 中直接输入：

> 查一下宁德时代的资金流向，看看主力今天是在买还是在卖
> 帮我筛选 PE 小于 20 且 ROE 大于 15% 的股票
> 今天哪个行业涨得最好？结合北向资金流向给我分析一下

Agent 会自动调用工具查出数据，然后基于数据做分析，返回完整的回答。

---

## 它是怎么工作的

```
用户输入 "宁德时代最近5个交易日行情"
        │
        ▼
  ① 名称解析：宁德时代 → 300750.SZ
        │
        ▼
  ② 意图识别：自然语言 → 判断为"日线查询"
        │
        ▼
  ③ SQL 执行：SELECT ... FROM daily WHERE ts_code='300750.SZ'
        │
        ▼
  ④ 格式化输出：表格文本 → 返回给 Agent
```

关键细节：

- **名称解析** — 内置 5529 只 A 股的名称 ↔ ts_code 映射，支持模糊匹配。你说"宁德时代"，它知道是 300750.SZ。
- **意图识别** — 基于关键词的路由策略。说"资金流向"走 moneyflow 表，说"财务"走 fina_indicator 表，说"北向"走 hsgt_moneyflow 表。
- **协议层** — 同时支持 OpenAI 的 `/v1/chat/completions` 和 MCP 的 `tools/list` + `tools/call`，兼容所有主流 Agent 工具。

---

## 开源与付费

| | 自部署（免费） | 托管 API（付费） |
|--|--------------|----------------|
| 费用 | MIT 开源，零成本 | 免费层 100次/天，开发者 ¥99/月 |
| 数据源 | 用户自己维护 | 我们维护，实时更新 |
| 运维 | 自己管数据库 | 零运维 |
| 适用人群 | 有技术能力的团队 | 不想搭数据 Pipeline 的个人/团队 |

GitHub: [https://github.com/Allan1900/stockpulse-sdk](https://github.com/Allan1900/stockpulse-sdk)

> ⚠️ 自部署版本默认绑定 localhost，仅限本地访问。如需对外暴露，请配置反向代理和 HTTPS。

---

## 一点背景

这个工具的背后，是一套跑了半年的 A 股数据 Pipeline。

每天收盘后自动拉取 20+ 个数据接口，覆盖日线、资金流向、财务数据、北向资金、龙虎榜、宏观指标。处理了无数次 schema 漂移、断点续传、限流调度、分区表优化。到现在积累了 3400万+ 行数据。

但我发现数据躺在数据库里并不值钱。**Agent 才是最好的数据查询接口。** 所以我把数据库和 Agent 之间的那一层封装开源了。

如果你也在做金融 + AI 方向的东西，欢迎来 GitHub 聊。

---

*觉得有用的话，点个 ⭐ 再走。*