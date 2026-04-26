# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import numpy as np

# ─── Parameters ──────────────────────────────────────────────────────────────
alpha0 = 1 / 137.035999084          # Fine‑structure constant at mu
gN = 1.0                            # Newtonian‑mode coupling
gDelta = 1.0                        # Archive‑mode coupling
mu = 1e2                            # Reference scale in GeV
planck_scale = 1.22e19              # Planck scale in GeV

def landau_pole_scale(factor, mDelta=0.0, qmax=planck_scale):
    """
    Compute the Landau‑pole scale q_L for a given Archive‑multiplicity factor.
    If mDelta > 0, the Archive contribution is suppressed by (q^2/(q^2+mDelta^2))^2.
    """
    # Beta‑function coefficient (1-loop)
    # b = 1 + (gN^2 + factor*gDelta^2)/(4π)   for massless case
    # For massive case we treat the factor as a running factor ~ (q^2/(q^2+mDelta^2))^2
    # Here we approximate by evaluating at the pole scale itself (self‑consistent).
    def beta_coeff(q):
        # Suppression factor for massive Archive mode
        sup = (q**2 / (q**2 + mDelta**2))**2 if mDelta > 0 else 1.0
        return 1 + (gN**2 + factor * sup * gDelta**2) / (4 * math.pi)

    # Solve for q_L from the RG equation analytically:
    # q_L^2 = mu^2 * exp( -π/(alpha0 * b(q_L)) )
    # We solve iteratively for self‑consistency.
    q = mu * 1e3   # initial guess well above mu
    for _ in range(50):
        b = beta_coeff(q)
        q_new = mu * math.exp(-math.pi / (2 * alpha0 * b))
        if abs(q_new - q) / q < 1e-6:
            break
        q = q_new
    return q

# ─── Scenarios ────────────────────────────────────────────────────────────────
scenarios = {
    "Original factor‑3 (massless)": {"factor": 3.0, "mDelta": 0.0},
    "Corrected factor‑1 (massless)": {"factor": 1.0, "mDelta": 0.0},
    "Massive Archive (mΔ=10⁶ GeV)": {"factor": 3.0, "mDelta": 1e6},
}

for name, cfg in scenarios.items():
    qL = landau_pole_scale(cfg["factor"], cfg["mDelta"])
    print(f"{name:35s} → Landau pole at q ≈ {qL:.2e} GeV")