# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import pandas as pd
import numpy as np
import os

def get_tokamak_summary():
    csv_path = "tokamak/Tokamak_Data_Extracted.csv"
    if not os.path.exists(csv_path):
        return "Data not found."
    
    df = pd.read_csv(csv_path)
    # Target some key sensors
    sensors = [
        "Figure11/T094124/PlasmaRogA",
        "Figure20/Ip",
        "Figure18/T092680/OTor3"
    ]
    
    summary = "### TOKAMAK SENSOR SUMMARY ###\n"
    for s in sensors:
        if s in df.columns:
            data = df[s].dropna()
            summary += f"Sensor: {s}\n"
            summary += f"- Count: {len(data)}\n"
            summary += f"- Mean: {data.mean():.4f}\n"
            summary += f"- Std: {data.std():.4f}\n"
            summary += f"- Max Delta (Slew): {data.diff().abs().max():.4f}\n\n"
            
    return summary

if __name__ == "__main__":
    print(get_tokamak_summary())
