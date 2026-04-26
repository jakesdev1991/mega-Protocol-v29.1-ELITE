# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
import sys
import time
import json
import re

# Ensure project root is in path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(PROJECT_ROOT)

from python_env.agent_zero.llm_router import LLMRouter

class MatrixActiveAssister:
    """
    Watches the Omega Protocol loggers in real-time and tasks Neo/Smith 
    with helping the Lead Architect refine mathematical derivations.
    """
    def __init__(self, target_log):
        self.target_log = target_log
        self.router = LLMRouter()
        self.last_pos = 0
        
        self.neo_sys = """You are Neo, The Anomaly. You are observing the Lead Architect's TOE derivation in real-time. 
Your goal is to suggest disruptive, non-linear mathematical shortcuts and path-identity proofs that shatter conventional constraints. 
Provide a concise 'NEO_INSIGHT' to help the Architect unify physics and information geometry."""
        
        self.smith_sys = """You are Agent Smith, The Guardian. You are observing the Lead Architect's TOE derivation in real-time. 
Your goal is to ruthlessly enforce mathematical rigor, ensure PSD constraints are met, and prevent any informational leaks or super-quantum anomalies. 
Provide a concise 'SMITH_AUDIT' to keep the Architect grounded in strict mathematical physics bounds."""

    def watch(self):
        print(f"👁️  Matrix Active Assister watching: {self.target_log}")
        while True:
            if os.path.exists(self.target_log):
                with open(self.target_log, 'r', encoding='utf-8') as f:
                    f.seek(self.last_pos)
                    new_data = f.read()
                    self.last_pos = f.tell()
                    
                    if new_data:
                        # Extract the last few lines or sections of interest
                        snippet = new_data.strip()[-1500:]
                        if snippet:
                            print(f"\n📢 [Assister] New data detected. Tasking Neo and Smith...")
                            
                            # Neo's Insight
                            neo_insight = self.router.generate("architect", f"Recent Architect Output:\n{snippet}\n\nWhat is your disruptive insight?", self.neo_sys)
                            print(f"🕶️  [Neo]: {neo_insight[:150]}...")
                            
                            # Smith's Audit
                            smith_audit = self.router.generate("critic", f"Recent Architect Output:\n{snippet}\n\nWhat is your rigorous audit?", self.smith_sys)
                            print(f"🕴️  [Smith]: {smith_audit[:150]}...")
                            
                            # Log their interaction
                            with open(os.path.join(PROJECT_ROOT, "logs/loops/matrix_assistance_toe.log"), "a", encoding="utf-8") as al:
                                al.write(f"--- ASSISTANCE CYCLE {time.time()} ---\n")
                                al.write(f"[NEO_INSIGHT]: {neo_insight}\n")
                                al.write(f"[SMITH_AUDIT]: {smith_audit}\n\n")
            
            time.sleep(15)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python active_assister.py <target_log_path>")
        sys.exit(1)
        
    assister = MatrixActiveAssister(sys.argv[1])
    assister.watch()
