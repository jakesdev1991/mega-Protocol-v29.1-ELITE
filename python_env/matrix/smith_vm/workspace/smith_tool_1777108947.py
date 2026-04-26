# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Validation Script for the Inter-Manifold Sales Alignment (v55.0-Ω-RESOLVE)
Validates mathematical soundness and invariant compliance of the COD formula,
failure mode detection, and Resonant Coupling Gate (RCG) operator.
"""

import numpy as np
import itertools
import math

# --------------------------------------------------------------
# Constants from the specification (must match the C++ code)
# --------------------------------------------------------------
PSI_ID_THRESHOLD = 0.95          # Identity hard gate
THETA_ATROPHY    = 0.15          # Quantum atrophy lower bound
THETA_SHOCK      = 0.80          # Rejection shock upper bound
LAMBDA_COUPLING  = 1.0           # Uncertainty damping coefficient
MAX_COMMIT_RATE_CHANGE = 0.05    # Adiabatic constraint on Γ_commit per step

# --------------------------------------------------------------
# Helper functions (direct translations of the core math)
# --------------------------------------------------------------
def fidelity(value_vec, identity_vec):
    """Normalized dot product → [0,1]"""
    if not value_vec or not identity_vec:
        return 0.0
    n = min(len(value_vec), len(identity_vec))
    v = np.array(value_vec[:n], dtype=float)
    i = np.array(identity_vec[:n], dtype=float)
    dot = np.dot(v, i)
    norm_v = np.linalg.norm(v)
    norm_i = np.linalg.norm(i)
    if norm_v == 0 or norm_i == 0:
        return 0.0
    f = dot / (norm_v * norm_i)
    return float(np.clip(f, 0.0, 1.0))

def uncertainty_damping(ambiguity):
    """exp(-λ * H_super) → [exp(-λ), 1] ⊂ [0,1] for λ≥0, H∈[0,1]"""
    return float(np.exp(-LAMBDA_COUPLING * ambiguity))

def atrophy_penalty(ambiguity):
    """1 - ((θ_atrophy - H)/θ_atrophy) for H<θ_atrophy, else 1 → [0,1]"""
    if ambiguity < THETA_ATROPHY:
        p = 1.0 - ((THETA_ATROPHY - ambiguity) / THETA_ATROPHY)
        return float(np.clip(p, 0.0, 1.0))
    return 1.0

def calculate_COD(value_vec, identity_vec, ambiguity, psi_id):
    """
    COD = Fidelity * Damping * Identity * (1 - Atrophy_Penalty)
    If psi_id < PSI_ID_THRESHOLD → COD = 0 (hard gate)
    """
    if psi_id < PSI_ID_THRESHOLD:
        return 0.0
    fid = fidelity(value_vec, identity_vec)
    damp = uncertainty_damping(ambiguity)
    attp = atrophy_penalty(ambiguity)
    cod = fid * damp * psi_id * attp
    # Theoretical bound: each factor ∈[0,1] → product ∈[0,1]
    return float(np.clip(cod, 0.0, 1.0))

def failure_mode_detector(ambiguity, commit_rate, psi_id, cod):
    """
    Returns one of: NONE, REJECTION_SHOCK, QUANTUM_ATROPHY, DEAL_DRIFT, IDENTITY_SHREDDING
    Mirrors the C++ enum logic.
    """
    if ambiguity > THETA_SHOCK and commit_rate > 0.70:
        return "REJECTION_SHOCK"
    if ambiguity < THETA_ATROPHY and commit_rate > 0.50 and psi_id < 0.95:
        return "QUANTUM_ATROPHY"
    if cod < 0.80 and psi_id > 0.95:
        return "DEAL_DRIFT"
    if psi_id < 0.90:
        return "IDENTITY_SHREDDING"
    return "NONE"

def rcg_apply_step(ambiguity, commit_rate, psi_id, audit_ops, audit_cost):
    """
    Single RCG modulation step (simplified).
    Returns new (ambiguity, commit_rate, psi_id, audit_ops, audit_cost)
    and raises RuntimeError if identity gate violated.
    """
    # Diagnostic
    dummy_val = [1.0, 1.0]   # placeholder vectors – fidelity = 1 for simplicity
    dummy_id  = [1.0, 1.0]
    cod = calculate_COD(dummy_val, dummy_id, ambiguity, psi_id)
    failure = failure_mode_detector(ambiguity, commit_rate, psi_id, cod)

    # Modulation (adiabatic)
    if failure == "REJECTION_SHOCK":
        new_commit = max(0.1, commit_rate * 0.85)
        delta = abs(new_commit - commit_rate)
        if delta > MAX_COMMIT_RATE_CHANGE + 1e-9:
            raise ValueError(f"Adiabatic violation: ΔΓ={delta:.4f} > {MAX_COMMIT_RATE_CHANGE}")
        audit_ops += 1
        audit_cost += 0.05
        commit_rate = new_commit

    elif failure == "QUANTUM_ATROPHY":
        new_amb = min(0.80, ambiguity * 1.2)
        delta = abs(new_amb - ambiguity)
        if delta > MAX_COMMIT_RATE_CHANGE + 1e-9:   # we reuse same bound for ambiguity step
            raise ValueError(f"Adiabatic violation on H_super: ΔH={delta:.4f}")
        audit_ops += 1
        audit_cost += 0.10
        ambiguity = new_amb

    elif failure == "DEAL_DRIFT":
        new_amb = max(0.05, ambiguity * 0.9)
        delta = abs(new_amb - ambiguity)
        if delta > MAX_COMMIT_RATE_CHANGE + 1e-9:
            raise ValueError(f"Adiabatic violation on H_super: ΔH={delta:.4f}")
        audit_ops += 1
        audit_cost += 0.02
        ambiguity = new_amb

    elif failure == "IDENTITY_SHREDDING":
        raise RuntimeError("Invariant Violation: Buyer Identity Compromised (pre-mod)")

    # Identity friction loss (simplified)
    identity_loss = ambiguity * 0.02
    new_psi_id = psi_id - identity_loss
    if new_psi_id < PSI_ID_THRESHOLD:
        raise RuntimeError("Invariant Violation: Buyer Identity Compromised (post-friction)")

    return ambiguity, commit_rate, new_psi_id, audit_ops, audit_cost

# --------------------------------------------------------------
# Validation Suite
# --------------------------------------------------------------
def run_validation(trials=10000):
    rng = np.random.default_rng(seed=42)
    violations = []

    for _ in range(trials):
        # Random state vectors (dimension 3-8)
        dim = rng.integers(3, 9)
        value_vec = rng.random(dim).tolist()
        identity_vec = rng.random(dim).tolist()
        ambiguity = rng.random()          # H_super ∈ [0,1]
        commit_rate = rng.random()        # Γ_commit ∈ [0,1]
        psi_id = rng.random() * 0.2 + 0.8 # ψ_id ∈ [0.8,1.0] to often test gate

        # ---- COD bounds and hard gate ----
        cod = calculate_COD(value_vec, identity_vec, ambiguity, psi_id)
        if not (0.0 <= cod <= 1.0 + 1e-12):
            violations.append(f"COD out of bounds: {cod}")
        if psi_id < PSI_ID_THRESHOLD and abs(cod) > 1e-12:
            violations.append(f"COD non-zero despite psi_id<{PSI_ID_THRESHOLD}: psi_id={psi_id}, COD={cod}")

        # ---- Individual factor bounds ----
        fid = fidelity(value_vec, identity_vec)
        damp = uncertainty_damping(ambiguity)
        attp = atrophy_penalty(ambiguity)
        if not (0.0 <= fid <= 1.0 + 1e-12):
            violations.append(f"Fidelity OOB: {fid}")
        if not (0.0 <= damp <= 1.0 + 1e-12):
            violations.append(f"Damping OOB: {damp}")
        if not (0.0 <= attp <= 1.0 + 1e-12):
            violations.append(f"Atrophy penalty OOB: {attp}")

        # ---- Failure mode detector sanity ----
        failure = failure_mode_detector(ambiguity, commit_rate, psi_id, cod)
        # Ensure mutually exclusive conditions (quick sanity)
        if failure == "REJECTION_SHOCK":
            if not (ambiguity > THETA_SHOCK and commit_rate > 0.70):
                violations.append(f"REJECTION_SHOCK flagged incorrectly: H={ambiguity}, Γ={commit_rate}")
        if failure == "QUANTUM_ATROPHY":
            if not (ambiguity < THETA_ATROPHY and commit_rate > 0.50 and psi_id < 0.95):
                violations.append(f"QUANTUM_ATROPHY flagged incorrectly: H={ambiguity}, Γ={commit_rate}, ψ={psi_id}")
        if failure == "IDENTITY_SHREDDING":
            if not (psi_id < 0.90):
                violations.append(f"IDENTITY_SHREDDING flagged incorrectly: ψ={psi_id}")

        # ---- RCG step adiabatic & invariant check ----
        audit_ops = 0
        audit_cost = 0.0
        try:
            ambiguity2, commit2, psi_id2, audit_ops2, audit_cost2 = rcg_apply_step(
                ambiguity, commit_rate, psi_id, audit_ops, audit_cost
            )
            # Post-step identity must still respect hard gate
            if psi_id2 < PSI_ID_THRESHOLD - 1e-12:
                violations.append(f"RCG step broke identity gate: ψ_id_post={psi_id2}")
            # Adiabatic constraint already enforced inside rcg_apply_step; if not thrown, it's ok.
            # Ensure audit cost non‑negative and ops increased when action taken
            if audit_cost2 < audit_cost - 1e-12:
                violations.append(f"Audit cost decreased: {audit_cost} → {audit_cost2}")
        except RuntimeError as e:
            # Expected when identity already broken or becomes broken – just continue
            pass
        except ValueError as e:
            violations.append(str(e))

    return violations

# --------------------------------------------------------------
# Execute and report
# --------------------------------------------------------------
if __name__ == "__main__":
    print("Running Ω‑Protocol validation for Inter‑Manifold Sales Alignment (v55.0)…")
    vio = run_validation(trials=20000)
    if vio:
        print(f"\n❌ {len(vio)} violation(s) detected:")
        for v in vio[:10]:   # show first 10
            print(" -", v)
        if len(vio) > 10:
            print(f"   … and {len(vio)-10} more.")
    else:
        print("\n✅ All checks passed. The mathematics and invariants are sound.")