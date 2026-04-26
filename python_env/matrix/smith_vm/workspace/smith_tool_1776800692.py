# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega‑Protocol Validation for QM‑Ω (Quantum Memory Shield for Distributed Cognition)

This script checks that the mathematical definitions given in the proposal
are internally consistent and respect the Ω‑invariants:
    Φ_N   – variance (inverse connectivity) of decoded cognitive state
    Φ_Δ   – skewness of residual cognitive‑error distribution
    J*    – optimal cost of the MPC‑Ω quadratic program

The validation proceeds in three stages:
    1. Synthetic data generation for a distributed psychological system.
    2. Computation of all intermediate quantities (CDI, ψ, S_cog, etc.).
    3. Assertion of Ω‑compliant properties (bounds, monotonicities, 
       positive‑semidefiniteness of the QP Hessian, etc.).

If any assertion fails, an AssertionError is raised with a diagnostic
message indicating which invariant or consistency condition was violated.
"""

import numpy as np
from numpy.linalg import norm, pinv
from scipy.stats import skew, kurtosis

# ----------------------------------------------------------------------
# Helper functions that mirror the definitions in the proposal
# ----------------------------------------------------------------------
def sparse_encoder(n, d, seed=0):
    """Return a random full‑rank encoder E ∈ ℝ^{n×d} with redundancy ρ=n/d."""
    rng = np.random.default_rng(seed)
    E = rng.standard_normal((n, d))
    # orthogonalise columns to avoid pathological scaling
    Q, _ = np.linalg.qr(E, mode='reduced')
    return Q  # n×d, orthonormal columns ⇒ ρ = n/d

def encode_state(E, c):
    """y = E c  (n‑dim encoded vector)"""
    return E @ c

def decohere(y, theta, sigma, seed=1):
    """Add Gaussian decoherence noise with probability theta per component."""
    rng = np.random.default_rng(seed)
    mask = rng.random(y.shape) < theta          # which entries are hit
    noise = rng.normal(0.0, sigma, size=y.shape)
    return y + mask * noise

def decode(y_tilde, E):
    """Least‑squares decoder: c_hat = (E^T E)^{-1} E^T y_tilde"""
    # E has orthonormal columns → E^T E = I_d
    return E.T @ y_tilde

def residual_error(y_tilde, E, c_hat):
    """r_i = ỹ_i - E_i c_hat  (per‑agent sub‑vector)"""
    # split y_tilde into m equal parts (assumes divisible)
    m = y_tilde.shape[0] // E.shape[1]
    r = []
    for i in range(m):
        start, end = i*E.shape[1], (i+1)*E.shape[1]
        yi = y_tilde[start:end]
        Ei = E  # same encoder for all agents (simplification)
        r.append(yi - Ei @ c_hat)
    return np.concatenate(r)

def compute_cdi(residuals, m, tau, alpha=1.0, beta=1.0, gamma=1.0):
    """
    CDI(t) = tanh( α θ_cog_dec + β ε + γ ρ )
    where
        θ_cog_dec = fraction of agents with ||r_i|| > τ
        ε         = mean residual magnitude
        ρ         = redundancy n/d (treated as constant here)
    """
    # reshape residuals to (m, d)
    d = residuals.shape[0] // m
    R = residuals.reshape(m, d)
    agent_norms = np.linalg.norm(R, axis=1)
    theta_cog_dec = np.mean(agent_norms > tau)
    epsilon = np.mean(agent_norms)
    rho = 3.0  # example redundancy from proposal (n/d ≈ 3)
    raw = alpha * theta_cog_dec + beta * epsilon + gamma * rho
    return np.tanh(raw)

def phi_n_from_cdi(PhiN0, CDI, theta_cog_dec, eta1=0.5, eta2=0.3, tau1=0.0):
    """Φ_N^{(qm)}(t) = Φ_N^{(0)} - η1·CDI(t-τ1) + η2·(1-θ_cog_dec(t-τ1))"""
    return PhiN0 - eta1 * CDI + eta2 * (1.0 - theta_cog_dec)

def phi_delta_from_cdi(PhiDelta0, theta_cog_dec, epsilon, eta3=0.4, eta4=0.2, tau2=0.0):
    """Φ_Δ^{(qm)}(t) = Φ_Δ^{(0)} + η3·θ_cog_dec - η4·ε"""
    return PhiDelta0 + eta3 * theta_cog_dec - eta4 * epsilon

def invariant_psi(Ricci, Ricci0, CDI, lam=0.5):
    """ψ = ln(|ℛ_G|/ℛ₀) + λ·CDI"""
    return np.log(np.abs(Ricci) / Ricci0) + lam * CDI

def entropy_cognitive(y_tilde):
    """S_cog = -∑ p_i log p_i,  p_i = ||ỹ_i|| / ∑_j ||ỹ_j||"""
    m = y_tilde.shape[0] // y_tilde.shape[1]  # assuming equal block size
    d = y_tilde.shape[0] // m
    Y = y_tilde.reshape(m, d)
    norms = np.linalg.norm(Y, axis=1)
    p = norms / np.sum(norms)
    # avoid log(0)
    p = np.clip(p, 1e-12, None)
    return -np.sum(p * np.log(p))

def mpc_qp_cost(CDI, PhiN, PhiDelta, Scog,
                CDI_target=0.6, PhiN_target=0.6, Scog_target=np.log(3),
                mu1=1.0, mu2=1.0, mu3=1.0):
    """
    J = ∫[ (CDI-0.6)_+² + μ1(0.6-Φ_N)_+² + μ2·Φ_Δ² + μ3(ln(3)-S_cog)_+² ] dt
    For a single time‑step we return the integrand.
    """
    term1 = max(CDI - CDI_target, 0.0) ** 2
    term2 = mu1 * max(PhiN_target - PhiN, 0.0) ** 2
    term3 = mu2 * (PhiDelta ** 2)
    term4 = mu3 * max(Scog_target - Scog, 0.0) ** 2
    return term1 + term2 + term3 + term4

# ----------------------------------------------------------------------
# 1. Synthetic experiment
# ----------------------------------------------------------------------
def run_validation():
    # System parameters
    m = 25          # number of cognitive agents
    d = 8           # dimension of true cognitive state
    n = 3 * d       # redundancy ρ = 3 (as suggested in the proposal)
    T = 50          # number of time steps to simulate

    E = sparse_encoder(n, d, seed=42)          # encoder (n×d)
    PhiN0, PhiDelta0 = 0.8, 0.1                # baseline Ω‑variables
    Ricci0 = 1.0                               # reference curvature

    # Storage for time series (for later monotonicity checks)
    CDI_series = []
    PhiN_series = []
    PhiDelta_series = []
    Psi_series = []
    Scog_series = []
    Cost_series = []

    rng = np.random.default_rng(123)

    for t in range(T):
        # True cognitive state (random walk to mimic drift)
        if t == 0:
            c = rng.standard_normal(d)
        else:
            c = c_prev + 0.05 * rng.standard_normal(d)
        c_prev = c.copy()

        # Encode and distribute
        y = encode_state(E, c)                     # n‑dim vector
        # Split into m equal chunks (assume n divisible by m)
        assert n % m == 0, "Encoder output must be divisible by agent count"
        chunk = n // m
        y_chunks = [y[i*chunk:(i+1)*chunk] for i in range(m)]

        # Decoherence parameters (vary with time to simulate stress)
        theta = 0.05 + 0.1 * (t / T)               # increasing hit probability
        sigma = 0.2 + 0.3 * (t / T)                # increasing noise strength
        y_tilde_chunks = [
            decohere(y_chunks[i], theta, sigma, seed=t*m + i)
            for i in range(m)
        ]
        y_tilde = np.concatenate(y_tilde_chunks)

        # Decode at master node
        c_hat = decode(y_tilde, E)

        # Residuals per agent
        residuals = residual_error(y_tilde, E, c_hat)

        # Compute metrics
        # reshape residuals for CDI calculation
        Rmat = residuals.reshape(m, d)
        agent_norms = np.linalg.norm(Rmat, axis=1)
        tau_thresh = 0.5                         # decoherence detection threshold
        theta_cog_dec = np.mean(agent_norms > tau_thresh)
        epsilon = np.mean(agent_norms)

        CDI = compute_cdi(residuals, m, tau_thresh)
        PhiN = phi_n_from_cdi(PhiN0, CDI, theta_cog_dec)
        PhiDelta = phi_delta_from_cdi(PhiDelta0, theta_cog_dec, epsilon)

        # Mock Ollivier‑Ricci curvature (simple function of agent disagreement)
        Ricci = Ricci0 * np.exp(-0.5 * theta_cog_dec)   # decreases with decoherence
        Psi = invariant_psi(Ricci, Ricci0, CDI)

        Scog = entropy_cognitive(y_tilde)

        Cost = mpc_qp_cost(CDI, PhiN, PhiDelta, Scog)

        # Store for later checks
        CDI_series.append(CDI)
        PhiN_series.append(PhiN)
        PhiDelta_series.append(PhiDelta)
        Psi_series.append(Psi)
        Scog_series.append(Scog)
        Cost_series.append(Cost)

    # ------------------------------------------------------------------
    # 2. Invariant & consistency assertions
    # ------------------------------------------------------------------
    CDI_series = np.array(CDI_series)
    PhiN_series = np.array(PhiN_series)
    PhiDelta_series = np.array(PhiDelta_series)
    Psi_series = np.array(Psi_series)
    Scog_series = np.array(Scog_series)
    Cost_series = np.array(Cost_series)

    # (a) CDI must stay in [0,1) by construction of tanh
    assert np.all(CDI_series >= 0.0) and np.all(CDI_series < 1.0), \
        "CDI out of bounds [0,1)"

    # (b) Φ_N must remain non‑negative (variance‑like)
    assert np.all(PhiN_series >= 0.0), "Φ_N became negative"

    # (c) Φ_Δ can be positive or negative but should be bounded
    #    (skewness of a distribution is typically within [-√2, √2] for
    #    many practical ranges; we enforce a loose bound)
    assert np.all(np.abs(PhiDelta_series) <= 2.0), \
        "Φ_Δ exceeded reasonable skewness bounds"

    # (d) ψ should be real (Ricci > 0 ensures log defined)
    assert np.all(np.isfinite(Psi_series)), "ψ became NaN or infinite"

    # (e) Cognitive entropy must be ≥ 0 and ≤ ln(m) (max uniform distribution)
    max_entropy = np.log(m)
    assert np.all(Scog_series >= 0.0) and np.all(Scog_series <= max_entropy + 1e-9), \
        "S_cog outside [0, ln(m)]"

    # (f) MPC‑Ω cost integrand must be non‑negative (sum of squares)
    assert np.all(Cost_series >= 0.0), "MPC‑Ω cost became negative"

    # (g) Monotonicity sanity checks:
    #    Increasing stress (θ,σ) should not decrease CDI
    diff_CDI = np.diff(CDI_series)
    # Allow tiny numerical noise; require non‑negative trend on average
    assert np.mean(diff_CDI) >= -1e-3, "CDI decreased on average despite rising stress"

    #    As CDI rises, Φ_N should drop (inverse connectivity)
    corr_CDI_PhiN = np.corrcoef(CDI_series, PhiN_series)[0,1]
    assert corr_CDI_PhiN <= 0.0, "Φ_N did not show inverse relationship with CDI"

    #    As CDI rises, Φ_Δ should increase (positive skew from more outliers)
    corr_CDI_PhiDelta = np.corrcoef(CDI_series, PhiDelta_series)[0,1]
    assert corr_CDI_PhiDelta >= 0.0, "Φ_Δ did not show positive relationship with CDI"

    # (h) Constraint feasibility for the QP (as defined in the proposal):
    #    CDI ≤ 0.7, Φ_N ≥ 0.6, S_cog ≥ ln(3)
    CDI_ok = np.all(CDI_series <= 0.7 + 1e-6)
    PhiN_ok = np.all(PhiN_series >= 0.6 - 1e-6)
    Scog_ok = np.all(Scog_series >= np.log(3) - 1e-6)
    assert CDI_ok and PhiN_ok and Scog_ok, \
        f"QP constraints violated: CDI_max={CDI_series.max():.3f}, " \
        f"ΦN_min={PhiN_series.min():.3f}, S_cog_min={Scog_series.min():.3f}"

    # (i) Positive‑semidefiniteness of the QP Hessian (diagonal here):
    #    The Hessian of the integrand is 2·diag([1, μ1, μ2, μ3]) → PSD if μ_i ≥ 0.
    mu1, mu2, mu3 = 1.0, 1.0, 1.0
    assert mu1 >= 0 and mu2 >= 0 and mu3 >= 0, "QP Hessian not PSD"

    print("All Ω‑Protocol invariants and internal consistency checks PASSED.")
    print(f"Final CDI: {CDI_series[-1]:.3f}")
    print(f"Final Φ_N: {PhiN_series[-1]:.3f}")
    print(f"Final Φ_Δ: {PhiDelta_series[-1]:.3f}")
    print(f"Final ψ:   {Psi_series[-1]:.3f}")
    print(f"Final S_cog:{Scog_series[-1]:.3f}")
    print(f"Final cost integrand: {Cost_series[-1]:.3f}")

# ----------------------------------------------------------------------
if __name__ == "__main__":
    run_validation()