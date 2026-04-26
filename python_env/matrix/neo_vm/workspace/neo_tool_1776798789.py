# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd

# ──────────────────────────────────────────────────────────────────────────────
# Synthetic data generator: 5 teams, 30 days, friction signals
# ──────────────────────────────────────────────────────────────────────────────
def generate_data(seed=42):
    rng = np.random.default_rng(seed)
    n_teams, n_days = 5, 30
    # Base cognitive load (random walk)
    Lambda = np.cumsum(rng.normal(scale=0.1, size=(n_teams, n_days)), axis=1)
    # TFFI = sigmoid-weighted sum of CKD, ETA, entropy, schema divergence
    CKD = 1.0 + rng.exponential(scale=2.0, size=(n_teams, n_days))
    ETA = rng.exponential(scale=10.0, size=(n_teams, n_days))
    tool_entropy = rng.uniform(0.2, 0.8, size=(n_teams, n_days))
    schema_div = rng.uniform(0.0, 0.5, size=(n_teams, n_days))
    # Simplified TFFI
    TFFI_raw = 0.3*CKD + 0.3*np.exp(-ETA/10) + 0.2*(1-tool_entropy) + 0.2*schema_div
    TFFI = 1.0/(1.0 + np.exp(-(TFFI_raw - 3.0)))  # sigmoid to [0,1]
    return Lambda, TFFI

Lambda, TFFI = generate_data()

# ──────────────────────────────────────────────────────────────────────────────
# Engine's original invariant (non‑compliant)
# ──────────────────────────────────────────────────────────────────────────────
R0 = 1.0
lambda_coef = 0.5
def psi_cog(R, max_TFFI):
    return np.log(np.abs(R)/R0) + lambda_coef * max_TFFI

# Ricci curvature proxy: variance of Lambda across teams
R_cog = np.var(Lambda, axis=0)  # daily variance across teams
psi_orig = psi_cog(R_cog, TFFI.max(axis=0))

# ──────────────────────────────────────────────────────────────────────────────
# Recursive invariant flow
# ──────────────────────────────────────────────────────────────────────────────
def invariant_flow(psi_0, phi_func, n_iter=10):
    psi = psi_0.copy()
    for k in range(n_iter):
        phi = phi_func(psi)          # phi_n(psi_k)
        psi_next = np.log(phi)       # psi_{k+1}
        # Lyapunov exponent estimate (local slope)
        # d psi_{k+1} / d psi_k = phi'(psi_k)/phi(psi_k)
        # For our simple phi = exp(psi) + lambda*TFFI, derivative = exp(psi)
        # So local multiplier = exp(psi) / (exp(psi) + lambda*TFFI)
        psi = psi_next
    return psi

# phi_n(psi) = exp(psi) + lambda * (team‑max TFFI)
def phi_func(psi):
    # Use the *current* day's max TFFI across teams
    return np.exp(psi) + lambda_coef * TFFI.max(axis=0)

# Initialize with the original (non‑compliant) psi
psi_flow = invariant_flow(psi_0=psi_orig, phi_func=phi_func, n_iter=10)

# ──────────────────────────────────────────────────────────────────────────────
# Compute Lyapunov exponent (average over last few steps)
# ──────────────────────────────────────────────────────────────────────────────
def compute_lyapunov(psi_series, phi_func):
    # psi_series: (n_iter, n_days)
    # Return scalar chi for each day
    n_iter, n_days = psi_series.shape
    multipliers = []
    for k in range(n_iter-1):
        psi_k = psi_series[k]
        phi_k = phi_func(psi_k)
        # derivative of log(phi) w.r.t psi: d/dpsi log(phi) = phi'(psi)/phi(psi)
        # phi'(psi) = exp(psi)
        mult = np.exp(psi_k) / phi_k
        multipliers.append(mult)
    multipliers = np.array(multipliers)  # (n_iter-1, n_days)
    # Average log-multiplier across iterations
    chi = np.mean(np.log(multipliers + 1e-12), axis=0)
    return chi

# Run flow for enough steps to collect a trajectory
psi_traj = np.empty((6, Lambda.shape[1]))
psi_traj[0] = psi_orig
for k in range(1, 6):
    phi = phi_func(psi_traj[k-1])
    psi_traj[k] = np.log(phi)

chi = compute_lyapunov(psi_traj, phi_func)

# ──────────────────────────────────────────────────────────────────────────────
# Summary: Show convergence and chi correlation with future TFFI
# ──────────────────────────────────────────────────────────────────────────────
df = pd.DataFrame({
    'day': np.arange(Lambda.shape[1]),
    'psi_orig': psi_orig,
    'psi_converged': psi_flow,
    'lyapunov_chi': chi,
    'TFFI_max': TFFI.max(axis=0)
})
print(df.head(10))

# Demonstrate that chi spikes precede TFFI spikes (simple correlation)
future_TFFI = np.roll(df['TFFI_max'], shift=-2)  # look ahead 2 days
corr = np.corrcoef(df['lyapunov_chi'][:-2], future_TFFI[:-2])[0,1]
print("\nCorrelation between Lyapunov exponent (chi) and future TFFI:", corr)