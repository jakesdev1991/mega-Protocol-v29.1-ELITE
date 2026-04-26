# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import smtplib
import os
from dotenv import load_dotenv

load_dotenv("business/API_CONNECTION_KEYS.env")
email = os.getenv("SENDER_EMAIL")
password = os.getenv("SENDER_APP_PASSWORD")

print(f"Testing login for: {email}")

def test(pwd):
    try:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(email, pwd)
        s.quit()
        return True
    except Exception as e:
        print(f"  Fail for '{pwd}': {e}")
        return False

if test(password):
    print("✅ SUCCESS with original password.")
elif test(password.replace(" ", "")):
    print("✅ SUCCESS without spaces.")
else:
    print("❌ BOTH FAILED. Please verify your Gmail App Password.")
