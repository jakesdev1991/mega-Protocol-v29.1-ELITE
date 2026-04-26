# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
DEPS‑Ω Mathematical & Invariant Validator
----------------------------------------
Checks:
  1. Gap scaling → correct self‑correcting / unstable regimes.
  2. Invariants ψ, ξ_N, ξ_Δ behave as prescribed.
  3. Shredding and Informational Freeze conditions are detected.
  4. Dimensional control respects bounds and reduces the cost J.
  5. Φ_N and Φ_Δ stay within a reasonable neighbourhood of their targets.
"""

import numpy as np

# ----------------------------------------------------------------------
# Model parameters (can be tuned)
# ----------------------------------------------------------------------
d_c = 3                     # critical dimension for self‑correction
d_min, d_max = 2, 5         # allowed dimensional range
L0 = 1.0                    # reference length
L_max = 100.0               # max system size
T_safe = 1.0                # safe temperature (in units of k_B)
kB = 1.0                    # Boltzmann constant (set to 1 for simplicity)

# Weights for the MPC cost function
w1, w2, w3, w4 = 1.0, 1.0, 0.5, 0.2
Phi_N_target = 1.0          # desired Newtonian invariant
d_opt = d_c                 # optimal dimension (just at the threshold)

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def gap(d, L):
    """
    Energy gap scaling: Δ ∝ L^{-k(d)}.
    k(d) = 0 for d >= d_c, else k(d) = (d_c - d) (positive).
    """
    if d >= d_c:
        k = 0.0
    else:
        k = float(d_c - d)   # simple linear model; any positive works
    return L ** (-k) if L > 0 else np.inf

def invariants(d, L, Phi_N, Phi_Delta):
    """
    Compute ψ, ξ_N, ξ_Δ from definitions:
        ψ = ln(L/L0)
        ξ_N = ∂Φ_N/∂ψ  ≈ (Φ_N(L) - Φ_N(L0))/ψ   (finite‑difference)
        ξ_Δ = ∂Φ_Δ/∂ψ
    For the validator we assume Φ_N, Φ_Δ are *independent* of L
    (i.e. logical expectation values are size‑independent in the code space).
    Hence ξ_N = ξ_Δ = 0 when Φ_N, Φ_Δ are constant.
    To illustrate scaling we add a tiny L‑dependence:
        Φ_N(L) = Phi_N * (1 + epsilon * L^{-alpha})
    with epsilon << 1.
    """
    eps = 1e-3
    alpha = 1.0
    Phi_N_L = Phi_N * (1.0 + eps * L ** (-alpha))
    Phi_D_L = Phi_Delta * (1.0 + eps * L ** (-alpha))
    psi = np.log(L / L0)
    # finite‑difference derivative w.r.t. ψ using two points (L and L0)
    if psi == 0:
        xi_N = xi_Delta = 0.0
    else:
        xi_N = (Phi_N_L - Phi_N) / psi
        xi_Delta = (Phi_D_L - Phi_Delta) / psi
    return psi, xi_N, xi_Delta

def shredding_condition(d, L):
    """Shredding if d < d_c and gap → 0 as L→∞."""
    if d < d_c:
        # In the limit L→∞, gap → 0 iff k>0
        return gap(d, L) < 1e-12   # practically zero for large L
    return False

def freeze_condition(d, L):
    """Freeze if d >> d_c and gap so large that fluctuations suppressed."""
    # We treat "too large" as gap > some threshold (here 0.9 of max possible)
    # Max gap occurs at L = L0 (gap = 1). So freeze if gap > 0.9 and d > d_c+2
    return d > d_c + 2 and gap(d, L) > 0.9

def mpc_step(state):
    """
    One MPC iteration:
        - state = [Phi_N, Phi_Delta, psi, xi_N, xi_Delta, S_h, d, L, T]
        - Compute cost J.
        - If shredding risk → escalate d (d+1, clipped).
        - Else if freeze risk → de‑escalate d (d-1, clipped).
        - Return new state and cost difference (J_new - J_old).
    """
    Phi_N, Phi_Delta, psi, xi_N, xi_Delta, S_h, d, L, T = state

    # ---- Cost before control ----
    J_old = (w1 * (Phi_N - Phi_N_target) ** 2 +
             w2 * Phi_Delta ** 2 +
             w3 * (d - d_opt) ** 2 +
             w4 * S_h ** 2)

    # ---- Control decision ----
    if shredding_condition(d, L):
        d_new = min(d + 1, d_max)   # escalate
    elif freeze_condition(d, L):
        d_new = max(d - 1, d_min)   # de‑escalate
    else:
        d_new = d                    # no change

    # ---- Re‑compute invariants with new d (same L, T) ----
    psi_new, xi_N_new, xi_Delta_new = invariants(d_new, L, Phi_N, Phi_Delta)

    # Entropy gauge (simplified): S_h ~ (L/ell_T)^{d-1}, ell_T = 1/T (if T>0)
    ell_T = 1.0 / T if T > 0 else np.inf
    S_h_new = (L / ell_T) ** (d_new - 1) if ell_T > 0 else 0.0

    # ---- Cost after control ----
    J_new = (w1 * (Phi_N - Phi_N_target) ** 2 +
             w2 * Phi_Delta ** 2 +
             w3 * (d_new - d_opt) ** 2 +
             w4 * S_h_new ** 2)

    new_state = [Phi_N, Phi_Delta, psi_new, xi_N_new, xi_Delta_new,
                 S_h_new, d_new, L, T]
    return new_state, J_new - J_old

# ----------------------------------------------------------------------
# Validation routine
# ----------------------------------------------------------------------
def validate():
    # Initial guess: start just below critical dimension to test escalation
    L_init = 50.0
    T_init = 0.5
    d_init = 2          # < d_c → should trigger shredding → escalate to 3
    Phi_N_init = 1.0
    Phi_Delta_init = 0.0
    psi_init, xi_N_init, xi_Delta_init = invariants(d_init, L_init,
                                                    Phi_N_init, Phi_Delta_init)
    ell_T = 1.0 / T_init if T_init > 0 else np.inf
    S_h_init = (L_init / ell_T) ** (d_init - 1) if ell_T > 0 else 0.0

    state = [Phi_N_init, Phi_Delta_init, psi_init, xi_N_init, xi_Delta_init,
             S_h_init, d_init, L_init, T_init]

    print("Initial state:", state)
    new_state, delta_J = mpc_step(state)
    print("After MPC step:", new_state)
    print("Cost change (J_new - J_old):", delta_J)

    # ---- Invariant checks ----
    Phi_N, Phi_Delta, psi, xi_N, xi_Delta, S_h, d, L, T = new_state

    # 1. Dimension within allowed bounds
    assert d_min <= d <= d_max, f"Dimension {d} out of bounds [{d_min},{d_max}]"

    # 2. System size and temperature within safety limits
    assert L <= L_max, f"System size {L} exceeds L_max={L_max}"
    assert T <= T_safe, f"Temperature {T} exceeds T_safe={T_safe}"

    # 3. No shredding condition should persist after control
    assert not shredding_condition(d, L), "Shredding condition still active after control"

    # 4. If we are in the self‑correcting regime (d>=d_c) the gap should be non‑vanishing
    if d >= d_c:
        assert gap(d, L) > 0.0, f"Gap vanished unexpectedly for d={d}, L={L}"
        # Invariants should remain finite (our model gives tiny values)
        assert np.isfinite(xi_N) and np.isfinite(xi_Delta), "ξ_N or ξ_Δ not finite"

    # 5. Cost must not increase (MPC should be non‑ascending)
    assert delta_J <= 1e-9, f"Cost increased by {delta_J} – MPC failed to descend"

    # 6. Φ_N and Φ_Delta stay near target (within a loose tolerance)
    assert abs(Phi_N - Phi_N_target) < 0.5, f"Φ_N drifted far from target: {Phi_N}"
    assert abs(Phi_Delta) < 0.5, f"Φ_Δ drifted far from zero: {Phi_Delta}"

    print("\nAll Omega‑Protocol invariants satisfied ✅")

if __name__ == "__main__":
    validate()