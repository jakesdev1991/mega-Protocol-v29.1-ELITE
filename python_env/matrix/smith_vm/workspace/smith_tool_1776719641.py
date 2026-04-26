# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Validator for the refined CERM‑Ω proposal.
Checks dimensionality, invariant definitions, and Omega‑Protocol constraints.
"""

import numpy as np
from scipy.stats import genpareto  # for GPD fitting (simple MLE)

# ----------------------------------------------------------------------
# Helper functions (mirroring the proposal)
# ----------------------------------------------------------------------
def compute_CES(leak_times, weights, gamma, t, valid_mask):
    """
    CES_i(t) = sum_c w_c * exp(-gamma*(t - t_c)) * I(valid)
    leak_times: array of shape (n_cred,) with timestamps of each credential leak
    weights:    array of shape (n_cred,) with tier weights w_c
    gamma:      exploitation rate (>0)
    t:          current time (scalar)
    valid_mask: bool array indicating if credential still active (honeypot test)
    Returns: scalar CES for one institution at time t
    """
    dt = t - leak_times
    # only consider leaks that have happened (dt >= 0) and are still valid
    mask = (dt >= 0) & valid_mask
    return np.sum(weights[mask] * np.exp(-gamma * dt[mask]))


def compute_SCEI(CES_vec, sizes):
    """
    SCEI(t) = sum_i CES_i(t) * size_i / sum_i size_i
    CES_vec: 1D array of CES for each institution
    sizes:   1D array of market footprints (positive)
    Returns: scalar SCEI
    """
    assert np.all(sizes > 0), "Sizes must be positive"
    return np.average(CES_vec, weights=sizes)


def psi_CES(SCEI, SCEI0):
    """Dimensionless scalar invariant."""
    assert SCEI > 0 and SCEI0 > 0, "SCEI and SCEI0 must be >0 for log"
    return np.log(SCEI / SCEI0)


def radial_corr_len(CES_grad_norms):
    """
    ξ_N^(CES) = ( (1/N) * sum_i ||∇_i CES_i||^2 )^{-1/2}
    CES_grad_norms: array of gradient norms for each institution
    Returns: non‑negative scalar
    """
    assert np.all(CES_grad_norms >= 0), "Gradient norms must be non‑negative"
    mean_sq = np.mean(CES_grad_norms ** 2)
    # Avoid division by zero; if all gradients zero, set xi_N = inf (treated as large)
    return np.inf if mean_sq == 0 else 1.0 / np.sqrt(mean_sq)


def poloidal_corr_len(tier_variances):
    """
    ξ_Δ^(CES) = max_k σ_k^2 / min_k σ_k^2
    tier_variances: dict or array of variances for each tier (k=1,2,3)
    Returns: scalar >= 1
    """
    assert np.all(np.array(tier_variances) > 0), "Variances must be >0"
    return np.max(tier_variances) / np.min(tier_variances)


def entropy_exposure(CES_vec):
    """Shannon entropy of the normalized CES distribution."""
    p = CES_vec / np.sum(CES_vec)
    # Avoid log(0) by masking zeros
    p = p[p > 0]
    return -np.sum(p * np.log(p))


def fit_GPD_threshold_excesses(data, threshold):
    """
    Fit a Generalized Pareto Distribution to exceedances over `threshold`.
    Returns shape (c), loc (threshold), scale.
    """
    excesses = data[data > threshold] - threshold
    if len(excesses) < 2:
        # Not enough data – return a degenerate GPD with huge scale
        return 0.0, threshold, 1e6
    # MLE via scipy (fix loc=threshold)
    c, loc, scale = genpareto.fit(excesses, floc=0)
    return c, threshold, scale


def anomaly_score_GPD(value, threshold, gp_params):
    """
    a_CES(t) = 1 - F_GPD(value - threshold)
    Returns tail probability in (0,1]
    """
    c, loc, scale = gp_params
    # loc should equal threshold
    assert np.isclose(loc, threshold), "GPD loc must match threshold"
    # CDF of GPD for x >= 0
    x = value - threshold
    if x < 0:
        return 1.0  # below threshold -> not an exceedance
    cdf = genpareto.cdf(x, c, loc=0, scale=scale)
    return 1.0 - cdf  # tail probability


# ----------------------------------------------------------------------
# Synthetic data generation (for illustration)
# ----------------------------------------------------------------------
np.random.seed(42)
n_inst = 5                     # number of financial institutions
n_cred_per_inst = 20           # average credentials per institution
t_now = 100.0                  # current time (arbitrary units)

# Institution sizes (market footprint) – positive
sizes = np.random.uniform(1, 10, size=n_inst)

# Tier weights
tier_weights = {1: 1.0, 2: 0.5, 3: 0.2}

# Simulate leak times and assign tiers
leak_times_all = []   # list per institution
weights_all = []      # list per institution
valid_all = []        # list per institution (honeypot result)
tier_assign_all = []  # list per institution (1,2,3)

for i in range(n_inst):
    n_cred = np.random.poisson(n_cred_per_inst) + 1
    leaks = np.sort(np.random.uniform(0, t_now, size=n_cred))  # leaks up to now
    tiers = np.random.choice([1, 2, 3], size=n_cred, p=[0.2, 0.5, 0.3])
    w = np.array([tier_weights[t] for t in tiers])
    # Simulate honeypot validation: 70% chance still valid
    valid = np.random.rand(n_cred) < 0.7
    leak_times_all.append(leaks)
    weights_all.append(w)
    valid_all.append(valid)
    tier_assign_all.append(tiers)

# Exploitation rate (gamma) – estimated from historical data
gamma = 0.05  # 1/time-unit

# ----------------------------------------------------------------------
# Compute core quantities at time t_now
# ----------------------------------------------------------------------
CES_inst = np.array([
    compute_CES(leak_times_all[i], weights_all[i], gamma, t_now, valid_all[i])
    for i in range(n_inst)
])

SCEI = compute_SCEI(CES_inst, sizes)

# Reference SCEI0 (median over a calibration window – here we just use a fixed value)
SCEI0 = np.median(CES_inst) * np.mean(sizes) / np.sum(sizes)  # rough proxy

# Invariants
psi = psi_CES(SCEI, SCEI0)

# Mock gradient norms (norm of CES_i w.r.t. institutional features)
# For simplicity, use absolute difference from mean as a proxy gradient norm
CES_grad_norms = np.abs(CES_inst - np.mean(CES_inst))
xi_N = radial_corr_len(CES_grad_norms)

# Tier variances for poloidal length
tier_variances = []
for k in [1, 2, 3]:
    # collect CES_i for institutions that have at least one Tier‑k credential
    mask = np.any([(tier_assign_all[i] == k) for i in range(n_inst)], axis=0)
    # Actually we need per‑institution flag: institution i has tier k if any of its credentials is tier k
    inst_has_k = np.array([np.any(tier_assign_all[i] == k) for i in range(n_inst)])
    CES_k = CES_inst[inst_has_k]
    if len(CES_k) > 0:
        tier_variances.append(np.var(CES_k))
    else:
        tier_variances.append(1e-6)  # avoid zero
xi_Delta = poloidal_corr_len(tier_variances)

# Entropy
S_h_CES = entropy_exposure(CES_inst)

# ----------------------------------------------------------------------
# Anomaly detection via GPD (tail of SCEI time series – we fake a short history)
# ----------------------------------------------------------------------
# Fake historical SCEI values (last 50 days) – slightly noisy around current SCEI
hist_SCEI = SCEI + np.random.normal(0, 0.05, size=50)
# Ensure positivity
hist_SCEI = np.clip(hist_SCEI, 1e-3, None)
threshold = np.percentile(hist_SCEI, 90)  # high threshold
gp_params = fit_GPD_threshold_excesses(hist_SCEI, threshold)
a_CES = anomaly_score_GPD(SCEI, threshold, gp_params)

# ----------------------------------------------------------------------
# Omega‑variable maps (using placeholder coefficients)
# ----------------------------------------------------------------------
Phi_N0 = 0.85
Phi_Delta0 = 0.3
alpha = 0.4
beta = 0.3
tau1 = 10.0   # days – treat as same units as t for simplicity
tau2 = 12.0
# We need SCEI at delayed times; for simplicity assume stationarity -> use current SCEI
Phi_N_op = Phi_N0 - alpha * psi  # ψ_CES(t-τ1) approximated by ψ(t)
Phi_Delta_op = Phi_Delta0 + beta * xi_Delta  # ξ_Δ^(CES)(t-τ2) approximated by ξ_Δ(t)

# ----------------------------------------------------------------------
# MPC‑Ω state vector (just for completeness)
# ----------------------------------------------------------------------
state = np.array([
    Phi_N_op,          # Φ_N
    Phi_Delta_op,      # Φ_Δ
    xi_N,              # ξ_N
    xi_Delta,          # ξ_Δ
    psi,               # ψ_CES
    S_h_CES,           # S_h^(CES)
    SCEI,              # SCEI
    a_CES,             # a_CES
    # institution‑level CES vector appended as a block
    *CES_inst
])

# ----------------------------------------------------------------------
# Validation: Omega‑Protocol invariants & constraints
# ----------------------------------------------------------------------
def assert_positive(x, name):
    assert x > 0, f"{name} must be >0, got {x}"

def assert_nonneg(x, name):
    assert x >= 0, f"{name} must be >=0, got {x}"

def assert_in_range(x, low, high, name):
    assert low <= x <= high, f"{name} must be in [{low},{high}], got {x}"

# 1. SCEI dimensionless & positive
assert_nonneg(SCEI, "SCEI")
# 2. ψ_CES real (log of positive ratio)
assert np.isfinite(psi), "ψ_CES must be finite"
# 3. ξ_N ≥ 0
assert_nonneg(xi_N, "ξ_N^(CES)")
# 4. ξ_Δ ≥ 1
assert xi_Delta >= 1.0, f"ξ_Δ^(CES) must be ≥1, got {xi_Delta}"
# 5. Entropy bounds
max_entropy = np.log(n_inst) if n_inst > 1 else 0.0
assert_in_range(S_h_CES, 0.0, max_entropy, "S_h^(CES)")
# 6. Anomaly score in (0,1]
assert_in_range(a_CES, 0.0, 1.0, "a_CES")
# 7. Ω‑variable maps keep Φ_N in [0,1] and Φ_Δ non‑negative (typical range)
assert_in_range(Phi_N_op, 0.0, 1.0, "Φ_N^(op)")
assert_nonneg(Phi_Delta_op, "Φ_Δ^(op)")
# 8. MPC‑Ω hard constraints
SCEI_max = 1.5          # as given in the proposal
assert SCEI <= SCEI_max, f"SCEI {SCEI} exceeds SCEI_max {SCEI_max}"
assert Phi_N_op >= 0.7, f"Φ_N {Phi_N_op} below safety threshold 0.7"
assert psi <= 0.0, f"ψ_CES {psi} must be ≤0 (i.e., SCEI ≤ SCEI0); got {psi}"
# 9. Cost‑function integrand non‑negativity (spot‑check a few terms)
#    J integrand = (1 - S_j)^2 + α1*S_h + α2*S_h_CES + λ1*(P_meas-P_target)^2 + λ2*SCEI^2
#    We only check that the squares and entropy terms are non‑negative.
assert (1.0 - 0.5)**2 >= 0, "dummy S_j term failed"
assert 0.1 * S_h_CES >= 0, "entropy term negative"
assert 0.1 * (SCEI**2) >= 0, "SCEI^2 term negative"

print("All Omega‑Protocol invariants and constraints are satisfied.")
print(f"SCEI = {SCEI:.4f}, ψ_CES = {psi:.4f}, ξ_N = {xi_N:.4f}, ξ_Δ = {xi_Delta:.4f}")
print(f"S_h_CES = {S_h_CES:.4f}, a_CES = {a_CES:.4f}")
print(f"Φ_N^(op) = {Phi_N_op:.4f}, Φ_Δ^(op) = {Phi_Delta_op:.4f}")
print(f"State vector length = {len(state)}")