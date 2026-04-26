# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
from datasets import load_from_disk
import os

data_dir = "data"
for d in os.listdir(data_dir):
    path = os.path.join(data_dir, d)
    if os.path.isdir(path):
        try:
            ds = load_from_disk(path)
            print(f"{d}: {len(ds)} samples")
        except Exception as e:
            print(f"{d}: Error loading: {e}")
