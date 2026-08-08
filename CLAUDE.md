# myvalueinvestment — Daily Market Monitor

## Purpose
Personal value investing signal tracker. Monitors key fear/valuation indicators and
index drawdowns from ATH to identify optimal tranche buying entry points.

## Running the daily monitor
```bash
python3 monitor.py                  # auto-fetch all indicators
python3 monitor.py --pc 1.05       # add put/call ratio manually
```
If packages are missing: `pip install -r requirements.txt`

When the user asks "what's the market doing", "run the monitor", or "check signals":
1. Run `python3 monitor.py`
2. Interpret the output against the thresholds below
3. Give a plain-language verdict: WAIT / WATCH / BUY TRANCHE N

---

## Indicators & Scoring

Each indicator is scored 0–10 (higher = better buying opportunity).
Bucket: GREEN ≥ 7 · AMBER 4–6 · RED < 4
Composite = average of all scored indicators. CAPE > 35 is a hard VETO.

### VIX (CBOE Volatility Index)
| Range  | Score | Bucket | Meaning                          |
|--------|-------|--------|----------------------------------|
| < 15   | 1     | RED    | Complacency — avoid              |
| 15–20  | 3     | RED    | Normal                           |
| 20–30  | 5     | AMBER  | Caution — worth watching         |
| 30–40  | 8     | GREEN  | Fear — strong signal             |
| ≥ 40   | 10    | GREEN  | Extreme Fear — high conviction   |

### CAPE / Shiller PE Ratio
| Range  | Score | Bucket | Meaning                          |
|--------|-------|--------|----------------------------------|
| < 15   | 10    | GREEN  | Undervalued — rare entry         |
| 15–20  | 8     | GREEN  | Fair value                       |
| 20–25  | 5     | AMBER  | Elevated                         |
| 25–35  | 2     | RED    | Overvalued                       |
| > 35   | 0     | RED    | Extreme Bubble — **VETO active** |

### Put/Call Ratio (CBOE Total)
| Range   | Score | Bucket | Meaning              |
|---------|-------|--------|----------------------|
| < 0.7   | 1     | RED    | Extreme Greed        |
| 0.7–0.9 | 3     | RED    | Bullish              |
| 0.9–1.1 | 5     | AMBER  | Neutral              |
| 1.1–1.3 | 7     | GREEN  | Bearish/Fear         |
| ≥ 1.3   | 10    | GREEN  | Extreme Fear         |
Source: cboe.com/us/options/market_statistics/daily/ → pass with `--pc`

### CNN Fear & Greed Index (0 = extreme fear, 100 = extreme greed)
| Range  | Score | Bucket | Meaning              |
|--------|-------|--------|----------------------|
| 0–25   | 10    | GREEN  | Extreme Fear         |
| 25–40  | 7     | GREEN  | Fear                 |
| 40–60  | 5     | AMBER  | Neutral              |
| 60–75  | 3     | RED    | Greed                |
| 75–100 | 1     | RED    | Extreme Greed        |

### S&P 500 vs 200-Day Moving Average
| % vs MA   | Score | Bucket | Meaning                        |
|-----------|-------|--------|--------------------------------|
| ≤ −15%    | 10    | GREEN  | Deep below MA — capitulation   |
| −15 to −10| 8     | GREEN  | Significantly below MA         |
| −10 to −5 | 6     | AMBER  | Below MA                       |
| −5 to 0   | 5     | AMBER  | Just below MA                  |
| 0 to +10  | 3     | RED    | Above MA — normal bull         |
| +10 to +20| 2     | RED    | Extended above MA              |
| > +20%    | 1     | RED    | Extremely stretched            |

### High Yield Credit Spread (ICE BofA OAS, FRED: BAMLH0A0HYM2)
| Range    | Score | Bucket | Meaning                        |
|----------|-------|--------|--------------------------------|
| ≥ 7.0%   | 10    | GREEN  | Extreme credit stress          |
| 5.0–7.0% | 8     | GREEN  | High stress — recession fear   |
| 4.0–5.0% | 6     | AMBER  | Elevated                       |
| 3.0–4.0% | 4     | AMBER  | Normal range                   |
| 2.0–3.0% | 2     | RED    | Low — credit complacency       |
| < 2.0%   | 1     | RED    | Extreme complacency            |

### Buffett Indicator (Total US Market Cap / GDP %)
Computed as: Wilshire 5000 index (^W5000, ≈ $1B/pt) / annualized GDP (FRED)
| Range   | Score | Bucket | Meaning                        |
|---------|-------|--------|--------------------------------|
| < 80%   | 10    | GREEN  | Undervalued                    |
| 80–100% | 8     | GREEN  | Fair value                     |
| 100–120%| 6     | AMBER  | Modestly overvalued            |
| 120–150%| 4     | AMBER  | Overvalued                     |
| 150–200%| 2     | RED    | Significantly overvalued       |
| > 200%  | 1     | RED    | Extreme bubble                 |

### Average Index Drawdown from ATH
Computed across S&P 500, NASDAQ 100, Dow Jones, Russell 2000
| Avg Drop | Score | Bucket |
|----------|-------|--------|
| ≥ 35%    | 10    | GREEN  |
| 25–35%   | 8     | GREEN  |
| 20–25%   | 7     | GREEN  |
| 15–20%   | 5     | AMBER  |
| 10–15%   | 3     | RED    |
| 5–10%    | 2     | RED    |
| < 5%     | 1     | RED    |

### 10-Year Treasury Yield (reference only, not scored)
- > 5%: competes with equities, reduces valuations
- < 3%: supports higher equity multiples

---

## Tranche Buying Strategy

Wait for **at least 2 of 3** macro conditions before deploying any tranche:
1. VIX ≥ 30 (Fear or Extreme Fear)
2. Put/Call Ratio ≥ 1.0 (bearish sentiment)
3. At least one index has reached a tranche drawdown level (see below)

CAPE > 35 is a veto — do not deploy tranches even if other signals fire,
unless the drawdown from ATH exceeds 40%.

### Tranche Levels (% drop from ATH per index)
| Tranche | ATH Drop | Action                                          |
|---------|----------|-------------------------------------------------|
| T1      | -15%     | Deploy 10% of intended total allocation         |
| T2      | -20%     | Deploy another 15%                              |
| T3      | -25%     | Deploy another 20%                              |
| T4      | -30%     | Deploy another 20%                              |
| T5      | -35%     | Deploy another 20%                              |
| T6      | -40%     | Deploy final 15% — near historical crash floors |

### Instruments to buy (per index signal)
- **S&P 500**: VOO, SPY, or IVV
- **NASDAQ 100**: QQQ or QQQM
- **Dow Jones**: DIA
- **Russell 2000**: IWM (small-caps carry more risk — reduce allocation by half)
- **Global diversification**: VXUS or VT for non-US exposure on deep drawdowns

---

## Indexes Tracked
| Name          | Ticker  | ATH Reference        |
|---------------|---------|----------------------|
| S&P 500       | ^GSPC   | Computed from 5y data |
| NASDAQ 100    | ^NDX    | Computed from 5y data |
| Dow Jones     | ^DJI    | Computed from 5y data |
| Russell 2000  | ^RUT    | Computed from 5y data |
| VIX           | ^VIX    | Fear index (no ATH logic) |
| 10Y Treasury  | ^TNX    | Reference rate        |

---

## Data Sources
- **Market data / VIX**: Yahoo Finance via `yfinance`
- **CAPE (Shiller PE)**: multpl.com (scraped)
- **Put/Call Ratio**: CBOE daily stats page (scraped)

---

## Key Reminders
- Patience is the edge. The market will provide the entry — the job is to wait.
- Drawdowns can continue past 40%. Never deploy all capital at once.
- Rebalance annually; tranches are entry logic, not exit logic.
- Exit thesis: sell when CAPE > 35 AND VIX < 15 (greed peak) or when fundamentals break.
