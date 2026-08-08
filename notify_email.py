#!/usr/bin/env python3
"""Send today's market report as an email.

Subject: Market Signals YYYY-MM-DD GREEN|AMBER|RED
Body:     full report text (plain text, monospace-friendly)
"""

import smtplib
import sys
from datetime import date
from email.mime.text import MIMEText
from pathlib import Path

PROJECT = Path(__file__).parent
CONFIG  = PROJECT / ".email"
REPORTS = PROJECT / "reports"


def load_config():
    if not CONFIG.exists():
        print("ERROR: .email config not found. Run: python3 setup_email.py")
        sys.exit(1)
    cfg = {}
    for line in CONFIG.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            cfg[k.strip()] = v.strip()
    return cfg


def parse_verdict(text):
    if "BUY SIGNAL" in text: return "GREEN"
    if "WATCH"      in text: return "AMBER"
    return "RED"  # covers VETO and WAIT


def main():
    cfg       = load_config()
    user      = cfg.get("GMAIL_USER", "")
    password  = cfg.get("GMAIL_APP_PASSWORD", "")
    recipient = cfg.get("GMAIL_RECIPIENT", user)

    if not user or not password or password.startswith("your_"):
        print("ERROR: credentials not configured. Run: python3 setup_email.py")
        sys.exit(1)

    today       = date.today().strftime("%Y-%m-%d")
    report_path = REPORTS / f"{today}.txt"

    if not report_path.exists():
        print(f"No report found at {report_path}. Run monitor.py first.")
        sys.exit(1)

    body    = report_path.read_text().strip()
    verdict = parse_verdict(body)
    subject = f"Market Signals {today} {verdict}"

    msg            = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"]    = user
    msg["To"]      = recipient

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(user, password)
            smtp.send_message(msg)
        print(f"Email sent: '{subject}' → {recipient}")
    except smtplib.SMTPAuthenticationError:
        print("ERROR: Gmail authentication failed. Check App Password in .email")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: failed to send email: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
