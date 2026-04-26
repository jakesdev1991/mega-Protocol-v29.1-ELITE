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
    
    # Target root/Figure20/Ip
    ip_wave = root[b'Figure20'][b'Ip']
    print(f"Type: {type(ip_wave)}")
    print(f"Attributes: {dir(ip_wave)}")
    
    if hasattr(ip_wave, 'wData'):
        print(f"wData type: {type(ip_wave.wData)}")
        if isinstance(ip_wave.wData, np.ndarray):
            print(f"wData shape: {ip_wave.wData.shape}")

except Exception as e:
    print(f"Failed: {e}")
