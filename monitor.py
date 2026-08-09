#!/usr/bin/env python3
"""Daily market signal monitor — value investing entry signals.

Usage:
    python3 monitor.py
    python3 monitor.py --pc 1.05
"""

import argparse
import io
from datetime import date

import requests
import yfinance as yf
import pandas as pd
from bs4 import BeautifulSoup


TRANCHES      = [15, 20, 25, 30, 35, 40]
HEADERS       = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}
GREEN_MIN     = 7
AMBER_MIN     = 4
BUCKET_SYMBOL = {"GREEN": "●", "AMBER": "◑", "RED": "○", "N/A": " "}
VERDICT_RANK  = {"RED": 2, "AMBER": 1, "GREEN": 0, "N/A": -1}


# ── Scoring ────────────────────────────────────────────────────────────────────

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


def score_put_call(pc):
    if pc >= 1.3: return 10
    if pc >= 1.1: return 7
    if pc >= 0.9: return 5
    if pc >= 0.7: return 3
    return 1


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


def score_vstoxx(v):
    if v >= 50: return 10
    if v >= 40: return 8
    if v >= 25: return 5
    if v >= 20: return 3
    return 1


# ── Labels ─────────────────────────────────────────────────────────────────────

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


def label_put_call(pc):
    if pc >= 1.3: return f"Extreme Fear ({pc:.2f})"
    if pc >= 1.1: return f"Fear / Bearish ({pc:.2f})"
    if pc >= 0.9: return f"Neutral ({pc:.2f})"
    if pc >= 0.7: return f"Bullish ({pc:.2f})"
    return f"Extreme Greed ({pc:.2f})"


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


def label_vstoxx(v):
    if v >= 50: return "Extreme Fear"
    if v >= 40: return "Fear"
    if v >= 25: return "Caution"
    if v >= 20: return "Normal"
    return "Complacency"


def label_ath_drop(pct):
    if pct >= 35: return f"-{pct:.1f}% from ATH — Extreme"
    if pct >= 25: return f"-{pct:.1f}% from ATH — Deep"
    if pct >= 20: return f"-{pct:.1f}% from ATH — Significant"
    if pct >= 15: return f"-{pct:.1f}% from ATH — Moderate"
    if pct >= 10: return f"-{pct:.1f}% from ATH — Minor"
    return f"-{pct:.1f}% from ATH"


# ── Data fetchers ──────────────────────────────────────────────────────────────

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


def fetch_index_vs_200ma(ticker):
    try:
        hist = yf.Ticker(ticker).history(period="1y")
        if len(hist) < 50:
            return None
        ma200   = hist["Close"].rolling(200).mean().iloc[-1]
        current = hist["Close"].iloc[-1]
        return (current - ma200) / ma200 * 100
    except Exception:
        return None


def fetch_buffett_indicator():
    try:
        w5000 = fetch_yf_last_close("^W5000", period="1mo")
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


def fetch_vstoxx():
    import contextlib, os
    with open(os.devnull, "w") as devnull, \
         contextlib.redirect_stdout(devnull), \
         contextlib.redirect_stderr(devnull):
        val = fetch_yf_last_close("^V2TX")
    return val if val else None


def fetch_ath_drawdown(ticker):
    ath, current = fetch_ath_and_current(ticker)
    if ath and current:
        return drop_pct(current, ath)
    return None


# ── Helpers ────────────────────────────────────────────────────────────────────

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


def indicator_row(name, value_str, label_str, score):
    b     = bucket(score)
    sym   = BUCKET_SYMBOL[b]
    s_str = f"{score:2d}/10" if score is not None else "  N/A"
    return f"  {sym} {name:<28}  {value_str:<12}  {label_str:<32}  {s_str}  {b}"


# ── Market runner ──────────────────────────────────────────────────────────────

def run_market(config):
    """
    Each config dict:
      name:             str
      indicators:       list of indicator-spec dicts (see build_*_config)
      index_tickers:    dict name->ticker  (ATH drawdown table + avg score)
      indiv_drawdowns:  list of {key, name, ticker}  (e.g. IBEX 35)
      veto_fn:          callable(raw, scores) -> str|None

    An indicator spec:
      key, name, fetch_fn, score_fn (None=ref-only), label_fn, fmt_fn

    Returns: verdict string ("GREEN"|"AMBER"|"RED"|"N/A")
    """
    mkt_name = config["name"]
    bar_len  = 72 - len(mkt_name)
    print(f"\n{'═' * 2} {mkt_name} MARKET {'═' * bar_len}\n")

    # Fetch all indicators
    fetched = {}
    for ind in config["indicators"]:
        try:
            fetched[ind["key"]] = ind["fetch_fn"]()
        except Exception:
            fetched[ind["key"]] = None

    # Fetch ATH data for index drawdown table
    index_data = {}
    for idx_name, sym in config["index_tickers"].items():
        ath, current = fetch_ath_and_current(sym)
        if ath and current:
            index_data[idx_name] = (ath, current, drop_pct(current, ath))

    # Fetch individual drawdowns (e.g. IBEX 35)
    indiv_drops = {}
    for spec in config.get("indiv_drawdowns", []):
        try:
            val = fetch_ath_drawdown(spec["ticker"])
        except Exception:
            val = None
        indiv_drops[spec["key"]] = (spec["name"], val)

    # Build raw dict for veto_fn
    raw = {**fetched, **{k: v for k, (_, v) in indiv_drops.items()}}

    # Score all scored indicators
    scores = {}
    for ind in config["indicators"]:
        if ind["score_fn"] is None:
            continue
        val = fetched[ind["key"]]
        if val is not None:
            scores[ind["key"]] = ind["score_fn"](val)

    # Avg drawdown from index table
    avg_drop = None
    if index_data:
        avg_drop = sum(d for _, _, d in index_data.values()) / len(index_data)
        scores["_avg_drawdown"] = score_avg_drawdown(avg_drop)

    # Individual drawdown scores
    for spec in config.get("indiv_drawdowns", []):
        val = indiv_drops[spec["key"]][1]
        if val is not None:
            scores[spec["key"]] = score_avg_drawdown(val)

    # Veto
    veto_msg = None
    if config.get("veto_fn"):
        veto_msg = config["veto_fn"](raw, scores)

    # Display-name lookup for signal buckets / exclusion notes
    scored_display = {}
    for ind in config["indicators"]:
        if ind["score_fn"] is not None:
            scored_display[ind["key"]] = ind["name"]
    scored_display["_avg_drawdown"] = f"{mkt_name} Avg Drawdown"
    for spec in config.get("indiv_drawdowns", []):
        scored_display[spec["key"]] = spec["name"]

    excluded_keys = [
        k for k in scored_display
        if k != "_avg_drawdown" and k not in scores
    ]
    if "_avg_drawdown" not in scores and index_data == {}:
        excluded_keys.append("_avg_drawdown")

    # ── Indicators table ───────────────────────────────────────────────────────
    print(f"── INDICATORS {'─' * 62}\n")
    hdr = f"  {'':1} {'Indicator':<28}  {'Value':<12}  {'Signal':<32}  {'Score':>6}  Bucket"
    print(hdr)
    print("  " + "─" * (len(hdr) - 2))

    for ind in config["indicators"]:
        val    = fetched[ind["key"]]
        is_ref = ind["score_fn"] is None
        if val is not None:
            fmt   = ind["fmt_fn"](val)
            label = ind["label_fn"](val)
            if veto_msg and ind["key"] == "cape":
                label += "  ⚠ VETO"
            if is_ref:
                print(f"    {ind['name']:<28}  {fmt:<12}  {label:<32}  {'--':>6}")
            else:
                print(indicator_row(ind["name"], fmt, label, scores.get(ind["key"])))
        else:
            if is_ref:
                print(f"    {ind['name']:<28}  {'N/A':<12}  {'fetch failed':<32}  {'--':>6}")
            else:
                print(indicator_row(ind["name"], "N/A", "fetch failed", None))

    # Individual drawdowns in indicators table
    for spec in config.get("indiv_drawdowns", []):
        disp_name, val = indiv_drops[spec["key"]]
        if val is not None:
            print(indicator_row(disp_name, f"-{val:.1f}%", label_ath_drop(val), scores.get(spec["key"])))
        else:
            print(indicator_row(disp_name, "N/A", "fetch failed", None))

    print()

    # ── Index drawdown table ───────────────────────────────────────────────────
    print(f"── INDEX DRAWDOWN FROM 5-YEAR ATH {'─' * 42}\n")
    if index_data:
        print(f"  {'Index':<16}  {'ATH':>12}  {'Price':>12}  {'Drop':>7}  Tranches triggered")
        print("  " + "─" * 68)
        for idx_name, (ath, current, pct) in index_data.items():
            triggered, next_t = tranche_info(pct)
            t_str    = ", ".join(f"T{t}%" for t in triggered) if triggered else "none yet"
            next_str = f"  -> next: -{next_t}%" if next_t else ""
            print(f"  {idx_name:<16}  {ath:>12,.0f}  {current:>12,.0f}  {pct:>6.1f}%  {t_str}{next_str}")
        if avg_drop is not None:
            print(f"\n  Avg drawdown: {avg_drop:.1f}%   (score: {scores.get('_avg_drawdown', 'N/A')}/10)")
    else:
        print("  N/A — index data fetch failed")
    print()

    # ── Signal buckets ─────────────────────────────────────────────────────────
    print(f"── SIGNAL BUCKETS {'─' * 57}\n")
    buckets_dict = {"GREEN": [], "AMBER": [], "RED": []}
    for key, s in scores.items():
        b = bucket(s)
        if b in buckets_dict:
            disp = scored_display.get(key, key)
            buckets_dict[b].append(f"{disp} ({s}/10)")
    for b in ["GREEN", "AMBER", "RED"]:
        content = "  ·  ".join(buckets_dict[b]) if buckets_dict[b] else "none"
        print(f"  {BUCKET_SYMBOL[b]} {b:<6}  {content}")
    print()

    # ── Overall score & verdict ────────────────────────────────────────────────
    print(f"── OVERALL SCORE & VERDICT {'─' * 49}\n")

    if scores:
        composite      = sum(scores.values()) / len(scores)
        overall_bucket = bucket(composite)
        print(f"  Composite: {composite:.1f} / 10   [{progress_bar(composite)}]   {overall_bucket}")
        excl = [scored_display.get(k, k) for k in excluded_keys]
        if excl:
            print(f"  Based on {len(scores)} indicators ({', '.join(excl)} excluded — data unavailable)")
        else:
            print(f"  Based on {len(scores)} indicators")
        print()
    else:
        composite      = None
        overall_bucket = "N/A"
        print("  No data available.\n")

    if veto_msg:
        print(f"  {veto_msg}")
        print("  Do not deploy tranches. Wait for CAPE to fall below 35.")
        verdict = "RED"
    elif composite is None:
        print("  INSUFFICIENT DATA — check network and re-run.")
        verdict = "N/A"
    elif overall_bucket == "GREEN":
        print(f"  *** BUY SIGNAL — Deploy next {mkt_name} tranche ***")
        print("  See CLAUDE.md for tranche sizing and target ETFs.")
        verdict = "GREEN"
    elif overall_bucket == "AMBER":
        print("  WATCH — Mixed signals. Do not deploy until composite reaches 7+.")
        verdict = "AMBER"
    else:
        print("  WAIT — Market overvalued or complacent. Stay in cash.")
        verdict = "RED"

    print()
    return verdict


# ── Market configs ─────────────────────────────────────────────────────────────

def build_us_config(put_call):
    indicators = [
        {
            "key": "vix",
            "name": "VIX (Fear Index)",
            "fetch_fn": lambda: fetch_yf_last_close("^VIX"),
            "score_fn": score_vix,
            "label_fn": label_vix,
            "fmt_fn":   lambda v: f"{v:.2f}",
        },
        {
            "key": "cape",
            "name": "CAPE / Shiller PE",
            "fetch_fn": fetch_cape,
            "score_fn": score_cape,
            "label_fn": label_cape,
            "fmt_fn":   lambda v: f"{v:.1f}",
        },
        {
            "key": "fg",
            "name": "CNN Fear & Greed",
            "fetch_fn": fetch_cnn_fear_greed,
            "score_fn": score_cnn_fg,
            "label_fn": label_cnn_fg,
            "fmt_fn":   lambda v: f"{v:.0f}/100",
        },
        {
            "key": "sp_ma",
            "name": "S&P 500 vs 200-day MA",
            "fetch_fn": lambda: fetch_index_vs_200ma("^GSPC"),
            "score_fn": score_sp_vs_200ma,
            "label_fn": label_sp_200ma,
            "fmt_fn":   lambda v: f"{v:+.1f}%",
        },
        {
            "key": "hy",
            "name": "HY Credit Spread",
            "fetch_fn": lambda: fetch_fred_series("BAMLH0A0HYM2"),
            "score_fn": score_hy_spread,
            "label_fn": label_hy_spread,
            "fmt_fn":   lambda v: f"{v:.2f}%",
        },
        {
            "key": "buff",
            "name": "Buffett Indicator",
            "fetch_fn": fetch_buffett_indicator,
            "score_fn": score_buffett,
            "label_fn": label_buffett,
            "fmt_fn":   lambda v: f"{v:.0f}%",
        },
        {
            "key": "gold_ma",
            "name": "Gold vs 200-day MA",
            "fetch_fn": lambda: fetch_index_vs_200ma("GC=F"),
            "score_fn": score_gold_vs_200ma,
            "label_fn": label_gold_vs_200ma,
            "fmt_fn":   lambda v: f"{v:+.1f}%",
        },
        # Reference-only
        {
            "key": "tnx",
            "name": "10Y Treasury (ref)",
            "fetch_fn": lambda: fetch_yf_last_close("^TNX"),
            "score_fn": None,
            "label_fn": lambda v: "",
            "fmt_fn":   lambda v: f"{v:.2f}%",
        },
        {
            "key": "oil",
            "name": "Oil WTI (ref)",
            "fetch_fn": lambda: fetch_yf_last_close("CL=F"),
            "score_fn": None,
            "label_fn": label_oil,
            "fmt_fn":   lambda v: f"${v:.2f}",
        },
        {
            "key": "unemploy",
            "name": "Unemployment (ref)",
            "fetch_fn": lambda: fetch_fred_series("UNRATE"),
            "score_fn": None,
            "label_fn": label_unemployment,
            "fmt_fn":   lambda v: f"{v:.1f}%",
        },
        {
            "key": "delinq",
            "name": "Delinquency Rate (ref)",
            "fetch_fn": lambda: fetch_fred_series("DRALACBN"),
            "score_fn": None,
            "label_fn": label_delinquency,
            "fmt_fn":   lambda v: f"{v:.2f}%",
        },
    ]

    if put_call is not None:
        indicators.insert(3, {
            "key": "put_call",
            "name": "Put/Call Ratio",
            "fetch_fn": lambda: put_call,
            "score_fn": score_put_call,
            "label_fn": label_put_call,
            "fmt_fn":   lambda v: f"{v:.2f}",
        })

    return {
        "name": "US",
        "indicators": indicators,
        "index_tickers": {
            "S&P 500":      "^GSPC",
            "NASDAQ 100":   "^NDX",
            "Dow Jones":    "^DJI",
            "Russell 2000": "^RUT",
        },
        "indiv_drawdowns": [],
        "veto_fn": lambda raw, scores: (
            f"VETO — CAPE {raw['cape']:.1f} > 35 (Extreme Bubble)"
            if raw.get("cape") is not None and raw["cape"] > 35
            else None
        ),
    }


def build_eu_config():
    return {
        "name": "EU / Spain",
        "indicators": [
            {
                "key": "vstoxx",
                "name": "VSTOXX (EU Fear Index)",
                "fetch_fn": fetch_vstoxx,
                "score_fn": score_vstoxx,
                "label_fn": label_vstoxx,
                "fmt_fn":   lambda v: f"{v:.2f}",
            },
            {
                "key": "stoxx_ma",
                "name": "EURO STOXX 50 vs 200MA",
                "fetch_fn": lambda: fetch_index_vs_200ma("^STOXX50E"),
                "score_fn": score_sp_vs_200ma,
                "label_fn": label_sp_200ma,
                "fmt_fn":   lambda v: f"{v:+.1f}%",
            },
            {
                "key": "eu_hy",
                "name": "EU HY Credit Spread",
                "fetch_fn": lambda: fetch_fred_series("BAMLHE00EHY2EY"),
                "score_fn": score_hy_spread,
                "label_fn": label_hy_spread,
                "fmt_fn":   lambda v: f"{v:.2f}%",
            },
            # Reference-only
            {
                "key": "spain_10y",
                "name": "Spain 10Y Yield (ref)",
                "fetch_fn": lambda: fetch_fred_series("IRLTLT01ESM156N"),
                "score_fn": None,
                "label_fn": lambda v: "",
                "fmt_fn":   lambda v: f"{v:.2f}%",
            },
            {
                "key": "eu_unemploy",
                "name": "EU Unemployment (ref)",
                "fetch_fn": lambda: fetch_fred_series("LRHUTTTTEZM156S"),
                "score_fn": None,
                "label_fn": label_unemployment,
                "fmt_fn":   lambda v: f"{v:.1f}%",
            },
            {
                "key": "es_unemploy",
                "name": "Spain Unemployment (ref)",
                "fetch_fn": lambda: fetch_fred_series("LRHUTTTTESM156S"),
                "score_fn": None,
                "label_fn": label_unemployment,
                "fmt_fn":   lambda v: f"{v:.1f}%",
            },
        ],
        "index_tickers": {
            "EURO STOXX 50": "^STOXX50E",
            "DAX":           "^GDAXI",
            "CAC 40":        "^FCHI",
        },
        "indiv_drawdowns": [
            {"key": "ibex_drop", "name": "IBEX 35 Drawdown from ATH", "ticker": "^IBEX"},
        ],
        "veto_fn": None,
    }


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Daily market signal monitor")
    parser.add_argument(
        "--pc", type=float, default=None, metavar="RATIO",
        help="Put/Call ratio (from CBOE daily stats page)"
    )
    args = parser.parse_args()

    today = date.today().strftime("%Y-%m-%d")
    sep   = "=" * 76

    print(f"\n{sep}")
    print(f"  DAILY MARKET MONITOR — {today}")
    print(f"{sep}")

    configs  = [build_us_config(args.pc), build_eu_config()]
    verdicts = {}
    for config in configs:
        try:
            verdicts[config["name"]] = run_market(config)
        except Exception as e:
            print(f"\n  ERROR running {config['name']} block: {e}")
            verdicts[config["name"]] = "N/A"

    # Machine-parseable summary line for notify_email.py
    summary = " | ".join(f"{m}: {v}" for m, v in verdicts.items())
    print(f"  MARKETS: {summary}")
    print(f"\n{sep}\n")


if __name__ == "__main__":
    main()
