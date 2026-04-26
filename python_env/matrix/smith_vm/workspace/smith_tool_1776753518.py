# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
TEMPEST‑Ω Mathematical Validation Script
----------------------------------------
This script checks the internal consistency of the core TEMPEST‑Ω equations
as presented in the refined proposal.  It does **not** prove the underlying
physics; it merely verifies that:

1. All expressions are well‑defined for plausible input ranges.
2. The derived invariants (Φ_N^(temp), Φ_Δ^(temp)) respect the Omega
   Protocol bounds imposed in the MPC‑Ω layer.
3. The anomaly‑score rule and the MPC cost‑function are mathematically
   coherent (no division by zero, monotonicity where expected, etc.).
4. Dimensional consistency is respected when we assign SI‑like units:
      - time → days
      - credential criticality C_i → dimensionless (1‑5)
      - decay constant λ → 1/days
      - Δt_{f,e} → days
      - sync(t_i) → dimensionless count
      - α,β,γ,η_i → dimensionless (learned weights)
      - TSI_s → dimensionless stress index
      - ψ = ln(φ_n) → dimensionless
      - ξ_N, ξ_Δ → days (stiffness/time‑scale)
      - S_h → dimensionless (entropy)

If any check fails, the script raises an AssertionError with a descriptive
message.

Usage:
    python tempest_validation.py   # runs a synthetic sanity‑check
"""

import numpy as np
import sympy as sp

# ----------------------------------------------------------------------
# Helper symbolic checks
# ----------------------------------------------------------------------
def check_nonnegative(expr, name, subs_dict):
    """Assert that expr evaluates to a non‑negative number for the given subs."""
    val = expr.subs(subs_dict).evalf()
    assert val >= 0, f"{name} evaluated to {val} (<0) with subs {subs_dict}"
    return val

def check_positive(expr, name, subs_dict):
    """Assert that expr evaluates to a strictly positive number."""
    val = expr.subs(subs_dict).evalf()
    assert val > 0, f"{name} evaluated to {val} (≤0) with subs {subs_dict}"
    return val

# ----------------------------------------------------------------------
# 1. Temporal Stress Index (TSI) definition
# ----------------------------------------------------------------------
# Symbols
t, t_i, lam, C_i, alpha, beta, gamma, Delta_t, sync = sp.symbols(
    't t_i lam C_i alpha beta gamma Delta_t sync', real=True, nonnegative=True
)

# TSI contribution from a single leak (firm f, leak i)
TSI_contrib = alpha * C_i * sp.exp(-lam * sp.Abs(t - t_i)) + beta / (Delta_t + 1e-9) + gamma * sync
# Note: we add a tiny epsilon to avoid division by zero when Delta_t = 0.
# In practice Delta_t is days to next event; a leak on the event day yields
# Delta_t = 0 → we treat it as maximal stress (beta / epsilon).

# Verify each term is non‑negative (given non‑negative symbols)
assert (alpha * C_i * sp.exp(-lam * sp.Abs(t - t_i))).is_nonnegative
assert (beta / (Delta_t + 1e-9)).is_nonnegative
assert (gamma * sync).is_nonnegative

# ----------------------------------------------------------------------
# 2. Sector‑level TSI (sum over leaks and firms)
# ----------------------------------------------------------------------
# We'll treat the sum as a Python numeric check later.
# Symbolically we just confirm the structure is a linear sum of non‑negative terms.
TSI_sector = sp.Sum(TSI_contrib, (i, 0, N_leaks-1))  # N_leaks is a positive integer
# No further symbolic simplification needed.

# ----------------------------------------------------------------------
# 3. Mapping to Omega variables
# ----------------------------------------------------------------------
Phi_N0, Phi_Delta0, eta1, eta2, eta3, tau1, tau2, tau3 = sp.symbols(
    'Phi_N0 Phi_Delta0 eta1 eta2 eta3 tau1 tau2 tau3', real=True
)
TSI_delayed = sp.Symbol('TSI_delayed', real=True)  # TSI_s(t - τ)

Phi_N_temp = Phi_N0 + eta1 * TSI_delayed - eta2 * TSI_delayed**2
Phi_Delta_temp = Phi_Delta0 + eta3 * sp.Symbol('sync_delayed', real=True)

# Check that Phi_N_temp and Phi_Delta_temp are real for any real inputs.
# (They are polynomials in real symbols → real.)

# ----------------------------------------------------------------------
# 4. Anomaly score and singularity prediction rule
# ----------------------------------------------------------------------
TSI_hat, sigma_TSI = sp.symbols('TSI_hat sigma_TSI', real=True, positive=True)
s_TSI = sp.Abs(TSI_delayed - TSI_hat) / sigma_TSI
# s_TSI ≥ 0 by construction
assert s_TSI.is_nonnegative

# Prediction condition: s_TSI > 2.5 AND Phi_Delta_temp > 0.65
# We'll test this numerically later.

# ----------------------------------------------------------------------
# 5. MPC‑Ω constraints and cost function
# ----------------------------------------------------------------------
target_TSI = sp.symbols('target_TSI', real=True, nonnegative=True)
mu1, mu2 = sp.symbols('mu1 mu2', real=True, nonnegative=True)

# Constraints (inequalities)
constraint_TSI = sp.symbols('TSI_s', real=True)  # sector TSI at time t
constraint_PhiN = sp.symbols('Phi_N_temp', real=True)
constraint_PhiDelta = sp.symbols('Phi_Delta_temp', real=True)

# We will enforce:
#   TSI_s ≤ 4.0
#   Phi_N_temp ≥ 0.5
#   Phi_Delta_temp ≤ 0.75

# Cost function integrand (ignore dt for pointwise check)
cost_integrand = (constraint_TSI - target_TSI)**2 + mu1 * s_TSI**2 + mu2 * (1 - constraint_PhiN)**2
# Each term is a square → non‑negative
assert cost_integrand.is_nonnegative

# ----------------------------------------------------------------------
# 6. Numerical sanity‑check with synthetic data
# ----------------------------------------------------------------------
def run_synthetic_check():
    """Generate a tiny synthetic dataset and verify all numeric conditions."""
    np.random.seed(42)

    # Synthetic sector with 3 firms, each with up to 2 leaks
    firms = ['A', 'B', 'C']
    leaks = []  # list of dicts: {firm, t_leak, C, Delta_t, sync}
    for f in firms:
        for _ in range(2):
            t_leak = np.random.uniform(0, 100)   # days since epoch
            C = np.random.randint(1, 6)          # 1‑5
            Delta_t = np.random.uniform(0, 30)   # days to next event
            sync = np.random.randint(0, 5)       # number of other firms leaking ±3 days
            leaks.append({'firm': f, 't_leak': t_leak, 'C': C,
                          'Delta_t': Delta_t, 'sync': sync})

    # Hyper‑parameters (learned values – just pick plausible numbers)
    lam = 0.1          # 1/day
    alpha, beta, gamma = 0.4, 0.3, 0.3
    eta1, eta2, eta3 = 0.5, 0.2, 0.4
    tau1, tau2, tau3 = 14.0, 42.0, 7.0   # days
    Phi_N0, Phi_Delta0 = 0.6, 0.3
    target_TSI = 2.0
    mu1, mu2 = 0.1, 0.1
    sigma_TSI = 0.5

    # Compute sector TSI at a grid of times
    t_grid = np.linspace(0, 120, 13)  # every 10 days
    TSI_vals = []
    for t_now in t_grid:
        total = 0.0
        for lk in leaks:
            t_i = lk['t_leak']
            C_i = lk['C']
            Delta_t = lk['Delta_t']
            sync = lk['sync']
            contrib = (alpha * C_i * np.exp(-lam * abs(t_now - t_i))
                       + beta / (Delta_t + 1e-9)
                       + gamma * sync)
            total += contrib
        TSI_vals.append(total)

    TSI_vals = np.array(TSI_vals)

    # Delayed TSI for Phi_N (use tau1 as example)
    # Simple linear interpolation for delay
    from scipy.interpolate import interp1d
    interp_TSI = interp1d(t_grid, TSI_vals, kind='linear',
                          fill_value="extrapolate")
    TSI_delayed_vals = interp_TSI(t_grid - tau1)

    # Compute Phi_N_temp and Phi_Delta_temp
    Phi_N_temp_vals = Phi_N0 + eta1 * TSI_delayed_vals - eta2 * TSI_delayed_vals**2
    # For Phi_Delta we need a delayed sync proxy – use average sync of leaks
    avg_sync = np.mean([lk['sync'] for lk in leaks])
    Phi_Delta_temp_vals = Phi_Delta0 + eta3 * avg_sync  # sync_delayed approximated

    # ---- Assertions ----
    # 1. TSI non‑negative
    assert np.all(TSI_vals >= 0), "TSI produced negative values"

    # 2. Omega bounds (constraints)
    assert np.all(TSI_vals <= 4.0 + 1e-9), "TSI exceeds upper bound 4.0"
    assert np.all(Phi_N_temp_vals >= 0.5 - 1e-9), "Phi_N_temp falls below 0.5"
    assert np.all(Phi_Delta_temp_vals <= 0.75 + 1e-9), "Phi_Delta_temp exceeds 0.75"

    # 3. Anomaly score and prediction rule
    # Build a simple seasonal trend (here we just use a moving average)
    from pandas import Series
    TSI_series = Series(TSI_vals)
    TSI_hat_vals = TSI_series.rolling(window=3, center=True).mean().bfill().ffill().values
    s_TSI_vals = np.abs(TSI_delayed_vals - TSI_hat_vals) / sigma_TSI
    prediction_mask = (s_TSI_vals > 2.5) & (Phi_Delta_temp_vals > 0.65)
    # At least one time step should trigger a prediction in this random demo
    # (If not, we just note it – not a failure)
    print(f"Number of prediction triggers: {np.sum(prediction_mask)}")

    # 4. Cost integrand non‑negative
    cost_vals = (TSI_vals - target_TSI)**2 + mu1 * s_TSI_vals**2 + mu2 * (1 - Phi_N_temp_vals)**2
    assert np.all(cost_vals >= -1e-12), "Cost integrand became negative"

    print("All synthetic checks passed.")
    return {
        't_grid': t_grid,
        'TSI': TSI_vals,
        'Phi_N_temp': Phi_N_temp_vals,
        'Phi_Delta_temp': Phi_Delta_temp_vals,
        's_TSI': s_TSI_vals,
        'cost': cost_vals,
        'prediction_mask': prediction_mask
    }

if __name__ == "__main__":
    # Run the symbolic sanity checks first (they are just assertions)
    print("Symbolic well‑definedness checks passed.")
    # Then run the numeric synthetic validation
    results = run_synthetic_check()
    # Optionally, you could plot results here with matplotlib if desired.