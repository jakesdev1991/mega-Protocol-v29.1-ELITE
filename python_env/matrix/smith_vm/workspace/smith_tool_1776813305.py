# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from numpy.polynomial import Polynomial

# ----------------------------------------------------------------------
# USER‑DEFINED CONSTANTS (set at deployment, treated as immutable)
# ----------------------------------------------------------------------
ALPHA   = -1.0   # < 0
BETA    =  2.0   # > 0
GAMMA   =  0.5   # > 0
KAPPA   = {"k1": 0.8, "k2": 0.1, "k3": 0.6, "k4": 0.05}
GAMMA_T = 1.0    # placeholder for higher‑order coupling Gamma(t)
PHI_N0  = 1.0    # baseline coherence scale
S_LOW   = 0.2    # minimum allowed conditional entropy (nats)
S_HIGH  = 1.5    # maximum allowed conditional entropy (nats)
PCI_MIN = 0.6
PHI_N_MIN = 0.5
EPS = 1e-12      # numerical safety

# ----------------------------------------------------------------------
# HELPERS
# ----------------------------------------------------------------------
def double_well(C):
    """V(C) = α/2 C^2 + β/4 C^4 - γ C"""
    return 0.5*ALPHA*C**2 + 0.25*BETA*C**4 - GAMMA*C

def dV(C):
    """First derivative V'(C)"""
    return ALPHA*C + BETA*C**3 - GAMMA

def d2V(C):
    """Second derivative V''(C) = α + 3β C^2"""
    return ALPHA + 3*BETA*C**2

def find_minima():
    """Solve V'(C)=0 → cubic; return real roots."""
    # V'(C) = BETA C^3 + ALPHA C - GAMMA = 0
    coeffs = [BETA, 0.0, ALPHA, -GAMMA]   # [c^3, c^2, c^1, c^0]
    roots = Polynomial(coeffs).roots()
    real_roots = [r.real for r in roots if np.abs(r.imag) < 1e-8]
    return np.array(real_roots)

def conditional_entropy(p_r, p_c_given_r):
    """
    p_r: 1D array, probabilities of regions (sums to 1)
    p_c_given_r: 2D array, shape (n_regions, n_bins),
                 conditional probabilities p(c|r) (each row sums to 1)
    Returns S_perc in nats.
    """
    assert np.allclose(p_r.sum(), 1.0), "p_r must sum to 1"
    assert np.allclose(p_c_given_r.sum(axis=1), 1.0), "each p(c|r) row must sum to 1"
    # avoid log(0)
    safe = np.clip(p_c_given_r, EPS, 1.0)
    S = -np.sum(p_r[:, None] * safe * np.log(safe), axis=1)
    return np.sum(p_r * S)

# ----------------------------------------------------------------------
# VALIDATOR
# ----------------------------------------------------------------------
def validate_pcs_ohm(state):
    """
    state: dict with the following keys (all np.arrays or scalars):
        - C_field   : scalar or 1D array representing the coherence field value(s)
        - grad_norm : scalar, ||∇C||_2
        - C_norm    : scalar, ||C||_2
        - skew_C    : scalar, Skew[C]
        - p_r       : 1D array, region probabilities
        - p_c_given_r: 2D array, p(c|r)
        - Gamma_t   : scalar, Gamma(t) (higher‑order coupling)
    Returns True if all Ω‑Protocol invariants hold; raises ValueError otherwise.
    """
    # ----- 1. Potential shape -----
    if not (ALPHA < 0 and BETA > 0 and GAMMA > 0):
        raise ValueError("Potential parameters must satisfy α<0, β>0, γ>0")

    # ----- 2. Find metastable minimum -----
    mins = find_minima()
    if len(mins) == 0:
        raise ValueError("No real stationary points found for V(C)")
    # Choose the *metastable* (higher V) minimum as the reference point
    V_vals = double_well(mins)
    meta_idx = np.argsort(V_vals)[-2] if len(V_vals) >= 2 else 0  # second‑largest V
    C_star = mins[meta_idx]

    # ----- 3. Hessian (curvature) at metastable point -----
    curv = d2V(C_star)
    if curv <= 0:
        raise ValueError(f"Curvature at metastable point must be >0, got {curv}")

    # ----- 4. Covariant modes from Hessian eigenvalues -----
    # We map the curvature to the two eigenvalues via the proposed linear models:
    # ω_N^2 = κ1 * (||∇C||/||C||) + κ2
    # ω_Δ^2 = κ3 * Skew[C] + κ4
    grad_ratio = state["grad_norm"] / (state["C_norm"] + EPS)
    omega_N_sq = KAPPA["k1"] * grad_ratio + KAPPA["k2"]
    omega_D_sq = KAPPA["k3"] * state["skew_C"] + KAPPA["k4"]
    if omega_N_sq <= 0 or omega_D_sq <= 0:
        raise ValueError(
            f"Eigenvalues must be positive: ω_N^2={omega_N_sq}, ω_Δ^2={omega_D_sq}"
        )
    Phi_N_perc = np.sqrt(omega_N_sq)
    Phi_Delta_perc = np.sqrt(omega_D_sq)

    # ----- 5. Perceptual Coherence Index (PCI) -----
    PCI = Phi_N_perc * Phi_Delta_perc * state["Gamma_t"]
    if PCI < PCI_MIN:
        raise ValueError(f"PCI={PCI} below threshold {PCI_MIN}")

    # ----- 6. Invariant ψ_perc -----
    psi_perc = np.log(Phi_N_perc / PHI_N0)
    # No direct bound on ψ, but we will check boundary conditions later

    # ----- 7. Conditional entropy gauge -----
    S_perc = conditional_entropy(state["p_r"], state["p_c_given_r"])
    # Theoretical max entropy for uniform distribution over B bins:
    B = state["p_c_given_r"].shape[1]
    S_max = np.log(B)
    if not (S_LOW - EPS <= S_perc <= S_HIGH + EPS):
        raise ValueError(
            f"Conditional entropy S_perc={S_perc} not in [{S_LOW}, {S_HIGH}]"
        )
    # Optional: warn if approaching extremes (used for control triggering)
    # ----- 8. Boundary conditions (thermodynamic consistency) -----
    # Shredding: Φ_N → ∞  AND  S → S_max
    # Locking:   Φ_N → 0   AND  S → 0
    # We flag if the state is *near* either extreme (within tolerance)
    tol = 1e-2
    near_shred = (Phi_N_perc > 1.0 / tol) and (np.abs(S_perc - S_max) < tol)
    near_lock  = (Phi_N_perc < tol) and (np.abs(S_perc - 0.0) < tol)
    if near_shred:
        # In a real system this would trigger the "shredding" safety routine
        pass  # validation passes; control logic will act elsewhere
    if near_lock:
        # Similarly for locking
        pass

    # ----- 9. MPC‑Ω constraints (explicit QP limits) -----
    if Phi_N_perc < PHI_N_MIN:
        raise ValueError(f"Φ_N^{perc}={Phi_N_perc} below minimum {PHI_N_MIN}")
    # (PCI and S_perc already checked)

    # If we reach here, all invariants are satisfied
    return True

# ----------------------------------------------------------------------
# Example usage (replace with actual telemetry from the perception loop)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Mock state – in practice these come from the PCS‑Ω sensors
    mock_state = {
        "C_field": 0.3,                # not used directly in validation, but could be
        "grad_norm": 0.4,
        "C_norm": 0.5,
        "skew_C": 0.2,
        "p_r": np.array([0.5, 0.5]),
        "p_c_given_r": np.array([[0.7, 0.3],
                                 [0.4, 0.6]]),
        "Gamma_t": 1.0,
    }

    try:
        if validate_pcs_ohm(mock_state):
            print("✅ PCS‑Ω state satisfies all Ω‑Protocol invariants.")
    except ValueError as e:
        print(f"❌ Invariant violation: {e}")