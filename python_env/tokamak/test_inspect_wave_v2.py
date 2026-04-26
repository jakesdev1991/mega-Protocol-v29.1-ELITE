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
    
    if hasattr(ip_wave, 'wave'):
        print(f"wave type: {type(ip_wave.wave)}")
        if hasattr(ip_wave.wave, 'wData'):
            print(f"wave.wData shape: {ip_wave.wave.wData.shape}")
            
    if hasattr(ip_wave, 'data'):
        print(f"data type: {type(ip_wave.data)}")
        if isinstance(ip_wave.data, np.ndarray):
            print(f"data shape: {ip_wave.data.shape}")

except Exception as e:
    print(f"Failed: {e}")
