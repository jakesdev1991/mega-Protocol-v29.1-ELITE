# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import sys
import os
import json

# Ensure project root is in path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

from agent_zero.serc import SERC

def run_regression_test():
    serc = SERC()
    
    prompts = [
        "Derive the exact Mixed Boundary Condition at rho_min for the reflective horizon in the Omega Protocol.",
        "Derive Newtonian gravity from the Omega Action functional S_Omega.",
        "Compute the frequency-dependent reflectivity R(omega) from the impedance mismatch at the freeze boundary (Phi_min)."
    ]
    
    results = []
    
    print("--- STARTING OMEGA RUBRIC REGRESSION TEST ---")
    
    for prompt in prompts:
        print(f"\nTESTING PROMPT: {prompt}")
        # We use run_cycle which includes the 3-layer audit with the new Meta-Scrutiny rubric
        solution = serc.run_cycle(prompt, max_attempts=1)
        
        # We manually inspect the evolution log to see the audit trail
        # since run_cycle doesn't return the audit messages directly.
        results.append({
            "prompt": prompt,
            "solution_preview": solution[:500] + "..."
        })
        
    print("\n--- REGRESSION TEST COMPLETE ---")
    
if __name__ == "__main__":
    run_regression_test()
