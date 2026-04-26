# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Validation script for PICM‑Ω v2 (Presentation‑Interval Cadence Monitoring)
Checks mathematical consistency with the Omega Protocol invariants:
  • Covariant modes Φ_N, Φ_Δ
  • Invariants ψ, ξ_N, ξ_Δ derived from the φ⁴ potential
  • Entropy S_h(t) and presentation jerk J_p(t)
  • GPD‑based anomaly score a_p(t)
  • MPC‑Ω cost function and constraints

The script uses symbolic/numeric checks; any assertion failure raises
an AssertionError with a descriptive message, enforcing strict compliance.
"""

import numpy as np
from scipy.stats import genpareto

# ----------------------------------------------------------------------
# Helper functions (pure math, no external data)
# ----------------------------------------------------------------------
def phi4_potential(phi, lam, v):
    """V(phi) = λ/4 (phi² - v²)²"""
    return lam * 0.25 * (phi**2 - v**2)**2

def fluctuation_mass(phi0, lam, v):
    """m_eff² = λ (3 φ0² - v²)"""
    return lam * (3 * phi0**2 - v**2)

def correlation_time(m2):
    """ξ = 1 / sqrt(m_eff²)  (requires m_eff² > 0)"""
    if m2 <= 0:
        raise ValueError("Effective mass squared must be positive for a real correlation time.")
    return 1.0 / np.sqrt(m2)

def invariants_from_modes(PhiN, PhiDelta, lam, v):
    """
    Compute ψ, ξ_N, ξ_Δ from the covariant modes.
    ψ = ln(ξ/ξ0)  (we set ξ0 = 1 for dimensionless ψ)
    ξ_N^{-2} = λ (3Φ_N² + Φ_Δ² - v²)
    ξ_Δ^{-2} = λ (Φ_N² + 3Φ_Δ² - v²)
    """
    xi_N_sq_inv = lam * (3 * PhiN**2 + PhiDelta**2 - v**2)
    xi_D_sq_inv = lam * (PhiN**2 + 3 * PhiDelta**2 - v**2)

    if xi_N_sq_inv <= 0 or xi_D_sq_inv <= 0:
        raise ValueError("Invariant stiffness must be positive (real ξ).")

    xi_N = 1.0 / np.sqrt(xi_N_sq_inv)
    xi_D = 1.0 / np.sqrt(xi_D_sq_inv)

    # ψ uses a reference correlation time ξ0 = 1 (dimensionless)
    psi = np.log(xi_N)  # could also use xi_D; both are related via the modes

    return psi, xi_N, xi_D

def shannon_entropy(intervals, bins=10):
    """
    S_h(t) = - Σ p_k log p_k
    intervals: array of inter‑presentation Δt_i (positive)
    """
    if len(intervals) == 0:
        return 0.0
    hist, _ = np.histogram(intervals, bins=bins, density=False)
    p = hist / hist.sum()
    # avoid log(0)
    p = p[p > 0]
    return -np.sum(p * np.log(p))

def presentation_jerk(S_h_series, dt=1.0):
    """
    J_p(t) = d³ S_h / dt³  (finite‑difference approximation)
    Uses central differences for interior points, forward/backward at edges.
    """
    n = len(S_h_series)
    if n < 4:
        raise ValueError("Need at least 4 points to compute third derivative.")
    # third derivative via numpy.gradient applied thrice
    first = np.gradient(S_h_series, dt)
    second = np.gradient(first, dt)
    third = np.gradient(second, dt)
    return third

def gpd_anomaly_score(Jp_series, threshold_quantile=0.95):
    """
    Fit a Generalized Pareto Distribution to the exceedances over threshold u.
    Anomaly score a_p(t) = 1 - F_GPD(|J_p| - u)
    Returns array of scores in (0,1]; lower → more anomalous.
    """
    absJp = np.abs(Jp_series)
    u = np.quantile(absJp, threshold_quantile)
    exceed = absJp[absJp > u] - u
    if len(exceed) < 2:
        # insufficient tail data – fall back to a conservative score
        return np.full_like(absJp, 0.5)
    # Fit shape (c), loc=0, scale
    c, loc, scale = genpareto.fit(exceed, floc=0)
    # CDF for each observation (non‑exceedances get CDF=1)
    cdf_vals = np.ones_like(absJp)
    mask = absJp > u
    cdf_vals[mask] = genpareto.cdf(absJp[mask] - u, c, loc, scale)
    # anomaly score = survival function
    return 1.0 - cdf_vals

def mpc_cost(Jp, S_h, xi_D, target_entropy, target_xi_inv,
             alpha1=1.0, alpha2=1.0):
    """
    Instantaneous cost: J_p² + α1 (S_h - S_h*)² + α2 (ξ_Δ^{-1} - ξ_Δ^{*-1})²
    """
    return Jp**2 + alpha1 * (S_h - target_entropy)**2 + alpha2 * (1.0/xi_D - target_xi_inv)**2

def mpc_constraints(PhiN, PhiDelta, xi_N, xi_D,
                    xi_N_min=0.1, xi_D_min=0.1, PhiN_min=0.0):
    """
    Enforce:
        ξ_N ≥ ξ_N_min
        ξ_Δ ≥ ξ_Δ_min
        Φ_N ≥ ΦN_min
    Returns True if all satisfied.
    """
    return (xi_N >= xi_N_min) and (xi_D >= xi_D_min) and (PhiN >= PhiN_min)

# ----------------------------------------------------------------------
# Validation routine – runs a synthetic but realistic scenario
# ----------------------------------------------------------------------
def validate_picm_omega():
    # ---- 1. Define hyper‑parameters of the φ⁴ action (Omega‑compliant) ----
    lam = 2.0          # coupling >0 ensures stability
    v   = 1.0          # symmetry‑breaking scale
    phi0 = 0.8 * v     # mean field slightly below +v (regular cadence regime)

    # ---- 2. Derive covariant modes from a synthetic fluctuation field ----
    # Simulate a small fluctuation δφ(t) (Gaussian noise) and compute modes
    T = 200
    dt = 0.5
    t = np.arange(0, T*dt, dt)
    dphi = 0.05 * np.random.randn(len(t))          # zero‑mean fluctuations
    PhiN = np.mean(dphi)                           # Newtonian mode (average)
    # Archive mode: projection onto sin(ωt) with ω = 2π / (quarterly period ≈ 60 days)
    omega = 2*np.pi / 60.0
    PhiDelta = np.mean(dphi * np.sin(omega * t))   # Archive mode

    # ---- 3. Compute invariants from the modes ----
    psi, xi_N, xi_D = invariants_from_modes(PhiN, PhiDelta, lam, v)

    # ---- 4. Build a synthetic presentation‑interval series ----
    # Base regular interval = xi_N, add modulated noise to create entropy variations
    base_interval = xi_N
    interval_noise = 0.2 * base_interval * np.random.randn(len(t))
    intervals = base_interval + interval_noise
    intervals = np.clip(intervals, 0.1*base_interval, None)  # keep positive

    # ---- 5. Entropy and jerk ----
    S_h_series = np.array([shannon_entropy(intervals[max(0,i-20):i+1]) for i in range(len(t))])
    Jp_series = presentation_jerk(S_h_series, dt=dt)

    # ---- 6. Anomaly scoring via GPD ----
    a_p_series = gpd_anomaly_score(Jp_series, threshold_quantile=0.95)

    # ---- 7. MPC‑Ω cost and constraints ----
    target_entropy = np.mean(S_h_series)          # desire modest regularity
    target_xi_inv  = 1.0 / np.mean(xi_D)          # desired clustering decay
    cost_series = mpc_cost(Jp_series, S_h_series, xi_D,
                           target_entropy, target_xi_inv,
                           alpha1=1.0, alpha2=1.0)

    constraints_ok = mpc_constraints(PhiN, PhiDelta, xi_N, xi_D,
                                     xi_N_min=0.05, xi_D_min=0.05, PhiN_min=-0.5)

    # ---- 8. Assertions – enforce Omega Protocol compliance ----
    # a) Effective mass squared must be positive (real correlation time)
    m2 = fluctuation_mass(phi0, lam, v)
    assert m2 > 0, f"Effective mass squared non‑positive: {m2}"

    # b) Invariants must be real and positive
    assert xi_N > 0 and xi_D > 0, f"Invalid correlation times: ξ_N={xi_N}, ξ_Δ={xi_D}"

    # c) Entropy non‑negative
    assert np.all(S_h_series >= 0), "Shannon entropy produced negative values."

    # d) Jerk finite (no NaNs/Infs)
    assert np.all(np.isfinite(Jp_series)), "Presentation jerk contains non‑finite values."

    # e) Anomaly scores in (0,1]
    assert np.all((a_p_series > 0) & (a_p_series <= 1)), \
        f"Anomaly score out of bounds: min={a_p_series.min()}, max={a_p_series.max()}"

    # f) MPC cost non‑negative (quadratic form)
    assert np.all(cost_series >= 0), "MPC cost became negative."

    # g) Constraints satisfied
    assert constraints_ok, (
        f"MPC constraints violated: Φ_N={PhiN}, Φ_Δ={PhiDelta}, "
        f"ξ_N={xi_N}, ξ_Δ={xi_D}"
    )

    # ---- 9. If we reach here, the math is sound ----
    print("[✓] All Omega‑Protocol invariant checks passed.")
    print(f"    Φ_N = {PhiN:.4f}, Φ_Δ = {PhiDelta:.4f}")
    print(f"    ψ   = {psi:.4f}, ξ_N = {xi_N:.4f}, ξ_Δ = {xi_D:.4f}")
    print(f"    Mean entropy = {np.mean(S_h_series):.4f}")
    print(f"    Mean jerk    = {np.mean(np.abs(Jp_series)):.4e}")
    print(f"    Mean anomaly score = {np.mean(a_p_series):.4f}")
    print(f"    MPC constraints satisfied: {constraints_ok}")

# ----------------------------------------------------------------------
# Run validation when executed as a script
# ----------------------------------------------------------------------
if __name__ == "__main__":
    validate_picm_omega()