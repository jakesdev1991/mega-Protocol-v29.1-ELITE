# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# ------------------------------
# Helper functions (as per CERM-Ω v2)
# ------------------------------

def compute_ces(institution_credentials, t, gamma, tier_weights):
    """
    institution_credentials: list of dicts for one institution,
        each dict: {'t_c': leak_time, 'tier': 1|2|3, 'valid': bool}
    t: current time (scalar)
    gamma: exploitation rate (scalar >0)
    tier_weights: dict {1:1.0, 2:0.5, 3:0.2}
    Returns CES_i(t)
    """
    ces = 0.0
    for c in institution_credentials:
        if not c['valid']:
            continue
        w = tier_weights[c['tier']]
        ces += w * np.exp(-gamma * (t - c['t_c']))
    return ces

def scei(ces_values, sizes):
    """
    ces_values: array-like of CES_i for all institutions
    sizes: array-like of institution size (market footprint)
    Returns SCEI(t) (dimensionless)
    """
    ces_values = np.asarray(ces_values, dtype=float)
    sizes = np.asarray(sizes, dtype=float)
    return np.sum(ces_values * sizes) / np.sum(sizes)

def psi_ces(scei_val, scei0):
    """Scalar invariant ψ_CES = ln(SCEI/SCEI0)"""
    return np.log(scei_val / scei0)

def radial_corr_len(ces_matrix, features):
    """
    ces_matrix: shape (N_institutions, T_time)
    features: shape (N_institutions, D_feature) – e.g., [log_size, sector_onehot, geo]
    Returns ξ_N^(CES)(t) for each time step.
    """
    N, T = ces_matrix.shape
    # gradient w.r.t. features: approximate by finite difference across institutions
    # For each time step, compute variance of CES across institutions per feature dimension
    # Then gradient magnitude squared ≈ sum over dimensions of (ΔCES/Δfeature)^2.
    # We'll use a simple proxy: variance of CES across institutions.
    # This avoids needing an explicit metric; still yields a positive length scale.
    var_across_inst = np.var(ces_matrix, axis=0)  # shape (T,)
    # Avoid division by zero
    var_across_inst = np.where(var_across_inst == 0, 1e-12, var_across_inst)
    xi_n = 1.0 / np.sqrt(var_across_inst)  # proportional to inverse std-dev
    return xi_n

def poloidal_corr_len(ces_matrix, tier_labels):
    """
    ces_matrix: shape (N, T)
    tier_labels: length N array with values 1,2,3 indicating highest tier of any credential
    Returns ξ_Δ^(CES)(t) = max_k σ_k^2 / min_k σ_k^2 (with regulariser ε)
    """
    T = ces_matrix.shape[1]
    eps = 1e-9
    xi_delta = np.zeros(T)
    for t in range(T):
        vars_per_tier = []
        for k in [1,2,3]:
            mask = (tier_labels == k)
            if np.any(mask):
                vars_per_tier.append(np.var(ces_matrix[mask, t]))
            else:
                vars_per_tier.append(eps)  # regularise empty tier
        xi_delta[t] = (np.max(vars_per_tier) + eps) / (np.min(vars_per_tier) + eps)
    return xi_delta

def entropy_ces(ces_values):
    """Shannon entropy of exposure distribution; returns 0 if total exposure == 0."""
    ces = np.asarray(ces_values, dtype=float)
    total = np.sum(ces)
    if total == 0:
        return 0.0
    p = ces / total
    # avoid log(0)
    p = np.where(p == 0, 1e-12, p)
    return -np.sum(p * np.log(p))

def map_to_phi_n(phi_n0, alpha, psi_ces_val, tau):
    """Φ_N^{(op)}(t) = Φ_N^{(0)} - α * ψ_CES(t-τ)"""
    return phi_n0 - alpha * psi_ces_val

def map_to_phi_delta(phi_delta0, beta, xi_delta_val, tau):
    """Φ_Δ^{(op)}(t) = Φ_Δ^{(0)} + β * ξ_Δ^{(CES)}(t-τ)"""
    return phi_delta0 + beta * xi_delta_val

def anomaly_score_gpd(scei_series, threshold_percentile=90):
    """
    Empirical approximation of GPD tail probability.
    Returns a_CES(t) = 1 - F_GPD(SCEI(t)-u) ≈ proportion of non-exceedances.
    """
    scei = np.asarray(scei_series)
    u = np.percentile(scei, threshold_percentile)
    exceedances = scei > u
    # empirical tail probability of exceedance
    tail_prob = np.mean(exceedances) if np.any(exceedances) else 0.0
    # a_CES = probability of NOT exceeding (i.e., 1 - tail probability)
    return 1.0 - tail_prob

def mpc_cost(phi_n, phi_delta, xi_n, xi_delta, psi_ces, sh_ces, scei, a_ces,
             sj, sh, p_meas, p_target,
             alpha1=1.0, alpha2=1.0, lambda1=1.0, lambda2=1.0):
    """
    Instantaneous cost integrand (simplified).
    All terms dimensionless; sj is jerk‑stability metric (0< sj ≤1).
    """
    cost = ((1.0 - sj)**2
            + alpha1 * sh
            + alpha2 * sh_ces
            + lambda1 * (p_meas - p_target)**2
            + lambda2 * scei**2)
    return cost

def check_constraints(scei_val, phi_n_val, psi_ces_val,
                      scei_max=1.5, phi_n_min=0.7):
    """Return True if all hard constraints satisfied."""
    return (scei_val <= scei_max) and (phi_n_val >= phi_n_min) and (psi_ces_val <= 0.0)

# ------------------------------
# Synthetic data generation for validation
# ------------------------------
np.random.seed(42)
N_inst = 20
T_steps = 100

# Institution sizes (market footprint)
sizes = np.random.uniform(0.5, 5.0, size=N_inst)  # arbitrary units

# Tier assignment: each institution gets a highest tier based on size bias
tier_labels = np.random.choice([1,2,3], size=N_inst, p=[0.2,0.5,0.3])

# Simulate credential leaks as Poisson process per institution
gamma = 0.1  # exploitation rate (1/day)
tier_weights = {1:1.0, 2:0.5, 3:0.2}

# For each institution, generate a few leak events
institution_credentials = []
for i in range(N_inst):
    n_leaks = np.random.poisson(lam=3)  # average 3 leaks over the horizon
    leaks = []
    for _ in range(n_leaks):
        t_c = np.random.uniform(0, T_steps*0.8)  # leak time
        tier = tier_labels[i]  # assume highest tier credential
        valid = np.random.rand() > 0.2  # 80% still valid
        leaks.append({'t_c': t_c, 'tier': tier, 'valid': valid})
    institution_credentials.append(leaks)

# Time axis
t_vals = np.arange(T_steps)

# Compute CES matrix (N x T)
ces_matrix = np.zeros((N_inst, T_steps))
for i in range(N_inst):
    for idx, t in enumerate(t_vals):
        ces_matrix[i, idx] = compute_ces(institution_credentials[i], t, gamma, tier_weights)

# Compute SCEI over time
scei_series = np.array([scei(ces_matrix[:, t], sizes) for t in range(T_steps)])

# Reference SCEI0 (median over calibration period, say first 30 steps)
scei0 = np.median(scei_series[:30])

# Compute invariants and derived quantities
psi_ces_series = psi_ces(scei_series, scei0)
# For radial correlation length we need a feature matrix – use log size and one-hot sector dummy
log_size = np.log(sizes)[:, None]
# dummy sector: 3 sectors randomly assigned
sector_onehot = np.eye(3)[np.random.choice(3, size=N_inst)]
features = np.hstack([log_size, sector_onehot])
xi_n_series = radial_corr_len(ces_matrix, features)  # shape (T,)

xi_delta_series = poloidal_corr_len(ces_matrix, tier_labels)  # shape (T,)

sh_ces_series = np.array([entropy_ces(ces_matrix[:, t]) for t in range(T_steps)])

# Map to Omega variables (choose arbitrary parameters)
phi_n0, phi_delta0 = 0.85, 0.3
alpha, beta = 0.1, 0.05
tau1, tau2 = 7, 7  # days lag (in steps assume 1‑day resolution)
phi_n_op = np.array([map_to_phi_n(phi_n0, alpha, psi_ces_series[max(0, t-tau1)], tau1)
                     for t in range(T_steps)])
phi_delta_op = np.array([map_to_phi_delta(phi_delta0, beta, xi_delta_series[max(0, t-tau2)], tau2)
                         for t in range(T_steps)])

# Anomaly detection
a_ces_series = np.array([anomaly_score_gpd(scei_series[:t+1]) for t in range(T_steps)])

# Dummy additional MPC inputs
sj_series = np.random.uniform(0.5, 1.0, size=T_steps)  # jerk‑stability (placeholder)
sh_series = np.random.uniform(0.1, 0.6, size=T_steps)  # market entropy
p_meas_series = np.random.uniform(0.9, 1.1, size=T_steps)  # power consumption
p_target = 1.0

# Compute cost and check constraints at each time step
cost_series = np.zeros(T_steps)
constraint_ok = np.zeros(T_steps, dtype=bool)

for t in range(T_steps):
    cost_series[t] = mpc_cost(
        phi_n_op[t], phi_delta_op[t],
        xi_n_series[t], xi_delta_series[t],
        psi_ces_series[t], sh_ces_series[t],
        scei_series[t], a_ces_series[t],
        sj_series[t], sh_series[t],
        p_meas_series[t], p_target
    )
    constraint_ok[t] = check_constraints(scei_series[t],
                                         phi_n_op[t],
                                         psi_ces_series[t])

# ------------------------------
# Validation assertions
# ------------------------------
# 1. No NaNs or Infs in any computed series
assert not np.any(np.isnan(ces_matrix)), "CES contains NaN"
assert not np.any(np.isinf(ces_matrix)), "CES contains Inf"
assert not np.any(np.isnan(scei_series)), "SCEI contains NaN"
assert not np.any(np.isinf(scei_series)), "SCEI contains Inf"
assert not np.any(np.isnan(psi_ces_series)), "ψ_CES contains NaN"
assert not np.any(np.isinf(psi_ces_series)), "ψ_CES contains Inf"
assert not np.any(np.isnan(xi_n_series)), "ξ_N contains NaN"
assert not np.any(np.isinf(xi_n_series)), "ξ_N contains Inf"
assert not np.any(np.isnan(xi_delta_series)), "ξ_Δ contains NaN"
assert not np.any(np.isinf(xi_delta_series)), "ξ_Δ contains Inf"
assert not np.any(np.isnan(sh_ces_series)), "S_h^(CES) contains NaN"
assert not np.any(np.isinf(sh_ces_series)), "S_h^(CES) contains Inf"

# 2. ξ_N > 0 (length scale positive)
assert np.all(xi_n_series > 0), "Radial correlation length non‑positive"

# 3. ξ_Δ >= 1 (by construction with regulariser)
assert np.all(xi_delta_series >= 1 - 1e-12), "Poloidal correlation length < 1"

# 4. Entropy non‑negative and ≤ log(N) (max entropy)
max_entropy = np.log(N_inst) if N_inst > 1 else 0.0
assert np.all(sh_ces_series >= -1e-12), "Negative entropy"
assert np.all(sh_ces_series <= max_entropy + 1e-12), "Entropy exceeds theoretical maximum"

# 5. Mapping to Φ_N and Φ_Δ yields sensible bounds (0‑1 ideally)
assert np.all((phi_n_op >= 0) & (phi_n_op <= 1)), "Φ_N^{(op)} out of [0,1]"
assert np.all((phi_delta_op >= 0) & (phi_delta_op <= 1)), "Φ_Δ^{(op)} out of [0,1]"

# 6. Anomaly score in [0,1]
assert np.all((a_ces_series >= 0) & (a_ces_series <= 1 + 1e-12)), "a_CES out of [0,1]"

# 7. Constraints satisfaction ratio (should be reasonably high)
constraint_ratio = np.mean(constraint_ok)
print(f"Constraint satisfaction ratio: {constraint_ratio:.3f}")
# Expect a decent ratio; if too low, parameters may be off.
assert constraint_ratio > 0.5, "Too many constraint violations"

# 8. Cost non‑negative
assert np.all(cost_series >= -1e-12), "Negative cost encountered"

print("All mathematical sanity checks passed.")
print(f"Mean SCEI: {np.mean(scei_series):.4f}")
print(f"Mean ψ_CES: {np.mean(psi_ces_series):.4f}")
print(f"Mean ξ_N: {np.mean(xi_n_series):.4f}")
print(f"Mean ξ_Δ: {np.mean(xi_delta_series):.4f}")
print(f"Mean entropy S_h^(CES): {np.mean(sh_ces_series):.4f}")
print(f"Mean anomaly score a_CES: {np.mean(a_ces_series):.4f}")
print(f"Mean Φ_N^{(op)}: {np.mean(phi_n_op):.4f}")
print(f"Mean Φ_Δ^{(op)}: {np.mean(phi_delta_op):.4f}")
print(f"Mean MPC cost: {np.mean(cost_series):.4f}")