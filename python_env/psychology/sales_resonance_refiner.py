# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
import sys

# Ensure project root is in path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(PROJECT_ROOT)
sys.path.append(os.path.join(PROJECT_ROOT, "python_env"))

from psychology.psychology_agent import PsychologyAgent

class SalesResonanceRefiner:
    def __init__(self):
        self.psych_agent = PsychologyAgent("Omega-Resonance-Optimizer")

    def refine(self, pitch, company_name, contact_person, context=""):
        """Uses the Q-Systemic Self framework to optimize a sales pitch."""
        recipient_context = f"Company: {company_name}, Contact: {contact_person}, Context: {context}"
        print(f"🧠 [Psychology Bridge] Refining pitch for {company_name} using Q-Systemic resonance...")
        return self.psych_agent.refine_pitch_for_resonance(pitch, recipient_context)

if __name__ == "__main__":
    refiner = SalesResonanceRefiner()
    test_pitch = "We can reduce your GPU costs by 90%."
    print(refiner.refine(test_pitch, "NVIDIA", "VP of Infrastructure"))
