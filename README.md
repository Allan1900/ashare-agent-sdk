# 🫀 StockPulse

**让 AI Agent 做 A 股分析——不仅仅是查数据。**  
AI Agent-native A-share financial analysis engine.

```bash
pip install stockpulse
stockpulse query "宁德时代最近5个交易日行情"
stockpulse report 宁德时代
stockpulse dashboard
```

---

## 📋 完整能力矩阵

### 一、数据查询（9 类）

| 类别 | CLI 示例 | 说明 |
|------|----------|------|
| 📈 日线行情 | `stockpulse query "宁德时代行情"` | 5529只股票，2015~至今，800万+行 |
| 💰 资金流向 | `stockpulse query "贵州茅台资金流向"` | 主力/散户/超大单净流入，890万+行 |
| 📊 财务指标 | `stockpulse query "比亚迪财务数据"` | EPS/ROE/营收/资本公积，22万+行 |
| 🏭 行业排行 | `stockpulse query "今日行业涨跌排行"` | 78个行业实时计算 |
| 🇭🇰 北向资金 | `stockpulse query "北向资金最近10天"` | ⭐ 沪深股通每日汇总 |
| 📋 龙虎榜 | `stockpulse query "龙虎榜 20260724"` | ⭐ 每日上榜明细，16万+行 |
| 🌐 宏观数据 | `stockpulse query "最新CPI数据"` | ⭐ CPI/PPI/PMI/GDP/M2/Shibor/LPR，20年 |
| 🔍 股票搜索 | `stockpulse query "搜索新能源汽车"` | 名称/代码模糊搜索 |
| 🎯 智能选股 | `stockpulse query "筛选PE<20"` | PE/PB/ROE/行业多维筛选 |

### 二、技术指标（6 大类，46 个）

```
趋势类 (12)   → MA5/10/20/60/120/250, EMA12/26/50, WMA, ADX, SAR, 金叉/死叉
动量类 (13)   → MACD, RSI6/12/24, KDJ, Williams%R, CCI, ROC, MFI, UltOsc, Aroon, BOP
量能类 (5)    → OBV, Chaikin A/D, A/D Osc
波动类 (3)    → ATR, BOLL, 布林带
形态识别 (8)   → Doji, Hammer, 吞没, 晨星, 黄昏星, 三白兵, 三乌鸦
信号检测 (3)   → 金叉, 死叉, RSI超买超卖
```

| 指标 | CLI | MCP 工具 | 说明 |
|------|-----|----------|------|
| 移动平均线 | `stockpulse indicator ma 300750.SZ` | `get_ma` | 6周期 |
| MACD | `stockpulse indicator macd 300750.SZ` | `get_macd` | DIF/DEA/柱 |
| RSI | `stockpulse indicator rsi 300750.SZ` | `get_rsi` | 6/12/24 |
| KDJ | `stockpulse indicator kdj 300750.SZ` | `get_kdj` | K/D/J |
| 布林带 | `stockpulse indicator boll 300750.SZ` | `get_boll` | 上/中/下轨 |
| 金叉/死叉 | — | `get_golden_cross` / `get_death_cross` | MA5/MA10信号 |
| RSI信号 | — | `get_rsi_signal` | 超买>80 / 超卖<20 |

### 三、AI 分析报告（⭐ 核心差异）

| 命令 | 说明 |
|------|------|
| `stockpulse report 宁德时代` | 完整分析报告 |
| `stockpulse report 300750.SZ --save` | 保存为 .md 文件 |

报告包含 **6 大模块 + 综合研判**：

```
📈 近期走势        → 趋势 + 位置分位
💰 资金流向分析    → 个股资金 + 北向资金
📊 财务健康        → EPS/ROE/ROA/同比
🔬 技术指标综合分析 → MA/MACD/RSI/KDJ/ADX/布林/ATR/量能/形态
🎯 综合研判        → 7多:2空 → 强烈看多 (HIGH置信度)
```

### 四、市场总览（新增）

| 工具 | 返回 |
|------|------|
| `get_market_overview` | 上证/深证/创业板/科创50 实时行情 |
| `get_sector_rotation` | 多周期行业涨跌幅聚合 |
| `get_stock_radar` | 估值/质量/动量/资金 四维评分 |

### 五、API 服务

**OpenAI 兼容协议**

```bash
stockpulse serve
# → http://localhost:8900
# → POST /v1/chat/completions (自然语言查询)
# → GET /v1/models
# → GET /health
```

**MCP 协议（Claude Code / Cursor）**

```bash
stockpulse mcp
# → http://localhost:8901/mcp/v1
# → GET /mcp/v1/tools/list (18 个工具)
# → POST /mcp/v1/tools/call
```

**Web Dashboard（Streamlit）**

```bash
stockpulse dashboard
# → http://localhost:8501
# 4 Tab: 智能查询 / 分析报告 / 技术指标 / 行业全景
```

### 六、快速开始

```bash
# 安装
pip install stockpulse

# 配置数据库
export STOCKPULSE_PG_URI="postgresql://user@host/db?options=-c%20search_path=ashare,public"

# 使用 CLI
stockpulse query "宁德时代最近5个交易日行情"
stockpulse query "贵州茅台资金流向"
stockpulse query "北向资金最近10天"
stockpulse indicator macd 300750.SZ
stockpulse report 宁德时代

# 启动服务
stockpulse serve      # API :8900
stockpulse mcp        # MCP :8901
stockpulse dashboard  # Web :8501
```

### 七、Docker

```bash
# 一键启动（API + PostgreSQL）
docker compose up -d

# 仅 API（外部 PG）
docker run -p 8900:8900 \
  -e STOCKPULSE_PG_URI="postgresql://user@host/db?options=-c%20search_path=ashare,public" \
  ghcr.io/Allan1900/stockpulse:latest
```

### 八、数据架构

```
数据来源: PostgreSQL (ashare schema)
更新频率: 每日收盘后自动更新
数据量:   3400万+ 行
覆盖:     2015~至今，5529只A股
```

| 表 | 行数 | 说明 |
|----|------|------|
| `daily` | 800万+ | 日线行情（分区表） |
| `daily_basic` | 1143万+ | 每日指标（PE/PB/市值） |
| `moneyflow` | 892万+ | 资金流向 |
| `fina_indicator` | 22万+ | 财务指标 |
| `hsgt_top10` | 5700+ | 北向资金十大活跃股 |
| `top_list` | 16万+ | 龙虎榜 |
| `stock_basic` | 5529 | 股票基本信息 |
| `trade_cal` | 4383+ | 交易日历 |

### 九、项目结构

```
stockpulse/
├── src/stockpulse/
│   ├── __init__.py      # 入口 + StockPulse 类
│   ├── engine.py        # 查询引擎（9数据 + 3市场工具）
│   ├── indicators.py    # 46技术指标（6大类）
│   ├── report.py        # AI分析报告（6模块+综合研判）
│   ├── server.py        # OpenAI兼容API
│   ├── mcp_server.py    # MCP协议服务器（18工具）
│   ├── cli.py           # CLI（9命令）
│   ├── dashboard.py     # Streamlit Web Dashboard（4Tab）
│   ├── auth.py          # API Key鉴权
│   ├── config.py        # 配置系统
│   └── utils.py         # 工具函数
├── Dockerfile           # 多阶段构建
├── docker-compose.yml   # 一键启动
├── docs/                # GitHub Pages
├── plans/               # 设计文档
└── pyproject.toml

GitHub: https://github.com/Allan1900/stockpulse
Pages:  https://Allan1900.github.io/stockpulse/
MCP.so: https://mcp.so (搜索 stockpulse)
```

---


## ⚖️ 数据说明 & 合规声明

StockPulse 的所有数据均来自 **公开API采集**，不涉及任何个人隐私数据或非公开数据。
本工具仅用于学术研究和数据分析目的，不构成投资建议。

## 📜 许可证

MIT