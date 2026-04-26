# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
TLSM-Ω mathematical invariant validator.
Checks:
    0 <= LSI <= 3.0
    0 <= Phi_N <= 0.85
    0 <= Phi_Delta <= 0.7
Using the formulas and parameters from the proposal.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# ----------------------------------------------------------------------
# Configuration (as per proposal)
# ----------------------------------------------------------------------
DELTA_T_DAYS = 30               # LSI window
LSI_CRIT = 2.5                  # critical threshold
ETA_N = 0.2                     # eta_1 in Phi_N
ETA_D1 = 0.15                   # eta_2 in Phi_Delta
ETA_D2 = 0.02                   # eta_3 in Phi_Delta
TAU1 = 60   # days ≈ 2 months
TAU2 = 30   # days ≈ 1 month
TAU3 = 90   # days ≈ 3 months
BASE_PHI_N = 0.4                # Phi_N^{(0)}
BASE_PHI_D = 0.3                # Phi_Delta^{(0)}

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def compute_lsi(leaks_df, reference_time):
    """
    leaks_df: DataFrame with columns ['leak_time','firm','scale','conf']
    reference_time: datetime, end of the window (window = [ref-DeltaT, ref])
    Returns LSI for that window.
    """
    start = reference_time - timedelta(days=DELTA_T_DAYS)
    window = leaks_df[(leaks_df['leak_time'] >= start) &
                      (leaks_df['leak_time'] < reference_time)]
    if window.empty:
        return 0.0
    N_leaks = window['firm'].nunique()          # unique firms with at least one leak
    # sum over all leak entries (not just unique firms) as per formula
    sum_SC = (window['scale'] * window['conf']).sum()
    N_firms = window['firm'].nunique()
    # Avoid division by zero
    if N_firms == 0:
        return 0.0
    lsi = (len(window) / DELTA_T_DAYS) * (sum_SC / N_firms)
    return lsi

def phi_n(lsi_val):
    return BASE_PHI_N + ETA_N * np.tanh(lsi_val / LSI_CRIT)

def phi_delta(lsi_val):
    return BASE_PHI_D + ETA_D1 * lsi_val - ETA_D2 * (lsi_val ** 2)

# ----------------------------------------------------------------------
# Synthetic data generator (for demonstration)
# ----------------------------------------------------------------------
def generate_synthetic_leaks(n_leaks=200, seed=42):
    np.random.seed(seed)
    start_date = datetime(2024, 1, 1)
    leaks = []
    firms = [f'Firm_{i}' for i in range(1, 6)]  # 5 firms
    for _ in range(n_leaks):
        firm = np.random.choice(firms)
        # leak time uniformly over 12 months
        leak_time = start_date + timedelta(days=np.random.randint(0, 365))
        # scale: normalised FLOPs (0.5–2.0)
        scale = np.random.uniform(0.5, 2.0)
        # confidentiality: 1,2,3 with weights
        conf = np.random.choice([1, 2, 3], p=[0.5, 0.3, 0.2])
        leaks.append({
            'leak_time': leak_time,
            'firm': firm,
            'scale': scale,
            'conf': conf
        })
    return pd.DataFrame(leaks)

# ----------------------------------------------------------------------
# Validation routine
# ----------------------------------------------------------------------
def validate_tlsm():
    leaks_df = generate_synthetic_leaks()
    # Sort by time for rolling window
    leaks_df = leaks_df.sort_values('leak_time').reset_index(drop=True)

    # We'll evaluate LSI at each leak timestamp (could also evaluate daily)
    violations = []
    for idx, row in leaks_df.iterrows():
        ref_time = row['leak_time']
        lsi = compute_lsi(leaks_df, ref_time)
        phi_n_val = phi_n(lsi)
        phi_d_val = phi_delta(lsi)

        # Invariant checks
        if not (0.0 <= lsi <= 3.0):
            violations.append((ref_time, f"LSI out of bounds: {lsi:.3f}"))
        if not (0.0 <= phi_n_val <= 0.85):
            violations.append((ref_time, f"Phi_N out of bounds: {phi_n_val:.3f}"))
        if not (0.0 <= phi_d_val <= 0.7):
            violations.append((ref_time, f"Phi_Delta out of bounds: {phi_d_val:.3f}"))

    if violations:
        print("❌ INVARIANT VIOLATIONS DETECTED:")
        for ts, msg in violations[:10]:  # show first 10
            print(f"  {ts}: {msg}")
        if len(violations) > 10:
            print(f"  ... and {len(violations)-10} more")
        raise AssertionError("TLSM-Ω protocol invariants violated.")
    else:
        print("✅ All Ω‑invariants satisfied for synthetic data.")
        # Additionally report statistics
        lsi_vals = [compute_lsi(leaks_df, t) for t in leaks_df['leak_time']]
        print(f"   LSI stats: min={np.min(lsi_vals):.3f}, "
              f"mean={np.mean(lsi_vals):.3f}, max={np.max(lsi_vals):.3f}")
        print(f"   Phi_N stats: min={np.min([phi_n(v) for v in lsi_vals]):.3f}, "
              f"mean={np.mean([phi_n(v) for v in lsi_vals]):.3f}, "
              f"max={np.max([phi_n(v) for v in lsi_vals]):.3f}")
        print(f"   Phi_D stats: min={np.min([phi_d(v) for v in lsi_vals]):.3f}, "
              f"mean={np.mean([phi_d(v) for v in lsi_vals]):.3f}, "
              f"max={np.max([phi_d(v) for v in lsi_vals]):.3f}")

if __name__ == "__main__":
    validate_tlsm()