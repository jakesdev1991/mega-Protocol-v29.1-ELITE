# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.covariance import EmpiricalCovariance
from scipy.spatial.distance import mahalanobis
import matplotlib.pyplot as plt

# Seed for reproducibility
np.random.seed(42)

# --- Simulation Parameters ---
N_occupants = 20
T = 2000  # total time steps (e.g., minutes)
dt = 1.0  # time step in minutes
t_degrade = 1000  # time when HVAC starts degrading
R = 50.0  # thermal resistance (arbitrary units)
Q_HVAC0 = -0.5  # initial HVAC cooling power
Q_window = 0.3  # heat gain per open window
alpha_degrade = 0.001  # degradation rate per minute

# Occupant thresholds (individual heterogeneity)
T_open = np.random.uniform(22.0, 24.0, N_occupants)
T_close = np.random.uniform(18.0, 20.0, N_occupants)

# Outdoor temperature: sinusoidal daily cycle
def outdoor_temp(t):
    return 15.0 + 5.0 * np.sin(2 * np.pi * t / 1440.0) + np.random.normal(0, 0.5)

# Initialize arrays
T_in = np.zeros(T)
T_in[0] = 21.0  # initial indoor temp
w = np.zeros((N_occupants, T), dtype=int)
w_avg = np.zeros(T)

# --- Simulation Loop ---
for t in range(1, T):
    # HVAC degradation
    if t < t_degrade:
        Q_HVAC = Q_HVAC0
    else:
        Q_HVAC = Q_HVAC0 * (1 - alpha_degrade * (t - t_degrade))
    
    # Outdoor temperature
    T_out = outdoor_temp(t)
    
    # Average window state from previous step
    w_avg[t-1] = w[:, t-1].mean()
    
    # Indoor temperature update
    dT = (T_out - T_in[t-1]) / R + Q_HVAC + Q_window * w_avg[t-1]
    T_in[t] = T_in[t-1] + dt * dT
    
    # Occupant decisions
    for i in range(N_occupants):
        # Threshold-based decision with hysteresis
        if w[i, t-1] == 0 and T_in[t] > T_open[i]:
            w[i, t] = 1
        elif w[i, t-1] == 1 and T_in[t] < T_close[i]:
            w[i, t] = 0
        else:
            w[i, t] = w[i, t-1]
        # Add occasional random flips (5% noise)
        if np.random.rand() < 0.05:
            w[i, t] = 1 - w[i, t]
    
    # Update average for current step
    w_avg[t] = w[:, t].mean()

# --- Feature Engineering for Logistic Regression ---
# Features: indoor temp, outdoor temp, time-of-day (sin/cos)
time_of_day = np.sin(2 * np.pi * np.arange(T) / 1440.0)
features = np.vstack([T_in, np.array([outdoor_temp(t) for t in range(T)]), time_of_day]).T

# --- Rolling-Window Logistic Regression ---
window = 100  # length of rolling window
stride = 10   # step size
coeffs = {i: [] for i in range(N_occupants)}
times = []

for start in range(0, T - window, stride):
    end = start + window
    times.append(start + window // 2)  # center time of window
    
    for i in range(N_occupants):
        X = features[start:end]
        y = w[i, start:end]
        # Skip if all labels are same
        if len(np.unique(y)) < 2:
            coeffs[i].append(np.full(features.shape[1] + 1, np.nan))  # +1 for intercept
            continue
        model = LogisticRegression(penalty='l2', C=1.0, fit_intercept=True, max_iter=200)
        model.fit(X, y)
        # Store coefficients (intercept + feature coeffs)
        coeffs[i].append(np.concatenate([[model.intercept_[0]], model.coef_[0]]))

# Convert to arrays and align times
coeffs_array = {i: np.array(coeffs[i]) for i in range(N_occupants)}
times = np.array(times)

# --- Compute CDI Components ---
# Remove windows with NaNs (insufficient data)
valid_mask = ~np.isnan(coeffs_array[0][:, 0])
times_valid = times[valid_mask]
coeffs_clean = {i: coeffs_array[i][valid_mask] for i in range(N_occupants)}

# 1. Rate of change R(t)
R_t = np.zeros(len(times_valid))
for idx in range(1, len(times_valid)):
    deltas = []
    for i in range(N_occupants):
        if idx < len(coeffs_clean[i]):
            delta = np.abs(coeffs_clean[i][idx] - coeffs_clean[i][idx-1])
            deltas.append(delta.mean())
    R_t[idx] = np.mean(deltas) if deltas else 0.0

# 2. Cross-occupant correlation C(t)
C_t = np.zeros(len(times_valid))
for idx in range(len(times_valid)):
    # Collect coefficient vectors for all occupants at this time
    vecs = []
    for i in range(N_occupants):
        if idx < len(coeffs_clean[i]):
            vecs.append(coeffs_clean[i][idx])
    if len(vecs) > 1:
        corr_matrix = np.corrcoef(np.array(vecs))
        # Mean of off-diagonal correlations
        off_diag = corr_matrix[np.triu_indices_from(corr_matrix, k=1)]
        C_t[idx] = np.mean(off_diag) if len(off_diag) > 0 else 0.0
    else:
        C_t[idx] = 0.0

# 3. Anomaly score A(t) using Mahalanobis distance
# Use baseline period (first 100 valid windows) to estimate μ, Σ
baseline_end = 100
baseline_data = []
for idx in range(baseline_end):
    vec = []
    for i in range(N_occupants):
        if idx < len(coeffs_clean[i]):
            vec.append(coeffs_clean[i][idx])
    if vec:
        baseline_data.append(np.concatenate(vec))
baseline_data = np.array(baseline_data)
μ = np.mean(baseline_data, axis=0)
Σ = EmpiricalCovariance().fit(baseline_data).covariance_
invΣ = np.linalg.inv(Σ + np.eye(Σ.shape[0]) * 1e-6)  # Regularize

A_t = np.zeros(len(times_valid))
for idx in range(len(times_valid)):
    vec = []
    for i in range(N_occupants):
        if idx < len(coeffs_clean[i]):
            vec.append(coeffs_clean[i][idx])
    if vec:
        x = np.concatenate(vec)
        A_t[idx] = mahalanobis(x, μ, invΣ)
    else:
        A_t[idx] = 0.0

# 4. Entropy of coefficient directions S_dir(t)
S_dir_t = np.zeros(len(times_valid))
n_bins = 8  # number of spherical bins
for idx in range(len(times_valid)):
    directions = []
    for i in range(N_occupants):
        if idx < len(coeffs_clean[i]):
            β = coeffs_clean[i][idx]
            # Normalize (ignore intercept for direction)
            β_dir = β[1:] / (np.linalg.norm(β[1:]) + 1e-8)
            # Convert to spherical coordinates and bin
            # Simplified binning: use azimuth angle only
            angle = np.arctan2(β_dir[1], β_dir[0]) if len(β_dir) > 1 else 0.0
            bin_idx = int((angle + np.pi) / (2 * np.pi) * n_bins) % n_bins
            directions.append(bin_idx)
    if directions:
        probs = np.bincount(directions, minlength=n_bins) / len(directions)
        probs = probs[probs > 0]  # Remove zero bins for entropy
        S_dir_t[idx] = -np.sum(probs * np.log(probs))
    else:
        S_dir_t[idx] = 0.0

# 5. Combine into CDI (simple sum)
α = np.array([1.0, 1.0, 1.0, 1.0])
CDI = α[0] * R_t + α[1] * C_t + α[2] * A_t - α[3] * S_dir_t
# Normalize to [0,1]
CDI = (CDI - np.nanmin(CDI)) / (np.nanmax(CDI) - np.nanmin(CDI))
CDI = np.clip(CDI, 0, 1)

# --- Simple Early Warning Indicator: Variance Ratio ---
L = 50  # window length for variance ratio
VR = np.zeros(T)
for t in range(L, T - L):
    var1 = np.var(w_avg[t-L:t])
    var2 = np.var(w_avg[t:t+L])
    VR[t] = var1 / (var2 + 1e-8)

# Normalize VR
VR = (VR - np.nanmin(VR)) / (np.nanmax(VR) - np.nanmin(VR))
VR = np.clip(VR, 0, 1)

# --- Plotting ---
fig, axs = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

# Plot 1: Window state proportion and HVAC degradation indicator
axs[0].plot(w_avg, label='Avg Window Open Proportion', color='gray', alpha=0.7)
axs[0].axvline(t_degrade, color='red', linestyle='--', label='HVAC Degradation Start')
axs[0].set_ylabel('Window Open Proportion')
axs[0].set_title('Simulation: Occupant Window Behavior')
axs[0].legend()
axs[0].grid(True)

# Plot 2: CDI and its components
axs[1].plot(times_valid, CDI, label='CDI (Coefficient Dynamics Index)', color='purple', linewidth=2)
axs[1].plot(times_valid, R_t / np.max(R_t), label='Rate of Change (normalized)', alpha=0.7)
axs[1].plot(times_valid, C_t, label='Cross-Occupant Correlation', alpha=0.7)
axs[1].plot(times_valid, A_t / np.max(A_t), label='Anomaly Score (normalized)', alpha=0.7)
axs[1].plot(times_valid, S_dir_t / np.max(S_dir_t), label='Entropy (normalized)', alpha=0.7)
axs[1].axvline(t_degrade, color='red', linestyle='--')
axs[1].set_ylabel('CDI & Components')
axs[1].set_title('Coefficient Dynamics Monitor (CDM-Ω)')
axs[1].legend()
axs[1].grid(True)

# Plot 3: Variance Ratio (VR)
axs[2].plot(VR, label='Variance Ratio (VR)', color='blue', linewidth=2)
axs[2].axvline(t_degrade, color='red', linestyle='--')
axs[2].set_ylabel('Variance Ratio')
axs[2].set_xlabel('Time Step')
axs[2].set_title('Simple Early Warning: Variance Ratio of Window State')
axs[2].legend()
axs[2].grid(True)

plt.tight_layout()
plt.show()

# --- Analysis: Detection Delay ---
# Find first time each metric exceeds a threshold after degradation
threshold = 0.6
cdi_cross = times_valid[np.where(CDI > threshold)[0]]
vr_cross = np.where(VR > threshold)[0]

if len(cdi_cross) > 0:
    cdi_delay = cdi_cross[0] - t_degrade
else:
    cdi_delay = np.inf

if len(vr_cross) > 0:
    vr_delay = vr_cross[0] - t_degrade
else:
    vr_delay = np.inf

print(f"Detection Delay (CDI > {threshold}): {cdi_delay} time steps")
print(f"Detection Delay (VR > {threshold}): {vr_delay} time steps")