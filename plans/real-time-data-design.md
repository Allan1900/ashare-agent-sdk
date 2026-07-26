# StockPulse 实时行情设计方案

## 背景

当前 StockPulse 使用 PostgreSQL 存储日频数据（每日收盘后更新），**无盘中实时数据**。
竞争对手（china-stock-mcp、Ashare-MCP等）全部支持实时行情，这是我们最大的功能缺口。

## 目标

在**不增加额外付费**（优先）或**最低成本**的前提下，为 StockPulse 增加盘中实时数据能力。

---

## 方案对比

### 方案 A：Tushare Pro 实时日线（推荐 ⭐）

| 项目 | 说明 |
|------|------|
| 接口 | `pro_bar(ts_code, freq='D', start_date=today)` |
| 费用 | **¥200/月**（实时日线权限） |
| 覆盖 | 全市场 A 股实时日线（开盘后 9:30 开始更新） |
| 频次 | 每分钟50次，一次可取全市场 |
| 优点 | 数据标准化、稳定、与你现有 Tushare 生态一致 |
| 缺点 | 需额外付费 |

### 方案 B：AKShare 东方财富实时行情（零成本）

| 项目 | 说明 |
|------|------|
| 接口 | `ak.stock_zh_spot_em()` |
| 费用 | **免费** |
| 覆盖 | 全市场实时行情（最新价、涨跌幅、成交量等） |
| 频次 | 无官方限制，但实际有反爬风险 |
| 优点 | 零成本、数据丰富（含换手率、量比、市盈率等） |
| 缺点 | 网络依赖（WSL 可能超时）、可能被限流/封IP |

### 方案 C：维持现状（零成本，零改动）

当前 PG 日频数据在**非交易时段**完全够用（复盘、策略回测、财务分析）。
实时行情只在**盘中决策场景**需要。

---

## 推荐架构：混合模式

```
用户请求 → 判断当前是否交易时段 (9:30-15:00)
         │
         ├── 交易时段 → 实时通道（AKShare/Tushare）
         │                ↓
         │              直接返回实时数据（不入 PG）
         │
         └── 非交易时段 → PG 数据通道（已有实现）
                          ↓
                        查询 daily 表
```

### 交易时段判断

```python
import datetime

def is_trading_time() -> bool:
    now = datetime.datetime.now()
    # 交易日判断：周一至周五 9:30-15:00
    if now.weekday() >= 5:  # 周末
        return False
    if now.hour < 9 or (now.hour == 9 and now.minute < 30):
        return False
    if now.hour >= 15:
        return False
    return True
```

### 实时接口封装（可选方案）

```python
# 方式 A: Tushare Pro 实时日线（付费，推荐）
def get_realtime_tushare(code: str) -> pd.DataFrame:
    import tushare as ts
    pro = ts.pro_api()
    df = pro.pro_bar(ts_code=code, freq='D',
                     start_date=datetime.today().strftime('%Y%m%d'))
    return df

# 方式 B: AKShare 实时行情（免费，有网络风险）
def get_realtime_akshare(code: str) -> pd.Series:
    import akshare as ak
    df = ak.stock_zh_spot_em()  # 全市场
    row = df[df['代码'] == code[:6]]
    return row.iloc[0] if not row.empty else None
```

---

## 实施建议

| 优先级 | 方案 | 成本 | 工作量 |
|--------|------|------|--------|
| 🥇 | **先用已有 PG 数据（已实现）** | ¥0 | 0 天 |
| 🥈 | **AKShare 免费实时（风险尝试）** | ¥0 | 1 天 |
| 🥉 | Tushare 实时日线（稳定付费） | ¥200/月 | 0.5 天 |

### 推荐路径

1. **先不买付费接口** — 当前 PG 数据已覆盖复盘/回测/分析场景
2. **轻量尝试 AKShare** — 写一个 `realtime.py` 模块，交易时段走 AKShare，非交易时段走 PG。WSL 网络通就上线，不通就退回 PG
3. **如果 AKShare 不稳定** — 再评估是否买 Tushare ¥200/月实时日线

---

## 是否需要现在实施？

**我的判断：当前 PG 数据 + 每日更新已经覆盖了 StockPulse 的核心使用场景**
（复盘分析、策略研究、财务研判、指标计算）。

实时行情只在以下场景需要：
- 盘中盯盘决策
- 盘中自动告警
- 盘中量化交易

如果你目前不需要这些场景，**实时行情可以不急着做**，先把已有的能力推出去验证市场反馈。