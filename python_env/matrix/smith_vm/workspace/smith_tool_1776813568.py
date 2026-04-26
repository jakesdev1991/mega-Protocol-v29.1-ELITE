# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEIS-Ω invariant validator.
Run: python3 seis_validator.py
"""

import numpy as np
from scipy.special import softmax
from typing import List, Tuple

# -------------------------- Model Parameters --------------------------
ALPHA = 1.0   # double-well curvature
BETA  = 1.0
GAMMA = 0.5   # gradient coefficient
KAPPA = 0.2   # coupling to IVI in psi
SIGMOID_STEEPNESS = 10.0
SIGMOID_SHIFT   = 0.0

BASELINE_PHI_N = 1.0   # Φ_N^0 from a trusted uniform stack
MIN_PHI_N      = 0.6   # QP lower bound
MIN_S_DEP      = np.log(4)  # ≈1.386
MAX_IVI        = 0.72   # alert threshold

# -------------------------- Helper Functions --------------------------
def double_well(S: np.ndarray) -> np.ndarray:
    """V(S) = -α/2 S^2 + β/4 S^4 + γ/2 (∇S)^2 ; gradient term omitted for uniform field."""
    return -0.5*ALPHA*S**2 + 0.25*BETA*S**4

def hessian_eigenvalues(S0: float) -> Tuple[float, float]:
    """
    Returns (ω_N^2, ω_Δ^2) for a uniform background S0.
    ω_N^2 = V''(S0)   (zero‑mode)
    ω_Δ^2 = γ * k_min^2 + third‑order moment proxy.
    We approximate skewness via the third central moment of S fluctuations.
    """
    Vpp = -ALPHA + 3*BETA*S0**2          # V''(S0)
    # For demonstration we set a small k_min = 0.1 (inverse lattice size)
    k_min = 0.1
    omega_N_sq = Vpp
    # Placeholder for skewness‑mode: we will compute actual skewness later
    omega_Delta_sq = GAMMA * k_min**2   # gradient contribution
    return omega_N_sq, omega_Delta_sq

def correlation_length_from_phi_N(phi_N: float) -> float:
    """ξ = sqrt(γ/(2α)) * (Φ_N^0 / Φ_N)  (derived from ω_N^2 = 2α)"""
    xi0 = np.sqrt(GAMMA/(2*ALPHA))   # baseline correlation length
    return xi0 * (BASELINE_PHI_N / phi_n) if phi_n > 0 else np.inf

def skewness_field(S_samples: np.ndarray) -> float:
    """Estimate skewness = E[(S-μ)^3]/σ^3."""
    mu = np.mean(S_samples)
    sigma = np.std(S_samples)
    if sigma == 0:
        return 0.0
    return np.mean((S_samples - mu)**3) / (sigma**3)

def conditional_entropy(category_probs: List[float],
                        integrity_distrs: List[np.ndarray]) -> float:
    """
    S_dep = Σ_c p(c) [ - Σ_s p(s|c) log p(s|c) ]
    integrity_distrs[c] is a normalized histogram over integrity scores for category c.
    """
    S = 0.0
    for p_c, hist in zip(category_probs, integrity_distrs):
        # avoid log(0)
        hist_safe = np.where(hist > 0, hist, 1e-12)
        S += -p_c * np.sum(hist_safe * np.log(hist_safe))
    return S

def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + np.exp(-SIGMOID_STEEPNESS * (x - SIGMOID_SHIFT)))

def compute_ivi(phi_N: float, phi_Delta: float) -> float:
    arg = ALPHA*phi_Delta - BETA*phi_N + GAMMA
    return sigmoid(arg)

def compute_psi(phi_N: float, ivi: float) -> float:
    return np.log(phi_N / BASELINE_PHI_N) + KAPPA * ivi

# -------------------------- Synthetic Data Generator --------------------------
def generate_synthetic_data(n_clusters: int = 50,
                            n_categories: int = 4) -> Tuple[
                                List[float],          # phi_N per cluster (scalar field approximation)
                                List[float],          # phi_Delta per cluster
                                List[float],          # category weights p(c)
                                List[np.ndarray],    # integrity histograms per category
                            ]:
    """Creates mock integrity scores for each cluster."""
    # True integrity field S ~ mixture of two Gaussians (trusted/compromised)
    S_trusted  = np.random.normal(loc=+0.8, scale=0.1, size=n_clusters//2)
    S_comprom  = np.random.normal(loc=-0.8, scale=0.1, size=n_clusters - n_clusters//2)
    S_all = np.concatenate([S_trusted, S_comprom])
    np.random.shuffle(S_all)

    # Assign each cluster to a category uniformly
    cat_ids = np.random.randint(0, n_categories, size=n_clusters)
    p_c = np.bincount(cat_ids, minlength=n_categories) / n_clusters

    # Build integrity histograms per category (10 bins from -1 to +1)
    bins = np.linspace(-1, 1, 11)
    hists = []
    for c in range(n_categories):
        mask = (cat_ids == c)
        hist, _ = np.histogram(S_all[mask], bins=bins, density=True)
        hists.append(hist)

    # Approximate φ_N and φ_Δ per cluster via local moments
    phi_Ns = []
    phi_Deltas = []
    for i in range(n_clusters):
        # Use a small neighbourhood (here just the whole set for simplicity)
        S_loc = S_all
        mu = np.mean(S_loc)
        sigma = np.std(S_loc) + 1e-9
        # ω_N^2 ~ V''(μ)
        omega_N_sq = -ALPHA + 3*BETA*mu**2
        phi_N = np.sqrt(np.abs(omega_N_sq))   # ensure non‑negative
        # ω_Δ^2 ~ gradient term + skewness contribution
        skew = skewness_field(S_loc)
        omega_Delta_sq = GAMMA * 0.1**2 + np.abs(skew)  # placeholder scaling
        phi_D = np.sqrt(np.abs(omega_Delta_sq))
        phi_Ns.append(phi_N)
        phi_Deltas.append(phi_D)

    return phi_Ns, phi_Deltas, p_c.tolist(), hists

# -------------------------- Validation Routine --------------------------
def validate_state(phi_Ns: List[float],
                   phi_Deltas: List[float],
                   p_c: List[float],
                   hists: List[np.ndarray]) -> None:
    """Check all Omega‑Protocol invariants and QP constraints."""
    # Aggregated observables (mean field approximation)
    phi_N_bar   = np.mean(phi_Ns)
    phi_Delta_bar = np.mean(phi_Deltas)
    S_dep = conditional_entropy(p_c, hists)
    ivi = compute_ivi(phi_N_bar, phi_Delta_bar)
    psi = compute_psi(phi_N_bar, ivi)

    # --- QP Constraints ---
    if phi_N_bar < MIN_PHI_N:
        raise RuntimeError(f"Φ_N ({phi_N_bar:.3f}) below minimum {MIN_PHI_N}")
    if S_dep < MIN_S_DEP:
        raise RuntimeError(f"Conditional entropy S_dep ({S_dep:.3f}) below ln(4)={MIN_S_DEP:.3f}")
    if ivi > MAX_IVI:
        raise RuntimeError(f"IVI ({ivi:.3f}) exceeds alert threshold {MAX_IVI}")

    # --- Invariant Bounds (optional sanity) ---
    # ψ should be finite; extreme values indicate boundary approach
    if not np.isfinite(psi):
        raise RuntimeError(f"ψ_dep is non‑finite: {psi}")

    # --- Boundary‑condition checks (informational) ---
    # Integrity Shredding: Φ_N→∞ & S_dep→0
    # Integrity Chaos:   Φ_N→0  & S_dep→S_max
    S_max = -np.sum(p_c * np.log(np.where(np.array(p_c)>0, p_c, 1e-12)))  # max entropy if uniform across cats
    if phi_N_bar > 10.0 and S_dep < 0.1:
        print("[INFO] Approaching Integrity Shredding regime")
    if phi_N_bar < 0.1 and S_dep > 0.9*S_max:
        print("[INFO] Approaching Integrity Chaos regime")

    # If we reach here, the state is compliant
    print("[OK] State complies with Omega Protocol:")
    print(f"  Φ_N   = {phi_N_bar:.3f}")
    print(f"  Φ_Δ   = {phi_Delta_bar:.3f}")
    print(f"  S_dep = {S_dep:.3f}")
    print(f"  IVI   = {ivi:.3f}")
    print(f"  ψ_dep = {psi:.3f}")

# -------------------------- Main Execution --------------------------
if __name__ == "__main__":
    np.random.seed(42)
    phi_Ns, phi_Deltas, p_c, hists = generate_synthetic_data()
    try:
        validate_state(phi_Ns, phi_Deltas, p_c, hists)
    except RuntimeError as e:
        print(f"[REJECT] {e}")
        # In a real MPC‑Ω loop this would trigger a control action (rollback, quarantine, …)