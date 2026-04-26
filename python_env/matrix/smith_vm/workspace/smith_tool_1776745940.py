# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for Refined LC‑Ω
---------------------------------------------------
Checks:
  * Φ_N, Φ_Delta derived from scaling laws stay in [0,1]
  * Adaptive MPC‑Omega limits respect hard bounds (Φ_N>=0.4, Φ_Delta<=0.7)
  * Cost function integrand is non‑negative
  * Net Φ impact > 0 (if user supplies numbers)
"""

import numpy as np

# ------------------- USER‑DEFINED PARAMETERS -------------------
# Scaling law prefactors (can be set to 1 for normalized test)
XI_N0 = 1.0
XI_D0 = 1.0

# Critical exponents – MUST be > 0 for a physically sensible crunch
ALPHA = 0.4   # liquidity‑number exponent
DELTA = 0.3   # divergence‑exponent

# Adaptive control parameters
KAPPA = 2.0   # steepness of sigmoid
LFI_MIN, LFI_MAX = -5.0, 5.0   # plausible LFI range

# Cost‑function weights (positive)
W1, W2 = 1.0, 1.0
LFI_TARGET = 0.0

# Φ‑impact accounting (short‑term cost, long‑term gain, both in % of baseline)
SHORT_TERM_COST = -13.0   # %
LONG_TERM_GAIN  =  70.0   # %

# ------------------- HELPER FUNCTIONS -------------------
def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))

def Phi_N_from_Lambda(Lambda):
    """Connectivity invariant from liquidity number."""
    xi_n = XI_N0 * (Lambda ** (-ALPHA))
    # Map correlation length to [0,1] via 1 - exp(-xi/xi0)  (monotonic, bounded)
    return 1.0 - np.exp(-xi_n / XI_N0)

def Phi_Delta_from_Grad(Grad):
    """Asymmetry invariant from normalized divergence."""
    xi_d = XI_D0 * (Grad ** (-DELTA))
    return 1.0 - np.exp(-xi_d / XI_D0)

def adaptive_limits(LFI):
    """Return time‑dependent min/max bounds for Φ_N and Φ_Delta."""
    s = sigmoid(-KAPPA * LFI)
    Phi_N_min = 0.4 + 0.3 * s          # ∈ [0.4, 0.7]
    Phi_Delta_max = 0.7 - 0.3 * s      # ∈ [0.4, 0.7]
    return Phi_N_min, Phi_Delta_max

def cost_integrand(Phi_N, Phi_Delta, s_c, LFI):
    """Integrand of the MPC‑Omega cost function (must be ≥0)."""
    return (1.0 - Phi_N)**2 + Phi_Delta**2 + W1 * s_c**2 + W2 * (LFI - LFI_TARGET)**2

# ------------------- VALIDATION -------------------
def main():
    print("=== Ω‑Protocol LC‑Ω Invariant Validation ===\n")

    # 1. Sweep dimensionless parameters
    Lambda_vals = np.logspace(-3, 2, 200)   # from 0.001 to 100
    Grad_vals   = np.logspace(-3, 2, 200)   # same for gradient term

    # Check Φ_N, Φ_Delta bounds
    Phi_N_vals = Phi_N_from_Lambda(Lambda_vals)
    Phi_D_vals = Phi_Delta_from_Grad(Grad_vals)

    assert np.all((0.0 <= Phi_N_vals) & (Phi_N_vals <= 1.0)), \
        "Φ_N out of [0,1] range"
    assert np.all((0.0 <= Phi_D_vals) & (Phi_D_vals <= 1.0)), \
        "Φ_Delta out of [0,1] range"
    print("✓ Φ_N and Φ_Delta stay within [0,1] for all tested Λ and ∇·J.")

    # 2. Adaptive limits vs hard bounds
    LFI_test = np.linspace(LFI_MIN, LFI_MAX, 400)
    for lfi in LFI_test:
        minN, maxD = adaptive_limits(lfi)
        assert minN >= 0.4 - 1e-12, f"Phi_N min < 0.4 at LFI={lfi}"
        assert maxD <= 0.7 + 1e-12, f"Phi_Delta max > 0.7 at LFI={lfi}"
    print("✓ Adaptive MPC‑Omega limits never violate hard bounds.")

    # 3. Cost integrand non‑negativity (sample random points)
    rng = np.random.default_rng(seed=42)
    for _ in range(1000):
        Phi_N = rng.random()
        Phi_D = rng.random()
        s_c   = rng.random() * 5.0   # arbitrary positive scale
        LFI   = rng.uniform(-5,5)
        assert cost_integrand(Phi_N, Phi_D, s_c, LFI) >= -1e-12, \
            "Negative cost integrand encountered"
    print("✓ Cost function integrand is non‑negative on random samples.")

    # 4. Φ‑impact accounting
    net_impact = SHORT_TERM_COST + LONG_TERM_GAIN
    print(f"\nΦ‑Impact Summary:")
    print(f"  Short‑term cost : {SHORT_TERM_COST:6.2f} %")
    print(f"  Long‑term gain  : {LONG_TERM_GAIN:6.2f} %")
    print(f"  Net 24‑mo impact: {net_impact:6.2f} %")
    if net_impact > 0:
        print("✓ Net Φ impact positive – proposal passes accounting check.")
    else:
        print("✗ Net Φ impact non‑positive – revisit cost/gain estimates.")

    print("\n=== Validation Complete ===")

if __name__ == "__main__":
    main()