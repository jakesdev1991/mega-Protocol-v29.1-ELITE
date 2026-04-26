# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Validation script for the Byzantine-Resilient Streaming Omega (BRS-Ω) proposal.

The script checks the mathematical soundness of the core equations and
verifies compliance with the Omega Protocol invariants:

    • Phi_N (strategic connectivity) must stay ≥ 0.6
    • Phi_Delta (information asymmetry) must stay ≤ 0.7
    • Corruption tolerance t must satisfy 0 ≤ t ≤ floor((m-1)/2)
    • Encoding sparsity s must stay within [s_min, s_max]
    • Loop latency ℓ(t,s) must not exceed the maximum allowed latency ℓ_max
    • The cost function J is non‑negative (as a sum of squares)

If any invariant is violated, the script raises an AssertionError with a
descriptive message.
"""

import numpy as np
from itertools import product

# ----------------------------------------------------------------------
# Helper functions that implement the equations from the proposal
# ----------------------------------------------------------------------
def latency(t: int, s: float, ell0: float, alpha: float, beta: float) -> float:
    """
    Latency model: ℓ(t,s) = ℓ0 + α * (t/m) - β * s
    (m is supplied externally; see validate() for its value)
    """
    return ell0 + alpha * (t / m) - beta * s


def phi_N_stream(PhiN0: float, ell: float, ell_max: float,
                 t: int, t_max: int,
                 gamma1: float, gamma2: float) -> float:
    """
    Φ_N^{(stream)} = Φ_N^{(0)} - γ1 * (ℓ/ℓ_max) + γ2 * (1 - t/t_max)
    """
    return PhiN0 - gamma1 * (ell / ell_max) + gamma2 * (1 - t / t_max)


def phi_Delta_stream(PhiDelta0: float, ell: float, ell_max: float,
                     t: int, t_max: int,
                     gamma3: float, gamma4: float) -> float:
    """
    Φ_Δ^{(stream)} = Φ_Δ^{(0)} + γ3 * (ℓ/ℓ_max) - γ4 * (t/t_max)
    """
    return PhiDelta0 + gamma3 * (ell / ell_max) - gamma4 * (t / t_max)


def cost_term(PhiN_stream_val: float, PhiDelta_stream_val: float,
              theta: float, t: int, m: int,
              ell: float,
              lambda1: float, lambda2: float) -> float:
    """
    One‑step contribution to the cost:
        (1 - Φ_N)^2 + Φ_Δ^2 + λ1 (θ - t/m)^2 + λ2 ℓ^2
    """
    term1 = (1.0 - PhiN_stream_val) ** 2
    term2 = PhiDelta_stream_val ** 2
    term3 = lambda1 * (theta - t / m) ** 2
    term4 = lambda2 * ell ** 2
    return term1 + term2 + term3 + term4


# ----------------------------------------------------------------------
# Validation routine
# ----------------------------------------------------------------------
def validate():
    """
    Run a grid‑search over plausible parameter values and assert that
    all Omega Protocol invariants hold.
    """
    # ------------------------------------------------------------------
    # Fixed protocol / system parameters (chosen to be realistic but
    # arbitrary – the validation should hold for any reasonable choice)
    # ------------------------------------------------------------------
    global m  # needed inside latency()
    m = 10                     # number of worker nodes
    t_max = (m - 1) // 2       # information‑theoretic bound
    s_min, s_max = 0.1, 0.9    # sparsity range (fraction of zero entries)
    ell_max = 5.0              # maximum allowable latency (ms)
    ell0 = 1.0                 # baseline latency
    alpha, beta = 2.0, 1.5     # latency model coefficients
    gamma1, gamma2 = 0.4, 0.3  # Φ_N mapping coefficients
    gamma3, gamma4 = 0.2, 0.25 # Φ_Δ mapping coefficients
    lambda1, lambda2 = 0.5, 0.1# cost weights
    PhiN0, PhiDelta0 = 0.8, 0.5# nominal Omega field values

    # ------------------------------------------------------------------
    # Discretise the search space
    # ------------------------------------------------------------------
    t_vals = range(0, t_max + 1)               # possible corruption tolerances
    s_vals = np.linspace(s_min, s_max, 9)      # sparsity samples
    theta_vals = np.linspace(0.0, 1.0, 6)      # estimated threat level
    ell_vals = []  # we will compute ℓ(t,s) on the fly

    # ------------------------------------------------------------------
    # Iterate over all combinations and check invariants
    # ------------------------------------------------------------------
    violations = []
    for t, s, theta in product(t_vals, s_vals, theta_vals):
        # ---- latency -------------------------------------------------
        ell = latency(t, s, ell0, alpha, beta)
        if ell < 0:
            violations.append(
                f"Negative latency: t={t}, s={s:.2f} → ℓ={ell:.3f}"
            )
            continue
        if ell > ell_max:
            violations.append(
                f"Latency exceeds ℓ_max: t={t}, s={s:.2f} → ℓ={ell:.3f} > {ell_max}"
            )
            continue

        # ---- Omega field variables ------------------------------------
        PhiN = phi_N_stream(PhiN0, ell, ell_max, t, t_max, gamma1, gamma2)
        PhiDelta = phi_Delta_stream(PhiDelta0, ell, ell_max, t, t_max,
                                   gamma3, gamma4)

        if PhiN < 0.6:
            violations.append(
                f"Φ_N below 0.6: t={t}, s={s:.2f}, θ={theta:.2f} → Φ_N={PhiN:.3f}"
            )
        if PhiDelta > 0.7:
            violations.append(
                f"Φ_Δ above 0.7: t={t}, s={s:.2f}, θ={theta:.2f} → Φ_Δ={PhiDelta:.3f}"
            )

        # ---- cost term (must be non‑negative) ------------------------
        J = cost_term(PhiN, PhiDelta, theta, t, m, ell, lambda1, lambda2)
        if J < -1e-12:  # allow tiny negative due to floating‑point round‑off
            violations.append(
                f"Negative cost: t={t}, s={s:.2f}, θ={theta:.2f} → J={J:.6f}"
            )

        # ---- encoding dimension sanity check -------------------------
        # Assume a mini‑batch size b = 5 (any positive integer works)
        b = 5
        b_prime = b + 2 * t
        if b_prime <= b:
            violations.append(
                f"Encoded dimension not larger than raw: t={t} → b'={b_prime} ≤ b={b}"
            )

    # ------------------------------------------------------------------
    # Report results
    # ------------------------------------------------------------------
    if violations:
        print("VALIDATION FAILED – Invariants violated:")
        for v in violations[:10]:  # show first 10 for brevity
            print(" -", v)
        if len(violations) > 10:
            print(f" ... and {len(violations)-10} more violations.")
        raise AssertionError("Omega Protocol invariants not satisfied.")
    else:
        print(
            f"VALIDATION PASSED – All {len(t_vals)*len(s_vals)*len(theta_vals)} "
            "parameter combinations satisfy the Omega Protocol invariants."
        )


# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------
if __name__ == "__main__":
    validate()