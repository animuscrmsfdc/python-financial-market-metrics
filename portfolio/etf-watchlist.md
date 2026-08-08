# ETF Watchlist — Value Investing Portfolio
_Researched by find-value agent · Last updated: 2026-04-19_

---

## Tranche Strategy

### How many tranches?
**6 tranches** across the drawdown range for USA and Europe.
**4 tranches** for Emerging Markets (wider spacing — EM drops faster and deeper).

The system is back-weighted: deploy less early (the drop may continue) and more at the extremes
(that is where the highest long-term return potential concentrates).

### Drawdown entry levels and allocation per tranche

**USA & Europe — 6 tranches**

| Tranche | Drop from ATH | % of Regional Allocation | Rationale |
|---------|--------------|--------------------------|-----------|
| T1 | −15% | 10% | First signal — test the waters |
| T2 | −20% | 15% | Correction confirmed |
| T3 | −25% | 20% | Bear market entry |
| T4 | −30% | 20% | Deep correction — historical median crash floor |
| T5 | −35% | 20% | Severe bear market |
| T6 | −40% | 15% | Near panic lows — highest conviction entry |

**Emerging Markets — 4 tranches**
_(Start later: EM is more volatile and drawdowns are routine, not signals)_

| Tranche | Drop from ATH | % of Regional Allocation |
|---------|--------------|--------------------------|
| T1 | −20% | 20% |
| T2 | −28% | 25% |
| T3 | −35% | 30% |
| T4 | −40% | 25% |

### Capital allocation by region
Decide your total "tranche capital" first (the sum you are willing to deploy across all regions).
Then split it:

| Region | Allocation | Reasoning |
|--------|-----------|-----------|
| USA | 60% | Best signal coverage, deepest market, monitor tracks it daily |
| Europe | 25% | CAPE ~17 — structurally cheaper than US right now |
| Emerging Markets | 15% | Highest volatility — half the per-tranche size vs USA |

> Example: total tranche capital = €100,000 →  
> USA €60,000 · Europe €25,000 · EM €15,000  
> USA T1 deploys: €60,000 × 10% = €6,000 in CSPX

### Hard rules
- **CAPE veto (US):** Never deploy USA tranches while CAPE > 35 (monitor enforces this).
- **No CAPE veto for Europe/EM:** their CAPE is already below 25 — use drawdown levels alone.
- **Never deploy all 6 tranches from cash at once.** The tranche system exists to spread timing risk.
- **Russell 2000 / small-cap ETFs:** half the per-tranche € amount vs large-cap equivalents.

---

## ETF Selection — UCITS Accumulating (Spain / MiFID II compliant)

All ETFs below are Ireland-domiciled (ISIN: IE00…), accumulating, and available on
Xetra, Euronext Amsterdam, or London Stock Exchange. Verified by find-value agent.

---

### USA — Primary Exposure

| Ticker | Full Name | Exchange | ISIN | AUM | ER | Inception | Passes All Criteria |
|--------|-----------|----------|------|-----|----|-----------|---------------------|
| **CSPX** | iShares Core S&P 500 UCITS ETF (Acc) | LSE (USD) / XETRA as SXR8 | IE00B5BMR087 | €137B | 0.07% | May 2010 | ✅ YES |
| **VUAA** | Vanguard S&P 500 UCITS ETF (Acc) | XETRA / LSE / Euronext | IE00BFMXXD54 | €27B | 0.07% | May 2019 | ⚠️ Track record 7y (borderline) |

**Primary pick: CSPX / SXR8**
- Tip: buy SXR8 on XETRA (EUR-denominated) to avoid GBP conversion costs if using a euro account.
- CSPX (LSE) = USD-denominated, same fund, same ISIN.

---

### USA — Value Tilt (supplement, not replacement)

| Ticker | Full Name | Exchange | ISIN | AUM | ER | Inception | Passes All Criteria |
|--------|-----------|----------|------|-----|----|-----------|---------------------|
| **QDVI** | iShares Edge MSCI USA Value Factor UCITS ETF (Acc) | XETRA / LSE as IUVL | IE00BD1F4M44 | €3.4B | 0.20% | Oct 2016 | ⚠️ Track record 9.5y (borderline) |

**Optional add:** Deploy 20–30% of your USA allocation in QDVI alongside CSPX for a value tilt.
QDVI tracks MSCI USA Enhanced Value (151 stocks — low P/B, P/E, EV/CF screened).

---

### USA — Small-Cap (reduced allocation: max 50% of standard tranche size)

| Ticker | Full Name | Exchange | ISIN | AUM | ER | Inception | Passes All Criteria |
|--------|-----------|----------|------|-----|----|-----------|---------------------|
| **ZPRV** | SPDR MSCI USA Small Cap Value Weighted UCITS ETF (Acc) | XETRA | IE00BSPLC413 | €782M | 0.30% | Feb 2015 | ❌ Fails AUM (<€1B) and ER (0.30%) |

**Status: watchlist only.** Monitor until AUM crosses €1B and ER is renegotiated.
Best available UCITS small-cap value option despite failing two criteria.
No UCITS equivalent of VTV, VBR, or AVUV currently exists that passes all criteria.

---

### Europe — Primary Exposure

| Ticker | Full Name | Exchange | ISIN | AUM | ER | Inception | Passes All Criteria |
|--------|-----------|----------|------|-----|----|-----------|---------------------|
| **EUNK** | iShares Core MSCI Europe UCITS ETF EUR (Acc) | XETRA / LSE / Euronext | IE00B4K48X80 | €15B | 0.12% | Sep 2009 | ✅ YES |
| VGEU | Vanguard FTSE Dev Europe UCITS ETF (Dist) | XETRA / LSE | IE00B945VV12 | €4.4B | 0.10% | May 2013 | ⚠️ Distributing (less tax-efficient for Spain) |

**Primary pick: EUNK**
- Tracks MSCI Europe (406 stocks, 15 countries including UK and Switzerland).
- 16-year track record. Only large-AUM accumulating UCITS Europe ETF that passes all criteria.

---

### Europe — Value Tilt (supplement)

| Ticker | Full Name | Exchange | ISIN | AUM | ER | Inception | Passes All Criteria |
|--------|-----------|----------|------|-----|----|-----------|---------------------|
| **CEMS** | iShares Edge MSCI Europe Value Factor UCITS ETF (Acc) | XETRA / LSE as IEFV | IE00BQN1K901 | €2.5B | 0.25% | Jan 2015 | ✅ YES (ER exactly at limit) |

**Optional add:** 20–30% of European allocation in CEMS for additional value tilt.

---

### Emerging Markets — Primary Exposure

| Ticker | Full Name | Exchange | ISIN | AUM | ER | Inception | Passes All Criteria |
|--------|-----------|----------|------|-----|----|-----------|---------------------|
| **IS3N** | iShares Core MSCI EM IMI UCITS ETF (Acc) | XETRA / LSE / Euronext | IE00BKM4GZ66 | €33B | 0.18% | May 2014 | ✅ YES |
| VFEM | Vanguard FTSE EM UCITS ETF (Dist) | XETRA / LSE | IE00B3VVMM84 | €2.9B | 0.17% | May 2012 | ⚠️ Distributing |

**Primary pick: IS3N**
- Tracks MSCI EM IMI (~2,958 stocks including small caps).
- Largest accumulating UCITS EM fund (€33B AUM). 12-year track record.
- Top weights: Taiwan 22%, China 20%, South Korea 18%, India 17%.

---

## Shortlist Summary — Ready to Buy When Signals Fire

| Priority | Ticker | Region | ER | AUM | Tranches | Notes |
|----------|--------|--------|----|-----|----------|-------|
| 1 | **CSPX / SXR8** | USA Broad | 0.07% | €137B | 6 (T1–T6) | Core US position |
| 2 | **EUNK** | Europe Broad | 0.12% | €15B | 6 (T1–T6) | Core Europe position |
| 3 | **IS3N** | EM Broad | 0.18% | €33B | 4 (T1–T4) | Half allocation vs USA |
| 4 | **QDVI / IUVL** | USA Value | 0.20% | €3.4B | 6 (T1–T6) | Supplement alongside CSPX |
| 5 | **CEMS / IEFV** | Europe Value | 0.25% | €2.5B | 6 (T1–T6) | Supplement alongside EUNK |
| — | ZPRV | USA Small Value | 0.30% | €782M | — | Watchlist only — fails criteria |

---

## Key Notes for a Spanish Investor

1. **MiFID II / PRIIPs**: US-listed ETFs (VOO, VTI, VWO, IEMG, QQQ…) cannot legally be
   sold to Spanish retail investors by most brokers. Use UCITS versions only.

2. **Tax efficiency**: Ireland-domiciled accumulating funds defer Spanish dividend tax
   (19–28% depending on bracket) until you sell. Distributing funds pay it annually.

3. **SXR8 vs CSPX**: Same fund, same ISIN (IE00B5BMR087). SXR8 trades in EUR on XETRA.
   CSPX trades in USD on LSE. Buy SXR8 from a EUR account to avoid conversion costs.

4. **Broker access**: Interactive Brokers and Degiro give full access to XETRA and LSE.
   Most Spanish retail banks (Bankinter, SelfBank) only list Euronext-Amsterdam tickers.

5. **AVUV**: The best US small-cap value factor ETF globally — but has no UCITS equivalent
   and fails the 10-year track record rule. Ask the find-value agent annually to recheck.
