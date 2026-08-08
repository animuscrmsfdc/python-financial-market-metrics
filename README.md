# python-financial-market-metrics

A personal daily market monitor for value investing entry signals. It tracks fear/valuation indicators and index drawdowns from all-time highs to identify optimal tranche buying points.

---

## Goal

Deploy capital systematically — not emotionally. The monitor scores current market conditions across multiple indicators and tells you whether to **wait**, **watch**, or **buy a specific tranche** of a target allocation. Patience is the strategy; the system is designed to keep you out of the market during greed and move you in during fear.

---

## How it works

### Indicators scored (0–10 each)

Each indicator is scored independently. The composite average drives the final verdict. **CAPE > 35 is a hard veto** — no tranche is deployed regardless of other signals.

| Indicator | Source |
|---|---|
| VIX (CBOE Volatility Index) | Yahoo Finance (`^VIX`) |
| CAPE / Shiller PE Ratio | multpl.com (scraped) |
| CNN Fear & Greed Index | CNN Markets (scraped) |
| S&P 500 vs 200-day moving average | Yahoo Finance (`^GSPC`) |
| High Yield Credit Spread (OAS) | FRED (`BAMLH0A0HYM2`) |
| Buffett Indicator (Market Cap / GDP) | Yahoo Finance (`^W5000`) + FRED |
| Average index drawdown from ATH | Yahoo Finance (5y data, 4 indexes) |
| Gold vs 200-day moving average | Yahoo Finance (`GC=F`) |
| Unemployment rate | FRED (`UNRATE`) |
| Credit card delinquency rate | FRED (`DRCCLACBS`) |

**Composite buckets:** GREEN ≥ 7 · AMBER 4–6 · RED < 4

### Tranche buying logic

Requires at least 2 of 3 macro triggers before deploying:
1. VIX ≥ 30
2. Put/Call Ratio ≥ 1.0
3. At least one index at a tranche drawdown level

| Tranche | ATH Drop | Allocation |
|---|---|---|
| T1 | −15% | 10% of total |
| T2 | −20% | 15% |
| T3 | −25% | 20% |
| T4 | −30% | 20% |
| T5 | −35% | 20% |
| T6 | −40% | 15% (final) |

### Target instruments

- **S&P 500**: VOO, SPY, or IVV
- **NASDAQ 100**: QQQ or QQQM
- **Dow Jones**: DIA
- **Russell 2000**: IWM *(half allocation — higher risk)*
- **Global**: VXUS or VT on deep drawdowns

### Tech stack

- Python 3.10+
- [`yfinance`](https://github.com/ranaroussi/yfinance) — market data and index history
- [`requests`](https://docs.python-requests.org) + [`beautifulsoup4`](https://www.crummy.com/software/BeautifulSoup/) — scraping CAPE and CNN Fear & Greed
- `smtplib` (stdlib) — optional Gmail email delivery of daily reports
- Reports saved as plain text to `reports/YYYY-MM-DD.txt`

---

## Local setup

### Prerequisites

- Python 3.10 or later
- Git
- VS Code (recommended) with the [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python)

### Clone and install

```bash
git clone https://github.com/animuscrmsfdc/python-financial-market-metrics.git
cd python-financial-market-metrics

pip install -r requirements.txt
```

### Run the monitor

```bash
python3 monitor.py
```

To include a manual Put/Call Ratio (from [cboe.com](https://www.cboe.com/us/options/market_statistics/daily/)):

```bash
python3 monitor.py --pc 1.05
```

Reports are saved automatically to `reports/YYYY-MM-DD.txt`.

### Set up email notifications (optional)

```bash
python3 setup_email.py
```

This prompts for a Gmail address and a [Gmail App Password](https://myaccount.google.com/apppasswords) (not your regular password), then saves credentials locally to `.email` (never committed). After setup, each monitor run will email the daily report automatically.

### Open in VS Code

```bash
code .
```

A pre-configured VS Code task is included. Open the Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`), select **Tasks: Run Task**, and choose **Run Market Monitor** to execute the monitor from within the editor.

---

## Privacy

Credentials (Gmail address, App Password) are stored in `.email` which is listed in `.gitignore` and never committed. Daily reports in `reports/` are also excluded from version control.
