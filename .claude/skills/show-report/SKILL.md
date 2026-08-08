---
description: Show a saved market report — latest by default, or pass a date YYYY-MM-DD
user-invocable: true
argument-hint: "[YYYY-MM-DD]"
---

Show a saved market report from the reports/ directory.

If $ARGUMENTS is provided and looks like a date (YYYY-MM-DD), read `reports/$ARGUMENTS.txt`.
Otherwise, list `reports/` and open the most recent file.

After displaying the full report text, add a 3-sentence summary:
- What the composite score and dominant bucket were that day
- The most notable signal (best or worst indicator)
- The verdict that was issued
