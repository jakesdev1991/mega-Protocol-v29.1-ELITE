# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
import sys
import time

# Ensure project root is in path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(PROJECT_ROOT)

from agent_zero.agent import Agent
from agent_zero.serc import SERC
from agent_zero.tokamak_combat import ArxivScraper

class TokamakHarvestJob:
    """
    New Job: Harvests latest fusion research and tests it against 
    the Omega Protocol's new Phi_Delta (Conjugate Dynamics) framework.
    """
    def __init__(self):
        self.scraper = ArxivScraper()
        self.serc = SERC()
        # Override scraper queries to focus on Tokamak + Phi_Delta physics
        self.scraper.queries = [
            "tokamak plasma disruption",
            "magnetic confinement stability",
            "reverse chain overlap density",
            "informational asymmetry tensor plasma",
            "bi-scalar omega action fusion",
            "plasma flux parity violation"
        ]

    def run_harvest_and_test(self, count=1):
        print(f"📡 [TokamakHarvest] Starting harvest of {count} papers...")
        
        for i in range(count):
            print(f"\n--- PAPER {i+1}/{count} ---")
            paper = self.scraper.fetch_next_paper()
            if not paper:
                print("⚠️ No paper found, skipping.")
                continue
            
            # The Task: Test this research against the NEW Section 4 (Conjugate Dynamics)
            task = f"""
            Analyze this research paper in the context of the NEW Omega Protocol Section 4 (Conjugate Dynamics).
            
            PAPER DATA:
            {paper}
            
            OBJECTIVE:
            1. Identify if the reported plasma phenomena can be modeled as a breakdown of the 
               forward/reverse informational flux (Phi+ / Phi-) handshake.
            2. Calculate the theoretical Informational Asymmetry Tensor (Delta_AB) for this scenario.
            3. Propose an update to the 'tokamak/Governor.hpp' constants based on this Delta_AB mapping.
            
            STRICT COMPLIANCE: 
            Use the Dual-Manifold runtime to ensure both Constructive and Anti-Agency viewpoints are captured.
            """
            
            print("🚀 [TokamakHarvest] Launching Dual-Manifold Co-evolution Loop...")
            try:
                # This invokes the v2 runtime (evolve_task)
                result = self.serc.run_dual_manifold_cycle(task)
                
                print("\n--- DUAL-MANIFOLD RESULT ---")
                print(result)
                
                # Log to special knowledge file
                os.makedirs("agent_zero/knowledge", exist_ok=True)
                with open("agent_zero/knowledge/tokamak_rcod_tests.md", "a", encoding="utf-8") as f:
                    f.write(f"\n\n## Test Run {time.ctime()}\n### Paper\n{paper}\n### Result\n{result}")
                
            except Exception as e:
                print(f"❌ Error in dual-manifold cycle: {e}")

if __name__ == "__main__":
    job = TokamakHarvestJob()
    job.run_harvest_and_test(count=1)
