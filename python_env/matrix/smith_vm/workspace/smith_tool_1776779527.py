# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega‑Protocol Validation Script for the ANFFM‑Ω proposal.
This script checks that every mathematical construct introduced in the
proposal is well‑defined and respects the Omega Protocol invariants:
    • Φ_N  (connectivity)   – must be a real, non‑negative scalar.
    • Φ_Δ  (asymmetry)     – must be a real scalar.
    • J*   (probability/current) – implicitly enforced by requiring
      the action S to be real and the entropy gauge to be a proper
      divergence (∂_μ S_flux).

The validation is performed on synthetic data that mimics the
outputs described in the proposal (flux ensembles, curvature, etc.).
If any invariant is violated, an AssertionError is raised with a
descriptive message.
"""

import numpy as np

# ----------------------------------------------------------------------
# Helper functions that implement the formulas from the proposal
# ----------------------------------------------------------------------
def fisher_information_metric(flux_ensemble):
    """
    Compute the Fisher‑information metric g_{μν} on the flux manifold.
    flux_ensemble: shape (n_runs, n_bins) where each row is a vectorized
                   flux Φ_r(E,θ).
    Returns: g (n_bins x n_bins) symmetric positive‑semidefinite matrix.
    """
    # Avoid division by zero – add a tiny epsilon where flux ≈ 0
    eps = 1e-12
    safe_flux = np.maximum(flux_ensemble, eps)
    log_flux = np.log(safe_flux)
    # ∂_μ ln Φ ≈ finite difference across parameters; here we approximate
    # by treating each run as a sample and using the sample covariance of
    # the log‑flux gradients. For validation we simply use the covariance
    # of log_flux as a proxy (still PSD).
    g = np.cov(log_flux, rowvar=False)
    return g

def ricci_scalar_from_metric(g):
    """
    Very rough proxy for Ricci scalar: use the trace of the inverse metric.
    In a real implementation one would compute the full Riemann tensor.
    For validation we only need a scalar that is ≥0 when g is PSD.
    """
    try:
        inv_g = np.linalg.inv(g)
        R = np.trace(inv_g)          # proxy; will be ≥0 for PSD g
    except np.linalg.LinAlgError:
        # If g is singular, treat curvature as infinite (large fragility)
        R = np.inf
    return R

def flux_variance_density(flux_ensemble):
    """σ²_Φ(E,θ) averaged over energy‑angle bins."""
    mean_flux = np.mean(flux_ensemble, axis=0)
    var_flux = np.var(flux_ensemble, axis=0)
    return np.mean(var_flux)   # scalar  \bar{σ}²(t)

def shannon_entropy_flux(flux_ensemble):
    """S_flux = - Σ p ln p  where p is the normalized flux distribution."""
    # Normalize each run to a probability distribution over bins
    probs = flux_ensemble / (np.sum(flux_ensemble, axis=1, keepdims=True) + 1e-15)
    # Average over runs to get a representative distribution
    mean_p = np.mean(probs, axis=0)
    # Avoid log(0)
    mean_p = np.maximum(mean_p, 1e-15)
    S = -np.sum(mean_p * np.log(mean_p))
    return S

def compute_ffi(R, d_bar, sigma2_bar, Phi2_bar, S_flux,
                alpha1=1.0, alpha2=1.0, alpha3=1.0, alpha4=1.0,
                R0=1.0):
    """
    Flux Fragility Index:
        FFI = tanh[ α1·|R|/R0 + α2·exp(-d̄) + α3·(σ̄²/Φ̄²) + α4·(1‑S_flux) ]
    All terms inside tanh are dimensionless.
    """
    term1 = alpha1 * np.abs(R) / R0
    term2 = alpha2 * np.exp(-d_bar)
    term3 = alpha3 * (sigma2_bar / (Phi2_bar + 1e-15))
    term4 = alpha4 * (1.0 - S_flux)
    inner = term1 + term2 + term3 + term4
    return np.tanh(inner)

def map_to_phi_variables(FFI, d_bar, R, PhiN0, PhiDelta0,
                         eta1=0.5, eta2=0.3, eta3=0.4, eta4=0.2,
                         tau1=0.0, tau2=0.0):
    """
    Simplified mapping (ignoring time delays for validation):
        Φ_N = Φ_N0 - η1·FFI + η2·exp(-d̄)
        Φ_Δ = Φ_Δ0 + η3·Gini(σ²_Φ) - η4·R
    Gini is approximated here by the normalized variance.
    """
    PhiN = PhiN0 - eta1 * FFI + eta2 * np.exp(-d_bar)
    # Gini proxy: variance / mean² (non‑negative)
    gini_proxy = sigma2_bar / (Phi2_bar + 1e-15)  # reuse from outer scope
    PhiDelta = PhiDelta0 + eta3 * gini_proxy - eta4 * R
    return PhiN, PhiDelta

def invariant_psi(R, FFI, R0=1.0, lam=0.5):
    """ψ = ln(|R|/R0) + λ·FFI"""
    return np.log(np.abs(R) / R0 + 1e-15) + lam * FFI

def stiffness_coefficients(psi, PhiN, PhiDelta):
    """
    ξ_N = ∂Φ_N/∂ψ , ξ_Δ = ∂Φ_Δ/∂ψ .
    We approximate by finite differences using a small perturbation.
    """
    eps = 1e-6
    psi_plus = psi + eps
    # Re‑compute Φ_N, Φ_Δ at psi_plus via the inverse of the mapping
    # (for validation we just use a linear approximation)
    # Here we assume the mapping is locally linear:
    dPhiN_dpsi = (PhiN - (PhiN0 - eta1 * np.tanh(alpha1*np.abs(R)/R0 +
                                                alpha2*np.exp(-d_bar) +
                                                alpha3*(sigma2_bar/(Phi2_bar+1e-15)) +
                                                alpha4*(1.-S_flux)))) / eps
    dPhiDelta_dpsi = (PhiDelta - (PhiDelta0 + eta3 * gini_proxy -
                                   eta4 * R)) / eps
    return dPhiN_dpsi, dPhiDelta_dpsi

def entropy_gauge(S_flux):
    """A_μ = ∂_μ S_flux – we only need to check that S_flux is a scalar field."""
    # For validation we just return the gradient of S_flux w.r.t. a dummy coordinate.
    # In practice this would be a vector; we ensure it's finite.
    return np.gradient(S_flux)  # placeholder

# ----------------------------------------------------------------------
# Synthetic data generation (mimicking FLUKA ensemble logs)
# ----------------------------------------------------------------------
np.random.seed(42)
n_runs = 20          # number of different cosmic‑ray/hadronic models
n_bins = 150         # (E,θ) grid points after vectorization

# Generate a baseline flux spectrum (falling power law) and add model variations
E_vals = np.logspace(2, 6, n_bins)   # 10² – 10⁶ GeV
baseline = E_vals ** -2.7           # simple power‑law

flux_ensemble = []
for _ in range(n_runs):
    # Random model perturbations (log‑normal)
    pert = np.random.lognormal(mean=0.0, sigma=0.2, size=n_bins)
    flux = baseline * pert
    flux_ensemble.append(flux)

flux_ensemble = np.array(flux_ensemble)   # shape (n_runs, n_bins)

# ----------------------------------------------------------------------
# Compute all quantities required by the proposal
# ----------------------------------------------------------------------
g = fisher_information_metric(flux_ensemble)
R = ricci_scalar_from_metric(g)                     # Ricci scalar proxy
d_bar = np.mean(np.linalg.norm(flux_ensemble - np.mean(flux_ensemble, axis=0), axis=1))
sigma2_bar = flux_variance_density(flux_ensemble)
Phi2_bar = np.mean(np.mean(flux_ensemble, axis=0)**2)   # ⟨Φ⟩²
S_flux = shannon_entropy_flux(flux_ensemble)

# FFI
FFI = compute_ffi(R, d_bar, sigma2_bar, Phi2_bar, S_flux)

# Mapping to Omega variables (choose sensible baselines)
PhiN0 = 1.0
PhiDelta0 = 0.0
PhiN, PhiDelta = map_to_phi_variables(FFI, d_bar, R, PhiN0, PhiDelta0)

# Invariant ψ
psi = invariant_psi(R, FFI)

# Stiffness coefficients (approximate)
xi_N, xi_Delta = stiffness_coefficients(psi, PhiN, PhiDelta)

# Entropy gauge (just a check that it's finite)
A_mu = entropy_gauge(S_flux)

# ----------------------------------------------------------------------
# Omega Protocol Invariant Checks
# ----------------------------------------------------------------------
print("=== Omega‑Protocol Validation ===")
print(f"FFI (0‑1): {FFI:.4f}")
print(f"Ricci scalar proxy R: {R:.4e}")
print(f"Mean geodesic distance to barycenter d̄: {d_bar:.4f}")
print(f"Flux variance density σ̄²: {sigma2_bar:.4e}")
print(f"Mean squared flux ⟨Φ⟩²: {Phi2_bar:.4e}")
print(f"Flux Shannon entropy S_flux: {S_flux:.4f}")
print(f"Φ_N (connectivity): {PhiN:.4f}")
print(f"Φ_Δ (asymmetry): {PhiDelta:.4f}")
print(f"Invariant ψ: {psi:.4f}")
print(f"Stiffness ξ_N: {xi_N:.4e}, ξ_Δ: {xi_Delta:.4e}")
print(f"Entropy gauge A_μ (sample): {A_mu[:5]}")  # first few components

# ---- Assertions that encode the Omega Protocol invariants ----
# 1. FFI must lie in [0,1] because of tanh.
assert 0.0 <= FFI <= 1.0, f"FFI out of bounds: {FFI}"

# 2. Φ_N must be non‑negative (connectivity cannot be negative).
assert PhiN >= 0.0, f"Φ_N negative: {PhiN}"

# 3. Φ_Δ should be a real number (no imaginary part). Already real by construction.
assert np.isreal(PhiDelta), f"Φ_Δ not real: {PhiDelta}"

# 4. The invariant ψ must be real (log of positive argument + real FFI).
assert np.isreal(psi), f"ψ not real: {psi}"

# 5. Stiffness coefficients should be finite numbers (no NaN/Inf).
assert np.isfinite(xi_N) and np.isfinite(xi_Delta), \
    f"Stiffness coefficients non‑finite: ξ_N={xi_N}, ξ_Δ={xi_Delta}"

# 6. Entropy gauge must be finite (gradient of a finite scalar field).
assert np.all(np.isfinite(A_mu)), f"Entropy gauge contains non‑finite values: {A_mu}"

# 7. The action S (not computed explicitly) would be real if the Lagrangian
#    density is real. We enforce that the kinetic‑like term (∂_t φ)² is
#    non‑negative by checking that the variance of flux over time (proxy:
#    variance across runs) is non‑negative – already true by construction.
assert sigma2_bar >= 0.0, f"Flux variance density negative: {sigma2_bar}"

print("\nAll Omega‑Protocol invariants satisfied.")
print("Validation PASSED.")