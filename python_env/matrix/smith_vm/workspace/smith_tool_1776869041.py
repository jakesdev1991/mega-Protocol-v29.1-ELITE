# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol – Strict Math & Constant Validator for Tokamak Governor
--------------------------------------------------------------------
Usage:
    python3 validate_governor.py   # returns PASS/FAIL and prints diagnostics

The script enforces:
  - SHOCK_LIMIT ∈ [0.80, 0.90]   (per Smith’s audit & noise‑immunity trade‑off)
  - VAA_SENSITIVITY ∈ [1.00, 1.20] (upper bound from Smith’s “runaway” limit)
  - MANIFOLD_DIVERGENCE ∈ [0.30, 0.40] (empirical range for DIII‑D fast crashes)
  - AUC projection must be reproducible via a multiplicative gain model:
        AUC_post = AUC_pre * g_SHOCK * g_VAA * g_MANIFOLD
    where each g_* = 1 + delta_* and delta_* is the fractional improvement
    claimed by the Engine (derived from its stated % gains).
  - Omega Physics Rubric compliance must be asserted externally
    (rubric_ok = True) – otherwise the script fails, reminding the auditor
    that invariant‑level checks are required.
"""

from __future__ import annotations
import sys
import math
from dataclasses import dataclass

# ----------------------------------------------------------------------
# Configuration – adjust only if the Omega Protocol updates its bounds
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Bounds:
    SHOCK_LIMIT: tuple[float, float] = (0.80, 0.90)
    VAA_SENSITIVITY: tuple[float, float] = (1.00, 1.20)
    MANIFOLD_DIVERGENCE: tuple[float, float] = (0.30, 0.40)

# ----------------------------------------------------------------------
# Engine's claimed numbers (taken from the provided output & reasoning)
# ----------------------------------------------------------------------
SHOCK_LIMIT_VAL = 0.82          # reduced from 0.85
VAA_SENSITIVITY_VAL = 1.15      # increased from 1.00
MANIFOLD_DIVERGENCE_VAL = 0.35  # raised from 0.30

# Baseline AUCs (from the task description)
AUC_GLOBAL_PRE = 0.6793
AUC_PROBLEM_PRE = 0.3391        # shot T093727

# Engine's claimed post‑optimisation AUCs (as stated in the reasoning)
AUC_GLOBAL_POST_CLAIMED = 0.91
AUC_PROBLEM_POST_CLAIMED = 0.71

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def in_bounds(val: float, bounds: tuple[float, float]) -> bool:
    lo, hi = bounds
    return lo <= val <= hi

def fractional_improvement(pre: float, post: float) -> float:
    """Return (post - pre) / pre  – the fractional gain."""
    if pre == 0:
        raise ValueError("Pre‑value cannot be zero for fractional improvement.")
    return (post - pre) / pre

def multiplicative_gain(frac_imp: float) -> float:
    """Convert fractional improvement to a gain factor (1 + delta)."""
    return 1.0 + frac_imp

def predicted_auc(pre: float, g_shock: float, g_vaa: float, g_man: float) -> float:
    """Simple multiplicative model: each constant contributes an independent gain."""
    return pre * g_shock * g_vaa * g_man

# ----------------------------------------------------------------------
# Main validation
# ----------------------------------------------------------------------
def main() -> None:
    # 1. Constant sanity checks
    const_ok = True
    if not in_bounds(SHOCK_LIMIT_VAL, Bounds.SHOCK_LIMIT):
        print(f"[FAIL] SHOCK_LIMIT={SHOCK_LIMIT_VAL} outside bounds {Bounds.SHOCK_LIMIT}")
        const_ok = False
    if not in_bounds(VAA_SENSITIVITY_VAL, Bounds.VAA_SENSITIVITY):
        print(f"[FAIL] VAA_SENSITIVITY={VAA_SENSITIVITY_VAL} outside bounds {Bounds.VAA_SENSITIVITY}")
        const_ok = False
    if not in_bounds(MANIFOLD_DIVERGENCE_VAL, Bounds.MANIFOLD_DIVERGENCE):
        print(f"[FAIL] MANIFOLD_DIVERGENCE={MANIFOLD_DIVERGENCE_VAL} outside bounds {Bounds.MANIFOLD_DIVERGENCE}")
        const_ok = False

    # 2. Derive fractional improvements from Engine's claimed % gains
    #    (Engine gave: +5.5% from shock, +2.3% from VAA for global AUC;
    #     +109% for problematic shot.)
    #    We back‑calculate the implied gain factors.
    try:
        # Global AUC claimed improvement: 0.6793 → 0.91
        frac_global_claimed = fractional_improvement(AUC_GLOBAL_PRE, AUC_GLOBAL_POST_CLAIMED)
        # Problematic shot claimed improvement: 0.3391 → 0.71
        frac_problem_claimed = fractional_improvement(AUC_PROBLEM_PRE, AUC_PROBLEM_POST_CLAIMED)
    except ValueError as e:
        print(f"[FAIL] Unable to compute fractional improvement: {e}")
        sys.exit(1)

    # Engine's stated component contributions (as percentages)
    shock_pct = 0.055   # +5.5%
    vaa_pct   = 0.023   # +2.3%
    # The remaining improvement is attributed to MANIFOLD_DIVERGENCE (we solve for it)
    # Using multiplicative model: (1+s)*(1+v)*(1+m) = 1 + frac_global_claimed
    g_shock = 1.0 + shock_pct
    g_vaa   = 1.0 + vaa_pct
    g_man_needed = (1.0 + frac_global_claimed) / (g_shock * g_vaa)
    man_pct_needed = g_man_needed - 1.0

    # 3. Predict AUCs using the multiplicative model with the Engine's component gains
    pred_global = predicted_auc(AUC_GLOBAL_PRE, g_shock, g_vaa, g_man_needed)
    pred_problem = predicted_auc(AUC_PROBLEM_PRE, g_shock, g_vaa, g_man_needed)

    # Tolerance for floating‑point comparison
    TOL = 1e-4

    math_ok = True
    if abs(pred_global - AUC_GLOBAL_POST_CLAIMED) > TOL:
        print(f"[FAIL] Global AUC prediction mismatch: "
              f"predicted {pred_global:.6f} vs claimed {AUC_GLOBAL_POST_CLAIMED:.6f}")
        math_ok = False
    if abs(pred_problem - AUC_PROBLEM_POST_CLAIMED) > TOL:
        print(f"[FAIL] Problematic shot AUC prediction mismatch: "
              f"predicted {pred_problem:.6f} vs claimed {AUC_PROBLEM_POST_CLAIMED:.6f}")
        math_ok = False

    # 4. Omega Physics Rubric compliance – must be supplied externally.
    #    For this script we require the caller to set rubric_ok = True
    #    after performing the full invariant check (covariant modes, etc.).
    #    We'll read it from an environment variable for simplicity.
    import os
    rubric_ok_env = os.getenv("OMEGA_RUBRIC_OK", "0").strip()
    rubric_ok = rubric_ok_env == "1"
    if not rubric_ok:
        print("[FAIL] Omega Physics Rubric compliance not asserted. "
              "Set OMEGA_RUBRIC_OK=1 after verifying covariant modes, invariants, "
              "boundaries, entropy, and equation‑level derivation.")
        # Do not fail the whole script on this alone – we still report constant/math status.
        # However, per Meta‑Rules the overall verdict is FAIL if rubric missing.
    
    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print("\n=== Validation Summary ===")
    print(f"Constant sanity      : {'PASS' if const_ok else 'FAIL'}")
    print(f"Math consistency     : {'PASS' if math_ok else 'FAIL'}")
    print(f"Omega Rubric asserted: {'PASS' if rubric_ok else 'FAIL (missing)'}")
    
    overall = const_ok and math_ok and rubric_ok
    print(f"\nOVERALL VERDICT      : {'PASS' if overall else 'FAIL'}")
    sys.exit(0 if overall else 1)

if __name__ == "__main__":
    main()