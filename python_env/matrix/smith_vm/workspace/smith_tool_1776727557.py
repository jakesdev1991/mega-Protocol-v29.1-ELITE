# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for Leak Pressure Monitoring (LPM-Ω)

Checks:
  - Φ_N ∈ [0, 1] and Φ_N ≥ Φ_N_min (default 0.7)
  - Φ_Δ ∈ [0, 1]
  - LPI is finite (no division by zero)
  - Anomaly score a ≥ 0
  - Lead time τ > 0
  - MPC-Ω QP feasibility: LPI ≤ LPI_max and Φ_N ≥ Φ_N_min simultaneously
"""

import numpy as np

# Optional: use cvxpy for QP feasibility check; fallback to simple linear check
try:
    import cvxpy as cp
    HAS_CVXPY = True
except Exception:  # pragma: no cover
    HAS_CVXPY = False

def safe_zscore(x, eps=1e-12):
    """Return z-score; if std == 0, return zeros to avoid division by zero."""
    mu = np.mean(x)
    sigma = np.std(x)
    if sigma < eps:
        return np.zeros_like(x)
    return (x - mu) / sigma

def compute_lpi(leak_counts, sentiments, risk_props,
                alpha=0.4, beta=0.4, gamma=0.2):
    """
    LPI(t) = alpha * Z_N(t) + beta * Z_s(t) + gamma * rho_risk(t)
    Inputs are 1‑D arrays (time series). Returns LPI time series.
    """
    Z_N = safe_zscore(leak_counts)
    Z_s = safe_zscore(sentiments)          # sentiment already negative‑biased
    # risk proportion already in [0,1]; no need to z‑score per spec
    rho = np.clip(risk_props, 0.0, 1.0)
    LPI = alpha * Z_N + beta * Z_s + gamma * rho
    return LPI

def map_to_phi(LPI, tau_N, tau_Delta,
               Phi_N0=0.85, Phi_Delta0=0.15,
               kappa_N=0.3, kappa_Delta=0.25, theta=0.5):
    """
    Φ_N(t) = Φ_N0 - kappa_N * max(0, LPI(t - tau_N) - theta)
    Φ_Δ(t) = Φ_Delta0 + kappa_Delta * sigmoid(LPI(t - tau_Delta))
    """
    # Shift LPI for lead times (assume tau >=0, pad with first value)
    def lag(x, lag_steps):
        if lag_steps <= 0:
            return x
        return np.concatenate([np.full(lag_steps, x[0]), x[:-lag_steps]])

    LPI_N = lag(LPI, int(np.round(tau_N)))
    LPI_D = lag(LPI, int(np.round(tau_Delta)))

    Phi_N = Phi_N0 - kappa_N * np.maximum(0.0, LPI_N - theta)
    # sigmoid
    Phi_Delta = Phi_Delta0 + kappa_Delta * (1.0 / (1.0 + np.exp(-LPI_D)))
    return Phi_N, Phi_Delta

def anomaly_score(LPI):
    """Simple STL‑like residual: detrended by subtracting moving average."""
    window = max(3, len(LPI)//5)  # crude trend estimate
    trend = np.convolve(LPI, np.ones(window)/window, mode='same')
    residual = LPI - trend
    sigma_res = np.std(residual) + 1e-12
    a = np.abs(residual) / sigma_res
    return a

def check_invariants(leak_counts, sentiments, risk_props,
                     tau_N=6.0, tau_Delta=6.0,
                     LPI_max=2.0, Phi_N_min=0.7):
    """Run all Omega Protocol checks; raise AssertionError on violation."""
    LPI = compute_lpi(leak_counts, sentiments, risk_props)
    assert np.all(np.isfinite(LPI)), "LPI contains NaN or Inf"

    Phi_N, Phi_Delta = map_to_phi(LPI, tau_N, tau_Delta)

    # Invariant 1: Φ_N bounds and minimum
    assert np.all(Phi_N >= 0.0) and np.all(Phi_N <= 1.0), \
        f"Φ_N out of [0,1]: min={Phi_N.min():.3f}, max={Phi_N.max():.3f}"
    assert np.all(Phi_N >= Phi_N_min), \
        f"Φ_N below minimum {Phi_N_min}: {Phi_N.min():.3f}"

    # Invariant 2: Φ_Δ bounds
    assert np.all(Phi_Delta >= 0.0) and np.all(Phi_Delta <= 1.0), \
        f"Φ_Δ out of [0,1]: min={Phi_Delta.min():.3f}, max={Phi_Delta.max():.3f}"

    # Invariant 3: Anomaly score non‑negative
    a = anomaly_score(LPI)
    assert np.all(a >= 0.0), "Anomaly score negative"

    # Invariant 4: Lead times positive
    assert tau_N > 0 and tau_Delta > 0, "Lead time tau must be >0"

    # Invariant 5: MPC‑Ω feasibility (simple linear check)
    # We need at least one time step where LPI <= LPI_max AND Φ_N >= Phi_N_min
    feasible = np.any((LPI <= LPI_max) & (Phi_N >= Phi_N_min))
    assert feasible, \
        "No feasible point for MPC‑Ω QP: LPI_max and Φ_N_min constraints conflict"

    # Optional: QP feasibility with cvxpy (if installed)
    if HAS_CVXPY:
        # Define a dummy decision variable u (scalar) that can shift LPI downwards
        u = cp.Variable()
        LPI_adj = LPI - u  # control can reduce LPI
        cost = cp.sum_squares(u)  # minimize control effort
        constraints = [LPI_adj <= LPI_max,
                       Phi_N0 - kappa_N * np.maximum(0.0, (LPI - u) - theta) >= Phi_N_min,
                       u >= 0]  # only reductions
        prob = cp.Problem(cp.Minimize(cost), constraints)
        try:
            prob.solve(solver=cp.OSQP, warm_start=True)
            assert prob.status in ("optimal", "optimal_inaccurate"), \
                f"QP infeasible: status {prob.status}"
        except Exception as e:  # pragma: no cover
            raise AssertionError(f"QP solver error: {e}")

    return {
        "LPI": LPI,
        "Phi_N": Phi_N,
        "Phi_Delta": Phi_Delta,
        "anomaly": a
    }

# ----------------------------------------------------------------------
# Synthetic test: generate plausible data and run the validator
if __name__ == "__main__":
    np.random.seed(42)
    T = 50  # days
    leak_counts = np.random.poisson(lam=2.0, size=T)          # occasional leaks
    sentiments = np.random.normal(loc=-0.3, scale=0.2, size=T) # bias negative
    risk_props = np.clip(np.random.beta(2,5, size=T), 0, 1)   # mostly low risk

    try:
        result = check_invariants(leak_counts, sentiments, risk_props,
                                 tau_N=6.0, tau_Delta=6.0,
                                 LPI_max=2.0, Phi_N_min=0.7)
        print("✅ All Omega Protocol invariants satisfied.")
        print(f"Final LPI mean: {result['LPI'].mean():.3f}")
        print(f"Final Φ_N mean: {result['Phi_N'].mean():.3f}")
        print(f"Final Φ_Δ mean: {result['Phi_Delta'].mean():.3f}")
    except AssertionError as err:
        print("❌ Invariant violation detected:")
        print(err)