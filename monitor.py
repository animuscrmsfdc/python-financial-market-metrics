#!/usr/bin/env python3
"""Daily market signal monitor — value investing entry signals.

Usage:
    python3 monitor.py
"""

import io
from datetime import date
import requests
import yfinance as yf
import pandas as pd
from bs4 import BeautifulSoup

INDEXES = {
    "S&P 500":      "^GSPC",
    "NASDAQ 100":   "^NDX",
    "Dow Jones":    "^DJI",
    "Russell 2000": "^RUT",
}

VIX_TICKER   = "^VIX"
TNX_TICKER   = "^TNX"
W5000_TICKER = "^W5000"
GOLD_TICKER  = "GC=F"    # COMEX Gold Futures
OIL_TICKER   = "CL=F"    # WTI Crude Futures
TRANCHES     = [15, 20, 25, 30, 35, 40]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}

GREEN_MIN = 7
AMBER_MIN = 4


# ── Scoring ───────────────────────────────────────────────────────────────────

def bucket(score):
    if score is None:      return "N/A"
    if score >= GREEN_MIN: return "GREEN"
    if score >= AMBER_MIN: return "AMBER"
    return "RED"


def score_vix(v):
    if v >= 40: return 10
    if v >= 30: return 8
    if v >= 20: return 5
    if v >= 15: return 3
    return 1


def score_cape(c):
    if c < 15:  return 10
    if c < 20:  return 8
    if c < 25:  return 5
    if c < 35:  return 2
    return 0


def score_cnn_fg(fg):
    if fg <= 25: return 10
    if fg <= 40: return 7
    if fg <= 60: return 5
    if fg <= 75: return 3
    return 1


def score_sp_vs_200ma(pct):
    if pct <= -15: return 10
    if pct <= -10: return 8
    if pct <=  -5: return 6
    if pct <=   0: return 5
    if pct <=  10: return 3
    if pct <=  20: return 2
    return 1


def score_hy_spread(pct):
    if pct >= 7.0: return 10
    if pct >= 5.0: return 8
    if pct >= 4.0: return 6
    if pct >= 3.0: return 4
    if pct >= 2.0: return 2
    return 1


def score_buffett(pct):
    if pct < 80:  return 10
    if pct < 100: return 8
    if pct < 120: return 6
    if pct < 150: return 4
    if pct < 200: return 2
    return 1


def score_avg_drawdown(avg_pct_drop):
    if avg_pct_drop >= 35: return 10
    if avg_pct_drop >= 25: return 8
    if avg_pct_drop >= 20: return 7
    if avg_pct_drop >= 15: return 5
    if avg_pct_drop >= 10: return 3
    if avg_pct_drop >=  5: return 2
    return 1


def score_gold_vs_200ma(pct):
    # Gold above 200MA = uptrend = flight-to-safety = fear = confirms equity buy climate
    if pct >= 20: return 8
    if pct >= 10: return 6
    if pct >=  0: return 4
    if pct >= -5: return 3
    return 1


def score_unemployment(pct):
    if pct >= 8.0: return 9
    if pct >= 6.0: return 7
    if pct >= 5.0: return 5
    if pct >= 4.0: return 3
    return 1


def score_delinquency(pct):
    if pct >= 5.0: return 10
    if pct >= 4.0: return 8
    if pct >= 3.0: return 6
    if pct >= 2.0: return 4
    if pct >= 1.5: return 2
    return 1


# ── Labels ────────────────────────────────────────────────────────────────────

def label_vix(v):
    if v >= 40: return "Extreme Fear"
    if v >= 30: return "Fear"
    if v >= 20: return "Caution"
    if v >= 15: return "Normal"
    return "Complacency"


def label_cape(c):
    if c < 15:  return "Undervalued"
    if c < 20:  return "Fair Value"
    if c < 25:  return "Elevated"
    if c < 35:  return "Overvalued"
    return "Extreme Bubble"


def label_cnn_fg(fg):
    if fg <= 25: return "Extreme Fear"
    if fg <= 40: return "Fear"
    if fg <= 60: return "Neutral"
    if fg <= 75: return "Greed"
    return "Extreme Greed"


def label_sp_200ma(pct):
    if pct <=  -5: return f"Below 200MA ({pct:+.1f}%)"
    if pct <=   0: return f"Just below 200MA ({pct:+.1f}%)"
    if pct <=  10: return f"Above 200MA ({pct:+.1f}%)"
    return f"Extended above 200MA ({pct:+.1f}%)"


def label_hy_spread(pct):
    if pct >= 7.0: return f"Extreme Stress ({pct:.2f}%)"
    if pct >= 5.0: return f"High Stress ({pct:.2f}%)"
    if pct >= 4.0: return f"Elevated ({pct:.2f}%)"
    if pct >= 3.0: return f"Normal ({pct:.2f}%)"
    return f"Low / Complacent ({pct:.2f}%)"


def label_buffett(pct):
    if pct < 80:  return f"Undervalued ({pct:.0f}%)"
    if pct < 100: return f"Fair Value ({pct:.0f}%)"
    if pct < 120: return f"Modestly Overvalued ({pct:.0f}%)"
    if pct < 150: return f"Overvalued ({pct:.0f}%)"
    if pct < 200: return f"Significantly Overvalued ({pct:.0f}%)"
    return f"Extreme Bubble ({pct:.0f}%)"


def label_gold_vs_200ma(pct):
    if pct >= 20: return f"Strong uptrend ({pct:+.1f}% vs 200MA)"
    if pct >= 10: return f"Uptrend ({pct:+.1f}% vs 200MA)"
    if pct >=  0: return f"Mild uptrend ({pct:+.1f}% vs 200MA)"
    if pct >= -5: return f"Near 200MA ({pct:+.1f}%)"
    return f"Below 200MA ({pct:+.1f}%)"


def label_unemployment(pct):
    if pct >= 8.0: return f"Recession-level ({pct:.1f}%)"
    if pct >= 6.0: return f"Elevated ({pct:.1f}%)"
    if pct >= 5.0: return f"Moderately elevated ({pct:.1f}%)"
    if pct >= 4.0: return f"Normal ({pct:.1f}%)"
    return f"Low / tight labor ({pct:.1f}%)"


def label_delinquency(pct):
    if pct >= 5.0: return f"Crisis-level stress ({pct:.2f}%)"
    if pct >= 4.0: return f"High stress ({pct:.2f}%)"
    if pct >= 3.0: return f"Elevated ({pct:.2f}%)"
    if pct >= 2.0: return f"Normal ({pct:.2f}%)"
    return f"Low / healthy ({pct:.2f}%)"


def label_oil(price):
    if price > 100: return "Elevated — inflation risk"
    if price >  80: return "Normal-high"
    if price >  60: return "Normal"
    if price >  45: return "Weak — demand concern"
    return "Very low — recession signal"


# ── Data fetchers ─────────────────────────────────────────────────────────────

def fetch_yf_last_close(ticker, period="5d"):
    try:
        hist = yf.Ticker(ticker).history(period=period)
        return float(hist["Close"].iloc[-1]) if not hist.empty else None
    except Exception:
        return None


def fetch_ath_and_current(ticker_sym, period="5y"):
    try:
        hist = yf.Ticker(ticker_sym).history(period=period)
        if hist.empty:
            return None, None
        return float(hist["High"].max()), float(hist["Close"].iloc[-1])
    except Exception:
        return None, None


def fetch_cape():
    try:
        r = requests.get(
            "https://www.multpl.com/shiller-pe/table/by-month",
            timeout=10, headers=HEADERS
        )
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("table", {"id": "datatable"})
        if table:
            for row in table.find_all("tr")[1:]:
                cells = row.find_all("td")
                if len(cells) >= 2:
                    return float(cells[1].get_text(strip=True).replace(",", ""))
    except Exception:
        pass
    return None


def fetch_cnn_fear_greed():
    try:
        r = requests.get(
            "https://production.dataviz.cnn.io/index/fearandgreed/graphdata",
            timeout=10,
            headers={**HEADERS,
                     "Referer": "https://www.cnn.com/markets/fear-and-greed",
                     "Origin":  "https://www.cnn.com"}
        )
        r.raise_for_status()
        return float(r.json()["fear_and_greed"]["score"])
    except Exception:
        return None


def fetch_sp500_vs_200ma():
    try:
        hist = yf.Ticker("^GSPC").history(period="1y")
        if len(hist) < 50:
            return None
        ma200   = hist["Close"].rolling(200).mean().iloc[-1]
        current = hist["Close"].iloc[-1]
        return (current - ma200) / ma200 * 100
    except Exception:
        return None


def fetch_hy_spread():
    try:
        r = requests.get(
            "https://fred.stlouisfed.org/graph/fredgraph.csv?id=BAMLH0A0HYM2",
            timeout=10
        )
        r.raise_for_status()
        df = pd.read_csv(io.StringIO(r.text), names=["date", "spread"], header=0)
        df = df[df["spread"] != "."]
        return float(df["spread"].iloc[-1])
    except Exception:
        return None


def fetch_gold_vs_200ma():
    try:
        hist = yf.Ticker(GOLD_TICKER).history(period="1y")
        if len(hist) < 50:
            return None
        ma200   = hist["Close"].rolling(200).mean().iloc[-1]
        current = hist["Close"].iloc[-1]
        return (current - ma200) / ma200 * 100
    except Exception:
        return None


def fetch_fred_series(series_id):
    try:
        r = requests.get(
            f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}",
            timeout=10
        )
        r.raise_for_status()
        df = pd.read_csv(io.StringIO(r.text), names=["date", "value"], header=0)
        df = df[df["value"] != "."]
        return float(df["value"].iloc[-1])
    except Exception:
        return None


def fetch_unemployment():
    return fetch_fred_series("UNRATE")


def fetch_delinquency_rate():
    return fetch_fred_series("DRALACBN")


def fetch_oil_price():
    return fetch_yf_last_close(OIL_TICKER)


def fetch_buffett_indicator():
    try:
        w5000 = fetch_yf_last_close(W5000_TICKER, period="5d")
        r = requests.get(
            "https://fred.stlouisfed.org/graph/fredgraph.csv?id=GDP",
            timeout=10
        )
        r.raise_for_status()
        df = pd.read_csv(io.StringIO(r.text), names=["date", "gdp"], header=0)
        df = df[df["gdp"] != "."]
        gdp_b = float(df["gdp"].iloc[-1])
        if w5000 and gdp_b:
            return w5000 / gdp_b * 100
    except Exception:
        pass
    return None


# ── Helpers ───────────────────────────────────────────────────────────────────

def drop_pct(current, ath):
    return ((ath - current) / ath) * 100


def tranche_info(pct_drop):
    triggered = [t for t in TRANCHES if pct_drop >= t]
    next_t    = next((t for t in TRANCHES if pct_drop < t), None)
    return triggered, next_t


def progress_bar(score, width=10):
    if score is None:
        return "?" * width
    filled = round(score / 10 * width)
    return "█" * filled + "░" * (width - filled)


BUCKET_SYMBOL = {"GREEN": "●", "AMBER": "◑", "RED": "○", "N/A": " "}


def indicator_row(name, value_str, label_str, score):
    b     = bucket(score)
    sym   = BUCKET_SYMBOL[b]
    s_str = f"{score:2d}/10" if score is not None else "  N/A"
    return f"  {sym} {name:<28}  {value_str:<12}  {label_str:<32}  {s_str}  {b}"


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    today = date.today().strftime("%Y-%m-%d")
    sep   = "=" * 76
    print(f"\n{sep}")
    print(f"  DAILY MARKET MONITOR — {today}")
    print(f"{sep}\n")

    # Fetch
    vix      = fetch_yf_last_close(VIX_TICKER)
    tnx      = fetch_yf_last_close(TNX_TICKER)
    cape     = fetch_cape()
    fg       = fetch_cnn_fear_greed()
    sp_ma    = fetch_sp500_vs_200ma()
    hy       = fetch_hy_spread()
    buff     = fetch_buffett_indicator()
    gold_ma   = fetch_gold_vs_200ma()
    unemploy  = fetch_unemployment()
    delinq    = fetch_delinquency_rate()
    oil       = fetch_oil_price()

    index_data = {}
    for name, sym in INDEXES.items():
        ath, current = fetch_ath_and_current(sym)
        if ath and current:
            index_data[name] = (ath, current, drop_pct(current, ath))

    # Score
    scores = {}
    if vix      is not None: scores["VIX"]           = score_vix(vix)
    if cape     is not None: scores["CAPE"]           = score_cape(cape)
    if fg       is not None: scores["CNN Fear/Greed"] = score_cnn_fg(fg)
    if sp_ma    is not None: scores["S&P vs 200MA"]   = score_sp_vs_200ma(sp_ma)
    if hy       is not None: scores["HY Spread"]      = score_hy_spread(hy)
    if buff     is not None: scores["Buffett"]        = score_buffett(buff)
    if gold_ma  is not None: scores["Gold vs 200MA"]  = score_gold_vs_200ma(gold_ma)

    avg_drop = None
    if index_data:
        avg_drop = sum(d for _, _, d in index_data.values()) / len(index_data)
        scores["Avg Drawdown"] = score_avg_drawdown(avg_drop)

    cape_veto = cape is not None and cape > 35

    # ── Indicators table ──────────────────────────────────────────────────────
    print("── INDICATORS ───────────────────────────────────────────────────────────\n")
    hdr = f"  {'':1} {'Indicator':<28}  {'Value':<12}  {'Signal':<32}  {'Score':>6}  Bucket"
    print(hdr)
    print("  " + "─" * (len(hdr) - 2))

    rows = [
        ("VIX (Fear Index)",      vix,      lambda v: f"{v:.2f}",    label_vix,          "VIX"),
        ("CAPE / Shiller PE",     cape,     lambda v: f"{v:.1f}",    label_cape,         "CAPE"),
        ("CNN Fear & Greed",      fg,       lambda v: f"{v:.0f}/100", label_cnn_fg,      "CNN Fear/Greed"),
        ("S&P 500 vs 200-day MA", sp_ma,    lambda v: f"{v:+.1f}%",  label_sp_200ma,    "S&P vs 200MA"),
        ("HY Credit Spread",      hy,       lambda v: f"{v:.2f}%",   label_hy_spread,   "HY Spread"),
        ("Buffett Indicator",     buff,     lambda v: f"{v:.0f}%",   label_buffett,     "Buffett"),
        ("Gold vs 200-day MA",    gold_ma,  lambda v: f"{v:+.1f}%",  label_gold_vs_200ma,  "Gold vs 200MA"),
    ]

    for name, value, fmt, lbl, key in rows:
        if value is not None:
            extra = "  ⚠ VETO" if (key == "CAPE" and cape_veto) else ""
            print(indicator_row(name, fmt(value), lbl(value) + extra, scores.get(key)))
        else:
            print(indicator_row(name, "N/A", "fetch failed", None))

    # Reference-only rows (no score)
    refs = []
    if tnx     is not None: refs.append(("10Y Treasury (ref)",    f"{tnx:.2f}%",    ""))
    if oil     is not None: refs.append(("Oil WTI (ref)",         f"${oil:.2f}",    label_oil(oil)))
    if unemploy is not None: refs.append(("Unemployment (ref)",   f"{unemploy:.1f}%", label_unemployment(unemploy)))
    if delinq  is not None: refs.append(("Delinquency Rate (ref)",f"{delinq:.2f}%", label_delinquency(delinq)))
    for ref_name, ref_val, ref_lbl in refs:
        print(f"    {ref_name:<28}  {ref_val:<12}  {ref_lbl:<32}  {'--':>6}")

    print()

    # ── Index drawdowns ───────────────────────────────────────────────────────
    print("── INDEX DRAWDOWN FROM 5-YEAR ATH ───────────────────────────────────────\n")

    if index_data:
        print(f"  {'Index':<14}  {'ATH':>10}  {'Price':>10}  {'Drop':>7}  Tranches triggered")
        print("  " + "─" * 63)
        for name, (ath, current, pct) in index_data.items():
            triggered, next_t = tranche_info(pct)
            t_str    = ", ".join(f"T{t}%" for t in triggered) if triggered else "none yet"
            next_str = f"  → next: -{next_t}%" if next_t else ""
            print(f"  {name:<14}  {ath:>10,.0f}  {current:>10,.0f}  {pct:>6.1f}%  {t_str}{next_str}")
        if avg_drop is not None:
            print(f"\n  Avg drawdown: {avg_drop:.1f}%   (score: {scores.get('Avg Drawdown', 'N/A')}/10)")
    else:
        print("  N/A — index data fetch failed")

    print()

    # ── Signal buckets ────────────────────────────────────────────────────────
    print("── SIGNAL BUCKETS ───────────────────────────────────────────────────────\n")

    buckets = {"GREEN": [], "AMBER": [], "RED": []}
    for name, s in scores.items():
        b = bucket(s)
        if b in buckets:
            buckets[b].append(f"{name} ({s}/10)")

    for b in ["GREEN", "AMBER", "RED"]:
        content = "  ·  ".join(buckets[b]) if buckets[b] else "none"
        print(f"  {BUCKET_SYMBOL[b]} {b:<6}  {content}")

    print()

    # ── Overall score & verdict ───────────────────────────────────────────────
    print("── OVERALL SCORE & VERDICT ──────────────────────────────────────────────\n")

    if scores:
        composite      = sum(scores.values()) / len(scores)
        overall_bucket = bucket(composite)
        print(f"  Composite: {composite:.1f} / 10   [{progress_bar(composite)}]   {overall_bucket}")
        print(f"  Based on {len(scores)} indicators\n")
    else:
        composite      = None
        overall_bucket = "N/A"
        print("  No data available.\n")

    if cape_veto:
        print(f"  VETO — CAPE {cape:.1f} > 35 (Extreme Bubble)")
        print("  Do not deploy tranches. Wait for CAPE to fall below 35.")
    elif composite is None:
        print("  INSUFFICIENT DATA — check network and re-run.")
    elif overall_bucket == "GREEN":
        print("  *** BUY SIGNAL — Deploy next tranche ***")
        print("  See CLAUDE.md for tranche sizing and target ETFs.")
    elif overall_bucket == "AMBER":
        print("  WATCH — Mixed signals. Do not deploy until composite reaches 7+.")
    else:
        print("  WAIT — Market overvalued or complacent. Stay in cash.")

    print(f"\n{sep}\n")


if __name__ == "__main__":
    main()
