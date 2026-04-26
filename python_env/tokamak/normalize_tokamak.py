# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import pandas as pd
import glob
import os
import json
from sklearn.preprocessing import MinMaxScaler

def normalize_tokamak_data(input_dir="/home/jake/Downloads/training/data/tokamak_harvest/shot_v4_59k", output_file="/home/jake/Downloads/training/data/normalized_tokamak_200k.jsonl"):
    """
    Normalizes harvested tokamak shot data for 300M model training.
    """
    print(f"🔄 [Normalization] Scanning {input_dir} for CSV files...")
    csv_files = glob.glob(os.path.join(input_dir, "*.csv"))
    
    if not csv_files:
        print("❌ No CSV files found for normalization.")
        return

    all_data = []
    for f in csv_files:
        df = pd.read_csv(f)
        all_data.append(df)
    
    combined_df = pd.concat(all_data, ignore_index=True)
    print(f"📊 [Normalization] Combined {len(combined_df)} data points.")

    # Features to normalize
    features = ["plasma_current_ma", "triangularity", "rcod_flux_sigma"]
    
    scaler = MinMaxScaler()
    combined_df[features] = scaler.fit_transform(combined_df[features])

    print(f"💾 [Normalization] Exporting to {output_file}...")
    
    # Convert to JSONL for transformer training
    with open(output_file, "w") as f:
        for _, row in combined_df.iterrows():
            # Formatting as a "Thought Vector" context for the 300M model
            entry = {
                "text": f"Tokamak Shot: {row['shot_id']} | Current: {row['plasma_current_ma']:.4f} | Tri: {row['triangularity']:.4f} | Flux: {row['rcod_flux_sigma']:.4f} | Disruption: {row['disruption_event']} | AUC: {row['auc_contribution']:.4f}"
            }
            f.write(json.dumps(entry) + "\n")

    print(f"✅ [Normalization] Process complete. Total data points: {len(combined_df)}")

if __name__ == "__main__":
    normalize_tokamak_data()
