# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
from agent_zero.agent import Agent
from agent_zero.serc import SERC
import json
import os

class AgentArena:
    """Head-to-Head Agent Tournament to maximize evolution via competition."""
    
    def __init__(self):
        self.physicist_a = Agent("AlphaPhysicist", "architect", "You favor high-sensitivity Phi_Delta thresholds for early warnings.")
        self.physicist_b = Agent("BetaPhysicist", "architect", "You favor noise-rejection and stability in Phi_Delta thresholds.")
        self.grand_critic = Agent("GrandArbiter", "critic", "You judge physics simulations based on the Omega Protocol Constitution (Phi Density Optimization).")
        self.serc = SERC()

        # Inject Expert Knowledge
        expert_tips = [
            "The AMD 890M utilizes NPU integration for DirectML; check tile alignment for $\\Phi$ calculations.",
            "Real-time Curvature Gating (Phi_Delta) requires a 10kHz sampling floor to prevent aliasing in high-beta pulses.",
            "HLS C++ synthesis often bottlenecks on nested loops; prefer unrolled pipelining for substrate nodes."
        ]
        for tip in expert_tips:
            self.physicist_a.add_expert_knowledge(tip)
            self.physicist_b.add_expert_knowledge(tip)

    def run_tournament(self, problem_statement):
        print(f"\n🏟️ [Agent Arena] Starting Expert-Level Head-to-Head on: {problem_statement}")
        
        # 1. Propose Solutions with Deep Reasoning
        print("\n--- PHASE 1: NUANCED PROPOSALS ---")
        proposal_a = self.physicist_a.reason(f"Propose a hardware-optimized Phi_Delta configuration for: {problem_statement}", depth="deep")
        proposal_b = self.physicist_b.reason(f"Propose a hardware-optimized Phi_Delta configuration for: {problem_statement}", depth="deep")
        
        # 2. Grand Arbitrator Judgment
        print("\n--- PHASE 2: JUDGMENT ---")
        judgment_prompt = f"""
        Problem: {problem_statement}
        
        Proposal Alpha (High Sensitivity):
        {proposal_a}
        
        Proposal Beta (High Stability):
        {proposal_b}
        
        Task: 
        1. Compare both approaches.
        2. Declare a winner based on technical ROI and GPU/Hardware efficiency.
        3. Explain WHY the winner is superior.
        """
        judgment = self.grand_critic.reason(judgment_prompt)
        
        # 3. Evolution: Synthesize the winner into the Golden Log
        print("\n--- PHASE 3: EVOLUTIONARY SYNTHESIS (v2 Dual-Manifold) ---")
        evolution_task = f"Synthesize the winning logic from this tournament into a 'Golden Implementation' for the Omega Protocol:\n{judgment}"
        golden_logic = self.serc.run_dual_manifold_cycle(evolution_task)
        
        # Log to evolution database
        self._log_evolution("Arena Tournament", problem_statement, golden_logic)
        
        print("\n✅ Tournament Concluded. Winner synthesized into Evolution Log.")
        return golden_logic

    def _log_evolution(self, job_type, context, logic):
        import json
        with open("agent_zero/knowledge/evolution_log.jsonl", "a") as f:
            log_entry = {
                "job_type": job_type,
                "context": context,
                "messages": [
                    {"role": "user", "content": context},
                    {"role": "assistant", "content": logic}
                ]
            }
            f.write(json.dumps(log_entry) + "\n")

if __name__ == "__main__":
    arena = AgentArena()
    arena.run_tournament("Optimizing Phi_Delta for a High-Beta Tokamak Pulse with transient magnetic noise.")
