# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import pandas as pd
import os

csv_path = "Tokamak_Data_Extracted.csv"
if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    for col in df.columns:
        valid_count = df[col].dropna().count()
        if valid_count > 100:
            print(f"{col}: {valid_count} points")
