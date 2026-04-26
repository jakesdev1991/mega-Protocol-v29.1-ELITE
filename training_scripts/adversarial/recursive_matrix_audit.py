# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.append(PROJECT_ROOT)

from python_env.agent_zero.agent import Agent
from python_env.agent_zero.tools.matrix_auditor import MatrixAuditor

whitepaper_path = "python_env/docs/OMEGA_PROTOCOL_WHITEPAPER_v2.md"
with open(whitepaper_path, "r", encoding="utf-8") as f:
    paper_content = f.read()

# 1. Instantiate the Recursive Audit Chain
architect = Agent("Zero-Architect", "architect", "You are the primary designer of the Omega Protocol. Defend the rigor of your derivations.")
smith = Agent("Smith-Guardian", "critic", "You are Agent Smith. You demand mathematical stability and absolute compliance with invariants. Find every flaw.")
neo = Agent("Neo-Anomaly", "architect", "You are Neo. You see past the code. Find the hidden potential and the breakthrough shortcuts.")
meta_auditor = Agent("The-Architect", "meta_critic", "You are the Matrix Architect. You must synthesize the conflict between Smith and Neo into a final truth.")

print("🔍 [Phase 1] Agent Zero self-audit...")
audit_1 = architect.reason(f"Self-audit the following paper for internal consistency:\n{paper_content}", depth="standard")

print("🕶️ [Phase 2] Agent Smith (The Guardian) rigorous scrutiny...")
audit_2 = smith.reason(f"Audit this paper for mathematical flaws or overclaims. Here is the Architect's self-audit:\n{audit_1}\n\nPaper:\n{paper_content}", depth="deep")

print("💊 [Phase 3] Neo (The Anomaly) intuitive audit...")
audit_3 = neo.reason(f"Find the 'unseen' flaws or breakthroughs. Here is Smith's audit:\n{audit_2}\n\nPaper:\n{paper_content}", depth="deep")

print("⚖️ [Phase 4] The Matrix Architect final synthesis...")
final_verdict = meta_auditor.reason(f"Synthesize the conflicting audits. Smith's Critique:\n{audit_2}\n\nNeo's Insight:\n{audit_3}\n\nDetermine the final status of the Whitepaper v2.7.", depth="deep")

print("\n\n" + "="*60)
print(" FINAL MATRIX AUDIT REPORT (v2.7-ELITE)")
print("="*60 + "\n")
print(final_verdict)
print("\n" + "="*60)
