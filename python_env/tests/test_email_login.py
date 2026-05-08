# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""Optional SMTP smoke test.

The Gmail login check requires real credentials and network access, so it should
not execute during module import or in default offline test runs.
"""

import os
import smtplib
import unittest

from dotenv import load_dotenv

load_dotenv("business/API_CONNECTION_KEYS.env")


def smtp_login_succeeds(email: str, password: str) -> bool:
    """Return whether Gmail SMTP accepts the supplied credentials."""
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(email, password)
    return True


@unittest.skipUnless(
    os.getenv("RUN_SMTP_TESTS") == "1",
    "set RUN_SMTP_TESTS=1 with SENDER_EMAIL and SENDER_APP_PASSWORD to run SMTP smoke test",
)
class EmailLoginTests(unittest.TestCase):
    def test_gmail_smtp_login_accepts_configured_credentials(self):
        email = os.getenv("SENDER_EMAIL")
        password = os.getenv("SENDER_APP_PASSWORD")
        self.assertIsNotNone(email, "SENDER_EMAIL is required when RUN_SMTP_TESTS=1")
        self.assertIsNotNone(password, "SENDER_APP_PASSWORD is required when RUN_SMTP_TESTS=1")

        candidates = [password]
        compact_password = password.replace(" ", "")
        if compact_password != password:
            candidates.append(compact_password)

        for candidate in candidates:
            try:
                if smtp_login_succeeds(email, candidate):
                    return
            except Exception as exc:  # pragma: no cover - diagnostic for manual smoke runs
                last_error = exc

        self.fail(f"Gmail SMTP rejected configured credentials: {last_error}")


if __name__ == "__main__":
    unittest.main()
