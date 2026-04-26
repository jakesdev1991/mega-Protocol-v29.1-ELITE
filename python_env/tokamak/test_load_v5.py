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
    
    def walk_tree(node, path="root"):
        if isinstance(node, dict):
            print(f"Folder: {path}")
            # In igor2, folders often have 'Waves' and 'Variables' keys
            if 'Waves' in node:
                print(f"  Found Waves in {path}: {list(node['Waves'].keys())}")
            if 'Variables' in node:
                # print(f"  Found Variables in {path}: {list(node['Variables'].keys())}")
                pass
            
            for k, v in node.items():
                if k not in ['Waves', 'Variables', 'Data', 'Header']:
                    walk_tree(v, f"{path}/{k}")
        
    walk_tree(root)

except Exception as e:
    print(f"Failed: {e}")
    import traceback
    traceback.print_exc()
