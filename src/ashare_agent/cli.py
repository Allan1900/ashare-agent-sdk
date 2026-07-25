"""CLI — ashare-agent command line interface."""

import sys
import click

from .config import get_settings
from .engine import (
    query_daily, query_daily_basic, query_moneyflow,
    query_financial, query_industry_performance,
    query_hsgt, query_hsgt_top, query_top_list, query_macro,
    search_stocks, screen_stocks,
)
from .utils import extract_code, detect_query_type, extract_days, fmt_df


@click.group()
def cli():
    """ashare-agent — AI Agent-native A-share data tool."""
    pass


@cli.command()
@click.argument("text", required=False, default="")
@click.option("--code", "-c", help="Stock code (e.g. 000001.SZ)")
@click.option("--days", "-d", type=int, default=20, help="Number of trading days")
def query(text, code, days):
    """Query A-share data using natural language."""
    q = text or click.get_text_stream("stdin").read().strip()
    if not q and not code:
        click.echo("Usage: ashare-agent query \"宁德时代最近5个交易日\"")
        click.echo("       ashare-agent query --code 000001.SZ --days 5")
        sys.exit(1)

    ts_code = code or extract_code(q)
    qtype = detect_query_type(q) if q else "daily"
    days_val = extract_days(q) if q else days

    try:
        if qtype == "daily" and ts_code:
            df = query_daily(ts_code, days_val)
        elif qtype == "moneyflow" and ts_code:
            df = query_moneyflow(ts_code, days_val)
        elif qtype == "financial" and ts_code:
            df = query_financial(ts_code)
        elif qtype == "industry":
            df = query_industry_performance()
        elif qtype == "hsgt":
            df = query_hsgt(days_val)
        elif qtype == "top_list":
            from .utils import extract_trade_date
            td = extract_trade_date(q)
            if td:
                df = query_top_list(td)
            else:
                click.echo("请提供日期，如：龙虎榜 20260724")
                sys.exit(1)
        elif qtype == "macro":
            macro_type = "cpi"
            for kw in ["cpi", "ppi", "pmi", "gdp", "m2", "shibor", "lpr"]:
                if kw in q.lower():
                    macro_type = kw
                    break
            df = query_macro(macro_type)
        elif qtype == "screen":
            import re
            pe_max = None; pb_max = None; roe_min = None
            m = re.search(r"pe<\s*(\d+)", q.lower())
            if m: pe_max = float(m.group(1))
            m = re.search(r"pb<\s*(\d+)", q.lower())
            if m: pb_max = float(m.group(1))
            m = re.search(r"roe>\s*(\d+)", q.lower())
            if m: roe_min = float(m.group(1))
            df = screen_stocks(pe_max=pe_max, pb_max=pb_max, roe_min=roe_min)
        elif qtype == "search":
            keyword = q.replace("搜索", "").replace("查找", "").replace("找股票", "").strip()
            df = search_stocks(keyword) if keyword else None
        else:
            click.echo("无法识别查询类型。试试：")
            click.echo("  ashare-agent query \"宁德时代最近5个交易日\"")
            click.echo("  ashare-agent query \"北向资金最近10天\"")
            click.echo("  ashare-agent query \"筛选 PE<20 的股票\"")
            sys.exit(1)

        if df is not None and not df.empty:
            click.echo(fmt_df(df))
        else:
            click.echo("无数据")

    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)


@cli.command()
def serve():
    """Start the OpenAI-compatible API server."""
    from .server import run_server
    run_server()


@cli.command()
def mcp():
    """Start the MCP protocol server."""
    from .mcp_server import run_mcp_server
    run_mcp_server()


@cli.command()
@click.option("--tier", default="free", help="Key tier: free/dev/pro")
@click.option("--limit", type=int, default=100, help="Daily request limit")
@click.option("--label", default="", help="Label for the key")
def genkey(tier, limit, label):
    """Generate a new API key."""
    from .auth import generate_key
    key = generate_key(tier=tier, daily_limit=limit, label=label)
    click.echo(f"API Key: {key}")
    click.echo(f"  Tier:   {tier}")
    click.echo(f"  Limit:  {limit}/day")
    if label:
        click.echo(f"  Label:  {label}")


@cli.command()
def keys():
    """List all API keys."""
    from .auth import list_keys
    for k in list_keys():
        click.echo(f"{k['key_id'][:20]}...  {k['tier']:6s}  "
                   f"{k['used_today']:>5d}/{k['daily_limit']:<5d}  {k['label']}")


if __name__ == "__main__":
    cli()