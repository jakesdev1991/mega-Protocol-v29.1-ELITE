# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import igor2.packed
import pandas as pd
import numpy as np

file_path = "DS2018-4.pxp"
try:
    print(f"Attempting to load {file_path} using igor2.packed.load...")
    pxp = igor2.packed.load(file_path)
    print("Success loading!")
    
    # Let's explore the structure
    def walk_dict(d, indent=0):
        for k, v in d.items():
            print('  ' * indent + str(k))
            if isinstance(v, dict):
                walk_dict(v, indent + 1)
            elif isinstance(v, np.ndarray):
                print('  ' * (indent + 1) + f"Array shape: {v.shape}")

    # pxp is usually a nested dict structure in newer igor2
    # print(pxp.keys())
    
except Exception as e:
    print(f"Failed: {e}")
