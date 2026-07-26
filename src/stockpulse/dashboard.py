"""
StockPulse Web Dashboard — Streamlit app.

Usage:
    stockpulse dashboard
    streamlit run src/stockpulse/dashboard.py
"""

import sys
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# ── Page config ────────────────────────────────────
st.set_page_config(
    page_title="StockPulse",
    page_icon="🫀",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Brand theme ────────────────────────────────────
DARK_NAVY = "#1a365d"
MID_NAVY = "#2a4a7f"
ACCENT = "#3b82f6"
BG_LIGHT = "#f0f4f8"

st.markdown(f"""
<style>
    .stApp {{ background: {BG_LIGHT}; }}
    h1, h2, h3 {{ color: {DARK_NAVY} !important; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 0; }}
    .stTabs [data-baseweb="tab"] {{
        background: {MID_NAVY}; color: white; border-radius: 8px 8px 0 0;
        padding: 8px 20px; margin-right: 2px;
    }}
    .stTabs [aria-selected="true"] {{ background: {DARK_NAVY} !important; }}
    .report-box {{
        background: white; border-radius: 12px; padding: 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 16px;
    }}
    .metric-card {{
        background: white; border-radius: 10px; padding: 16px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04); text-align: center;
    }}
</style>
""", unsafe_allow_html=True)


# ── Imports (lazy to avoid startup delays) ─────────
def get_engine():
    from stockpulse.engine import (
        query_daily, query_daily_basic, query_moneyflow,
        query_financial, query_industry_performance,
        query_hsgt, query_hsgt_top, query_top_list, query_macro,
        search_stocks, screen_stocks, name_to_code,
    )
    return {
        "daily": query_daily, "basic": query_daily_basic,
        "mf": query_moneyflow, "fin": query_financial,
        "ind": query_industry_performance,
        "hsgt": query_hsgt, "hsgt_top": query_hsgt_top,
        "top_list": query_top_list, "macro": query_macro,
        "search": search_stocks, "screen": screen_stocks,
        "n2c": name_to_code,
    }


def get_indicators():
    from stockpulse.indicators import (
        calc_ma, calc_macd, calc_rsi, calc_kdj, calc_boll, calc_all,
    )
    return {"ma": calc_ma, "macd": calc_macd, "rsi": calc_rsi,
            "kdj": calc_kdj, "boll": calc_boll, "all": calc_all}


def get_report():
    from stockpulse.report import analyze
    return analyze


# ── Header ─────────────────────────────────────────
col1, col2 = st.columns([1, 5])
with col1:
    st.markdown("<h1 style='margin:0'>🫀</h1>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<h1 style='margin:0; color:{DARK_NAVY}'>StockPulse</h1>",
                unsafe_allow_html=True)
    st.caption("AI Agent-native A-share Financial Analysis Engine")

# ── Tabs ───────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(
    ["🔍 智能查询", "📊 分析报告", "📈 技术指标", "🏭 行业全景"]
)

# ════════════════════════════════════════════════════
# TAB 1 — 智能查询
# ════════════════════════════════════════════════════
with tab1:
    st.markdown("### 🔍 智能查询")
    st.caption("输入自然语言查询 A 股数据，例如：")

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.code("宁德时代最近5个交易日行情")
    with col_b:
        st.code("贵州茅台资金流向")
    with col_c:
        st.code("比亚迪财务数据")

    query_text = st.text_input("查询", placeholder="输入查询内容…",
                               label_visibility="collapsed")

    if query_text:
        from stockpulse.server import _resolve_code, _route_query
        with st.spinner("查询中…"):
            try:
                # Try the full route first
                result = _route_query(query_text)
                st.markdown(f'<div class="report-box">{result}</div>',
                            unsafe_allow_html=True)
            except Exception as e:
                st.error(f"查询出错: {e}")
    else:
        st.info("输入查询内容开始探索")

# ════════════════════════════════════════════════════
# TAB 2 — 分析报告
# ════════════════════════════════════════════════════
with tab2:
    st.markdown("### 📊 AI 分析报告")
    st.caption("输入股票名称或代码，生成完整分析报告")

    code_input = st.text_input("股票", placeholder="例如：宁德时代 或 300750.SZ",
                               label_visibility="collapsed",
                               key="report_code")

    if code_input:
        analyze = get_report()
        with st.spinner("正在生成分析报告（拉取数据 + 计算46个指标 + 综合研判）…"):
            try:
                report_md = analyze(code_input)
                st.markdown(f'<div class="report-box">{report_md}</div>',
                            unsafe_allow_html=True)
            except Exception as e:
                st.error(f"报告生成失败: {e}")

# ════════════════════════════════════════════════════
# TAB 3 — 技术指标
# ════════════════════════════════════════════════════
with tab3:
    st.markdown("### 📈 技术指标")
    st.caption("选择股票和指标类型，查看交互式图表")

    col_code, col_ind, col_days = st.columns([2, 2, 1])
    with col_code:
        code_ind = st.text_input("股票代码", "300750.SZ",
                                 label_visibility="collapsed",
                                 placeholder="股票代码").strip().upper()
    with col_ind:
        ind_type = st.selectbox("指标", ["MA", "MACD", "RSI", "KDJ", "BOLL"],
                                label_visibility="collapsed")
    with col_days:
        days = st.number_input("天数", 30, 500, 120, 10,
                               label_visibility="collapsed")

    if code_ind and ind_type:
        eng = get_engine()
        ind = get_indicators()

        with st.spinner("计算指标中…"):
            df = eng["daily"](code_ind, days)
            if df.empty:
                st.warning(f"无数据: {code_ind}")
            else:
                df = df.sort_values("trade_date")
                fig = None

                if ind_type == "MA":
                    r = ind["ma"](df)
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df["trade_date"], y=df["close"],
                                              name="收盘价", line=dict(color="#1a365d")))
                    for c in ["ma5", "ma10", "ma20", "ma60"]:
                        if c in r.columns:
                            fig.add_trace(go.Scatter(x=df["trade_date"], y=r[c],
                                                      name=c.upper(),
                                                      line=dict(dash="dot")))
                    fig.update_layout(title=f"{code_ind} 均线系统", height=500)

                elif ind_type == "MACD":
                    r = ind["macd"](df)
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df["trade_date"], y=r["dif"],
                                              name="DIF", line=dict(color="#3b82f6")))
                    fig.add_trace(go.Scatter(x=df["trade_date"], y=r["dea"],
                                              name="DEA", line=dict(color="#ef4444")))
                    colors = ["#22c55e" if v >= 0 else "#ef4444" for v in r["macd"]]
                    fig.add_trace(go.Bar(x=df["trade_date"], y=r["macd"],
                                          name="MACD柱", marker_color=colors))
                    fig.update_layout(title=f"{code_ind} MACD", height=500)

                elif ind_type == "RSI":
                    r = ind["rsi"](df)
                    fig = go.Figure()
                    for c in ["rsi6", "rsi12", "rsi24"]:
                        if c in r.columns:
                            fig.add_trace(go.Scatter(x=df["trade_date"], y=r[c],
                                                      name=c.upper()))
                    fig.add_hline(y=80, line_dash="dash", line_color="red",
                                   annotation_text="超买")
                    fig.add_hline(y=20, line_dash="dash", line_color="green",
                                   annotation_text="超卖")
                    fig.update_layout(title=f"{code_ind} RSI", height=500,
                                      yaxis_range=[0, 100])

                elif ind_type == "KDJ":
                    r = ind["kdj"](df)
                    fig = go.Figure()
                    for c in ["k", "d", "j"]:
                        fig.add_trace(go.Scatter(x=df["trade_date"], y=r[c],
                                                  name=c.upper()))
                    fig.update_layout(title=f"{code_ind} KDJ", height=500)

                elif ind_type == "BOLL":
                    r = ind["boll"](df)
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df["trade_date"], y=df["close"],
                                              name="收盘价", line=dict(color="#1a365d")))
                    fig.add_trace(go.Scatter(x=df["trade_date"], y=r["boll_upper"],
                                              name="上轨", line=dict(dash="dot", color="#ef4444")))
                    fig.add_trace(go.Scatter(x=df["trade_date"], y=r["boll_middle"],
                                              name="中轨", line=dict(dash="dot", color="#3b82f6")))
                    fig.add_trace(go.Scatter(x=df["trade_date"], y=r["boll_lower"],
                                              name="下轨", line=dict(dash="dot", color="#22c55e")))
                    fig.update_layout(title=f"{code_ind} 布林带", height=500)

                if fig:
                    fig.update_layout(template="plotly_white",
                                      hovermode="x unified",
                                      margin=dict(l=40, r=40, t=40, b=40))
                    st.plotly_chart(fig, width='stretch')

# ════════════════════════════════════════════════════
# TAB 4 — 行业全景
# ════════════════════════════════════════════════════
with tab4:
    st.markdown("### 🏭 行业全景")
    st.caption("各行业实时涨跌排行")

    eng = get_engine()
    with st.spinner("加载行业数据…"):
        df_ind = eng["ind"]()

    if df_ind is None or df_ind.empty:
        st.warning("无行业数据")
    else:
        # Heatmap-style bar chart
        df_ind = df_ind.sort_values("avg_change", ascending=True)
        colors = ["#ef4444" if v < 0 else "#22c55e" for v in df_ind["avg_change"]]

        fig = go.Figure(go.Bar(
            x=df_ind["avg_change"],
            y=df_ind["industry"],
            orientation="h",
            marker_color=colors,
            text=df_ind["avg_change"].round(2),
            textposition="outside",
        ))
        fig.update_layout(
            title="行业涨跌幅排行",
            height=max(400, len(df_ind) * 22),
            xaxis_title="涨跌幅 %",
            template="plotly_white",
            margin=dict(l=10, r=50, t=40, b=10),
        )
        st.plotly_chart(fig, width='stretch')

        # Data table
        with st.expander("查看完整数据"):
            display_df = df_ind.sort_values("avg_change", ascending=False).rename(columns={
                "industry": "行业", "stock_count": "股票数",
                "avg_change": "平均涨跌幅%",
            })
            st.dataframe(display_df, width='stretch', hide_index=True)

# ── Footer ─────────────────────────────────────────
st.divider()
st.caption(f"🫀 StockPulse v0.3.0 · 数据来源: PostgreSQL · "
           f"报告生成: {datetime.now():%Y-%m-%d %H:%M}")