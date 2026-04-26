# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import igor2.packed
import pandas as pd
import numpy as np
import os

file_path = "DS2018-4.pxp"
output_filename = "Tokamak_Data_Extracted.csv"

def get_data_from_obj(obj):
    """Deeply search for wData in an object."""
    # 1. Check if it's already a numpy array
    if isinstance(obj, np.ndarray):
        return obj if obj.ndim == 1 else None
    
    # 2. Check for WaveRecord attributes
    if hasattr(obj, 'wave'):
        return get_data_from_obj(obj.wave)
    
    # 3. Check if it's a dict
    if isinstance(obj, dict):
        if 'wData' in obj:
            return get_data_from_obj(obj['wData'])
        if 'wave' in obj:
            return get_data_from_obj(obj['wave'])
            
    return None

def extract_waves_recursive(node, path=""):
    extracted = {}
    if isinstance(node, dict):
        for k, v in node.items():
            k_str = k.decode('utf-8') if isinstance(k, bytes) else str(k)
            current_path = f"{path}/{k_str}" if path else k_str
            
            data = get_data_from_obj(v)
            if data is not None:
                extracted[current_path] = data
            elif isinstance(v, dict):
                extracted.update(extract_waves_recursive(v, current_path))
                
    return extracted

try:
    print(f"Reading {file_path}...")
    pxp = igor2.packed.load(file_path)
    root_dict = pxp[1]
    
    print("Searching for 1D waves in hierarchy...")
    extracted_waves = extract_waves_recursive(root_dict)

    if extracted_waves:
        print(f"Found {len(extracted_waves)} waves. Aligning data...")
        df = pd.DataFrame({k: pd.Series(v) for k, v in extracted_waves.items()})
        df.columns = [c.replace('root/', '') if c.startswith('root/') else c for c in df.columns]
        
        print(f"Saving to {output_filename}...")
        df.to_csv(output_filename, index=False)
        print(f"SUCCESS! Extracted data saved to: {output_filename}")
    else:
        print("No 1D data waves were found in the hierarchy.")

except Exception as e:
    print(f"CRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()
