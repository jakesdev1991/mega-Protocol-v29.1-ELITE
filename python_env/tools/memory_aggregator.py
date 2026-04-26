# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import psutil
from collections import defaultdict

def aggregate_memory():
    totals = defaultdict(float)
    counts = defaultdict(int)
    
    for proc in psutil.process_iter(['name', 'memory_info']):
        try:
            name = proc.info['name']
            mem = proc.info['memory_info'].rss / (1024 * 1024 * 1024) # GB
            totals[name] += mem
            counts[name] += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
            
    print("\n" + "="*50)
    print(f"{'Process Family':<25} | {'Count':<8} | {'Total RAM (GB)':<15}")
    print("="*50)
    
    # Sort by memory
    sorted_families = sorted(totals.items(), key=lambda x: x[1], reverse=True)
    
    for name, mem in sorted_families[:15]:
        if mem > 0.01:
            print(f"{name:<25} | {counts[name]:<8} | {mem:.2f} GB")
    
    total_found = sum(totals.values())
    print("="*50)
    print(f"Total Aggregated RAM: {total_found:.2f} GB")

if __name__ == "__main__":
    aggregate_memory()
