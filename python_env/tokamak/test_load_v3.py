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
    print(f"List length: {len(pxp)}")
    for i, item in enumerate(pxp):
        print(f"Item {i}: {type(item)}")
        # If it's a PackedFileRecord, it might have a 'content' or something
        if hasattr(item, 'content'):
             print(f"  Has content! Type: {type(item.content)}")
             if isinstance(item.content, (list, tuple, dict)):
                 print(f"  Content size: {len(item.content)}")
        
        # Check for common igor2 record attributes
        for attr in ['recordType', 'name', 'data', 'wave', 'variables']:
            if hasattr(item, attr):
                val = getattr(item, attr)
                print(f"  {attr}: {type(val)}")

except Exception as e:
    print(f"Failed: {e}")
