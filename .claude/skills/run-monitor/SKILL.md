---
description: Run the daily market monitor and get a plain-language interpretation of all signals
user-invocable: true
---

Run the daily market monitor by executing:

```bash
python3 monitor.py
```

After the script completes, provide a concise interpretation structured as:

1. **Score** — composite score and bucket (GREEN / AMBER / RED)
2. **Standout signals** — any indicators not in RED, or the most alarming RED ones
3. **CAPE status** — whether the veto is active and what it means right now
4. **Drawdown** — how far each index is from its ATH and which tranches (if any) are triggered
5. **Verdict** — one sentence: what to do today (wait / watch / buy tranche N)

Keep the interpretation under 10 lines. Be direct — this is a daily decision-support tool.
