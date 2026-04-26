# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Ω‑Protocol invariant validator for TDIS‑Ω.
Checks:
  1. Conservation of the backup current J^μ.
  2. Equality of the two definitions of ψ_backup.
Usage:
    python validate_tdis_omega.py --data backup_data.npz
The NPZ file should contain arrays:
    time   : 1D array of timestamps (seconds)
    PhiN   : Φ_N^{backup}(t)
    PhiD   : Φ_Δ^{backup}(t)
    Pers1  : Persistence_1(t)
    Pers0  : scalar Persistence_0 (constant)
    Sbackup: S_backup(t)
    BII    : Backup Integrity Index (optional, for extra sanity)
"""

import numpy as np
import argparse
import sys

def parse_args():
    p = argparse.ArgumentParser(description="Validate TDIS‑Ω Ω‑Protocol invariants")
    p.add_argument("--data", required=True, help="NPZ file with timeseries data")
    p.add_argument("--tol_J", type=float, default=1e-6,
                   help="Absolute tolerance for ∂_μ J^μ (default: 1e-6)")
    p.add_argument("--tol_psi", type=float, default=1e-6,
                   help="Absolute tolerance for ψ_backup equality (default: 1e-6)")
    return p.parse_args()

def load_data(npz_path):
    try:
        d = np.load(npz_path)
    except Exception as e:
        sys.exit(f"Failed to load {npz_path}: {e}")
    required = ["time", "PhiN", "PhiD", "Pers1", "Pers0", "Sbackup"]
    for k in required:
        if k not in d:
            sys.exit(f"Missing required array '{k}' in {npz_path}")
    return {k: d[k] for k in required}

def finite_difference(arr, dt):
    """First‑order forward difference; returns same shape with last element set to NaN."""
    deriv = np.empty_like(arr)
    deriv[:-1] = (arr[1:] - arr[:-1]) / dt
    deriv[-1] = np.nan
    return deriv

def main():
    args = parse_args()
    data = load_data(args.data)

    t = data["time"]
    if t.ndim != 1:
        sys.exit("Time array must be 1‑D")
    dt = np.diff(t)
    if not np.allclose(dt, dt[0]):
        sys.exit("Non‑uniform time spacing not supported in this simple validator")
    dt = dt[0]

    PhiN = data["PhiN"]
    PhiD = data["PhiD"]
    Pers1 = data["Pers1"]
    Pers0 = float(data["Pers0"])   # expect scalar
    Sbackup = data["Sbackup"]

    # ------------------------------------------------------------------
    # 1. Current conservation: J^μ = sqrt(2) * Φ_Δ * δ^μ_0
    #    ∂_μ J^μ = ∂_0 (sqrt(2) * Φ_Δ)  (spatial parts zero)
    # ------------------------------------------------------------------
    J0 = np.sqrt(2.0) * PhiD               # time component only
    dJ0_dt = finite_difference(J0, dt)    # ∂_0 J^0
    # For a conserved current we require ∂_μ J^μ = 0 → dJ0_dt ≈ 0
    max_div = np.nanmax(np.abs(dJ0_dt))
    print(f"[Current] max |∂_μ J^μ| = {max_div:.3e}")
    if max_div > args.tol_J:
        print(f"[FAIL] Current non‑conservation exceeds tolerance {args.tol_J}")
        sys.exit(1)
    else:
        print("[PASS] Current conservation satisfied.")

    # ------------------------------------------------------------------
    # 2. ψ_backup invariant equivalence
    #    ψ1 = ln(Φ_N/Φ_N0)   with Φ_N0 = Φ_N(t=0) (or a reference value)
    #    ψ2 = ln(Persistence_1 / Persistence_0)
    # ------------------------------------------------------------------
    PhiN0 = PhiN[0]   # reference at t=0; could also be a prescribed constant
    psi1 = np.log(PhiN / PhiN0)
    psi2 = np.log(Pers1 / Pers0)
    diff_psi = np.abs(psi1 - psi2)
    max_psi = np.nanmax(diff_psi)
    print(f"[ψ] max |ψ1 - ψ2| = {max_psi:.3e}")
    if max_psi > args.tol_psi:
        print(f"[FAIL] ψ_backup invariant mismatch exceeds tolerance {args.tol_psi}")
        sys.exit(1)
    else:
        print("[PASS] ψ_backup invariant satisfied.")

    # Optional extra sanity: BII bounds
    if "BII" in data:
        BII = data["BII"]
        if np.any((BII < 0) | (BII > 1)):
            print("[WARN] BII values outside [0,1] range detected.")
        else:
            print("[INFO] BII within expected bounds.")

    print("\nAll Ω‑Protocol invariant checks passed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())