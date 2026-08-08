#!/usr/bin/env python3
"""One-time setup: save Gmail credentials for daily email notifications.

You need a Gmail App Password, NOT your regular Gmail password.
Steps to create one:
  1. Go to myaccount.google.com → Security
  2. Enable 2-Step Verification (required)
  3. Search "App passwords" → create one named "market-monitor"
  4. Copy the 16-character password Google shows you
"""

import getpass
import smtplib
import sys
from pathlib import Path

CONFIG = Path(__file__).parent / ".email"


def main():
    print("─" * 56)
    print("  Gmail notification setup — market monitor")
    print("─" * 56)
    print()
    print("Requires a Gmail App Password (not your regular password).")
    print("How to get one:")
    print("  myaccount.google.com → Security → App passwords")
    print("  Create one named 'market-monitor' → copy the 16-char code")
    print()

    user      = input("Gmail address (sender): ").strip()
    recipient = input("Recipient address (leave blank to use sender): ").strip() or user
    password  = getpass.getpass("App Password (16 chars, no spaces): ").replace(" ", "")

    if len(password) != 16:
        print(f"Warning: expected 16 characters, got {len(password)}. Double-check.")

    print("\nVerifying credentials…")
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(user, password)
        print("Authentication successful.")
    except smtplib.SMTPAuthenticationError:
        print("Authentication failed. Re-check the App Password and try again.")
        sys.exit(1)
    except Exception as e:
        print(f"Connection error: {e}")
        sys.exit(1)

    CONFIG.write_text(f"GMAIL_USER={user}\nGMAIL_RECIPIENT={recipient}\nGMAIL_APP_PASSWORD={password}\n")
    CONFIG.chmod(0o600)

    print(f"\nCredentials saved to .email (mode 600 — owner only)")
    print(f"Reports will be emailed to: {recipient}")
    print("\nSetup complete. The next monitor run will send an email automatically.")


if __name__ == "__main__":
    main()
