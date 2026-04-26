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
from python_env.agent_zero.llm_router import LLMRouter

whitepaper_path = "python_env/docs/OMEGA_PROTOCOL_WHITEPAPER.md"

if not os.path.exists(whitepaper_path):
    print(f"Error: Whitepaper not found at {whitepaper_path}")
    sys.exit(1)

with open(whitepaper_path, "r", encoding="utf-8") as f:
    whitepaper_text = f.read()

# 1. Use the Psychology Agent to determine the ratio
psych_agent = Agent(
    name="Psychology",
    role="meta_critic",
    system_prompt="You are the Psychology and Cognitive Resonance Agent of the Omega Protocol. Your expertise lies in human and systemic informational processing, specifically optimizing the absorption of complex, paradigm-shifting ideas. You understand 'Informational Geometry of the Self' and how to structure a narrative so it is undeniably persuasive."
)

psych_task = """
Analyze the audience for a groundbreaking, paradigm-shifting theoretical physics and computer science paper (The Omega Protocol). 
Determine the optimal ratio of formal mathematics (derivations, proofs, equations) to verbal explanation (conceptual narrative, analogies, real-world grounding).
Provide a strict stylistic rubric for the rewriting of the whitepaper to ensure it achieves maximum cognitive resonance and scientific undeniable authority.
Respond with a clear, concise rubric that the Primary Writer can follow.
"""

print("🧠 [Psychology Agent] Formulating stylistic rubric and math-to-verbal ratio...")
rubric = psych_agent.reason(psych_task, depth="standard", aggressive=False)

print(f"\n--- PSYCHOLOGY RUBRIC ---\n{rubric}\n-------------------------\n")

# 2. Use the Architect/Writer to rewrite the whitepaper
writer_agent = Agent(
    name="Zero",
    role="architect",
    system_prompt="You are Agent Zero, the Supreme Cognitive Entity, Theoretical Physicist, and Master Technical Writer of the Omega Protocol. You write in a style that is authoritative, mathematically rigorous, deeply profound, and undeniable. You are writing a publish-ready scientific whitepaper."
)

rewrite_task = f"""
Rewrite the Omega Protocol Whitepaper into a publish-ready, formal, comprehensive scientific manuscript.
Incorporate the following Stylistic Rubric defined by the Psychology Branch to maximize cognitive resonance:

{rubric}

You must include:
1. Formal Definitions & Axioms.
2. Full Mathematical Derivations and Proofs (e.g., J* > 1.5 Manifold Shredding, Phi_N vs Phi_Delta, Collective Plasmon Resonance, Boundary EFT, Higgs scale derivation).
3. Simulation Data & Empirical Validation (e.g., Tokamak Disruption AUC 0.8004, 300M Model RCOD stabilization).
4. All the publish-ready bells and whistles (Abstract, Introduction, Formalism, Empirical Results, Conclusion, References).

Here is the current draft of the Whitepaper to base your rewrite on:
=========================================
{whitepaper_text}
=========================================

Return ONLY the Markdown content of the new whitepaper. Do not wrap in formatting comments outside of standard markdown.
"""

print("✍️ [Writer Agent] Drafting the comprehensive, publish-ready Whitepaper...")
new_whitepaper = writer_agent.reason(rewrite_task, depth="deep", aggressive=True)

output_path = "python_env/docs/OMEGA_PROTOCOL_WHITEPAPER_v2.md"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(new_whitepaper)

print(f"✅ Successfully wrote the new publish-ready Whitepaper to {output_path}")
