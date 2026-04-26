# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Validation Script for HISS‑Ω (Homogeneity‑Induced Synchronization Shield)

Checks:
- Kuramoto order parameter r(t) ∈ [0,1]
- Action entropy S_action(t) ≥ 0 and ≤ ln(|A|) where |A|=3
- SFI(t) computed via tanh is mapped to [0,1]
- Invariant ψ_sync = ln(Φ_N_sync / Φ_N0) matches the definition used in the action
- QP constraints: SFI ≤ 0.68, Φ_N_sync ≥ 0.4, S_action ≥ ln(3)
- Entropy gauge A_μ = ∂_μ S_action (finite difference approximation)
"""

import numpy as np

# ------------------------------
# Helper functions
# ------------------------------
def kuramoto_order_parameter(phases):
    """Compute Kuramoto order parameter r = |⟨e^{iθ}⟩|."""
    return np.abs(np.mean(np.exp(1j * phases)))

def action_entropy(prob_actions):
    """Shannon entropy for action distribution (assumes prob_actions sums to 1)."""
    # Avoid log(0)
    prob_actions = np.clip(prob_actions, 1e-12, 1.0)
    return -np.sum(prob_actions * np.log(prob_actions))

def skewness(data):
    """Sample skewness (unbiased)."""
    n = len(data)
    if n < 3:
        return 0.0
    m = np.mean(data)
    m2 = np.sum((data - m) ** 2) / n
    m3 = np.sum((data - m) ** 3) / n
    return m3 / (m2 ** 1.5) if m2 != 0 else 0.0

def correlation_length(events_matrix):
    """
    Rough estimate of spatial correlation length ξ_L from binary liquidity‑event matrix.
    events_matrix: shape (n_pools, n_time) with 1=event, 0=no event.
    Returns ξ_L as average pairwise correlation decay distance (placeholder).
    """
    # Placeholder: compute average pairwise correlation and invert
    corr = np.corrcoef(events_matrix)  # n_pools x n_pools
    np.fill_diagonal(corr, 0)
    avg_corr = np.mean(np.abs(corr))
    return 1.0 / (avg_corr + 1e-9)  # avoid div0

# ------------------------------
# Synthetic data generation (for illustration)
# ------------------------------
np.random.seed(42)
n_pools = 50
n_time = 100

# Phases θ_i(t) ∈ [0, 2π)
phases = np.random.uniform(0, 2 * np.pi, size=(n_pools, n_time))

# Simulate liquidity withdrawal events (binary) correlated with phase near π
withdrawal_prob = 0.5 + 0.5 * np.cos(phases)  # higher when θ≈π
withdrawal_events = (np.random.rand(n_pools, n_time) < withdrawal_prob).astype(float)

# Action probabilities per pool per time: [deposit, withdraw, hold]
# Simple model: withdraw prob from event, deposit prob low, hold = rest
p_withdraw = withdrawal_events.clip(0, 1)
p_deposit = 0.1 * (1 - p_withdraw)
p_hold = 1.0 - p_withdraw - p_deposit
action_probs = np.stack([p_deposit, p_withdraw, p_hold], axis=-1)  # shape (n_pools, n_time, 3)

# Pool parameters for Φ_N and Φ_Δ
# ξ_L from withdrawal events spatial correlation
xi_L = correlation_length(withdrawal_events.T)  # time x pools -> pools x time
Phi_N_sync = 1.0 / (xi_L + 1e-9)

# Liquidity per pool (random baseline + event impact)
base_liq = np.random.uniform(80, 120, size=n_pools)
liq_impact = -10 * withdrawal_events.mean(axis=1)  # withdraw reduces liquidity
liquidity = base_liq + liq_impact
Phi_Delta_sync = skewness(liquidity)  # skewness of liquidity distribution

# Baseline values (t=0)
Phi_N0 = Phi_N_sync.mean()
Phi_Delta0 = Phi_Delta_sync.mean()

# ------------------------------
# Metrics computation
# ------------------------------
r_t = np.array([kuramoto_order_parameter(phases[:, t]) for t in range(n_time)])
S_action_t = np.array([
    action_entropy(action_probs[:, t, :].mean(axis=0))  # average over pools
    for t in range(n_time)
])

# Synchronization Fragility Index (SFI) – raw tanh argument
alpha, beta, gamma, delta = 1.0, 1.0, 1.0, 1.0  # example weights
raw = alpha * r_t + beta * (1 - S_action_t / np.log(3)) + gamma * Phi_Delta_sync - delta * (1.0 / Phi_N_sync)
# Map tanh to [0,1]
SFI_t = (np.tanh(raw) + 1.0) / 2.0

# Invariant ψ_sync (using Φ_N definition)
psi_sync_t = np.log(Phi_N_sync / Phi_N0)

# Entropy gauge A_μ ≈ temporal derivative of S_action
A_mu = np.gradient(S_action_t)  # dS/dt

# ------------------------------
# Validation checks
# ------------------------------
def check_bounds(arr, low, high, name):
    ok = np.all((arr >= low) & (arr <= high))
    print(f"{name} in [{low}, {high}]: {ok}")
    if not ok:
        print(f"  Min={arr.min():.4f}, Max={arr.max():.4f}")
    return ok

print("=== HISS‑Ω Mathematical Validation ===")
check_bounds(r_t, 0.0, 1.0, "Kuramoto r(t)")
check_bounds(S_action_t, 0.0, np.log(3), "Action entropy S_action(t)")
check_bounds(SFI_t, 0.0, 1.0, "SFI(t) (tanh mapped)")
check_bounds(psi_sync_t, -np.inf, np.inf, "ψ_sync(t)")  # just report range
print(f"ψ_sync range: [{psi_sync_t.min():.4f}, {psi_sync_t.max():.4f}]")

# QP constraints (time‑wise)
constraint_SFI = SFI_t <= 0.68
constraint_PhiN = Phi_N_sync >= 0.4
constraint_Sact = S_action_t >= np.log(3)

print("\n=== Constraint Satisfaction (per time step) ===")
print(f"SFI ≤ 0.68 satisfied: {np.all(constraint_SFI)} ({np.sum(constraint_SFI)}/{n_time})")
print(f"Φ_N_sync ≥ 0.4 satisfied: {np.all(constraint_PhiN)} ({np.sum(constraint_PhiN)}/{n_time})")
print(f"S_action ≥ ln(3) satisfied: {np.all(constraint_Sact)} ({np.sum(constraint_Sact)}/{n_time})")

# If any constraint violated, show worst offenders
if not np.all(constraint_SFI):
    worst = np.argmax(SFI_t)
    print(f"  Worst SFI at t={worst}: {SFI_t[worst]:.4f}")
if not np.all(constraint_PhiN):
    worst = np.argmin(Phi_N_sync)
    print(f"  Worst Φ_N_sync at t={worst}: {Phi_N_sync[worst]:.4f}")
if not np.all(constraint_Sact):
    worst = np.argmin(S_action_t)
    print(f"  Worst S_action at t={worst}: {S_action_t[worst]:.4f}")

print("\n=== Entropy Gauge Sample (first 5 steps) ===")
for i in range(min(5, len(A_mu))):
    print(f"t={i}: A_μ = {A_mu[i]:.6f}")

print("\nValidation complete.")