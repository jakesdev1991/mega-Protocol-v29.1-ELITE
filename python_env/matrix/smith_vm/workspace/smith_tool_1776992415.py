# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator – Systemic Reboot via Intellectual Validation
--------------------------------------------------------------------------------
Checks:
  1. Psi_id >= PSI_ID_THRESHOLD (hard gate)
  2. COD >= COD_THRESHOLD for a stable reboot
  3. No identity‑shredding condition:
         H_val > H_VAL_LIMIT and xi_reset > XI_RESET_MAX and psi_id < PSI_ID_CRITICAL
  4. All quantities dimensionless (implicitly enforced by using pure floats)
  5. Exponential arguments dimensionless via Lambda, Gamma coupling constants
"""

import math
from typing import List, Tuple

# ----------------------------------------------------------------------
# Omega Protocol Constants (must match the specification)
# ----------------------------------------------------------------------
PSI_ID_THRESHOLD   = 0.95   # hard gate for identity continuity
PSI_ID_CRITICAL    = 0.90   # dissociation risk threshold
XI_RESET_MIN       = 0.3
XI_RESET_DEFAULT   = 1.0
XI_RESET_MAX       = 2.5
H_VAL_LIMIT        = 0.85
COD_THRESHOLD      = 0.80
LAMBDA_COUPLING    = 1.0
GAMMA_COUPLING     = 0.5
K_BOLTZMANN        = 1.0   # for audit‑cost (k ln 2)

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def shannon_entropy(probs: List[float]) -> float:
    """Normalized Shannon entropy → [0,1]."""
    if not probs:
        return 0.0
    # Clip to avoid log(0)
    clipped = [max(p, 1e-12) for p in probs]
    raw = -sum(p * math.log(p) for p in clipped)
    max_ent = math.log(len(probs))
    return max(0.0, min(1.0, raw / max_ent))

def fidelity(u: List[float], v: List[float]) -> float:
    """|<u|v>|^2 normalized to [0,1]."""
    if len(u) != len(v):
        raise ValueError("State vectors must have equal dimension")
    dot = sum(a * b for a, b in zip(u, v))
    norm_u = math.sqrt(sum(a * a for a in u))
    norm_v = math.sqrt(sum(b * b for b in v))
    if norm_u == 0.0 or norm_v == 0.0:
        return 0.0
    fid = abs(dot) / (norm_u * norm_v)
    return max(0.0, min(1.0, fid))  # clamp

def reboot_cod(psi_old: List[float],
               psi_new: List[float],
               h_val: float,
               xi_reset: float) -> float:
    """COD = |<old|new>|^2 * exp(-Lambda*H) * exp(-Gamma*Xi)."""
    fid = fidelity(psi_old, psi_new)
    damp = math.exp(-LAMBDA_COUPLING * h_val)
    stiff = math.exp(-GAMMA_COUPLING * xi_reset)
    return fid * damp * stiff

def identity_shredding_risk(h_val: float,
                            xi_reset: float,
                            psi_id: float) -> bool:
    """Boolean check of the three‑condition shredding regime."""
    return (h_val > H_VAL_LIMIT) and (xi_reset > XI_RESET_MAX) and (psi_id < PSI_ID_CRITICAL)

def phi_density_impact(h_val: float,
                       cod_gain: float,
                       audit_complexity: float = 1.0) -> float:
    """Φ_net = cod_gain - 0.5*H_val - k ln 2 * audit_complexity."""
    validation_cost = 0.5 * h_val
    audit_entropy   = K_BOLTZMANN * math.log(2.0) * audit_complexity
    return cod_gain - validation_cost - audit_entropy

# ----------------------------------------------------------------------
# Main validation routine
# ----------------------------------------------------------------------
def validate_reboot(psi_old: List[float],
                    psi_new: List[float],
                    validation_data: List[float],
                    xi_reset: float,
                    psi_id: float) -> Tuple[bool, str]:
    """
    Returns (is_ok, message). Raises AssertionError on invariant breach.
    """
    # 1. Identity hard gate
    if psi_id < PSI_ID_THRESHOLD:
        raise AssertionError(f"Identity continuity breach: psi_id={psi_id} < threshold {PSI_ID_THRESHOLD}")

    # 2. Compute validation entropy
    h_val = shannon_entropy(validation_data)

    # 3. Compute COD
    cod = reboot_cod(psi_old, psi_new, h_val, xi_reset)

    # 4. Failure‑mode checks
    if identity_shredding_risk(h_val, xi_reset, psi_id):
        raise AssertionError(
            f"Identity‑shredding risk: H_val={h_val:.3f} > {H_VAL_LIMIT}, "
            f"Xi_reset={xi_reset:.3f} > {XI_RESET_MAX}, Psi_id={psi_id:.3f} < {PSI_ID_CRITICAL}"
        )
    # Optional: warn on low COD (not a hard gate but indicates instability)
    if cod < COD_THRESHOLD:
        # Not raising; just informational
        warn = f"Low COD warning: {cod:.3f} < {COD_THRESHOLD}"
    else:
        warn = "COD within acceptable range."

    # 5. Φ‑density impact (informational)
    cod_gain = max(0.0, cod - 0.5)  # example gain metric; can be replaced
    phi_net = phi_density_impact(h_val, cod_gain)

    # Assemble message
    msg = (f"H_val={h_val:.3f}, COD={cod:.3f}, Xi_reset={xi_reset:.3f}, "
           f"Psi_id={psi_id:.3f}, Φ_net={phi_net:.3f}. {warn}")
    return True, msg

# ----------------------------------------------------------------------
# Example usage (can be removed/replaced by unit tests)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Example state vectors (normalized for simplicity)
    psi_old = [0.8, 0.6]
    psi_new = [0.78, 0.62]
    validation_data = [0.2, 0.3, 0.5]   # probability distribution
    xi_reset = 1.2
    psi_id = 0.96

    ok, message = validate_reboot(psi_old, psi_new, validation_data, xi_reset, psi_id)
    print("Validation PASSED:", message)