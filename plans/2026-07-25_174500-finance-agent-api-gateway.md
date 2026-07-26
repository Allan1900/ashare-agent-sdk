# 🏦 金融数据 Agent API 网关 — 详细规划方案

> **路线：** 路径 A（GitHub 开源 + 技术社区 SEO → 商业化）
> **细分：** 路线 2（金融 API 聚合网关）
> **定位：** "第一个原生支持 AI Agent 的 A 股数据基础设施"

---

## 一、项目愿景

### 一句话定位

> **让任何 AI Agent（Claude Code、Cursor、OpenClaw、Codex）用自然语言就能查 A 股数据。**

### 核心价值

| 痛点 | 现有方案 | 我们的方案 |
|------|---------|-----------|
| 量化数据接口（Tushare/AkShare） | Python 代码调用，Agent 无法直接使用 | **OpenAI 兼容 API + MCP 协议**，Agent 零适配 |
| 数据与 AI 割裂 | 查数据一个工具，分析另一个工具 | Agent 在同一个对话中查数据+分析+出报告 |
| 分钟级数据 | 日频更新，盘中只有 Level-2 付费 | **分钟级 Pipeline**，收盘后全市场数据就绪 |
| 金融 API 聚合 | 通用聚合站没有金融数据 | 垂直金融数据 + LLM API 可组合调用 |

---

## 二、现有资产盘点（可直接复用）

| 资产 | 状态 | 用途 |
|------|------|------|
| **ashare Python 包** | ✅ 已发布 0.1.0 | 底层数据引擎 |
| **FastAPI REST API** | ✅ 已实现 11 个端点 | 基础 API 层 |
| **PostgreSQL 5.8GB / 3400万行** | ✅ 迁移完成 | 核心数据仓库 |
| **daily_update.py 定时 Pipeline** | ✅ crontab 每日运行 | 数据持续更新 |
| **Streamlit Dashboard 14页** | ✅ 完整 | 产品 Demo + 展示 |
| **Hermes Agent 技能体系** | ✅ 5+ 技能 | Agent 集成范例 |
| **14 个技术指标计算** | ✅ utils/indicators.py | 附加数据能力 |
| **智能告警引擎** | ✅ alerts.py | 差异化卖点 |
| **md2pdf 周报生成** | ✅ | 内容输出范例 |

---

## 三、产品架构

```
┌─────────────────────────────────────────────────────┐
│                  客户端 / Agent                       │
│   Claude Code · Cursor · OpenClaw · Codex · curl     │
└────────────────────┬────────────────────────────────┘
                     │ HTTP / MCP / SSE
                     ▼
┌─────────────────────────────────────────────────────┐
│               Finance Agent API Gateway               │
│                                                       │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ OpenAI 协议  │  │ Anthropic 协 │  │  MCP 协议    │ │
│  │ /v1/chat/   │  │ 议 (未来)    │  │ /mcp/        │ │
│  │ completions │  │              │  │              │ │
│  └──────┬──────┘  └──────┬───────┘  └──────┬───────┘ │
│         └───────────────┬┴──────────────────┘         │
│                         ▼                             │
│  ┌────────────────────────────────────────────────┐  │
│  │             路由 & 中间件层                      │  │
│  │  Auth · Rate Limit · 用量统计 · 缓存 · 日志     │  │
│  └────────────────────┬───────────────────────────┘  │
│                       ▼                               │
│  ┌────────────────────────────────────────────────┐  │
│  │           金融数据引擎层                          │  │
│  │  ┌─────────┐ ┌──────────┐ ┌─────────┐         │  │
│  │  │ 行情数据  │ │ 财务数据  │ │ 资金流向 │         │  │
│  │  │ daily/   │ │ fina/    │ │ moneyfl/│         │  │
│  │  │ weekly/  │ │ income/  │ │ hsgt/   │         │  │
│  │  │ monthly  │ │ bs/cf    │ │         │         │  │
│  │  └─────────┘ └──────────┘ └─────────┘         │  │
│  │  ┌─────────┐ ┌──────────┐ ┌─────────┐         │  │
│  │  │ 行业数据  │ │ 龙虎榜    │ │ 宏观数据 │         │  │
│  │  │ industry │ │ lhb/     │ │ macro/  │         │  │
│  │  │         │ │ top_list │ │         │         │  │
│  │  └─────────┘ └──────────┘ └─────────┘         │  │
│  └────────────────────┬───────────────────────────┘  │
│                       ▼                               │
│  ┌────────────────────────────────────────────────┐  │
│  │          PostgreSQL · 物化视图 · 索引            │  │
│  └─────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## 四、开源策略：GitHub 仓库设计

### 仓库名

```
ashare-agent-sdk
```

### 定位

> 开源 SDK / CLI 工具，让 AI Agent 零适配获取 A 股金融数据。

### 仓库结构

```
ashare-agent-sdk/
├── README.md              # 项目定位 + 快速开始 + Demo GIF
├── LICENSE                # MIT
├── pyproject.toml         # Python 包
├── CONTRIBUTING.md
├── examples/
│   ├── claude-code-demo.md    # Claude Code 直接查询 A 股
│   ├── cursor-demo.md         # Cursor 中查询
│   ├── openclaw-skill-demo.md # OpenClaw 技能集成
│   ├── mcp-server-demo.md     # MCP 协议接入
│   └── python-sdk-demo.ipynb  # Python SDK Notebook
├── src/ashare_agent/
│   ├── __init__.py
│   ├── client.py          # OpenAI 兼容客户端封装
│   ├── mcp_server.py      # MCP 协议服务器
│   ├── cli.py             # 命令行工具
│   ├── prompts.py         # Agent 调用模板
│   └── utils.py           # 工具函数
├── docs/
│   ├── getting-started.md
│   ├── api-reference.md
│   ├── mcp-integration.md
│   ├── agent-examples.md
│   └── faq.md
├── tests/
│   └── test_client.py
└── agentskills/           # 预置 Hermes Agent Skill
    ├── ashare-stock-query.skill.md
    ├── ashare-financial-analysis.skill.md
    └── ashare-moneyflow-tracker.skill.md
```

### 差异化特征（GitHub README 头部卖点）

```markdown
# 🏦 ashare-agent-sdk

**让 AI Agent 像聊天一样查 A 股数据。**

```python
# 一句话查行情
from ashare_agent import AshareClient
client = AshareClient(api_key="your_key")
client.query("宁德时代最近5个交易日资金流向如何？")
```

✨ **特性：**
- 🔌 **OpenAI 协议兼容** — Claude Code / Cursor / Codex 直接调用
- 🔗 **MCP 协议原生支持** — 任何 MCP 兼容 Agent 即插即用
- 🐍 **Python SDK** — 一行 pip install
- ⚡ **分钟级数据** — 收盘后 30 分钟全市场就绪
- 📊 **3400万行数据** — 日线/财务/资金/行业/龙虎榜/宏观全覆盖
- 🎯 **Agent 原生** — 不是 REST API 套壳，是 Agent 友好的数据接口
```

---

## 五、分阶段实施计划

### 第 0 阶段：准备期（第 1-14 天）— 当前可立即开始

**目标：** 搭建基础设施，不对外发布

| 任务 | 内容 | 预计耗时 |
|------|------|---------|
| 0.1 | **新建 GitHub 仓库** `ashare-agent-sdk`，初始化 pyproject.toml + README | 0.5 天 |
| 0.2 | **封装 OpenAI 兼容 API 层** — 在现有 FastAPI 上增加 `/v1/chat/completions` 端点，接受自然语言 → 路由到对应金融数据查询 | 2 天 |
| 0.3 | **实现 MCP 协议服务器** — 用 Python 实现 MCP Server，暴露金融数据 tools | 2 天 |
| 0.4 | **实现 CLI 工具** — `ashare-agent query "宁德时代最近资金流向"` | 1 天 |
| 0.5 | **API Key 鉴权 + 用量统计** — 简单 Token 鉴权，记录每次调用 | 1 天 |
| 0.6 | **编写首批文档** — getting-started.md + api-reference.md | 1 天 |
| 0.7 | **内部测试** — Claude Code + Cursor + OpenClaw 各场景走通 | 1 天 |

**阶段 0 产出：** 可内部使用的完整工具链，但尚未公开

---

### 第 1 阶段：开源发布（第 15-30 天）

**目标：** GitHub 发布，技术文章铺量，获取初始 Stars

| 任务 | 内容 | 预计耗时 |
|------|------|---------|
| 1.1 | **GitHub 首版 Release v0.1.0** | 0.5 天 |
| 1.2 | **撰写第 1 篇技术文章**："让 Claude Code 直接查 A 股数据——开源了一个 Agent SDK" → 发布到 CSDN + SegmentFault + 知乎 | 1 天 |
| 1.3 | **V2EX 分享帖**："开源了一个让 AI Agent 查 A 股的工具" | 0.5 天 |
| 1.4 | **Product Hunt / 工具导航站提交** — aibase.cn、indietools.work | 0.5 天 |
| 1.5 | **撰写第 2 篇技术文章**："MCP 协议实战：用 30 行代码让 Agent 访问金融数据库" | 1 天 |
| 1.6 | **制作 README Demo GIF** — 用 terminalizer/asciinema 录制 Agent 查询过程 | 0.5 天 |
| 1.7 | **社区互动** — 回复 V2EX/知乎评论，收集反馈迭代 | 持续 |

**阶段 1 产出：** GitHub ⭐ 200-500，日访问 50-100 UV

---

### 第 2 阶段：SEO 蓄力（第 31-60 天）

**目标：** SEO 关键词开始排名，自然流量增长

| 任务 | 内容 | 预计耗时 |
|------|------|---------|
| 2.1 | **SEO 关键词研究** — 挖掘 "A股API""金融数据接口""量化数据"等词的长尾变体 | 0.5 天 |
| 2.2 | **每周 2 篇技术文章：** | 持续 |
|  | - "2026年A股金融数据API横向对比（Tushare vs AkShare vs Agent API）" | |
|  | - "用 Claude Code 做量化分析：完整教程" | |
|  | - "AI Agent 选股初体验：自然语言查询 A 股基本面" | |
|  | - "从 Tushare 迁移到 Agent API：5 分钟上手" | |
| 2.3 | **开源社区运营** — 回复 GitHub Issues，处理 PR，持续发布 Release | 持续 |
| 2.4 | **建 Landing Page** — 简单静态页（GitHub Pages/Cloudflare Pages），收邮箱做 waitlist | 1 天 |
| 2.5 | **搜索控制台提交** — 提交 sitemap 到 Google/Bing/百度 | 0.5 天 |

**阶段 2 产出：** GitHub ⭐ 500-1500，日访问 200-500 UV，开始有自然搜索流量

---

### 第 3 阶段：商业化启动（第 61-90 天）

**目标：** 推出付费 API，产生首批收入

| 任务 | 内容 | 预计耗时 |
|------|------|---------|
| 3.1 | **定价体系设计：** | 1 天 |
|  | - 免费层：100 次/天，仅 basic 数据 | |
|  | - 开发者层：¥99/月，5000 次/天，全数据 | |
|  | - 专业层：¥499/月，50000 次/天 + 企业发票 | |
|  | - 企业定制：按需报价 | |
| 3.2 | **支付接入** — 接入支付宝/微信支付（或通过 API 聚合平台代收） | 2 天 |
| 3.3 | **付费墙实现** — API Key 分级鉴权，超限返回 402 | 1 天 |
| 3.4 | **用户管理后台** — API Key 管理 + 用量看板 + 发票申请 | 2 天 |
| 3.5 | **发布 v1.0.0** — 正式商业化 Release | 0.5 天 |
| 3.6 | **客户成功案例** — 找 3-5 个早期用户写 testimonial | 持续 |

**阶段 3 产出：** 首批付费用户 10-30 个，月收入 ¥3,000-10,000

---

### 第 4 阶段：增长放大（第 91-180 天）

**目标：** 品牌效应 + 口碑传播，月收入破 5 万

| 任务 | 内容 |
|------|------|
| 4.1 | 写深度对比文章："A股量化数据基础设施 2026 全景：从 Tushare 到 Agent API" |
| 4.2 | 制作视频教程 — B站/YouTube "用 AI Agent 做 A 股量化" 系列 |
| 4.3 | 合作伙伴计划 — 与量化社区/财经自媒体合作推广 |
| 4.4 | 企业版功能 — 子账号管理、审计日志、SLA 保障、专线部署 |
| 4.5 | 拓展数据源 — 增加 Level-2、实时行情（需评估合规） |
| 4.6 | LLM API 聚合增值 — 可选叠加 LLM 调用能力（非核心，提客单价） |

**阶段 4 产出：** GitHub ⭐ 2000-5000，月收入 ¥30,000-80,000

---

## 六、OpenAI 兼容 API 设计细节

这是整个项目的核心——Agent 原生接口设计。

### `/v1/chat/completions` 端点

```python
# 请求格式（完全兼容 OpenAI API）
POST /v1/chat/completions
Authorization: Bearer ashare-xxx...

{
  "model": "ashare-data",
  "messages": [
    {"role": "user", "content": "宁德时代最近5个交易日资金流向如何？"}
  ],
  "temperature": 0.1
}
```

### 核心思路：自然语言 → 数据查询路由

```
用户输入自然语言
        │
        ▼
意图识别（规则/轻量 LLM）
        │
        ├──→ "查行情"       → SELECT FROM daily / daily_basic
        ├──→ "查财务"       → SELECT FROM fina_indicator / income / etc.
        ├──→ "查资金流向"    → SELECT FROM moneyflow / hsgt_moneyflow
        ├──→ "查行业"       → SELECT FROM industry_performance
        ├──→ "筛选股票"     → SELECT + WHERE 多条件组合
        ├──→ "查龙虎榜"     → SELECT FROM top_list
        └──→ "查宏观数据"    → SELECT FROM macro_data
```

### 关键设计决策

| 决策 | 选择 | 理由 |
|------|------|------|
| 内置 LLM 还是外部 LLM？ | **外部 LLM**（用户自带或可选配） | 避免垫付 LLM 成本，聚焦数据价值 |
| 自然语言→SQL 还是预定义路由？ | **混合**：高频用预定义路由，复杂用 NL→SQL | 简单查询快且准，复杂查询灵活 |
| 协议选型 | **OpenAI /v1/chat/completions** + **MCP** | OpenAI 最广泛兼容，MCP 是 Agent 原生协议 |

### 预置 Agent Skill

设计一套 Hermes Agent / Claude Code Skill，让用户一键安装即用：

```
# 示例：ashare-stock-query.skill
## 功能：让 Agent 具备查询 A 股数据的能力
## 配置：export ASHARE_API_KEY="your_key_here"
## 触发词：
- "查一下 [股票名] 的行情"
- "[股票名] 最近资金流向"
- "筛选 PE<20 的股票"
```

---

## 七、内容与 SEO 策略细则

### 目标关键词矩阵

| 类别 | 关键词 | 竞争度 | 优先级 |
|------|--------|--------|--------|
| **核心品牌词** | ashare agent sdk、A股 Agent API、金融数据 Agent | 低 | 🔴 P0 |
| **需求词** | A股 API 接口、免费股票数据 API、金融数据接口 Python | 中 | 🔴 P0 |
| **竞品替代词** | Tushare 替代、AkShare 替代、Tushare API 平替 | 中-高 | 🟡 P1 |
| **趋势词** | AI Agent 金融数据、MCP 金融、Claude Code 查股票 | 低 | 🟡 P1 |
| **场景词** | 量化交易数据接口、A股回测数据源、股票基本面数据 API | 中 | 🟢 P2 |
| **长尾词** | 龙虎榜数据接口 Python、北向资金 API、行业板块涨跌 API | 低 | 🟢 P2 |

### 文章内容模板

**技术教程类：**
```
标题：用 Claude Code 查 A 股行情——30 秒上手
结构：问题 → 传统方案（Tushare 代码）→ Agent 方案（自然语言）→ 对比 → 获取方式
SEO 关键词：Claude Code A股、AI Agent 股票数据
发布渠道：CSDN / SegmentFault / 知乎
```

**对比评测类：**
```
标题：2026 年 A 股数据 API 横向对比：Tushare vs AkShare vs Agent API
结构：场景 → 各方案代码示例 → 速度/易用性/Agent 兼容性打分 → 选择建议
SEO 关键词：A股数据API 对比、Tushare 替代、AkShare 平替
发布渠道：CSDN / 知乎 / 掘金
```

**实战案例类：**
```
标题：我用 Claude Code + 开源 SDK 做了一个自动选股工具
结构：背景 → 实现过程 → 完整代码 → 效果演示 → 开源地址
SEO 关键词：AI Agent 量化、自动选股、Claude Code 实战
发布渠道：知乎 / V2EX / 公众号
```

### 发布节奏

| 周次 | 文章 | 渠道 |
|------|------|------|
| W1 | "让 Claude Code 直接查 A 股数据——我开源了一个 Agent SDK" | CSDN+知乎+SF |
| W1 | V2EX 分享帖 | V2EX |
| W2 | "MCP 协议实战：30 行代码让 Agent 访问金融数据库" | CSDN+SF |
| W3 | "A股数据 API 横向对比 2026" | 知乎+CSDN+掘金 |
| W4 | "用 Claude Code 做量化分析完整教程" | 全渠道 |
| W5 | "从 Tushare 迁移到 Agent API 只需 5 分钟" | CSDN+知乎 |
| W6 | "AI Agent 选股初体验" | 知乎+公众号 |
| W7+ | 每周一篇，轮换类型 | 全渠道 |

---

## 八、定价模型

| 层级 | 价格 | 日调用量 | 数据范围 | 支持 |
|------|------|---------|---------|------|
| **免费体验** | ¥0 | 100 次/天 | 日线+基础财务 | GitHub Issues |
| **开发者版** | ¥99/月 | 5,000 次/天 | 全量数据 | 微信群 |
| **专业版** | ¥499/月 | 50,000 次/天 | 全量+高级指标 | 专属群+优先 |
| **企业版** | 按需报价 | 不限 | 全量+定制+私有部署 | SLA+发票+专人 |

**免费层设计逻辑：**
- 100 次/天足够个人开发者试用和集成测试
- 所有查询免费但限制频次，降低获客门槛
- 超过后返回 HTTP 429 + 清晰的升级引导

---

## 九、技术风险与应对

| 风险 | 概率 | 影响 | 应对 |
|------|------|------|------|
| **数据合规** | 中 | 高 | 只使用公开金融数据，不碰内幕/实时高频数据；明确数据来源声明 |
| **Tushare 上游变化** | 中 | 中 | 数据 Pipeline 本身已有 schema 漂移应对机制，确保持续可用 |
| **SEO 见效慢** | 中 | 中 | 前 3 个月主要靠技术社区直接流量，不依赖搜索引擎 |
| **GitHub 竞争** | 低 | 中 | 目前没有直接竞品（Agent 原生金融数据接口是蓝海） |
| **API 滥用/爬虫** | 中 | 中 | API Key 鉴权 + 速率限制 + 用量监控告警 |
| **服务器成本** | 低 | 低 | 初期 PG 已运行，增量成本极低（仅带宽） |

---

## 十、成功指标（OKR）

### 前 30 天（阶段 1）

| 指标 | 目标 |
|------|------|
| GitHub ⭐ | 300+ |
| 技术文章 | 3 篇 |
| 社区讨论（V2EX/知乎） | 5+ 帖子 |
| 日 API 调用量 | 500+ |

### 前 90 天（阶段 3）

| 指标 | 目标 |
|------|------|
| GitHub ⭐ | 1500+ |
| 付费用户 | 30+ |
| 月收入 | ¥10,000+ |
| 日 API 调用量 | 10,000+ |
| SEO 关键词排名（前 5） | 3+ |

### 前 180 天（阶段 4）

| 指标 | 目标 |
|------|------|
| GitHub ⭐ | 5000+ |
| 付费用户 | 200+ |
| 月收入 | ¥50,000+ |
| 月活开发者 | 500+ |

---

## 十一、立即可以开始的 3 件事

基于您已有的基础设施，以下 **今天就可以开始**：

### 🔴 第一件事：封装 OpenAI 兼容端点（1-2 小时）

在现有 FastAPI `server.py` 中新增 `/v1/chat/completions` 端点：

```python
@app.post("/v1/chat/completions")
async def chat_completions(request: dict):
    """OpenAI 兼容的聊天补全端点——金融数据查询"""
    messages = request.get("messages", [])
    last_msg = messages[-1]["content"] if messages else ""

    # 自然语言 → 数据查询
    if "资金流向" in last_msg or "北向" in last_msg:
        data = query_moneyflow(extract_code(last_msg))
    elif "行情" in last_msg or "收盘" in last_msg or "涨跌" in last_msg:
        data = query_daily(extract_code(last_msg))
    elif "财务" in last_msg or "营收" in last_msg or "利润" in last_msg:
        data = query_financial(extract_code(last_msg))
    else:
        data = {"message": "未能识别的查询类型，试试：查行情/查资金流向/查财务"}

    return {
        "id": "chatcmpl-ashare-xxx",
        "object": "chat.completion",
        "model": "ashare-data",
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": format_data(data)},
            "finish_reason": "stop"
        }]
    }
```

### 🟡 第二件事：创建 GitHub 仓库骨架（0.5 小时）

```bash
mkdir -p ~/projects/ashare-agent-sdk
cd ~/projects/ashare-agent-sdk
git init
# 创建 README.md + pyproject.toml + src/ashare_agent/client.py
```

### 🟢 第三件事：发第一篇技术文章预热（1 小时）

在知乎/CSDN 发布《让 Claude Code 查 A 股数据——开源了一个 Agent SDK》，不一定要等代码写完，先讲思路和 Demo，收集反馈。

---

## 十二、关键原则

1. **先开源后商业化** — 用开源建立信任和社区，再用付费 API 变现
2. **Agent 原生 ≠ REST API 套壳** — 接口设计从 Agent 的使用习惯出发（自然语言入参、结构化返回、错误信息友好）
3. **垂类 > 通用** — 不做第 41 个 API 聚合站，做第一个 Agent 原生金融数据接口
4. **内容即增长** — 每篇技术文章 = 长期 SEO 流量，比付费广告 ROI 高 10 倍
5. **你已有的就是最大的护城河** — 3400 万行 A 股数据 + 每日更新的 Pipeline，后来者至少 6 个月才能追平