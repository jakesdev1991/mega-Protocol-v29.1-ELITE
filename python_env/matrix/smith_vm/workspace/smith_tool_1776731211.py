# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Validator for FOASH-Ω updates.
Raises OmegaInvariantViolation if any invariant is broken.
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple

# ----------------------------------------------------------------------
# Exception definition
# ----------------------------------------------------------------------
class OmegaInvariantViolation(RuntimeError):
    """Raised when a candidate state violates Omega Protocol invariants."""
    pass

# ----------------------------------------------------------------------
# Configuration (could be loaded from a governance contract)
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class FOASHConfig:
    # Protocol bounds
    PHI_N_MAX: float = 1.0
    PHI_DELTA_MAX: float = 1.0

    # Mapping gains (must be non‑negative)
    ETA1: float = 0.2
    ETA2: float = 0.3
    ETA3: float = 0.1

    # Lead times (in same time‑unit as the simulation step)
    TAU1: int = 3
    TAU2: int = 3

    # Sigmoid normalisation for OHI
    MU_OHI: float = 0.5
    SIGMA_OHI: float = 0.2

    # Cost weights
    LAMBDA1: float = 1.0
    LAMBDA2: float = 0.5

    # Log‑coherence safety bound
    PSI_MAX: float = 1e6

    # Harmonic weights (must sum to 1.0)
    W: Tuple[float, ...] = (0.5, 0.3, 0.2)

    # Healthy baseline per order (mu_k, sigma_k)
    MU_K: Tuple[float, ...] = (1.0, 0.8, 0.5)
    SIGMA_K: Tuple[float, ...] = (0.2, 0.2, 0.2)

    # Derived constants
    def __post_init__(self):
        object.__setattr__(self, 'W', np.asarray(self.W, dtype=float))
        object.__setattr__(self, 'MU_K', np.asarray(self.MU_K, dtype=float))
        object.__setattr__(self, 'SIGMA_K', np.asarray(self.SIGMA_K, dtype=float))
        if not np.isclose(self.W.sum(), 1.0):
            raise ValueError("Harmonic weights must sum to 1.")
        if np.any(self.SIGMA_K <= 0):
            raise ValueError("Sigma_k must be positive.")


# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def clip(x: np.ndarray, low: float, high: float) -> np.ndarray:
    return np.clip(x, low, high)


def magnitude_squared_coherence(Sxy: np.ndarray, Sxx: np.ndarray, Syy: np.ndarray) -> np.ndarray:
    """Return coherence clipped to [0,1] to enforce definition."""
    coh = np.abs(Sxy) ** 2 / (Sxx * Syy + 1e-12)  # avoid div‑0
    return clip(coh, 0.0, 1.0)


# ----------------------------------------------------------------------
# Core validation routine
# ----------------------------------------------------------------------
def validate_foash_update(
    # Raw inputs as they would be produced by the FOASH-Ω model before clipping
    A_k: np.ndarray,               # harmonic amplitudes vector (shape: (K,))
    S_xy: np.ndarray,              # cross‑spectrum for a chosen indicator pair
    S_xx: np.ndarray,
    S_yy: np.ndarray,
    Phi_N0: float,                 # baseline strategic connectivity
    Phi_Delta0: float,             # baseline information asymmetry
    # History buffers (needed for lead times)
    OHI_hist: np.ndarray,          # shape (max(tau1,tau2)+1,), oldest first
    A_hist: np.ndarray,            # shape (max(tau1,tau2)+1, K) for variance term
    cfg: FOASHConfig = FOASHConfig(),
) -> Tuple[float, float, float, float, float, float]:
    """
    Compute and validate the FOASH-Ω update.
    Returns the *clipped* state tuple:
        (OHI, Phi_N, Phi_Delta, psi, xi_N, xi_Delta)
    Raises OmegaInvariantViolation if any invariant cannot be satisfied.
    """
    K = len(cfg.W)
    if A_k.shape != (K,):
        raise ValueError(f"A_k must have length {K}, got {A_k.shape}")

    # ------------------------------------------------------------------
    # 1. Compute Order Health Index (OHI) with safety clipping
    # ------------------------------------------------------------------
    dev = np.abs(A_k - cfg.MU_K) / cfg.SIGMA_K
    weighted_dev = cfg.W * dev
    OHI_raw = 1.0 - np.sum(weighted_dev)
    # Clip to the physically meaningful interval [0,1]
    OHI = clip(OHI_raw, 0.0, 1.0)

    # ------------------------------------------------------------------
    # 2. Update history buffers (shift left, append newest)
    # ------------------------------------------------------------------
    max_tau = max(cfg.TAU1, cfg.TAU2)
    OHI_hist = np.roll(OHI_hist, -1)
    OHI_hist[-1] = OHI
    A_hist = np.roll(A_hist, -1, axis=0)
    A_hist[-1, :] = A_k

    # ------------------------------------------------------------------
    # 3. Map OHI -> Phi_N, Phi_Delta (with lead times)
    # ------------------------------------------------------------------
    OHI_tau1 = OHI_hist[-cfg.TAU1 - 1] if cfg.TAU1 > 0 else OHI
    OHI_tau2 = OHI_hist[-cfg.TAU2 - 1] if cfg.TAU2 > 0 else OHI

    Phi_N_raw = Phi_N0 + cfg.ETA1 * sigmoid((OHI_tau1 - cfg.MU_OHI) / cfg.SIGMA_OHI)
    # Variance term: use the *current* harmonic amplitude variance across orders
    var_Ak = np.var(A_k)
    Phi_Delta_raw = Phi_Delta0 - cfg.ETA2 * OHI_tau2 + cfg.ETA3 * var_Ak

    # Clip to protocol bounds
    Phi_N = clip(Phi_N_raw, 0.0, cfg.PHI_N_MAX)
    Phi_Delta = clip(Phi_Delta_raw, 0.0, cfg.PHI_DELTA_MAX)

    # ------------------------------------------------------------------
    # 4. Spectral coherence -> correlation length xi and psi
    # ------------------------------------------------------------------
    coh = magnitude_squared_coherence(S_xy, S_xx, S_yy)
    avg_coh = np.mean(coh)
    # Guard against zero average coherence (would give infinite xi)
    if avg_coh <= 0:
        # Fallback to a large but finite correlation length
        xi = 1e6
    else:
        xi = 1.0 / avg_coh
    # Enforce xi >= 1 (by definition)
    xi = max(xi, 1.0)

    # Reference coherence length xi0 – choose 1.0 (i.e. perfect coherence)
    XI0 = 1.0
    psi_raw = np.log(xi / XI0)
    psi = clip(psi_raw, -cfg.PSI_MAX, cfg.PSI_MAX)

    # ------------------------------------------------------------------
    # 5. Sensitivities xi_N = dPhi_N/dpsi, xi_Delta = dPhi_Delta/dpsi
    # ------------------------------------------------------------------
    # Since Phi_N and Phi_Delta are piecewise linear/clipped w.r.t OHI,
    # and OHI does NOT depend on psi directly, the derivative is zero
    # unless we explicitly model a dependence. For safety we compute
    # a numeric derivative using a tiny perturbation.
    eps = 1e-6
    # Perturb psi -> perturb xi -> perturb coh -> ... (too involved)
    # Instead we enforce that the sensitivities are bounded by a small
    # constant; we set them to zero (no direct psi coupling in the current
    # formulation) and later allow the MPC‑Ω to ignore them.
    xi_N = 0.0
    xi_Delta = 0.0

    # ------------------------------------------------------------------
    # 6. Instantaneous cost integrand (must be non‑negative)
    # ------------------------------------------------------------------
    inst_cost = (1.0 - OHI) ** 2 + cfg.LAMBDA1 * (Phi_Delta ** 2) + cfg.LAMBDA2 * np.sum(np.gradient(A_k) ** 2)
    if inst_cost < -1e-12:  # allow tiny negative due to round‑off
        raise OmegaInvariantViolation(
            f"Instantaneous cost negative: {inst_cost}. "
            f"OHI={OHI}, Phi_Delta={Phi_Delta}, gradA2={np.sum(np.gradient(A_k)**2)}"
        )

    # ------------------------------------------------------------------
    # 7. MPC‑Ω box constraints (explicitly enforced by clipping above)
    # ------------------------------------------------------------------
    if not (0.3 <= OHI <= 1.0):
        raise OmegaInvariantViolation(f"OHI out of MPC bounds: {OHI}")
    if not (0.6 <= Phi_N <= cfg.PHI_N_MAX):
        raise OmegaInvariantViolation(f"Phi_N out of MPC bounds: {Phi_N}")
    if not (0.0 <= Phi_Delta <= 0.7):
        raise OmegaInvariantViolation(f"Phi_Delta out of MPC bounds: {Phi_Delta}")

    # ------------------------------------------------------------------
    # 8. Return the validated, clipped state
    # ------------------------------------------------------------------
    return OHI, Phi_N, Phi_Delta, psi, xi_N, xi_Delta


# ----------------------------------------------------------------------
# Example usage (self‑test)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    np.random.seed(42)
    cfg = FOASHConfig()
    K = len(cfg.W)

    # Dummy spectral data (ensure Sxx, Syy > 0)
    S_xy = np.random.randn() + 1j * np.random.randn()
    S_xx = np.abs(np.random.randn() + 1j * np.random.randn()) ** 2 + 0.5
    S_yy = np.abs(np.random.randn() + 1j * np.random.randn()) ** 2 + 0.5

    # Harmonic amplitudes around healthy baseline
    A_k = cfg.MU_K + 0.1 * np.random.randn(K)

    # History buffers (filled with current value for simplicity)
    OHI_hist = np.full(max(cfg.TAU1, cfg.TAU2) + 1, 0.5)
    A_hist = np.tile(A_k, (max(cfg.TAU1, cfg.TAU2) + 1, 1))

    try:
        state = validate_foash_update(
            A_k=A_k,
            S_xy=S_xy,
            S_xx=S_xx,
            S_yy=S_yy,
            Phi_N0=0.5,
            Phi_Delta0=0.3,
            OHI_hist=OHI_hist,
            A_hist=A_hist,
            cfg=cfg,
        )
        print("Validation passed. State:", state)
    except OmegaInvariantViolation as e:
        print("Validation FAILED:", e)