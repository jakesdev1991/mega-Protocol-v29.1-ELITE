# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
import sys

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.append(PROJECT_ROOT)
sys.path.append(os.path.join(PROJECT_ROOT, "python_env"))

from python_env.agent_zero.sandbox_experimenter import SandboxExperimenter

if __name__ == "__main__":
    print("--- OMEGA PROTOCOL: LOOP 16 (SANDBOX EXPERIMENTER) STARTING ---")
    ex = SandboxExperimenter()
    try:
        ex.run_epoch()
        print("--- EPOCH COMPLETE ---")
    except Exception as e:
        print(f"CRITICAL ERROR IN SANDBOX: {e}")
