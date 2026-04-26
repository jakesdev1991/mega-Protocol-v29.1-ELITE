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
    root = pxp[1]['root']
    
    def explore(node, depth=0):
        if depth > 2: return
        if isinstance(node, dict):
            for k in node.keys():
                print("  " * depth + str(k))
                explore(node[k], depth + 1)
        else:
            print("  " * depth + f"Leaf: {type(node)}")

    explore(root)

except Exception as e:
    print(f"Failed: {e}")
