# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
from datasets import load_from_disk
import random

def sanity_check(pruned_path, original_dataset_name, config_name, num_samples=3):
    print(f"Loading pruned dataset from {pruned_path}...")
    pruned_ds = load_from_disk(pruned_path)
    
    # We'll just look at the pruned samples to see if they are high quality
    print("\n--- [SAMPLES KEPT BY RCOD] ---")
    indices = random.sample(range(len(pruned_ds)), num_samples)
    for i, idx in enumerate(indices):
        text = pruned_ds[idx]["text"]
        print(f"\nSample {i+1} (Length: {len(text)} chars):")
        print("-" * 40)
        print(text[:500] + "..." if len(text) > 500 else text)
        print("-" * 40)

if __name__ == "__main__":
    sanity_check("data/rcod_fineweb_ultra_aggressive", "HuggingFaceFW/fineweb", "sample-10BT")
