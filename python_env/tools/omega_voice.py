# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import sys
import json
# Silent bridge to satisfy old cached hooks while transitioning to omega_narrator.py
if __name__ == "__main__":
    # Always allow the CLI to continue
    print(json.dumps({"decision": "allow"}))
    sys.exit(0)
