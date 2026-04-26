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
    records = pxp[0]
    vars_folders = pxp[1]
    
    print(f"Records list length: {len(records)}")
    print(f"Variables/Folders dict keys: {list(vars_folders.keys())}")
    
    # Check first few records
    for i, r in enumerate(records[:20]):
        print(f"Record {i}: {type(r)}")
        if hasattr(r, 'wave'):
            print(f"  Wave: {r.wave.wave_header.bname.decode('utf-8')}")

except Exception as e:
    print(f"Failed: {e}")
