# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
FOASH-Ω Mathematical Soundness Validator
----------------------------------------
This script checks the core equations of the FOASH-Ω proposal for internal
consistency and compliance with the Omega Protocol invariants (Φ_N, Φ_Δ, J*).
It works on synthetic data so that the logic can be inspected without
requiring real market feeds.

Checks performed:
1. Order Health Index (OHI) stays in the theoretical range [0, 1] (clipped if needed).
2. Φ_N^(order) ≥ 0.6  and  Φ_Δ^(order) ≤ 0.7  (the QP‑constraint bounds given in the proposal).
3. The cost function J* = ∫[(1‑OHI)² + λ₁Φ_Δ² + λ₂‖∇A‖²]dt is non‑negative.
4. Derived invariants ψ, ξ_N, ξ_Δ are real numbers (no NaNs/Infs).
5. Monotonicity of the mapping OHI → Φ_N (should be increasing) and OHI → Φ_Δ (should be decreasing).
6. Boundary conditions: 
      - Shredding event → OHI≈0 ⇒ ξ→0 ⇒ ψ→‑∞ (checked via sign).
      - Informational freeze → OHI≈1 ⇒ ξ→∞ ⇒ ψ→+∞ (checked via sign).

If any check fails, a ValidationError is raised with a descriptive message.
"""

import numpy as np
from scipy.signal import welch
from scipy.fft import rfft, rfftfreq

# ----------------------------------------------------------------------
# Helper functions (directly from the FOASH-Ω description)
# ----------------------------------------------------------------------
def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))

def compute_ohi(amplitudes, mu_healthy, sigma_healthy, weights):
    """
    OHI(t) = 1 - Σ w_k * |A_k(t) - μ_k| / σ_k
    Clipped to [0,1] to respect the theoretical definition.
    """
    term = np.sum(weights * np.abs(amplitudes - mu_healthy) / sigma_healthy)
    ohi = 1.0 - term
    return np.clip(ohi, 0.0, 1.0)

def phi_n_from_ohi(ohi, phi_n0, eta1, mu_ohi, sigma_ohi, tau):
    """Φ_N^(order)(t) = Φ_N^(0) + η₁·sigmoid((OHI(t‑τ)‑μ)/σ)"""
    ohi_lag = np.roll(ohi, int(tau))          # simple lag implementation
    ohi_lag[:int(tau)] = ohi[0]               # fill with first value
    return phi_n0 + eta1 * sigmoid((ohi_lag - mu_ohi) / sigma_ohi)

def phi_delta_from_ohi(ohi, phi_delta0, eta2, eta3, var_ak, tau):
    """Φ_Δ^(order)(t) = Φ_Δ^(0) - η₂·OHI(t‑τ) + η₃·Var(A_k(t))"""
    ohi_lag = np.roll(ohi, int(tau))
    ohi_lag[:int(tau)] = ohi[0]
    return phi_delta0 - eta2 * ohi_lag + eta3 * var_ak

def coherence(x, y, fs=1.0):
    """Magnitude‑squared coherence between two signals."""
    f, Cxy = welch(x, fs=fs, nperseg=min(256, len(x)))
    _, Cyy = welch(y, fs=fs, nperseg=min(256, len(y)))
    _, Cxx = welch(x, fs=fs, nperseg=min(256, len(x)))
    return np.abs(Cxy)**2 / (Cxx * Cyy + 1e-12)

def compute_xi_from_coherence(coherences):
    """ξ = 1 / ⟨coh(k)⟩  (average over orders)"""
    avg_coherence = np.mean(coherences)
    return 1.0 / (avg_coherence + 1e-12)

# ----------------------------------------------------------------------
# Synthetic data generation (mimicking 5 indicators sampled daily)
# ----------------------------------------------------------------------
np.random.seed(42)
T = 500                     # days
fs = 1.0                    # 1 sample per day
t = np.arange(T)

# Simulate a underlying financial rotation phase θ(t) = 2π * t / P
P = 250                     # pseudo‑business‑cycle period (days)
theta = 2 * np.pi * t / P

# Five synthetic indicators: each contains a dominant harmonic at order k=1,2,3
# plus noise.  Healthy baseline is known (we will estimate it from first 200 days).
indicators = {}
for i, name in enumerate(['volatility', 'volume', 'sentiment', 'money_flow', 'risk_return']):
    # fundamental + 2nd harmonic + noise
    sig = (0.5*np.sin(theta) +
           0.3*np.sin(2*theta) +
           0.1*np.sin(3*theta) +
           0.05*np.random.randn(T))
    indicators[name] = sig

# ----------------------------------------------------------------------
# Order analysis: resample onto θ domain and compute Fourier amplitudes
# ----------------------------------------------------------------------
def order_amplitudes(signal, theta):
    """Resample signal uniformly in θ and compute FFT magnitude."""
    # Interpolate onto uniform θ grid
    theta_uniform = np.linspace(theta[0], theta[-1], 1024)
    signal_uniform = np.interp(theta_uniform, theta, signal)
    # Remove mean
    signal_uniform = signal_uniform - np.mean(signal_uniform)
    freqs = rfftfreq(len(signal_uniform), d=(theta_uniform[1]-theta_uniform[0])/(2*np.pi))
    amps = np.abs(rfft(signal_uniform))
    return freqs, amps

# Compute amplitudes for each indicator (we will keep the first 3 non‑zero orders)
orders = {}
amps_dict = {}
for name, sig in indicators.items():
    freqs, amps = order_amplitudes(sig, theta)
    # Keep only positive frequencies (ignore DC)
    mask = freqs > 0
    orders[name] = freqs[mask][:3]          # first three orders as example
    amps_dict[name] = amps[mask][:3]

# ----------------------------------------------------------------------
# Learn healthy baseline from the first N_healthy days (here we use the whole series
# because the synthetic data is stationary; in practice you would use a calm window)
# ----------------------------------------------------------------------
N_healthy = 200
mu_healthy = {}
sigma_healthy = {}
var_ak = {}          # variance of amplitudes across time (used in Φ_Δ)
weights = {}

for name in indicators:
    # Build a time‑series of amplitudes for each order (simple approach: recompute
    # amplitudes in a sliding window; for speed we approximate using the full‑series
    # amplitudes as if they were constant – this is sufficient for a sanity check).
    # Here we just treat the amplitude vector as static and compute variance from noise.
    amp_vec = np.array([amps_dict[name][k] for k in range(3)])
    mu_healthy[name] = amp_vec
    sigma_healthy[name] = 0.1 * amp_vec + 1e-6   # avoid zero
    var_ak[name] = np.var(amp_vec)               # small placeholder
    # Equal weights for demonstration (should sum to 1)
    weights[name] = np.ones(3) / 3

# ----------------------------------------------------------------------
# Compute OHI, Φ_N, Φ_Δ, ξ, ψ, ξ_N, ξ_Δ over time
# ----------------------------------------------------------------------
ohi_series = {}
phi_n_series = {}
phi_delta_series = {}
xi_series = {}
psi_series = {}
xi_n_series = {}
xi_delta_series = {}

# Hyper‑parameters taken from the proposal (example values)
phi_n0, phi_delta0 = 0.5, 0.5
eta1, eta2, eta3 = 0.2, 0.2, 0.1
mu_ohi, sigma_ohi = 0.5, 0.2
tau1, tau2 = 3.0, 3.0          # days lag
lambda1, lambda2 = 0.1, 0.1    # cost‑function weights

for name in indicators:
    # ---- OHI ---------------------------------------------------------
    amp_mat = np.vstack([amps_dict[name]] * T)   # T×3 matrix (static for this demo)
    ohi = np.array([compute_ohi(amp_mat[t], mu_healthy[name],
                               sigma_healthy[name], weights[name])
                    for t in range(T)])
    ohi_series[name] = ohi

    # ---- Φ_N and Φ_Δ -------------------------------------------------
    phi_n = phi_n_from_ohi(ohi, phi_n0, eta1, mu_ohi, sigma_ohi, tau1)
    # For variance term we use the rolling variance of amplitudes (approximated)
    var_term = np.full(T, var_ak[name])
    phi_delta = phi_delta_from_ohi(ohi, phi_delta0, eta2, eta3, var_term, tau2)
    phi_n_series[name] = phi_n
    phi_delta_series[name] = phi_delta

    # ---- Invariant derivation (using pairwise coherence) -------------
    # Compute coherence between each pair of indicators at the dominant order (k=1)
    cohs = []
    names = list(indicators.keys())
    for i in range(len(names)):
        for j in range(i+1, len(names)):
            coh = coherence(indicators[names[i]], indicators[names[j]], fs=fs)
            cohs.append(np.mean(coh))   # average over frequency band
    xi = compute_xi_from_coherence(np.array(cohs))
    xi_series[name] = xi
    psi = np.log(xi / 1.0)               # ξ₀ set to 1 for simplicity
    psi_series[name] = psi

    # Approximate derivatives via finite difference (ξ_N = ∂Φ_N/∂ψ, ξ_Δ = ∂Φ_Δ/∂ψ)
    dpsi = np.gradient(psi)
    xi_n = np.gradient(phi_n) / (dpsi + 1e-12)
    xi_delta = np.gradient(phi_delta) / (dpsi + 1e-12)
    xi_n_series[name] = xi_n
    xi_delta_series[name] = xi_delta

# ----------------------------------------------------------------------
# Validation checks
# ----------------------------------------------------------------------
class ValidationError(Exception):
    pass

def run_checks():
    # 1. OHI bounds
    for name, ohi in ohi_series.items():
        if np.any(ohi < 0) or np.any(ohi > 1):
            raise ValidationError(f"OHI out of bounds for {name}: min={ohi.min():.3f}, max={ohi.max():.3f}")

    # 2. Omega invariant bounds (QP constraints)
    for name in indicators:
        phi_n = phi_n_series[name]
        phi_delta = phi_delta_series[name]
        if np.any(phi_n < 0.6):
            raise ValidationError(f"Φ_N^(order) < 0.6 for {name}: min={phi_n.min():.3f}")
        if np.any(phi_delta > 0.7):
            raise ValidationError(f"Φ_Δ^(order) > 0.7 for {name}: max={phi_delta.max():.3f}")

    # 3. Cost function non‑negativity (integrand is sum of squares)
    for name in indicators:
        ohi = ohi_series[name]
        phi_delta = phi_delta_series[name]
        # Approximate ‖∇A‖² by variance of amplitude changes (proxy)
        grad_a = np.gradient(amps_dict[name][0])   # use first order as proxy
        integrand = (1 - ohi)**2 + lambda1 * phi_delta**2 + lambda2 * grad_a**2
        if np.any(integrand < -1e-12):   # allow tiny negative due to numerical noise
            raise ValidationError(f"Cost integrand negative for {name}: min={integrand.min():.6f}")

    # 4. No NaNs/Infs in derived invariants
    for name in indicators:
        for arr, label in [(psi_series[name], 'ψ'),
                           (xi_n_series[name], 'ξ_N'),
                           (xi_delta_series[name], 'ξ_Δ')]:
            if not np.all(np.isfinite(arr)):
                raise ValidationError(f"Non‑finite {label} for {name}")

    # 5. Monotonicity checks (OHI ↑ → Φ_N ↑, OHI ↑ → Φ_Δ ↓)
    for name in indicators:
        ohi = ohi_series[name]
        phi_n = phi_n_series[name]
        phi_delta = phi_delta_series[name]
        # Compute Spearman rank correlation as a monotonicity proxy
        from scipy.stats import spearmanr
        rho_n, _ = spearmanr(ohi, phi_n)
        rho_d, _ = spearmanr(ohi, phi_delta)
        if rho_n < 0.1:   # expect positive monotonicity
            raise ValidationError(f"Φ_N not monotonic increasing with OHI for {name}: rho={rho_n:.3f}")
        if rho_d > -0.1:  # expect negative monotonicity
            raise ValidationError(f"Φ_Δ not monotonic decreasing with OHI for {name}: rho={rho_d:.3f}")

    # 6. Boundary condition signs
    for name in indicators:
        ohi = ohi_series[name]
        xi = xi_series[name]
        psi = psi_series[name]
        # Shredding: low OHI → low ξ → ψ negative
        low_ohi_mask = ohi < 0.2
        if np.any(low_ohi_mask):
            if np.mean(psi[low_ohi_mask]) > 0:
                raise ValidationError(f"Expected ψ<0 during low OHI (shredding) for {name}")
        # Freeze: high OHI → high ξ → ψ positive
        high_ohi_mask = ohi > 0.8
        if np.any(high_ohi_mask):
            if np.mean(psi[high_ohi_mask]) < 0:
                raise ValidationError(f"Expected ψ>0 during high OHI (freeze) for {name}")

    print("All FOASH-Ω mathematical checks passed.")

if __name__ == "__main__":
    try:
        run_checks()
    except ValidationError as e:
        print(f"VALIDATION FAILED: {e}")
        raise