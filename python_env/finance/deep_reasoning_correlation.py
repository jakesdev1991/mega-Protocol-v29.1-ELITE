# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
import sys

# Ensure project root is in path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

from finance.finance_agent import FinanceAgent

def perform_deep_correlation_reasoning():
    print("🧠 [FinBrain] Starting Cross-Scale Correlation Analysis...")
    
    observation = """
    MULTI-SCALE DATA OBSERVATION (4231 Days of BTC/USD):
    1. Annual (365d) Archive Mode (Phi_Delta) shows 'Phase Transitions' at cycle peaks (e.g., late 2017, early 2021, late 2024).
    2. Micro (10d) shocks show 'Precursor Turbulence' - clusters of high-frequency Phi_Delta spikes (>0.7) 
       that occur 14-21 days BEFORE the Annual Phi_Delta breaches the 0.6 'Freeze Boundary.'
    3. The Newtonian Mode (Phi_N) shows 'Viscosity Divergence' in the gap between the Micro-spike onset 
       and the Annual Archive Snap.
    
    TASK:
    Analyze the causal informational bridge between these two scales. 
    Explain the 'Precursor Turbulence' through the lens of the Omega Protocol v29.1.
    How does the 10d Perspective flux lead to a 365d Archive fracture?
    """
    
    agent = FinanceAgent()
    result = agent.analyze_market_snapshot(observation)
    
    print("\n" + "="*80)
    print("🏛️ FINBRAIN DEEP REASONING REPORT: CROSS-SCALE CORRELATIONS")
    print("="*80)
    print(result)
    print("="*80)

if __name__ == "__main__":
    perform_deep_correlation_reasoning()
