"""Buffett-style value investing analysis built on yfinance data."""

from dataclasses import dataclass, field

import pandas as pd
import yfinance as yf


@dataclass
class Criterion:
    name: str
    value: object
    passed: bool
    note: str = ""


@dataclass
class AnalysisResult:
    ticker: str
    company_name: str
    criteria: list = field(default_factory=list)
    score: int = 0
    max_score: int = 0
    verdict: str = ""
    history: pd.DataFrame = None


def _safe(d, key, default=None):
    val = d.get(key, default)
    return default if val is None else val


def _avg(series):
    series = series.dropna()
    return series.mean() if len(series) else None


def fetch_data(ticker: str):
    t = yf.Ticker(ticker)
    info = t.info or {}
    financials = t.financials if t.financials is not None else pd.DataFrame()
    balance_sheet = t.balance_sheet if t.balance_sheet is not None else pd.DataFrame()
    cashflow = t.cashflow if t.cashflow is not None else pd.DataFrame()
    history = t.history(period="5y")
    return info, financials, balance_sheet, cashflow, history


def analyze(ticker: str) -> AnalysisResult:
    info, fin, bs, cf, history = fetch_data(ticker)

    if not info or info.get("regularMarketPrice") is None and info.get("currentPrice") is None:
        raise ValueError(f"未能获取到 {ticker} 的数据，请检查代码是否正确（美股/港股代码，如 AAPL、0700.HK）")

    company_name = info.get("longName") or info.get("shortName") or ticker
    criteria = []

    # 1. ROE > 15%
    roe = _safe(info, "returnOnEquity")
    roe_pct = roe * 100 if roe is not None else None
    criteria.append(Criterion(
        "净资产收益率 ROE",
        f"{roe_pct:.1f}%" if roe_pct is not None else "N/A",
        roe_pct is not None and roe_pct > 15,
        "ROE > 15% 体现持续的盈利能力（巴菲特核心标准）",
    ))

    # 2. 毛利率稳定且较高 (> 40%)
    gross_margin = _safe(info, "grossMargins")
    gm_pct = gross_margin * 100 if gross_margin is not None else None
    criteria.append(Criterion(
        "毛利率",
        f"{gm_pct:.1f}%" if gm_pct is not None else "N/A",
        gm_pct is not None and gm_pct > 40,
        "高毛利率反映品牌/定价权护城河",
    ))

    # 3. 负债率：负债权益比 < 0.5 (即 debtToEquity < 50, yfinance以百分数表示)
    d2e = _safe(info, "debtToEquity")
    criteria.append(Criterion(
        "负债权益比",
        f"{d2e:.1f}%" if d2e is not None else "N/A",
        d2e is not None and d2e < 80,
        "低杠杆经营，财务稳健（< 80% 为佳）",
    ))

    # 4. 自由现金流为正
    fcf = _safe(info, "freeCashflow")
    criteria.append(Criterion(
        "自由现金流",
        f"{fcf/1e8:.1f}亿" if fcf is not None else "N/A",
        fcf is not None and fcf > 0,
        "持续正向自由现金流，说明业务能自我造血",
    ))

    # 5. 营业利润率 > 15%
    op_margin = _safe(info, "operatingMargins")
    op_pct = op_margin * 100 if op_margin is not None else None
    criteria.append(Criterion(
        "营业利润率",
        f"{op_pct:.1f}%" if op_pct is not None else "N/A",
        op_pct is not None and op_pct > 15,
        "高营业利润率体现成本控制与定价能力",
    ))

    # 6. PE 合理（< 25）
    pe = _safe(info, "trailingPE")
    criteria.append(Criterion(
        "市盈率 PE(TTM)",
        f"{pe:.1f}" if pe is not None else "N/A",
        pe is not None and 0 < pe < 25,
        "PE < 25 视为估值相对合理（行业不同需酌情调整）",
    ))

    # 7. PB 合理（< 5，结合高ROE可适当放宽）
    pb = _safe(info, "priceToBook")
    criteria.append(Criterion(
        "市净率 PB",
        f"{pb:.1f}" if pb is not None else "N/A",
        pb is not None and 0 < pb < 5,
        "PB 越低安全边际越大，高ROE企业可适当容忍更高PB",
    ))

    # 8. 5年营收复合增长（用history近似不准，改用financials Total Revenue趋势）
    revenue_growth = _safe(info, "revenueGrowth")
    rg_pct = revenue_growth * 100 if revenue_growth is not None else None
    criteria.append(Criterion(
        "营收增长率(同比)",
        f"{rg_pct:.1f}%" if rg_pct is not None else "N/A",
        rg_pct is not None and rg_pct > 0,
        "持续增长的营收是企业长期竞争力的体现",
    ))

    # 9. 流动比率 > 1.5
    current_ratio = _safe(info, "currentRatio")
    criteria.append(Criterion(
        "流动比率",
        f"{current_ratio:.2f}" if current_ratio is not None else "N/A",
        current_ratio is not None and current_ratio > 1.5,
        "短期偿债能力充足（> 1.5 较安全）",
    ))

    score = sum(1 for c in criteria if c.passed)
    max_score = len(criteria)

    if score >= max_score * 0.75:
        verdict = "值得长期关注 —— 基本面符合大多数巴菲特式价值投资标准"
    elif score >= max_score * 0.5:
        verdict = "中性 —— 部分指标达标，建议结合行业与估值进一步研究"
    else:
        verdict = "暂不建议 —— 多数核心指标未达到价值投资标准"

    return AnalysisResult(
        ticker=ticker,
        company_name=company_name,
        criteria=criteria,
        score=score,
        max_score=max_score,
        verdict=verdict,
        history=history,
    )
