# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
import sys
import json
import time
from .agent import Agent
from .llm_router import LLMRouter
from .tools.registry import registry

class SandboxExperimenter:
    """
    Loop 16: The Sandbox Experimentation Loop.
    Operates outside standard boundaries for high-velocity discovery.
    Requires external audit to leave the sandbox.
    """
    def __init__(self):
        self.router = LLMRouter()
        self.neo = Agent("Neo-Experimenter", "experimenter", 
                         "You are Neo in the Sandbox. You work without normal boundaries to find breakthroughs. Use search and tools aggressively.")
        self.smith = Agent("Smith-Guardian", "critic", 
                          "You are Agent Smith in the Sandbox. You monitor Neo and ensure invariants aren't shattered, but you allow high-velocity experimentation within the walls.")
        self.sandbox_log = "python_env/agent_zero/knowledge/sandbox_evolution.jsonl"

    def run_epoch(self):
        print("\n🌪️ [Loop 16] Starting Sandbox Experimentation Epoch...")
        
        # 1. Neo proposes a high-velocity experiment or search goal
        proposal = self.neo.reason("Propose a high-velocity search or experiment goal for the Omega Protocol. Focus on quantum breakthroughs or AI architectural evolution.", aggressive=True)
        print(f"🕶️ [Neo] Proposal: {proposal[:200]}...")

        # 2. Neo executes searches and tools
        # (For this loop, we simulate the agent loop by having it use the searxng tool if needed)
        search_results = registry.invoke("searxng_search", _agent_name="Neo-Experimenter", query="latest quantum gravity computer science breakthroughs 2026")
        print(f"🔍 [SearXNG] Search complete. Results obtained.")

        # 3. Neo synthesizes results
        synthesis = self.neo.reason(f"Synthesize these search results with your proposal:\n{search_results}", aggressive=True)
        
        # 4. Smith Audits the result
        audit = self.smith.reason(f"Audit this Sandbox Synthesis for invariants and safety:\n{synthesis}", aggressive=False)
        print(f"🕴️ [Smith] Audit: {audit[:200]}...")

        # 5. Check if it should "Leave the Sandbox"
        if "REJECT" not in audit:
            print("🚀 [Sandbox] Experiment successful. Storing in Sandbox Log.")
            self._log_experiment(proposal, synthesis, audit)
            
            # 6. Audit to Exit Rule
            self._propose_to_exit(synthesis)
        else:
            print("🧱 [Sandbox] Experiment contained by Smith. Refinement needed.")

    def _log_experiment(self, proposal, synthesis, audit):
        record = {
            "timestamp": time.time(),
            "proposal": proposal,
            "synthesis": synthesis,
            "audit": audit
        }
        with open(self.sandbox_log, "a") as f:
            f.write(json.dumps(record) + "\n")

    def _propose_to_exit(self, synthesis):
        """
        Implements the user's rule: proposed exits must be audited for real-world rules.
        Ambiguous things are shelved for user review.
        """
        print("⚖️ [Sandbox] Evaluating if insight should leave the sandbox...")
        exit_auditor = Agent("Exit-Auditor", "meta_critic", 
                             "You are the Exit Auditor. Evaluate if this insight follows real-world laws and safety rules. Respond with 'EXIT: APPROVED', 'EXIT: AMBIGUOUS (SHELF)', or 'EXIT: DENIED'.")
        
        verdict = exit_auditor.reason(f"Evaluate this Sandbox Insight for real-world application (nothing illegal, safe for reality):\n{synthesis}")
        
        if "EXIT: APPROVED" in verdict:
            print("🔓 [EXIT] Insight approved to leave sandbox. Notifying Matrix Architect.")
        elif "EXIT: AMBIGUOUS" in verdict:
            print("📁 [SHELF] Insight is ambiguous. Shelving for User (Jake) Review.")
            with open("python_env/agent_zero/knowledge/user_review_needed.jsonl", "a") as f:
                f.write(json.dumps({"type": "ambiguous_exit", "content": synthesis, "verdict": verdict}) + "\n")
        else:
            print("🔒 [DENIED] Insight blocked from leaving sandbox.")

if __name__ == "__main__":
    ex = SandboxExperimenter()
    while True:
        try:
            ex.run_epoch()
            time.sleep(3600) # Run every hour
        except Exception as e:
            print(f"Error in Sandbox Loop: {e}")
            time.sleep(60)
