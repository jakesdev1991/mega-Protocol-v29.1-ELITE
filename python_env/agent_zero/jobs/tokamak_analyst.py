# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
from agent_zero.agent import Agent
from agent_zero.serc import SERC
from tokamak.data_summary import get_tokamak_summary
import os
import sys

class TokamakAnalystJob:
    """Specialized Agent Zero job for fusion reactor disruption analysis."""
    
    def __init__(self):
        # High-intellect architect for physics reasoning
        self.physicist = Agent("PlasmaPhysicist", "architect", "You are a nuclear fusion researcher specializing in plasma disruptions and Phi_Delta metrics.")
        # Verifier for safety thresholds
        self.serc = SERC()
        
    def run_analysis(self):
        print("\n🚀 [TokamakAnalyst] Starting Disruption Analysis via Agent Zero...")
        
        # 1. Get Data Stats
        data_stats = get_tokamak_summary()
        print(f"Stats gathered for sensors.")
        
        # 2. Physics Reasoning
        reasoning_prompt = f"""
        Analyze the following Tokamak sensor statistics:
        {data_stats}
        
        Current Phi_Delta Validation found 23,766 shocks (Phi_Delta > 0.7) in PlasmaRogA (131k points).
        
        Task:
        1. Evaluate if the current SHOCK_LIMIT (0.70) is too sensitive.
        2. Propose new HLS-ready C++ constants for 'tokamak/Plasma-20260331T014334Z-3-001/Plasma/Governor.hpp.new'.
        3. Specifically focus on: SHOCK_LIMIT, SENSOR_SLEW_LIMIT, and FLOW_ENTER.
        """
        
        analysis = self.physicist.reason(reasoning_prompt)
        
        # 3. Evolutionary Loop (v2 Dual-Manifold) to refine the C++ constants
        print("\n--- PHASE 3: EVOLUTIONARY SYNTHESIS (v2 Dual-Manifold) ---")
        refine_task = f"Refine these proposed C++ constants into a valid C++ constexpr block, ensuring they are HLS-compatible and meet safety margins for 10kHz control loops:\n{analysis}"
        final_constants = self.serc.run_dual_manifold_cycle(refine_task)
        
        print("\n--- FINAL AGENT ZERO PROPOSAL ---")
        print(final_constants)
        
        # Save to knowledge base
        os.makedirs("agent_zero/knowledge", exist_ok=True)
        with open("agent_zero/knowledge/tokamak_analysis.md", "w", encoding="utf-8") as f:
            f.write(f"# Tokamak Disruption Analysis Report\n\n## Data Stats\n{data_stats}\n\n## AI Analysis\n{analysis}\n\n## Final Proposed Constants\n{final_constants}")
            
        return final_constants

if __name__ == "__main__":
    # Ensure PYTHONPATH is set so imports work
    analyst = TokamakAnalystJob()
    analyst.run_analysis()
