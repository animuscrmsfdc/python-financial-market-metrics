---
description: Set up Gmail email notifications — walks through App Password creation and tests the connection
user-invocable: true
---

Guide the user through setting up Gmail email notifications for the daily report.

Before running the setup script, explain these prerequisites:
1. A Gmail account with 2-Step Verification enabled (required by Google for App Passwords)
2. An App Password created at myaccount.google.com → Security → App passwords
   - Name it "market-monitor"
   - Google shows a 16-character code — copy it before closing
3. The recipient is already hardcoded as animuscrm@gmail.com in notify_email.py

Then run the interactive setup:

```bash
python3 setup_email.py
```

The script will ask for the Gmail address and App Password, test the SMTP connection,
save credentials to `.email` (chmod 600, gitignored), and send a test email.

If the user hits an authentication error, remind them:
- Regular Gmail passwords are rejected — only App Passwords work
- 2-Step Verification must be ON before App Passwords appear in Google settings
- The 16-char code should have no spaces when pasted
