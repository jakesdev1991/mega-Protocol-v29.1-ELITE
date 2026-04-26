# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import time
import os
import sys
import subprocess

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

from biology.co_evolution_loop import main as co_evo_main

def run_epoch(rounds=2):
    """
    Biology Evolution Trainer Epoch.
    Runs a fixed number of rounds and then exits.
    """
    print(f"🧬 [Biology Evolution] Starting {rounds}-round evolution epoch...")
    for round_num in range(1, rounds + 1):
        print(f"\n--- Co-Evolution Round {round_num} ---")
        try:
            co_evo_main()
        except Exception as e:
            print(f"Error in co-evolution: {e}")
        
        if round_num < rounds:
            print("Waiting 5 seconds before next round...")
            time.sleep(5)
    
    print("\n🧬 [Biology Evolution] Epoch Complete.")

if __name__ == "__main__":
    run_epoch()