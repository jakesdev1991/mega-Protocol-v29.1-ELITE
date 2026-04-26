# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Omega Protocol Invariant Validator – Credential Delegation Risk Subsystem
Checks the mathematical soundness of the core formulas presented in the
scrutiny audit (v62.0-Ω) against the Protocol’s absolute invariants:
    • All primary metrics must be dimensionless and bounded in [0, 1].
    • Safety‑gate hierarchy must be integrity‑first (Ψ ≥ 0.95 → …).
    • Φ‑density accounting must be honest (audit cost subtracted, no inflated claims).
    • No log‑transforms or unbounded operations on core metrics.
"""

import math
from typing import Tuple

# ----------------------------------------------------------------------
# Helper: assert a value lies in [0, 1] (with tiny tolerance for FP error)
def in_unit_interval(x: float, eps: float = 1e-12) -> bool:
    return -eps <= x <= 1.0 + eps

# ----------------------------------------------------------------------
# 1. Credential Delegation Risk (CDR) – core physics‑specific metric
def credential_delegation_risk(
    exposure: float,
    chain_risk: float,
    chain_integrity: float
) -> Tuple[float, bool]:
    """
    Returns (risk, ok) where risk ∈ [0,1] if inputs are valid.
    Formula: risk = exposure * chain_risk * (1 - chain_integrity)
    """
    if not all(in_unit_interval(v) for v in (exposure, chain_risk, chain_integrity)):
        return 0.0, False

    integrity_factor = 1.0 - chain_integrity          # ∈ [0,1]
    raw = exposure * chain_risk * integrity_factor    # product of [0,1] → [0,1]
    risk = min(max(raw, 0.0), 1.0)                     # explicit clamp (defensive)
    return risk, in_unit_interval(risk)

# ----------------------------------------------------------------------
# 2. COD (Collateral Orthogonality Degree) – credential‑aware extension
#    Matches UIPO v65.0 structure: COD = fidelity * instability_penalty *
#    exposure_penalty * credential_penalty, each factor ∈ [0,1].
def cod_credential_aware(
    fidelity: float,
    instability_penalty: float,
    exposure_penalty: float,
    credential_penalty: float
) -> Tuple[float, bool]:
    if not all(in_unit_interval(v) for v in
               (fidelity, instability_penalty, exposure_penalty, credential_penalty)):
        return 0.0, False

    cod = fidelity * instability_penalty * exposure_penalty * credential_penalty
    return cod, in_unit_interval(cod)

# ----------------------------------------------------------------------
# 3. Φ‑density net gain – audit‑cost honesty check
def phi_net_gain(
    cod_before: float,
    cod_after: float,
    audit_checks: int,
    audit_entropy_per_check: float = 0.02
) -> Tuple[float, bool]:
    """
    Implements: raw_gain = cod_after - cod_before
                audit_cost = audit_checks * audit_entropy_per_check
                net = raw_gain - audit_cost
    Returns (net_gain, ok) where ok signals that the calculation respected
    the Protocol’s honesty rule (no hidden inflations).
    """
    if not (in_unit_interval(cod_before) and in_unit_interval(cod_after)):
        return 0.0, False
    if audit_checks < 0 or audit_entropy_per_check < 0:
        return 0.0, False

    raw_gain = cod_after - cod_before               # can be negative; that’s fine
    audit_cost = audit_checks * audit_entropy_per_check
    net_gain = raw_gain - audit_cost
    # Honesty rule: we do *not* clamp net_gain to [0,1]; it may be negative
    # (a loss). The invariant is merely that we subtracted the audit cost.
    return net_gain, True   # always mathematically sound if inputs valid

# ----------------------------------------------------------------------
# 4. Safety‑gate hierarchy validator
def safety_gate_ok(
    psi_integrity: float,
    credential_risk: float,
    cod: float,
    psi_threshold: float = 0.95,
    cred_risk_max: float = 0.30,
    cod_threshold: float = 0.85
) -> bool:
    """
    Returns True iff the hierarchy permits ACTION (PROCEED).
    Hierarchy: Ψ ≥ psi_threshold AND credential_risk ≤ cred_risk_max AND cod ≥ cod_threshold
    """
    return (in_unit_interval(psi_integrity) and psi_integrity >= psi_threshold and
            in_unit_interval(credential_risk) and credential_risk <= cred_risk_max and
            in_unit_interval(cod) and cod >= cod_threshold)

# ----------------------------------------------------------------------
# Demo / self‑test – uses values taken from the audit’s illustrative tables
if __name__ == "__main__":
    print("=== Omega Protocol Mathematical Soundness Check ===")

    # Example inputs that satisfy the audit’s claims
    exp = 0.4          # credential_exposure
    cr  = 0.6          # access_chain_risk
    ci  = 0.8          # chain_integrity → high integrity
    risk, ok_r = credential_delegation_risk(exp, cr, ci)
    print(f"CDR({exp}, {cr}, {ci}) = {risk:.4f}  {'OK' if ok_r else 'FAIL'}")

    # COD example (all penalties in [0,1])
    fid = 0.9
    inst_pen = math.exp(-0.5)   # ≈0.606
    exp_pen  = math.exp(-0.3)   # ≈0.741
    cred_pen = math.exp(-0.2)   # ≈0.819
    cod_val, ok_c = cod_credential_aware(fid, inst_pen, exp_pen, cred_pen)
    print(f"COD = {cod_val:.4f}  {'OK' if ok_c else 'FAIL'}")

    # Φ‑density gain example
    cod_before = 0.70
    cod_after  = 0.78
    checks     = 4
    gain, _    = phi_net_gain(cod_before, cod_after, checks)
    print(f"Φ‑net gain (ΔCOD={cod_after-cod_before:+.2f}, audits={checks}) = {gain:+.4f}")

    # Safety gate test
    psi = 0.96
    gate_ok = safety_gate_ok(psi, risk, cod_val)
    print(f"Safety gate (Ψ={psi}, risk={risk:.3f}, COD={cod_val:.3f}) → {'PROCEED' if gate_ok else 'BLOCK'}")

    # Final verdict
    all_ok = ok_r and ok_c and gate_ok
    print("\nResult:", "META‑PASS – all core invariants satisfied" if all_ok
          else "META‑FAIL – invariant violation detected")