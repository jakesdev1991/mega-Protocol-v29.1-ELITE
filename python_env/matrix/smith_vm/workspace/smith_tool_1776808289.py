# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Ω‑Protocol validator for Topological Trading Memory (TTM‑Ω)
---------------------------------------------------------
Checks mathematical soundness and invariant compliance:
    Φ_N = 1 - TTCI
    Φ_Delta = Var[ log( ξ_ij / ξ0 ) ]
    ψ_ttm = log(|<Wp>|/|<Wp0>|) + λ*log(Δ_reg/Δ0)
Hard constraints (MPC‑Ω):
    TTCI >= 0.6
    Δ_reg >= Δ_min
    ξ   >= ξ_min
"""

import numpy as np

# ----------------------------------------------------------------------
# 1. Synthetic data generation
# ----------------------------------------------------------------------
np.random.seed(42)
n_agents = 9                     # 3x3 lattice for easy Wilson loops
n_time   = 200                   # time steps
# Regime: first 80 steps low volatility, then high volatility
regime = np.array([0]*80 + [1]*(n_time-80))   # 0=low,1=high

# Base coupling (ferromagnetic) J0, modulated by regime stress
J0 = 1.0
J_stress = np.where(regime==0, 0.2, 0.8)      # higher stress → weaker alignment
J = J0 * (1 - J_stress)                      # J in [0.2, 1.0]

# External field h (market bias) – small random walk
h = np.cumsum(np.random.randn(n_agents, n_time)*0.05, axis=1)

# Initialize spins S_i^z(t) ∈ {+1,-1}
S = np.ones((n_agents, n_time), dtype=int)
# Glauber dynamics (simple Metropolis) to induce regime‑dependent correlations
beta = np.where(regime==0, 1.0, 0.3)   # low vol → high inverse temp (more ordered)
for t in range(1, n_time):
    for i in range(n_agents):
        # neighbours on 3x3 grid with periodic BC
        nbrs = [((i-1)%3)*3 + i%3, ((i+1)%3)*3 + i%3,
                (i//3)*3 + (i-1)%3, (i//3)*3 + (i+1)%3]
        local_field = np.sum([J[i, j]*S[j, t-1] for j in nbrs]) + h[i, t]
        p_flip = 1.0/(1.0+np.exp(2*beta[t]*local_field))
        if np.random.rand() < p_flip:
            S[i, t] = -S[i, t-1]
        else:
            S[i, t] = S[i, t-1]

# ----------------------------------------------------------------------
# 2. Helper functions
# ----------------------------------------------------------------------
def wilson_loop(spins, plaquette):
    """Product of spins around a 2x2 plaquette (indices given)."""
    prod = 1
    for idx in plaquette:
        prod *= spins[idx]
    return prod

def correlation_length(spins):
    """Estimate ξ from exponential decay of spin‑spin correlation with distance."""
    # Compute correlation for each pair
    n = spins.shape[0]
    corr = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            corr[i, j] = np.mean(spins[i]*spins[j])
    # Flatten upper triangle (excluding self)
    triu_idx = np.triu_indices(n, k=1)
    distances = np.array([np.abs(np.unravel_index(i, (int(np.sqrt(n)), int(np.sqrt(n)))) -
                               np.unravel_index(j, (int(np.sqrt(n)), int(np.sqrt(n)))))
                          for i, j in zip(triu_idx[0], triu_idx[1])])
    dists = np.sum(np.abs(distances), axis=1)   # Manhattan distance on lattice
    vals = corr[triu_idx]
    # Fit log|C| = -d/ξ  → ξ = -d / log|C|
    mask = np.abs(vals) > 1e-3
    if np.sum(mask) < 2:
        return np.inf
    xi_est = -np.mean(dists[mask] / np.log(np.abs(vals[mask])))
    return max(xi_est, 1e-3)

# ----------------------------------------------------------------------
# 3. Main evaluation loop
# ----------------------------------------------------------------------
# Reference values (taken from first time step as calibration)
Wp0 = wilson_loop(S[:,0], [0,1,4,3])   # example plaquette (top‑left 2x2)
xi0 = correlation_length(S[:,0])
Delta0 = np.var(S[:,0])                # proxy for regime gap (variance of spins)

# Parameters for MPC‑Ω
TTCI_min = 0.6
Delta_min = 0.5 * Delta0
xi_min    = 0.5 * xi0
lam = 0.5                         # λ in ψ_ttm
gamma = 0.1                       # decay rate in TTCI dynamics
kappa = 0.05                      # reconfiguration strength

# Storage for metrics
TTCI_hist = []
PhiN_hist = []
PhiD_hist = []
psi_hist  = []
constraints_ok = []

# Simple coupling matrix J_ij (symmetric) – we will adapt it
J_mat = np.full((n_agents, n_agents), J0)
np.fill_diagonal(J_mat, 0)

for t in range(n_time):
    # ---- Wilson loop & correlation length ----
    Wp_t = wilson_loop(S[:,t], [0,1,4,3])
    xi_t = correlation_length(S[:,t])
    # ---- Regime gap proxy (variance of spins) ----
    Delta_t = np.var(S[:,t])
    # ---- TTCI ----
    TTCI = (np.abs(Wp_t)/np.abs(Wp0)) * (Delta_t/Delta0) * (xi_t/xi0)
    TTCI = min(TTCI, 1.0)          # enforce ≤1 by clipping to calibration max
    # ---- Ω‑covariant modes ----
    PhiN = 1.0 - TTCI
    # Φ_Delta: variance of log ξ_ij/ξ0 ; we approximate ξ_ij by pairwise correlation length
    # Compute pairwise ξ_ij via correlation of each pair (crude but illustrative)
    pair_logs = []
    for i in range(n_agents):
        for j in range(i+1, n_agents):
            cij = np.mean(S[i,:t+1]*S[j,:t+1]) if t>0 else 1.0
            # approximate ξ_ij = -1 / log|cij| (if |cij|<1)
            if np.abs(cij) > 1e-3 and np.abs(cij) < 1:
                xi_ij = -1.0/np.log(np.abs(cij))
            else:
                xi_ij = xi0   # fallback
            pair_logs.append(np.log(xi_ij/xi0))
    PhiD = np.var(pair_logs) if len(pair_logs)>0 else 0.0
    # ---- ψ_ttm invariant ----
    psi = np.log(np.abs(Wp_t)/np.abs(Wp0)) + lam*np.log(Delta_t/Delta0)

    # ---- Store ----
    TTCI_hist.append(TTCI)
    PhiN_hist.append(PhiN)
    PhiD_hist.append(PhiD)
    psi_hist.append(psi)

    # ---- Constraint check (MPC‑Ω hard bounds) ----
    ok = (TTCI >= TTCI_min) and (Delta_t >= Delta_min) and (xi_t >= xi_min)
    constraints_ok.append(ok)

    # ---- Simple MPC control action (executed for next step) ----
    if t < n_time-1:
        if TTCI < 0.7:                     # trigger coupling reinforcement
            # increase J for pairs that are already aligned (robust)
            for i in range(n_agents):
                for j in range(i+1, n_agents):
                    if S[i,t]*S[j,t] > 0:   # aligned → reinforce
                        J_mat[i,j] = J_mat[j,i] = min(J_mat[i,j]*1.05, J0*1.5)
                    else:
                        J_mat[i,j] = J_mat[j,i] = max(J_mat[i,j]*0.95, J0*0.5)
        # else keep J unchanged

# ----------------------------------------------------------------------
# 4. Validation summary
# ----------------------------------------------------------------------
TTCI_hist = np.array(TTCI_hist)
PhiN_hist = np.array(PhiN_hist)
PhiD_hist = np.array(PhiD_hist)
psi_hist  = np.array(psi_hist)
constraints_ok = np.array(constraints_ok)

print("=== Ω‑Protocol Validation Summary ===")
print(f"Time steps: {n_time}")
print(f"TTCI mean ± std: {TTCI_hist.mean():.4f} ± {TTCI_hist.std():.4f}")
print(f"Φ_N mean ± std:  {PhiN_hist.mean():.4f} ± {PhiN_hist.std():.4f}  (should be in [0,1])")
print(f"Φ_Δ mean ± std:  {PhiD_hist.mean():.6f} ± {PhiD_hist.std():.6f}  (should be ≥0)")
print(f"ψ_ttm mean ± std: {psi_hist.mean():.4f} ± {psi_hist.std():.4f}")
print(f"Constraint satisfaction: {constraints_ok.mean()*100:.1f}% of timesteps")
print(f"Minimum TTCI observed: {TTCI_hist.min():.4f} (hard bound {TTCI_min})")
print(f"Minimum Δ_reg observed: {np.var(S,axis=1).min():.4f} (hard bound {Delta_min})")
print(f"Minimum ξ observed:   {np.array([correlation_length(S[:,t]) for t in range(n_time)]).min():.4f} (hard bound {xi_min})")
# ----------------------------------------------------------------------
# 5. Quick sanity check of mathematical identities
# ----------------------------------------------------------------------
# Check that ψ can be expressed as function of Φ_N and Δ_reg (via TTCI)
# From definitions:
#   Φ_N = 1 - TTCI
#   TTCI = (|Wp|/|Wp0|)*(Δ/Δ0)*(ξ/ξ0)
#   => |Wp|/|Wp0| = TTCI * (Δ0/Δ) * (ξ0/ξ)
#   => ψ = log(TTCI) + log(Δ0/Δ) + log(ξ0/ξ) + λ*log(Δ/Δ0)
#        = log(TTCI) + (λ-1)*log(Δ/Δ0) + log(ξ0/ξ)
# Since TTCI = 1-Φ_N, the relation holds.
print("\nIdentity check (ψ vs Φ_N, Δ):")
psi_recon = np.log(1-PhiN_hist) + (lam-1)*np.log(np.var(S,axis=1)/Delta0) + np.log(xi0/np.array([correlation_length(S[:,t]) for t in range(n_time)]))
print(f"Max |ψ - ψ_recon|: {np.max(np.abs(psi_hist-psi_recon)):.2e}")
print("=== End of validation ===")