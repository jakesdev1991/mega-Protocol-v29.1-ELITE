# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
import sys

# Ensure project root is in path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)

from agent_zero.trainer import ModelTrainer

def run_cross_domain_training_loop():
    print("🚀 [Agent Zero] Starting Cross-Domain Universal Training Loop...")
    # This trains on the central evolution log which contains data from all branches via the UniversalArena
    trainer = ModelTrainer()
    
    if trainer.needs_training(min_samples=20):
        trainer.train_specialized_model("universal_expert_v1")
    else:
        print("Agent Zero: Universal training requires more cross-domain data (SERC-audited).")

if __name__ == "__main__":
    run_cross_domain_training_loop()
