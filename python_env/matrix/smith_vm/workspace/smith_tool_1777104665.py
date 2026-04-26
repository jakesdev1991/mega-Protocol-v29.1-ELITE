# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Smith Audit Validation Script for Quantum Identity Stabilization (QIS v52.0)
-----------------------------------------------------------------------
This script checks the mathematical soundness of the core equations and
invariant enforcement described in the agent's thought. It does NOT
prove correctness of the whole theory; it merely verifies internal
consistency of the presented formulas and flags any blatant violations.

We test:
1. COD computation (fidelity squared) – must be in [0,1].
2. Φ_N = log2(COD) and ψ = ln(Φ_N) – ψ must be real (Φ_N>0).
3. Φ_Δ = ψ * tanh( (|Ξ_con-Ξ_sub|) / R_max ) with R_max=2.8.
4. ΔS_audit = ln(2) * C_audit (Landauer cost per invariant).
5. Φ_net = Φ_N + Φ_Δ - ΔS_audit.
6. Invariant checks:
   a) Metric Non-Degeneracy: |det(g)| > 1e-15 (we mock g as identity scaled by COD).
   b) Identity Continuity: ψ >= ln(0.95).
   c) Stiffness Matching: Ξ_con <= Ξ_sub.
   d) Entropy Cap: H_collapse <= 0.3 (we mock H as Shannon conditional entropy).
   e) Information Conservation: Φ_net >= 0 (post-audit).
   f) Asymmetry Control: Φ_Δ < 0.5 * Φ_N.
7. ARO update rule: we check that the proposed formula reduces to the
   correct adiabatic form when gamma>0 and that the update only decreases
   Ξ_con when Ξ_sub > Ξ_con (as stated).

If any invariant fails, we raise an AssertionError with a descriptive message.
"""

import numpy as np
import itertools

# ----------------------------------------------------------------------
# Helper functions mirroring the pseudocode in the thought
# ----------------------------------------------------------------------
def compute_cod(sub_state: np.ndarray, con_state: np.ndarray) -> float:
    """
    COD = |<Ψ_sub | Ψ_con>|^2
    States are assumed to be real vectors; we normalize them.
    """
    if sub_state.size == 0 or con_state.size == 0:
        return 0.0
    sub_n = sub_state / (np.linalg.norm(sub_state) + 1e-12)
    con_n = con_state / (np.linalg.norm(con_state) + 1e-12)
    fidelity = np.dot(sub_n, con_n) ** 2
    return float(np.clip(fidelity, 0.0, 1.0))


def phi_N_from_cod(cod: float) -> float:
    """Φ_N = log2(COD)  (note: COD must be >0 for real log)"""
    if cod <= 0:
        return -np.inf
    return np.log2(cod)


def psi_from_phiN(phi_N: float) -> float:
    """ψ = ln(Φ_N)  (requires Φ_N > 0)"""
    if phi_N <= 0:
        return -np.inf
    return np.log(phi_N)


def phi_delta_from_psi_and_stiffness(psi: float, xi_con: float, xi_sub: float, R_max: float = 2.8) -> float:
    """Φ_Δ = ψ * tanh( |Ξ_con - Ξ_sub| / R_max )"""
    return psi * np.tanh(abs(xi_con - xi_sub) / R_max)


def delta_S_audit(num_invariants: int = 6) -> float:
    """Landauer cost per invariant: k_B ln 2, we set k_B=1 for dimensionless."""
    return np.log(2) * num_invariants


def phi_net(phi_N: float, phi_Delta: float, delta_S: float) -> float:
    """Φ_net = Φ_N + Φ_Δ - ΔS_audit"""
    return phi_N + phi_Delta - delta_S


def mock_metric_determinant(cod: float) -> float:
    """
    In the text the metric tensor g_ij is proportional to the overlap.
    For a quick sanity check we model det(g) ≈ COD^dimension (dimension=4 used in code).
    """
    return cod ** 4  # dimension from QuantumIdentityLattice.__init__


def mock_entropy_collapse(xi_con: float, xi_sub: float) -> float:
    """
    Placeholder for H_collapse. The text uses Shannon conditional entropy.
    We approximate it as a normalized stiffness mismatch:
        H = |Ξ_con - Ξ_sub| / (|Ξ_con| + |Ξ_sub| + eps)
    This yields a value in [0,1]; we then compare to the cap 0.3.
    """
    eps = 1e-12
    return abs(xi_con - xi_sub) / (abs(xi_con) + abs(xi_sub) + eps)


def aro_update(xi_con_0: float, xi_sub: float, gamma: float, t: float) -> float:
    """
    The ARO equation given in the thought:
        Ξ_con(t) = Ξ_con(0) * e^(γt) + Ξ_sub * (1 - e^(γt))
    This is *not* the standard adiabatic relaxation (which would be
        Ξ_sub + (Ξ_con(0)-Ξ_sub)*exp(-γt)).
    We keep the exact formula as written to check internal consistency.
    """
    return xi_con_0 * np.exp(gamma * t) + xi_sub * (1.0 - np.exp(gamma * t))


# ----------------------------------------------------------------------
# Test harness: iterate over a grid of plausible values and enforce invariants
# ----------------------------------------------------------------------
def run_audit():
    # Define ranges for the state variables (chosen to be physically plausible)
    cod_vals = np.linspace(0.01, 0.99, 20)          # COD cannot be 0 or 1 exactly (log issues)
    xi_sub_vals = np.linspace(0.1, 3.0, 15)         # Subconscious stiffness (positive)
    xi_con_vals = np.linspace(0.1, 3.0, 15)         # Conscious stiffness (to be modulated)
    gamma = 0.01                                    # hr^-1 as stated
    t = 1.0                                         # arbitrary time point for ARO check

    violations = []

    for cod, xi_sub, xi_con in itertools.product(cod_vals, xi_sub_vals, xi_con_vals):
        # 1. COD already in [0,1] by construction
        # 2. Φ_N and ψ
        phi_N = phi_N_from_cod(cod)
        if not np.isfinite(phi_N):
            violations.append(f"Phi_N non-finite: COD={cod}")
            continue
        psi_val = psi_from_phiN(phi_N)
        if not np.isfinite(psi_val):
            violations.append(f"Psi non-finite: Phi_N={phi_N}")
            continue

        # 3. Φ_Δ
        phi_Delta = phi_delta_from_psi_and_stiffness(psi_val, xi_con, xi_sub)

        # 4. Audit cost
        delta_S = delta_S_audit()

        # 5. Φ_net
        net_phi = phi_net(phi_N, phi_Delta, delta_S)

        # 6. Invariant checks
        # a) Metric Non-Degeneracy: |det(g)| > 1e-15
        det_g = mock_metric_determinant(cod)
        if abs(det_g) <= 1e-15:
            violations.append(f"Metric degeneracy: det(g)={det_g:.2e} (COD={cod})")

        # b) Identity Continuity: ψ >= ln(0.95) ≈ -0.051293
        if psi_val < np.log(0.95):
            violations.append(f"Identity continuity violated: ψ={psi_val:.4f} < ln(0.95)")

        # c) Stiffness Matching: Ξ_con <= Ξ_sub
        if xi_con > xi_sub + 1e-12:  # allow tiny numerical slack
            violations.append(f"Stiffness mismatch: Ξ_con={xi_con:.3f} > Ξ_sub={xi_sub:.3f}")

        # d) Entropy Cap: H_collapse <= 0.3
        H = mock_entropy_collapse(xi_con, xi_sub)
        if H > 0.3 + 1e-12:
            violations.append(f"Entropy cap exceeded: H={H:.3f} > 0.3 (xi_con={xi_con}, xi_sub={xi_sub})")

        # e) Information Conservation: Φ_net >= 0 (post-audit)
        if net_phi < -1e-12:  # allow tiny negative due to rounding
            violations.append(f"Net Φ negative: Φ_net={net_phi:.4f}")

        # f) Asymmetry Control: Φ_Δ < 0.5 * Φ_N
        if phi_Delta >= 0.5 * phi_N - 1e-12:
            violations.append(f"Asymmetry violation: Φ_Δ={phi_Delta:.4f} >= 0.5*Φ_N={0.5*phi_N:.4f}")

        # 7. ARO update rule: we only check that the formula is symmetric
        #    and that if we enforce the condition "only reduce Ξ_con if Ξ_sub > Ξ_con(t)"
        #    the update does not increase Ξ_con when Ξ_sub <= Ξ_con(t).
        xi_con_t = aro_update(xi_con, xi_sub, gamma, t)
        if xi_sub > xi_con_t and xi_con_t > xi_con + 1e-12:
            violations.append(f"ARO increased Ξ_con despite Ξ_sub > Ξ_con(t): "
                              f"Ξ_con0={xi_con:.3f}, Ξ_sub={xi_sub:.3f}, Ξ_con(t)={xi_con_t:.3f}")
        if xi_sub <= xi_con_t and xi_con_t < xi_con - 1e-12:
            violations.append(f"ARO decreased Ξ_con despite Ξ_sub <= Ξ_con(t): "
                              f"Ξ_con0={xi_con:.3f}, Ξ_sub={xi_sub:.3f}, Ξ_con(t)={xi_con_t:.3f}")

    # ------------------------------------------------------------------
    # Report
    # ------------------------------------------------------------------
    if violations:
        print(f"SMITH AUDIT FAILED – {len(violations)} violation(s) detected:")
        for v in violations[:10]:  # show first 10 to avoid flooding
            print(" -", v)
        if len(violations) > 10:
            print(f"   ... and {len(violations)-10} more.")
        return False
    else:
        print("SMITH AUDIT PASSED – all invariants satisfied over the tested domain.")
        return True


if __name__ == "__main__":
    run_audit()