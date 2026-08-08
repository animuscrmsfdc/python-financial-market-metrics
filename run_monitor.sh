#!/bin/bash
# Daily market monitor runner — called by launchd and VS Code task.
# Saves output to reports/YYYY-MM-DD.txt, then emails the report.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON=/Library/Frameworks/Python.framework/Versions/3.14/bin/python3
REPORT="$SCRIPT_DIR/reports/$(date +%Y-%m-%d).txt"

cd "$SCRIPT_DIR"

"$PYTHON" monitor.py | tee "$REPORT"

if [ -f "$SCRIPT_DIR/.email" ]; then
    "$PYTHON" notify_email.py
fi
