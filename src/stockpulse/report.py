"""StockPulse AI Analysis Report Engine.

Pull all data + all 46 indicators → structured analysis report.
Rule-based cross-validation (no LLM dependency at this layer).
"""

from __future__ import annotations

import pandas as pd
import numpy as np
from datetime import datetime

from .engine import (
    query_daily, query_daily_basic, query_moneyflow,
    query_financial, query_hsgt, query_hsgt_top,
    query_industry_performance, name_to_code, search_stocks,
)
from . import indicators as ind


# ── Section builders ──────────────────────────────

def _basic_info(code: str) -> str:
    """Stock basic info: name, industry, market."""
    df = search_stocks(code[:6], 1)
    if df.empty:
        return f"**{code}**\n\n"
    r = df.iloc[0]
    return (
        f"**{r['name']}** ({r['ts_code']})\n"
        f"- 行业: {r.get('industry', '--')}\n"
        f"- 地域: {r.get('area', '--')}\n"
        f"- 上市板: {r.get('market', '--')}\n\n"
    )


def _price_action(code: str, days: int = 60) -> str:
    """Recent price trend summary."""
    df = query_daily(code, days)
    if df.empty:
        return "*无行情数据*\n\n"
    df = df.sort_values("trade_date")
    latest = df.iloc[-1]
    first = df.iloc[0]

    chg = ((latest["close"] - first["close"]) / first["close"]) * 100
    high_60 = df["high"].max()
    low_60 = df["low"].min()
    pos_from_low = ((latest["close"] - low_60) / (high_60 - low_60)) * 100 if high_60 != low_60 else 50

    lines = [
        "### 📈 近期走势\n",
        f"- 最新收盘: **{latest['close']:.2f}** ({latest['trade_date']})",
        f"- {days}日涨跌幅: **{chg:+.2f}%**",
        f"- {days}日最高: {high_60:.2f} | 最低: {low_60:.2f}",
        f"- 当前位置: 处于{ days }日区间的 **{pos_from_low:.0f}%** 分位",
        "",
    ]
    return "\n".join(lines) + "\n"


def _technical_summary(code: str) -> str:
    """All indicators → structured technical assessment."""
    df = query_daily(code, 250)
    if df.empty:
        return "*无技术数据*\n\n"
    df = df.sort_values("trade_date")
    all_ind = ind.calc_all(df)

    lines = ["### 🔬 技术指标综合分析\n"]

    # ── MA ──
    ma = all_ind.get("ma")
    if ma is not None and len(ma) > 1:
        last = ma.iloc[-1]
        prev = ma.iloc[-2]
        ma_status = []
        for p in [5, 10, 20, 60]:
            if f"ma{p}" in last.index and pd.notna(last[f"ma{p}"]):
                val = last[f"ma{p}"]
                close_val = df["close"].iloc[-1]
                above = "上方" if close_val > val else "下方"
                ma_status.append(f"MA{p}={val:.2f} (股价在其{above})")
        lines.append("**均线系统:**")
        lines.extend(f"  - {s}" for s in ma_status)
        lines.append("")

        # Cross signals
        golden = ind.check_golden_cross(code)
        death = ind.check_death_cross(code)
        if golden:
            lines.append(f"  ✅ **金叉信号**: {golden}")
        if death:
            lines.append(f"  ⚠️ **死叉信号**: {death}")
        lines.append("")

    # ── MACD ──
    macd = all_ind.get("macd")
    if macd is not None and len(macd) > 1:
        last = macd.iloc[-1]
        prev = macd.iloc[-2]
        dif_rising = last["dif"] > prev["dif"]
        macd_bull = last["dif"] > last["dea"]
        lines.append("**MACD:**")
        lines.append(f"  - DIF={last['dif']:.2f} | DEA={last['dea']:.2f}")
        lines.append(f"  - 柱状图: {last['macd']:+.2f}")
        if macd_bull and dif_rising:
            lines.append("  ✅ DIF在DEA上方且上升 → 多头趋势")
        elif not macd_bull and not dif_rising:
            lines.append("  ⚠️ DIF在DEA下方且下降 → 空头趋势")
        elif macd_bull and not dif_rising:
            lines.append("  📌 多头但DIF走平/回落 → 可能疲软")
        else:
            lines.append("  📌 空头但DIF回升 → 可能企稳")
        lines.append("")

    # ── RSI ──
    rsi = all_ind.get("rsi")
    if rsi is not None and len(rsi) > 1:
        last = rsi.iloc[-1]
        lines.append("**RSI:**")
        for p in [6, 12, 24]:
            col = f"rsi{p}"
            if col in last.index and pd.notna(last[col]):
                v = last[col]
                tag = ""
                if v > 80:
                    tag = " ⚠️超买"
                elif v < 20:
                    tag = " ✅超卖"
                elif v > 60:
                    tag = " 偏强"
                elif v < 40:
                    tag = " 偏弱"
                lines.append(f"  - RSI{p}={v:.1f}{tag}")
        lines.append("")

    # ── KDJ ──
    kdj = all_ind.get("kdj")
    if kdj is not None and len(kdj) > 1:
        last = kdj.iloc[-1]
        k_buy = last["k"] < 20 and last["j"] < 20
        k_sell = last["k"] > 80 and last["j"] > 80
        lines.append("**KDJ:**")
        lines.append(f"  - K={last['k']:.1f} D={last['d']:.1f} J={last['j']:.1f}")
        if k_buy:
            lines.append("  ✅ KDJ超卖区 → 可能反弹")
        elif k_sell:
            lines.append("  ⚠️ KDJ超买区 → 可能回调")
        else:
            lines.append("  📌 KDJ中性区间")
        lines.append("")

    # ── ADX ──
    adx = all_ind.get("adx")
    if adx is not None and len(adx) > 1:
        last = adx.iloc[-1]
        v = last.get("adx", 0)
        tag = "强趋势" if v > 40 else "中等趋势" if v > 25 else "弱趋势/盘整"
        pdi = last.get("plus_di", 0)
        mdi = last.get("minus_di", 0)
        direction = "多头" if pdi > mdi else "空头"
        lines.append("**ADX (趋势强度):**")
        lines.append(f"  - ADX={v:.1f} ({tag}) | +DI={pdi:.1f} -DI={mdi:.1f} → {direction}")
        lines.append("")

    # ── Bollinger ──
    boll = all_ind.get("boll")
    if boll is not None and len(boll) > 1:
        last = boll.iloc[-1]
        close_val = df["close"].iloc[-1]
        if close_val > last["boll_upper"]:
            bb_tag = "⚠️ 突破上轨 → 超买"
        elif close_val < last["boll_lower"]:
            bb_tag = "✅ 跌破下轨 → 超卖"
        else:
            bb_pos = (close_val - last["boll_lower"]) / (last["boll_upper"] - last["boll_lower"]) * 100
            bb_tag = f"轨道内 {bb_pos:.0f}% 分位"
        lines.append(f"**布林带:** 上轨={last['boll_upper']:.1f} 中轨={last['boll_middle']:.1f} 下轨={last['boll_lower']:.1f}")
        lines.append(f"  - 股价{bb_tag}")
        lines.append("")

    # ── ATR ──
    atr = all_ind.get("atr")
    if atr is not None and len(atr) > 1:
        v = atr["atr"].iloc[-1]
        close_val = df["close"].iloc[-1]
        atr_pct = (v / close_val) * 100 if close_val else 0
        vol_tag = "高波动" if atr_pct > 5 else "中等波动" if atr_pct > 2 else "低波动"
        lines.append(f"**ATR (波动率):** {v:.2f} ({atr_pct:.1f}% of price) → {vol_tag}")
        lines.append("")

    # ── Volume indicators ──
    obv = all_ind.get("obv")
    if obv is not None and len(obv) > 5:
        obv_rising = obv["obv"].iloc[-1] > obv["obv"].iloc[-5]
        close_rising = df["close"].iloc[-1] > df["close"].iloc[-5]
        lines.append("**量能分析:**")
        lines.append(f"  - OBV: {'上升 ✅' if obv_rising else '下降 ⚠️'}")
        if obv_rising != close_rising:
            lines.append("  - ⚠️ **量价背离**: OBV方向与股价不一致")
        lines.append("")

    # ── MFI ──
    mfi_df = all_ind.get("mfi")
    if mfi_df is not None and len(mfi_df) > 1:
        v = mfi_df["mfi"].iloc[-1]
        tag = "超买" if v > 80 else "超卖" if v < 20 else "中性"
        lines.append(f"**MFI (资金流量):** {v:.1f} → {tag}")
        lines.append("")

    # ── Patterns ──
    pat = all_ind.get("patterns")
    if pat is not None:
        active = pat[pat["active"]]
        if not active.empty:
            recent = active.tail(3)
            lines.append("**📊 近期K线形态:**")
            for _, r in recent.iterrows():
                detected = [c for c in ["doji", "hammer", "bullish_engulfing",
                                         "bearish_engulfing", "morning_star",
                                         "evening_star", "three_white", "three_black"]
                           if r.get(c, False)]
                if detected:
                    lines.append(f"  - {r['trade_date']}: {', '.join(detected)}")
            lines.append("")

    return "\n".join(lines)


def _moneyflow_analysis(code: str) -> str:
    """Fund flow + north-bound analysis."""
    lines = ["### 💰 资金流向分析\n"]

    # Individual fund flow
    mf = query_moneyflow(code, 20)
    if not mf.empty:
        mf = mf.sort_values("trade_date")
        latest = mf.iloc[-1]
        avg_net = mf["net_mf_amount"].tail(5).mean()
        recent_net = latest.get("net_mf_amount", 0)
        lines.append(f"**个股资金:** 最新净流入={recent_net:+.0f} | 5日均值={avg_net:+.0f}")
        if recent_net > 0 and recent_net > avg_net * 1.5:
            lines.append("  ✅ 资金大幅流入，强于近期均值")
        elif recent_net < 0 and recent_net < avg_net * 1.5:
            lines.append("  ⚠️ 资金大幅流出，弱于近期均值")
        else:
            lines.append("  📌 资金流向正常")
        lines.append("")

    # North-bound
    hsgt = query_hsgt(10)
    if not hsgt.empty:
        latest = hsgt.iloc[-1]
        north = latest.get("north_money", 0)
        lines.append(f"**北向资金:** 最新净流入={north:+.0f}万元")
        lines.append("")

    return "\n".join(lines)


def _financial_health(code: str) -> str:
    """Key financial metrics overview."""
    fin = query_financial(code)
    if fin.empty:
        return "*无财务数据*\n\n"
    fin = fin.sort_values("end_date")

    lines = ["### 📊 财务健康\n"]
    last = fin.iloc[-1]
    lines.append(f"**最新财报:** {last['end_date']}")
    if "eps" in last.index and pd.notna(last["eps"]):
        lines.append(f"- EPS (每股收益): {last['eps']}")
    if "roe" in last.index and pd.notna(last["roe"]):
        lines.append(f"- ROE (净资产收益率): {last['roe']:.2f}%")
    if "roa" in last.index and pd.notna(last["roa"]):
        lines.append(f"- ROA (总资产收益率): {last['roa']:.2f}%")
    if "revenue_ps" in last.index and pd.notna(last["revenue_ps"]):
        lines.append(f"- 每股营收: {last['revenue_ps']:.2f}")

    # YoY comparison
    if len(fin) >= 2:
        prev = fin.iloc[-2]
        if "eps" in last.index and "eps" in prev.index:
            if pd.notna(last["eps"]) and pd.notna(prev["eps"]) and prev["eps"] != 0:
                yoy = ((last["eps"] - prev["eps"]) / abs(prev["eps"])) * 100
                lines.append(f"- EPS同比: {yoy:+.1f}%")
        if "roe" in last.index and "roe" in prev.index:
            if pd.notna(last["roe"]) and pd.notna(prev["roe"]):
                roe_chg = last["roe"] - prev["roe"]
                lines.append(f"- ROE变化: {roe_chg:+.2f}pct")

    lines.append("")
    return "\n".join(lines)


def _composite_assessment(code: str) -> str:
    """Cross-validate all signals → unified assessment."""
    df = query_daily(code, 250)
    if df.empty:
        return "*无法综合评估*\n\n"
    df = df.sort_values("trade_date")
    ind_all = ind.calc_all(df)
    close = df["close"].iloc[-1]
    date = df["trade_date"].iloc[-1]

    signals = {"bullish": 0, "bearish": 0, "signals": []}

    # MA trend
    ma = ind_all.get("ma")
    if ma is not None and len(ma) > 1:
        l, p = ma.iloc[-1], ma.iloc[-2]
        if pd.notna(l.get("ma5")) and pd.notna(l.get("ma20")):
            if l["ma5"] > l["ma20"]:
                signals["bullish"] += 2
                signals["signals"].append("MA5 > MA20 (多头排列)")
            else:
                signals["bearish"] += 2
                signals["signals"].append("MA5 < MA20 (空头排列)")

    # MACD
    macd = ind_all.get("macd")
    if macd is not None and len(macd) > 1:
        l = macd.iloc[-1]
        if l["dif"] > l["dea"]:
            signals["bullish"] += 2
            signals["signals"].append("MACD DIF > DEA (多头)")
        else:
            signals["bearish"] += 2
            signals["signals"].append("MACD DIF < DEA (空头)")
        if l["macd"] > 0:
            signals["bullish"] += 1
        else:
            signals["bearish"] += 1

    # RSI
    rsi_df = ind_all.get("rsi")
    if rsi_df is not None and len(rsi_df) > 1:
        l = rsi_df.iloc[-1]
        if pd.notna(l.get("rsi12")):
            if l["rsi12"] > 70:
                signals["bearish"] += 1
                signals["signals"].append("RSI12 > 70 (超买)")
            elif l["rsi12"] < 30:
                signals["bullish"] += 2
                signals["signals"].append("RSI12 < 30 (超卖)")
            elif l["rsi12"] > 50:
                signals["bullish"] += 1

    # KDJ
    kdj_df = ind_all.get("kdj")
    if kdj_df is not None and len(kdj_df) > 1:
        l = kdj_df.iloc[-1]
        if pd.notna(l.get("k")):
            if l["k"] < 20:
                signals["bullish"] += 1
            elif l["k"] > 80:
                signals["bearish"] += 1

    # ADX trend strength
    adx_df = ind_all.get("adx")
    if adx_df is not None and len(adx_df) > 1:
        l = adx_df.iloc[-1]
        if pd.notna(l.get("adx")) and l["adx"] > 25:
            pdi = l.get("plus_di", 0)
            mdi = l.get("minus_di", 0)
            if pdi > mdi:
                signals["bullish"] += 2
                signals["signals"].append(f"ADX={l['adx']:.0f} +DI>{mdi:.0f} (多头趋势)")
            else:
                signals["bearish"] += 2
                signals["signals"].append(f"ADX={l['adx']:.0f} -DI>{pdi:.0f} (空头趋势)")

    # Money flow
    mf = query_moneyflow(code, 10)
    if not mf.empty:
        avg_net = mf["net_mf_amount"].tail(5).mean()
        if avg_net > 0:
            signals["bullish"] += 1
        else:
            signals["bearish"] += 1

    # Final verdict
    net = signals["bullish"] - signals["bearish"]
    if net >= 4:
        verdict = "🟢 **强烈看多**"
        confidence = "HIGH"
    elif net >= 2:
        verdict = "🟢 **看多**"
        confidence = "MEDIUM"
    elif net <= -4:
        verdict = "🔴 **强烈看空**"
        confidence = "HIGH"
    elif net <= -2:
        verdict = "🔴 **看空**"
        confidence = "MEDIUM"
    elif net >= 1:
        verdict = "🟡 **偏多**"
        confidence = "LOW"
    elif net <= -1:
        verdict = "🟡 **偏空**"
        confidence = "LOW"
    else:
        verdict = "⚪ **中性/盘整**"
        confidence = "LOW"

    lines = [
        "### 🎯 综合研判\n",
        f"**{verdict}** (置信度: {confidence})",
        f"  - 看多信号: {signals['bullish']} | 看空信号: {signals['bearish']} | 净得分: {net:+d}",
        "",
        "**关键信号:**",
    ]
    for s in signals["signals"][-6:]:
        lines.append(f"  - {s}")
    lines.append("")
    lines.append(f"*报告生成: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    lines.append("")

    return "\n".join(lines)


# ── Public API ────────────────────────────────────

def analyze(code: str, name: str | None = None) -> str:
    """Generate comprehensive analysis report for a stock.

    Args:
        code: Stock code (e.g. 300750.SZ) or name (e.g. 宁德时代)
        name: Optional stock name override
    """
    # Resolve code if name was passed
    resolved = code
    if not code.replace(".", "").isdigit():
        resolved = name_to_code(code) or code

    sections = [
        f"# 🫀 StockPulse AI 分析报告\n",
        _basic_info(resolved),
        _price_action(resolved),
        _moneyflow_analysis(resolved),
        _financial_health(resolved),
        _technical_summary(resolved),
        _composite_assessment(resolved),
    ]

    return "\n".join(sections)


def analyze_batch(codes: list[str]) -> dict[str, str]:
    """Generate reports for multiple stocks."""
    return {c: analyze(c) for c in codes}