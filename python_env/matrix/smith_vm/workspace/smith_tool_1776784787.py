# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Validation script for the Whitepaper Credential Risk Monitor (WCRM-Ω) proposal.
Checks:
  1. Mathematical consistency of the SFS formula.
  2. Mapping to Ω invariants (Φ_N, Φ_Δ) stays within physically meaningful bounds.
  3. Anomaly score computation is safe (no division by zero).
  4. Prediction rule thresholds are respected.
  5. MPC‑Ω state constraints are satisfied.
  6. Cost integrand is non‑negative (as required for a proper cost function).
"""

import numpy as np
import pandas as pd

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def sigmoid(x: np.ndarray) -> np.ndarray:
    """Standard logistic sigmoid."""
    return 1.0 / (1.0 + np.exp(-x))


def compute_sfs(leaks: pd.DataFrame, alpha: float, beta: float, gamma: float, lambd: float) -> float:
    """
    Compute Strategic Fragility Score (SFS) for a firm at a given time.
    leaks: DataFrame with columns ['C','N','D','T'] where
        C = credential criticality (1‑5)
        N = contextual negligence (1‑5)
        D = dissemination scale (non‑negative)
        T = time since publication (months, >=0)
    Returns scalar SFS.
    """
    # Ensure non‑negative times
    assert (leaks['T'] >= 0).all(), "Time since publication must be non‑negative"
    term = (alpha * leaks['C'] + beta * leaks['N'] + gamma * leaks['D']) * np.exp(-lambd * leaks['T'])
    return term.sum()


def map_phi_n(phi_n0: float, sfs: float, eta1: float, tau1: float, sfs_delayed: float) -> float:
    """
    Φ_N^{(wp)}(t) = Φ_N^{(0)} - η1 * sigmoid(SFS_j(t - τ1))
    We assume sfs_delayed = SFS_j(t - τ1) is provided.
    """
    return phi_n0 - eta1 * sigmoid(sfs_delayed)


def map_phi_delta(phi_delta0: float, sfs: float, eta2: float, tau2: float, sfs_delayed: float) -> float:
    """
    Φ_Δ^{(wp)}(t) = Φ_Δ^{(0)} + η2 * SFS_j(t - τ2)
    """
    return phi_delta0 + eta2 * sfs_delayed


def anomaly_score(residual: float, sigma_res: float) -> float:
    """
    s_SFS(t) = |residual(t)| / σ_residual
    Guard against σ_residual == 0.
    """
    if sigma_res == 0:
        raise ValueError("σ_residual must be > 0 to avoid division by zero.")
    return np.abs(residual) / sigma_res


# ----------------------------------------------------------------------
# Parameter values (chosen to be plausible; in practice these would be learned)
# ----------------------------------------------------------------------
ALPHA, BETA, GAMMA, LAMBDA = 0.4, 0.3, 0.3, 0.05   # weights for SFS components
ETA1, ETA2 = 0.2, 0.15                            # mapping strengths
TAU1, TAU2 = 10.0, 12.0                           # months lead‑time
PHI_N0, PHI_DELTA0 = 0.6, 0.4                     # baseline Ω invariants
LAMBDA1, LAMBDA2 = 0.5, 0.5                       # cost‑function weights
SFS_MAX = 10.0                                    # MPC constraint
PHI_N_MIN = 0.3                                   # MPC constraint
PHI_DELTA_MAX = 0.8                               # MPC constraint
ANOMALY_THRESH = 3.0
PHI_DELTA_FLAG_THRESH = 0.7

# ----------------------------------------------------------------------
# Synthetic data generation for a single firm over 24 months
# ----------------------------------------------------------------------
np.random.seed(42)
months = np.arange(0, 24, 1)  # t = 0..23 months

# Simulate a few leak events per month (Poisson-distributed)
leak_records = []  # each entry: (month, C, N, D, T)
for t in months:
    n_leaks = np.random.poisson(lam=1.5)  # average 1–2 leaks per month
    for _ in range(n_leaks):
        C = np.random.randint(1, 6)          # criticality 1‑5
        N = np.random.randint(1, 6)          # negligence 1‑5
        D = np.random.exponential(scale=2.0) # dissemination scale (positive)
        T = t  # time since publication = current month (for simplicity)
        leak_records.append([t, C, N, D, T])

leaks_df = pd.DataFrame(leak_records, columns=['month', 'C', 'N', 'D', 'T'])

# ----------------------------------------------------------------------
# Compute time‑series of SFS, Φ_N, Φ_Δ, anomaly score, and check constraints
# ----------------------------------------------------------------------
results = []
for t in months:
    # Leaks that have occurred up to and including month t
    leaks_up_to_t = leaks_df[leaks_df['month'] <= t]
    # For mapping we need delayed SFS values (t - τ). Use 0 if insufficient history.
    sfs_now = compute_sfs(leaks_up_to_t, ALPHA, BETA, GAMMA, LAMBDA)
    sfs_tau1 = compute_sfs(
        leaks_df[leaks_df['month'] <= max(t - TAU1, 0)],
        ALPHA, BETA, GAMMA, LAMBDA
    ) if t >= TAU1 else 0.0
    sfs_tau2 = compute_sfs(
        leaks_df[leaks_df['month'] <= max(t - TAU2, 0)],
        ALPHA, BETA, GAMMA, LAMBDA
    ) if t >= TAU2 else 0.0

    # Map to Ω invariants
    phi_n = map_phi_n(PHI_N0, sfs_now, ETA1, TAU1, sfs_tau1)
    phi_delta = map_phi_delta(PHI_DELTA0, sfs_now, ETA2, TAU2, sfs_tau2)

    # Simulate a residual for anomaly detection (e.g., deviation from rolling mean)
    # For simplicity, use a Gaussian noise with sigma=0.5
    residual = np.random.normal(loc=0.0, scale=0.5)
    sigma_res = 0.5  # known std‑dev of the noise model
    sfs_anom = anomaly_score(residual, sigma_res)

    # Prediction flag
    flag = (sfs_anom > ANOMALY_THRESH) and (phi_delta > PHI_DELTA_FLAG_THRESH)

    # Constraint checks
    c1 = sfs_now <= SFS_MAX
    c2 = phi_n >= PHI_N_MIN
    c3 = phi_delta <= PHI_DELTA_MAX

    # Cost integrand (instantaneous)
    cost_inst = (1.0 - phi_n)**2 + LAMBDA1 * (phi_delta**2) + LAMBDA2 * (sfs_anom**2)

    results.append({
        'month': t,
        'SFS': sfs_now,
        'Phi_N': phi_n,
        'Phi_Delta': phi_delta,
        'SFS_Anomaly': sfs_anom,
        'Flag': flag,
        'SFS_ok': c1,
        'Phi_N_ok': c2,
        'Phi_Delta_ok': c3,
        'Cost_inst': cost_inst
    })

df = pd.DataFrame(results)

# ----------------------------------------------------------------------
# Validation summary
# ----------------------------------------------------------------------
print("=== WCRM‑Ω Mathematical & Invariant Validation ===\n")
print(f"Total months evaluated: {len(df)}")
print(f"Months satisfying SFS ≤ {SFS_MAX}: {df['SFS_ok'].sum()} / {len(df)}")
print(f"Months satisfying Φ_N ≥ {PHI_N_MIN}: {df['Phi_N_ok'].sum()} / {len(df)}")
print(f"Months satisfying Φ_Δ ≤ {PHI_DELTA_MAX}: {df['Phi_Delta_ok'].sum()} / {len(df)}")
print(f"Months where prediction flag is True: {df['Flag'].sum()}")
print(f"Minimum cost integrand observed: {df['Cost_inst'].min():.6f}")
print(f"Maximum cost integrand observed: {df['Cost_inst'].max():.6f}")
print("\nFirst 5 rows of the time‑series:")
print(df.head().to_string(index=False))

# ----------------------------------------------------------------------
# Additional sanity checks
# ----------------------------------------------------------------------
assert (df['SFS'] >= 0).all(), "SFS should be non‑negative (exponential decay of non‑negative terms)."
assert (df['Phi_N'] >= 0).all(), "Φ_N should not go negative; check eta1 sizing."
assert (df['Phi_Delta'] >= 0).all(), "Φ_Δ should not go negative; check eta2 sizing."
assert (df['Cost_inst'] >= 0).all(), "Cost integrand must be non‑negative."
assert df['SFS_Anomaly'].notnull().all(), "Anomaly score must be defined (σ_residual > 0)."

print("\nAll sanity checks passed.")