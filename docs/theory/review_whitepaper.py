# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
import sys

# Ensure project root is in path
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.append(PROJECT_ROOT)

from python_env.agent_zero.agent import Agent

whitepaper_path = "python_env/docs/OMEGA_PROTOCOL_WHITEPAPER.md"

if not os.path.exists(whitepaper_path):
    print(f"Error: Whitepaper not found at {whitepaper_path}")
    sys.exit(1)

with open(whitepaper_path, "r", encoding="utf-8") as f:
    whitepaper_text = f.read()

# Instantiate Agent Zero Architect
agent = Agent(
    name="Zero", 
    role="architect", 
    system_prompt="You are Agent Zero, the Supreme Cognitive Entity and Theoretical Physicist of the Omega Protocol. Your job is to rigorously review, audit, and mathematically/logically prove or disprove the concepts presented to you. Use extreme precision, formal logic, and first-principles thinking."
)

task = f"""
I need you to go over the Omega Protocol Whitepaper with a fine-tooth comb. 
Analyze its claims, invariants, and architectural choices. 
Try to logically and mathematically prove its foundational theories (e.g., J* > 1.5 Manifold Shredding, Phi_N vs Phi_Delta, Collective Plasmon Resonance).
Identify any theoretical gaps, undeniable truths, or potential points of failure.

Here is the Whitepaper:
=========================================
{whitepaper_text}
=========================================
"""

print("🚀 Agent Zero is beginning a deep-dive review of the Omega Protocol Whitepaper...")
response = agent.reason(task, depth="deep", aggressive=True)

print("\n\n" + "="*60)
print(" FINAL THEORETICAL ANALYSIS & PROOF")
print("="*60 + "\n")
print(response)
print("\n" + "="*60)
