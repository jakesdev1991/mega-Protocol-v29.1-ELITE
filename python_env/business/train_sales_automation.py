# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
import sys
import json

# Ensure project root is in path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)

from agent_zero.trainer import ModelTrainer

def run_sales_training_loop():
    print("🚀 [Business] Starting Sales Automation Training Loop...")
    trainer = ModelTrainer(data_path="business/knowledge/sales_logs.jsonl")
    
    # Simulate data check
    if trainer.needs_training(min_samples=5):
        trainer.train_specialized_model("sales_pro_v2")
    else:
        print("Business: Not enough sales data yet. Scraper is still gathering leads.")

if __name__ == "__main__":
    run_sales_training_loop()
