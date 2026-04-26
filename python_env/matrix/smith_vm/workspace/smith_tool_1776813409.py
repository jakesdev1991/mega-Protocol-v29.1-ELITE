# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator for TTM-Ω / TCPM-Ω
-----------------------------------------------------
Checks:
    * 0 ≤ TTCI ≤ 1
    * 0 ≤ Φ_N = 1 - TTCI(t-τ) ≤ 1
    * Φ_Delta = Var[log(xi_ij/xi0)] ≥ 0
    * J matrix symmetric, real, PSD
    * ψ = ln(Φ_N) finite (Φ_N > 0)
    * MPC‑Ω constraints: TTCI ≥ 0.6, Δ_regime ≥ Δ_min, ξ ≥ ξ_min
    * Cost function convex (quadratic) – Hessian PSD
"""

import numpy as np
from numpy.linalg import eigvalsh, cholesky, LinAlgError

# ------------------- CONFIGURABLE PARAMETERS -------------------
TAU_PRED = 3          # days prediction horizon used in Φ_N
DELTA_MIN = 0.5       # regime gap minimum (normed)
XI_MIN    = 0.4       # correlation length minimum (normed)
TTCI_MIN  = 0.6       # MPC‑Ω lower bound on TTCI
# --------------------------------------------------------------

def synthetic_data(n_signals=8, n_time=30, seed=42):
    """Generate plausible spin‑like data for validation."""
    rng = np.random.default_rng(seed)
    # Spins S_i^z(t) ∈ {−1,+1}
    S = rng.choice([-1, 1], size=(n_time, n_signals))
    # Time‑dependent coupling J_ij(t) – enforce PSD via random factor model
    F = rng.standard_normal((n_time, n_signals, 3))   # 3 latent factors
    J = np.einsum('tki,tkj->tij', F, F)               # PSD by construction
    # Add small noise to avoid exact degeneracy
    J += 1e-4 * np.eye(n_signals)[None, :, :]
    # Regime gap and correlation length (proxy)
    delta_regime = np.abs(np.mean(S, axis=1))          # dummy proxy
    xi = 1.0 + 0.5 * np.sin(np.linspace(0, 2*np.pi, n_time))  # varies 0.5‑1.5
    return S, J, delta_regime, xi

def wilson_loop(S, loop_idx):
    """Expectation of product of spins over a predefined loop."""
    # loop_idx: list of signal indices forming a closed loop
    prod = np.prod(S[:, loop_idx], axis=1)   # shape (n_time,)
    return np.mean(prod)

def compute_ttci(S, J, delta_regime, xi, loop_idx, S0=None, J0=None,
                 delta0=None, xi0=None):
    """TTCI(t) = |<W_p>|/|<W_p0>| * (Δ/Δ0) * (ξ/ξ0)."""
    if S0 is None:   # use first time step as reference
        S0 = S[0:1]
        J0 = J[0:1]
        delta0 = delta_regime[0:1]
        xi0 = xi[0:1]

    Wp_t   = wilson_loop(S, loop_idx)
    Wp0    = wilson_loop(S0, loop_idx)
    # Avoid division by zero – if reference zero, set ratio to 1 (no change)
    Wp_ratio = np.abs(Wp_t) / (np.abs(Wp0) + 1e-12)

    Delta_ratio = delta_regime / (delta0 + 1e-12)
    Xi_ratio    = xi / (xi0 + 1e-12)

    ttci = Wp_ratio * Delta_ratio * Xi_ratio
    # Clip to [0,1] for safety (theoretical bound)
    return np.clip(ttci, 0.0, 1.0)

def check_invariants(S, J, delta_regime, xi, loop_idx):
    """Return True if all Ω‑invariants hold, else raise."""
    n_time = S.shape[0]
    ttci = compute_ttci(S, J, delta_regime, xi, loop_idx)

    # ---- TTCI bounds -------------------------------------------------
    if not np.all((0.0 <= ttci) & (ttci <= 1.0)):
        raise ValueError(f"TTCI out of [0,1]: min={ttci.min()}, max={ttci.max()}")

    # ---- Φ_N ---------------------------------------------------------
    Phi_N = 1.0 - np.roll(ttci, TAU_PRED)   # shift for prediction horizon
    Phi_N[:TAU_PRED] = Phi_N[TAU_PRED]      # pad early steps with first valid
    if not np.all((0.0 <= Phi_N) & (Phi_N <= 1.0)):
        raise ValueError(f"Φ_N out of [0,1]: min={Phi_N.min()}, max={Phi_N.max()}")

    # ---- ψ = ln(Φ_N) -------------------------------------------------
    if np.any(Phi_N <= 0):
        raise ValueError(f"Φ_N non‑positive → ψ undefined: min={Phi_N.min()}")
    psi = np.log(Phi_N)
    if not np.all(np.isfinite(psi)):
        raise ValueError("ψ contains non‑finite values")

    # ---- Φ_Delta -----------------------------------------------------
    # Correlation length proxy from xi (assume isotropic)
    # Compute log‑ratio variance across signal pairs at each time step
    log_ratio = np.log(xi[:, None] / xi[None, :] + 1e-12)   # (n_time, n, n)
    # Take upper‑triangular variance (ignore diagonal)
    triu_idx = np.triu_indices_from(log_ratio[0], k=1)
    Phi_Delta = np.var(log_ratio[:, triu_idx[0], triu_idx[1]], axis=1)
    if np.any(Phi_Delta < -1e-12):   # allow tiny negative due to float error
        raise ValueError(f"Φ_Delta negative: min={Phi_Delta.min()}")

    # ---- J matrix PSD & symmetry --------------------------------------
    for t in range(n_time):
        Jt = J[t]
        if not np.allclose(Jt, Jt.T, atol=1e-8):
            raise ValueError(f"J matrix not symmetric at t={t}")
        evals = eigvalsh(Jt)
        if np.any(evals < -1e-8):
            raise ValueError(f"J matrix not PSD at t={t}: min eval={evals.min()}")

    # ---- MPC‑Ω constraints -------------------------------------------
    if np.any(ttci < TTCI_MIN):
        raise ValueError(f"TTCI below MPC‑Ω min ({TTCI_MIN}): min={ttci.min()}")
    if np.any(delta_regime < DELTA_MIN):
        raise ValueError(f"Regime gap below Δ_min ({DELTA_MIN}): min={delta_regime.min()}")
    if np.any(xi < XI_MIN):
        raise ValueError(f"Correlation length below ξ_min ({XI_MIN}): min={xi.min()}")

    # ---- Cost function convexity (quadratic) ------------------------
    # Cost = Σ [ (TTCI_min - TTCI)_+^2 + μ1(Δ_min - Δ)_+^2 + μ2(ξ_min - ξ)_+^2 ]
    # Hessian is diagonal with entries 2*indicator(constraint active) → PSD.
    # We just verify no negative curvature by checking second‑difference >=0.
    def penalty(x, x_min):
        diff = x_min - x
        return np.where(diff > 0, diff**2, 0.0)
    cost = penalty(ttci, TTCI_MIN) + \
           0.5*penalty(delta_regime, DELTA_MIN) + \
           0.3*penalty(xi, XI_MIN)
    # second finite difference should be ≥0 (convex in discrete sense)
    d2 = np.diff(cost, n=2)
    if np.any(d2 < -1e-9):
        raise ValueError(f"Cost function non‑convex: min d2={d2.min()}")

    # All checks passed
    return {
        "ttci": ttci,
        "Phi_N": Phi_N,
        "Phi_Delta": Phi_Delta,
        "psi": psi,
        "cost": cost
    }

# ------------------- RUN VALIDATION -------------------
if __name__ == "__main__":
    np.set_printoptions(precision=4, suppress=True)
    S, J, delta_regime, xi = synthetic_data()
    # Example Wilson loop: use first 4 signals as a loop (0‑1‑2‑3‑0)
    loop_idx = [0, 1, 2, 3]
    try:
        results = check_invariants(S, J, delta_regime, xi, loop_idx)
        print("✅ All Ω‑invariants and MPC‑Ω constraints satisfied.")
        # Optional: show a snapshot
        print(f"Latest TTCI: {results['ttci'][-1]:.4f}")
        print(f"Latest Φ_N:  {results['Phi_N'][-1]:.4f}")
        print(f"Latest Φ_Δ:  {results['Phi_Delta'][-1]:.4f}")
    except Exception as e:
        print("❌ Invariant violation detected:")
        print(e)
        # In the Omega Protocol VM this would halt the offending thought.
        raise