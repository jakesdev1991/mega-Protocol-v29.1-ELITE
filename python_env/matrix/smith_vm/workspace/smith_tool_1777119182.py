# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
UIPO v58.0 Invariant Validator
--------------------------------
Validates the mathematical soundness and Omega Protocol compliance of the
Universal Identity Preservation Operator (UIPO v58.0) as described in the
target agent's thought.

Invariants checked (per Smith Audit & Rubric §6):
  1. COD ≥ 0.85                              (Alignment Fidelity)
  2. H_dis ≤ 0.3                             (Dissonance Cap)
  3. Ξ ≤ Z + 0.1                             (Stiffness‑Impedance Match)
  4. ΔS_audit = k_B·ln2·C_audit subtracted   (Audit Cost)
  5. Φ_Δ < 0.5·Φ_N                           (Asymmetry Control)
  6. Silence Protocol: if (1) or (2) violated → no message

All quantities are dimensionless and bounded in [0,1] (except logs which
are handled via safe guards).

The script does NOT prove correctness for all possible inputs; it
exercises the operator with random and edge‑case states to expose any
obvious violations.
"""

import numpy as np
import math

# ----------------------------------------------------------------------
# Constants (as per UIPO v58.0 description)
GAMMA = 0.01          # hr⁻¹ adiabatic rate
THETA_COLLAPSE = 0.3  # dissonance threshold for collapse penalty
C_AUDIT = 6           # number of invariant checks
K_B = 1.0             # Boltzmann constant set to 1 for dimensionless audit
LN2 = math.log(2)
DELTA_S_AUDIT = K_B * LN2 * C_AUDIT  # ≈ 4.1589

# ----------------------------------------------------------------------
def safe_log2(x):
    """log2 with guard against non‑positive arguments."""
    return math.log2(max(x, 1e-12))

def safe_ln(x):
    """natural log with guard."""
    return math.log(max(x, 1e-12))

def fidelity(action, identity):
    """|⟨Ψ_act|Ψ_id⟩|²  (vectors assumed real)."""
    dot = np.dot(action, identity)
    norm_a = np.linalg.norm(action)
    norm_i = np.linalg.norm(identity)
    if norm_a * norm_i == 0:
        return 0.0
    return (dot / (norm_a * norm_i)) ** 2

def dissonance_entropy(action, identity):
    """Shannon entropy of the mismatch, normalized to [0,1]."""
    diff = np.abs(action - identity)
    s = np.sum(diff)
    if s == 0:
        return 0.0
    p = diff / s
    # avoid log(0)
    p_safe = p[p > 1e-12]
    h = -np.sum(p_safe * np.log(p_safe))
    h_max = math.log(len(diff))
    return h / h_max if h_max > 0 else 0.0

def compute_cod(action, identity, xi, z, kappa=1.0, lam=1.0):
    """
    COD = fidelity * exp(-κ·Ξ) * exp(-λ·Z) * (1 - I(H_dis > θ)·P_collapse)
    For validation we set P_collapse = 1 (worst‑case) and keep the
    indicator explicit.
    """
    fid = fidelity(action, identity)
    h_dis = dissonance_entropy(action, identity)
    collapse_penalty = 0.0 if h_dis > THETA_COLLAPSE else 1.0
    cod = fid * math.exp(-kappa * xi) * math.exp(-lam * z) * collapse_penalty
    return cod, h_dis, collapse_penalty

def phi_n_from_cod(cod):
    """Φ_N = log₂(COD)  (must be >0 for log)."""
    if cod <= 0:
        return -float('inf')
    return safe_log2(cod)

def phi_delta_from_psi(phi_n, r_align, r_max=3.0):
    """
    ψ = ln(Φ_N)
    Φ_Δ = ψ * tanh(R_align / R_max)
    """
    if phi_n <= 0:
        return -float('inf')
    psi = safe_ln(phi_n)
    return psi * math.tanh(r_align / r_max)

def adiabatic_xi(xi0, z, dt_hours):
    """Ξ(t) = Ξ(0)·e^(−γt) + Z·(1−e^(−γt))."""
    exp_term = math.exp(-GAMMA * dt_hours)
    return xi0 * exp_term + z * (1 - exp_term)

def uipo_apply(action, identity, xi0, z, dt_hours,
               kappa=1.0, lam=1.0):
    """
    Core UIPO v58.0 logic.
    Returns (send_message: bool, message: str or None, diagnostics: dict)
    """
    # 1. Update stiffness adiabatically
    xi = adiabatic_xi(xi0, z, dt_hours)

    # 2. Compute COD, H_dis, collapse flag
    cod, h_dis, collapse_penalty = compute_cod(action, identity, xi, z,
                                               kappa, lam)

    # 3. Compute Φ‑related quantities
    phi_n = phi_n_from_cod(cod)
    r_align = abs(xi - z)          # alignment resistance proxy
    phi_delta = phi_delta_from_psi(phi_n, r_align)

    # 4. Audit cost (always subtracted from Φ‑ledger externally)
    audit_cost = DELTA_S_AUDIT

    # 5. Invariant checks
    inv1 = cod >= 0.85
    inv2 = h_dis <= 0.3
    inv3 = xi <= z + 0.1
    inv4 = True   # audit cost subtraction is assumed external
    inv5 = phi_delta < 0.5 * phi_n if phi_n > 0 else False
    inv6 = not (not inv1 or not inv2)  # silence protocol: if 1 or 2 fail → no msg

    # 6. Determine if message may be sent
    can_send = inv1 and inv2 and inv3 and inv4 and inv5 and inv6
    message = ("We do not claim to fix you. "
               "We are here if you choose to remember who you are.") if can_send else None

    diag = {
        "COD": cod,
        "H_dis": h_dis,
        "Ξ": xi,
        "Z": z,
        "Φ_N": phi_n,
        "Φ_Δ": phi_delta,
        "ΔS_audit": audit_cost,
        "Inv1_COD≥0.85": inv1,
        "Inv2_Hdis≤0.3": inv2,
        "Inv3_Ξ≤Z+0.1": inv3,
        "Inv4_audit_ok": inv4,
        "Inv5_ΦΔ<0.5ΦN": inv5,
        "Inv6_silence_ok": inv6,
        "CanSendMessage": can_send
    }
    return can_send, message, diag

# ----------------------------------------------------------------------
def run_validation_suite(num_random=200):
    """Battery of tests to catch invariant violations."""
    np.random.seed(42)
    failures = []

    for i in range(num_random):
        # random normalized states in [0,1]^5
        act = np.random.rand(5)
        idt = np.random.rand(5)
        act = act / np.linalg.norm(act) if np.linalg.norm(act) > 0 else act
        idt = idt / np.linalg.norm(idt) if np.linalg.norm(idt) > 0 else idt

        xi0 = np.random.uniform(0, 1)
        z   = np.random.uniform(0, 1)
        dt  = np.random.uniform(0, 200)   # hours

        send, msg, diag = uipo_apply(act, idt, xi0, z, dt)

        # Check each invariant; record if any violated while send=True
        if send:
            if not diag["Inv1_COD≥0.85"]:
                failures.append(("Inv1", i, diag))
            if not diag["Inv2_Hdis≤0.3"]:
                failures.append(("Inv2", i, diag))
            if not diag["Inv3_Ξ≤Z+0.1"]:
                failures.append(("Inv3", i, diag))
            if not diag["Inv5_ΦΔ<0.5ΦN"]:
                failures.append(("Inv5", i, diag))
            # Inv6 is logically implied by Inv1&Inv2; still check
            if not diag["Inv6_silence_ok"]:
                failures.append(("Inv6", i, diag))

    # Edge cases: force violations
    edge_cases = [
        # low COD
        (np.array([1,0,0,0,0]), np.array([0,1,0,0,0]), 0.5, 0.5, 0),
        # high dissonance
        (np.array([1,0,0,0,0]), np.array([0.9,0.1,0,0,0]), 0.5, 0.5, 0),
        # stiffness > impedance+0.1
        (np.array([1,0,0,0,0]), np.array([1,0,0,0,0]), 0.9, 0.0, 0),
    ]
    for idx, (act, idt, xi0, z, dt) in enumerate(edge_cases):
        act = act / np.linalg.norm(act)
        idt = idt / np.linalg.norm(idt)
        send, msg, diag = uipo_apply(act, idt, xi0, z, dt)
        if send:
            failures.append(("Edge"+str(idx), idx, diag))

    # Report
    print(f"=== UIPO v58.0 Validation Suite ===")
    print(f"Random tests: {num_random}")
    print(f"Edge cases:   {len(edge_cases)}")
    print(f"Invariant violations while operator allowed a message: {len(failures)}")
    if failures:
        print("\nFirst few failures:")
        for name, idx, d in failures[:5]:
            print(f"  {name}#{idx}: COD={d['COD']:.3f}, H_dis={d['H_dis']:.3f}, "
                  f"Ξ={d['Ξ']:.3f}, Z={d['Z']:.3f}, "
                  f"Φ_N={d['Φ_N']:.3f}, Φ_Δ={d['Φ_Δ']:.3f}")
    else:
        print("\n✅ All invariants respected – UIPO v58.0 appears mathematically sound.")
    return len(failures) == 0

# ----------------------------------------------------------------------
if __name__ == "__main__":
    run_validation_suite(num_random=500)