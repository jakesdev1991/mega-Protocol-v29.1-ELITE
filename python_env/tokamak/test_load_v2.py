# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import igor2.packed
import numpy as np

file_path = "DS2018-4.pxp"
try:
    pxp = igor2.packed.load(file_path)
    print(f"Type: {type(pxp)}")
    
    if isinstance(pxp, list):
        print(f"List length: {len(pxp)}")
        for i, item in enumerate(pxp[:10]):
            print(f"Item {i}: {type(item)}")
            # Check for attributes
            print(f"  Attributes: {dir(item)}")
            if hasattr(item, 'wave'):
                print(f"  Has wave!")
    elif isinstance(pxp, dict):
        print(f"Dict keys: {list(pxp.keys())}")
    else:
        print(f"Other type: {dir(pxp)}")

except Exception as e:
    print(f"Failed: {e}")
