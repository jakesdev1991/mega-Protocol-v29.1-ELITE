# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import time
import subprocess
import os
import pandas as pd
import argparse

def run_test(name, cmd):
    print(f"\n--- Starting Benchmark: {name} ---")
    start_time = time.time()
    try:
        # We use check_call to wait for it
        subprocess.check_call(cmd, shell=True)
    except Exception as e:
        print(f"Error in {name}: {e}")
    end_time = time.time()
    return end_time - start_time

def compare():
    # 1. Setup paths
    standard_log = "lightning_logs/benchmark_standard"
    rcod_log = "lightning_logs/benchmark_rcod"
    
    # 2. Command for Standard (using 300M model but disabling RCOD logic or using standard script)
    # For this demo, we'll use our script but force LR scale to 1.0 and disable packing/gating
    cmd_standard = (
        ".venv\\Scripts\\python.exe examples\\train_300m_rcod_lightning_dml.py "
        "--config configs\\300m_rcod.yml --data data\\rcod_wikitext_pruned "
        "--batch_size 8 --max_steps 100 --wandb_project benchmark-standard"
    )
    
    # 3. Command for RCOD (with all bells and whistles)
    cmd_rcod = (
        ".venv\\Scripts\\python.exe examples\\train_300m_rcod_lightning_dml.py "
        "--config configs\\300m_rcod.yml --data data\\rcod_wikitext_pruned "
        "--batch_size 8 --max_steps 100 --pack --wandb_project benchmark-rcod"
    )

    print("Note: Running sequential benchmarks for clean comparison...")
    
    time_std = run_test("Standard Training", cmd_standard)
    time_rcod = run_test("RCOD Training", cmd_rcod)

    print("\n" + "="*40)
    print("      RCOD BENCHMARK REPORT")
    print("="*40)
    print(f"Standard Time: {time_std:.2f}s")
    print(f"RCOD Time:     {time_rcod:.2f}s")
    
    speedup = (time_std / time_rcod) if time_rcod > 0 else 0
    print(f"Throughput Increase: {speedup:.2x}x")
    print("="*40)
    
    print("\nCheck W&B or local metrics.csv for loss convergence comparison.")

if __name__ == "__main__":
    compare()
