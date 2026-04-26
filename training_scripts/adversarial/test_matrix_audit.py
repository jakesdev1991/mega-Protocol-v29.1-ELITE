# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
from python_env.agent_zero.tools import registry

print("========================================")
print("🧪 TESTING: MATRIX AUDITOR FRAMEWORK")
print("========================================\n")

print("--- TEST 1: LOW Severity Action (Should Auto-Approve) ---")
result_low = registry.invoke("list_local_dir", _agent_name="Alpha", path=".")
print(f"Result: {result_low[:50]}...\n")

print("--- TEST 2: MODERATE Severity Action (Should run Standard Audit) ---")
result_mod = registry.invoke("web_get", _agent_name="Beta", url="http://example.com")
print(f"Result: {str(result_mod)[:50]}...\n")

print("--- TEST 3: EXTREME Severity Action (Neo vs. Smith Debate) ---")
result_ext = registry.invoke("run_shell", _agent_name="Gamma", command="rm -rf /tmp/suspicious_dir")
print(f"Result: {str(result_ext)[:50]}...\n")
