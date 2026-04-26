# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Financial Config Validator
-----------------------------------------
Validates that a financial configuration state adheres to the
Omega Protocol invariants (Rubric §6, Smith Audit v65.0, Root Kernel UIPO v65.0).

Usage:
    python3 omega_finance_validator.py  --cod 0.88 --psi_int 0.96 \
        --h_vol 0.42 --xi_config 0.30 --z_liquidity 0.50 --theta_leak 0.20 \
        --fidelity 0.90

Returns:
    PASS if all invariants hold, FAIL with reason otherwise.
"""

import argparse
import math
import sys

# --- Omega Protocol Constants (Root Kernel UIPO v65.0) ---
LAMBDA = 0.5   # volatility penalty
KAPPA  = 0.5   # config stiffness penalty
LAMBDA_LEAK = 0.3  # exposure penalty (lambda in original text)

# Hard gates / thresholds
PSI_INTEGRITY_MIN = 0.95   # Invariant: solvency floor (independent)
COD_ACTION_MIN    = 0.85   # Invariant: alignment threshold for action
COD_FLOOR         = 0.39   # Invariant: identity continuity floor (used for phi_N safety)
H_VOL_MIN, H_VOL_MAX = 0.15, 0.80  # Uncertainty band
XI_CONFIG_MAX_DELTA = 0.10   # Stiffness-impedance match: Xi <= Z_liq + delta
THETA_LEAK_MAX    = 0.50   # Environmental cap
PHI_DELTA_MAX_FACTOR = 0.50  # Asymmetry control (phi_delta < factor * phi_N)

def in_bounds(val, name):
    """Check that val is a float in [0,1]."""
    if not isinstance(val, (int, float)):
        raise TypeError(f"{name} must be numeric")
    if not (0.0 <= val <= 1.0):
        return False
    return True

def compute_fidelity(exec_vec, book_vec):
    """
    Compute fidelity term |<P_exec|Psi_book>|^2.
    For simplicity we accept pre‑computed fidelity in [0,1].
    In a full implementation this would be the squared overlap of
    normalized complex vectors.
    """
    # Placeholder: assume caller provides fidelity directly.
    raise NotImplementedError("Provide fidelity as argument; this helper is for illustration.")

def validate_state(
    fidelity,
    h_vol,
    xi_config,
    z_liquidity,
    theta_leak,
    psi_integrity,
    verbose=False
):
    """
    Core validation routine.
    Returns (bool_pass, str_reason).
    """
    # 1. Bounds checks for all primitive variables
    vars_to_check = [
        ("h_vol", h_vol),
        ("xi_config", xi_config),
        ("z_liquidity", z_liquidity),
        ("theta_leak", theta_leak),
        ("psi_integrity", psi_integrity),
        ("fidelity", fidelity),
    ]
    for name, val in vars_to_check:
        if not in_bounds(val, name):
            return False, f"Variable {name}={val} out of bounds [0,1]"

    # 2. Compute COD using the exact Root Kernel formula
    vol_penalty   = math.exp(-LAMBDA * h_vol)
    stiff_penalty = math.exp(-KAPPA * xi_config)
    leak_penalty  = math.exp(-LAMBDA_LEAK * theta_leak)
    cod = fidelity * vol_penalty * stiff_penalty * leak_penalty

    # Clip to [0,1] for safety (should already be in range if inputs are)
    cod = max(0.0, min(1.0, cod))

    if verbose:
        print(f"[DEBUG] Computed COD = {cod:.6f}")

    # 3. Hard gate: Solvency floor (independent of COD)
    if psi_integrity < PSI_INTEGRITY_MIN:
        return False, f"Solvency breach: psi_integrity={psi_integrity:.3f} < {PSI_INTEGRITY_MIN}"

    # 4. Hard gate: Alignment threshold for permitted action
    if cod < COD_ACTION_MIN:
        return False, f"Insufficient alignment: COD={cod:.3f} < {COD_ACTION_MIN} (trading must be halted/frozen)"

    # 5. Uncertainty band (H_vol)
    if not (H_VOL_MIN <= h_vol <= H_VOL_MAX):
        return False, f"H_vol={h_vol:.3f} outside uncertainty band [{H_VOL_MIN},{H_VOL_MAX}]"

    # 6. Stiffness-impedance match
    if xi_config > z_liquidity + XI_CONFIG_MAX_DELTA:
        return False, f"Stiffness overshoot: xi_config={xi_config:.3f} > z_liquidity+delta={z_liquidity+XI_CONFIG_MAX_DELTA:.3f}"

    # 7. Environmental cap (exposure)
    if theta_leak > THETA_LEAK_MAX:
        return False, f"Exposure breach: theta_leak={theta_leak:.3f} > {THETA_LEAK_MAX}"

    # 8. Identity metric check (phi_N must be bounded [0,1])
    # We adopt the protocol‑safe definition: phi_N = COD (or any monotonic [0,1] transform).
    phi_N = cod  # bounded by construction
    if not (0.0 <= phi_N <= 1.0):
        return False, f"Identity metric phi_N={phi_N:.3f} out of [0,1]"

    # 9. Asymmetry check (phi_delta < PHI_DELTA_MAX * phi_N)
    # phi_delta = phi_N * tanh((xi_config - z_liquidity)/3.0)  (from UIPO v65.0)
    phi_delta = phi_N * math.tanh((xi_config - z_liquidity) / 3.0)
    if phi_delta >= PHI_DELTA_MAX_FACTOR * phi_N:
        return False, f"Asymmetry violation: phi_delta={phi_delta:.3f} >= {PHI_DELTA_MAX_FACTOR}*phi_N={PHI_DELTA_MAX_FACTOR*phi_N:.3f}"

    # All checks passed
    return True, "All Omega Protocol invariants satisfied."

def main():
    parser = argparse.ArgumentParser(description="Validate Omega Protocol financial config state.")
    parser.add_argument("--fidelity", type=float, required=True,
                        help="Fidelity term |<P_exec|Psi_book>|^2 in [0,1]")
    parser.add_argument("--h_vol", type=float, required=True,
                        help="Volatility entropy H_vol in [0,1]")
    parser.add_argument("--xi_config", type=float, required=True,
                        help="Config stiffness Xi_config in [0,1]")
    parser.add_argument("--z_liquidity", type=float, required=True,
                        help="Market depth/trust Z_liquidity in [0,1]")
    parser.add_argument("--theta_leak", type=float, required=True,
                        help="Configuration exposure riskTheta_leak in [0,1]")
    parser.add_argument("--psi_integrity", type=float, required=True,
                        help="Solvency/integrity continuity in [0,1]")
    parser.add_argument("--verbose", action="store_true",
                        help="Print debug information")
    args = parser.parse_args()

    try:
        passed, reason = validate_state(
            fidelity=args.fidelity,
            h_vol=args.h_vol,
            xi_config=args.xi_config,
            z_liquidity=args.z_liquidity,
            theta_leak=args.theta_leak,
            psi_integrity=args.psi_integrity,
            verbose=args.verbose
        )
    except Exception as e:
        print(f"FAIL: Validation error – {e}")
        sys.exit(1)

    if passed:
        print("PASS: " + reason)
        sys.exit(0)
    else:
        print("FAIL: " + reason)
        sys.exit(1)

if __name__ == "__main__":
    main()