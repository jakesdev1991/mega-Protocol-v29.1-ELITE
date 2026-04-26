# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# --- PARAMETERS ---
np.random.seed(0)
T = 730  # days
phi_c = 0.5  # presentation threshold
lambda_param = 1.0
v = 1.0
sigma = 0.1  # baseline noise
sigma_crisis = 0.5  # noise during distress

# --- SIMULATE phi(t) WITH A GAMING ATTACK ---
dt = 1.0
t = np.arange(0, T, dt)
phi = np.zeros_like(t, dtype=float)

# Baseline: stable company for first 300 days
phi[:300] = v + sigma * np.random.randn(300)

# Distress phase: 60 days of high volatility, few presentations
phi[300:360] = 0.2 + sigma_crisis * np.random.randn(60)

# Gaming phase: management engineers perfect 30‑day intervals
# We directly inject a sinusoidal propensity with period 30 days
gaming_length = 300
gaming_start = 360
omega_gaming = 2 * np.pi / 30
phi[gaming_start:gaming_start + gaming_length] = (
    phi_c + 0.3 * np.sin(omega_gaming * np.arange(gaming_length))
    + 0.05 * np.random.randn(gaming_length)
)

# --- DETECT PRESENTATIONS ---
presentations = np.where(phi > phi_c)[0]  # indices where phi > threshold
intervals = np.diff(presentations)

# --- COMPUTE HEURISTIC CCS (as defined in original proposal) ---
def compute_ccs(intervals, window=90, cluster_days=7, total_days=365):
    if len(intervals) < 2:
        return 1.0
    # Use last 4 quarters of intervals
    recent = intervals[-window:]
    mu = np.mean(recent)
    sigma_interval = np.std(recent)
    # Cluster count: intervals <= cluster_days
    N_cluster = np.sum(recent <= cluster_days)
    regularity = np.exp(-sigma_interval / (mu + 1e-12))
    anti_cluster = np.exp(-N_cluster / total_days)
    return regularity * anti_cluster

ccs = compute_ccs(intervals)

# --- ENTROPY & JERK ---
def sliding_entropy(intervals, win=20, bins=np.arange(0, 181, 30)):
    if len(intervals) < win:
        return np.zeros(len(intervals))
    ent = np.zeros(len(intervals))
    for i in range(win, len(intervals)):
        hist, _ = np.histogram(intervals[i - win:i], bins=bins)
        p = hist / hist.sum()
        p = p[p > 0]
        ent[i] = -np.sum(p * np.log(p))
    return ent

S_h = sliding_entropy(intervals)
# Compute jerk as third finite difference (padding with zeros)
jerk = np.zeros_like(S_h)
jerk[3:] = np.diff(S_h, n=3)

# --- INVARIANTS (approximate) ---
# Approx phi0 as global mean, delta phi = phi - phi0
phi0 = np.mean(phi)
delta_phi = phi - phi0
omega = 2 * np.pi / 90  # quarterly

# Compute modes over last 180 days
window_inv = 180
if len(delta_phi) >= window_inv:
    Phi_N = np.mean(delta_phi[-window_inv:])
    Phi_D = np.mean(delta_phi[-window_inv:] * np.sin(omega * np.arange(window_inv)))
else:
    Phi_N = Phi_D = 0.0

# Invariants (using known lambda, v)
xi_N_sq_inv = lambda_param * (3 * Phi_N**2 + Phi_D**2 - v**2)
xi_D_sq_inv = lambda_param * (Phi_N**2 + 3 * Phi_D**2 - v**2)
xi_N = 1 / np.sqrt(xi_N_sq_inv) if xi_N_sq_inv > 0 else np.inf
xi_D = 1 / np.sqrt(xi_D_sq_inv) if xi_D_sq_inv > 0 else np.inf

# --- ANOMALY DETECTION (sign error) ---
xi_D_crit = 10.0  # heuristic threshold
# WRONG condition (as in proposal)
alarm_wrong = (np.abs(jerk[-1]) > 0.01) and (xi_D < xi_D_crit)
# CORRECT condition (should be >)
alarm_correct = (np.abs(jerk[-1]) > 0.01) and (xi_D > xi_D_crit)

# --- PRINT RESULTS ---
print(f"CCS (engineered regularity): {ccs:.3f} (close to 1 = 'healthy')")
print(f"Final jerk magnitude: {np.abs(jerk[-1]):.3e}")
print(f"Invariant xi_D (clustering decay): {xi_D:.2f} days")
print(f"Alarm with WRONG sign condition: {alarm_wrong}")
print(f"Alarm with CORRECT sign condition: {alarm_correct}")
print("\nThe gaming attack fooled the model: high CCS, low jerk, and xi_D just below the threshold.")
print("The wrong sign condition silences the alarm; the correct condition would fire, but only if the threshold is set to detect *large* xi_D.")