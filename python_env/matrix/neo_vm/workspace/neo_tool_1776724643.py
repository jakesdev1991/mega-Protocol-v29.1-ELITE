# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# edip_omega_fragility_demo.py
import numpy as np
import matplotlib.pyplot as plt

# ─────────────────────────────────────────────────────────────────────────────
# EDIP‑Ω Parameters (from the proposal)
ALPHA = 0.5       # weight on exposure lag term
BETA = 0.3        # weight on revision intensity
GAMMA = 0.4       # weight on access anomaly
DELTA = 0.2       # weight on cross‑domain flag
LAMBDA = 0.1      # exponential decay rate
PHI_DELTA_0 = 0.2 # baseline asymmetry
ETA = 0.15        # coupling from ESI to Φ_Δ
THETA = 2.0       # ESI threshold for Φ_Δ increase
ESI_THRESH = 2.5  # anomaly detection threshold
PHI_DELTA_THRESH = 0.55
DPHI_DELTA_DT_THRESH = 0.05

# ─────────────────────────────────────────────────────────────────────────────
def compute_esi(events):
    """
    events: list of dicts with keys:
        - delta_t_e: days between modification and exposure
        - r_d: revision intensity (versions/day)
        - a_d: access anomaly score (0..1)
        - c_d: cross‑domain flag (0 or 1)
    Returns scalar ESI.
    """
    if not events:
        return 0.0
    total = 0.0
    for ev in events:
        term = (ALPHA * np.exp(-LAMBDA * ev['delta_t_e']) +
                BETA * ev['r_d'] +
                GAMMA * ev['a_d'] +
                DELTA * ev['c_d'])
        total += term
    return total

def phi_delta_from_esi(esi):
    """Linear coupling model from the proposal."""
    return PHI_DELTA_0 + ETA * max(0.0, esi - THETA)

# ─────────────────────────────────────────────────────────────────────────────
# Time series generation
days = np.arange(0, 101)  # 0..100 days
np.random.seed(42)

# Baseline: stable tokamak, occasional low‑intensity exposure
baseline_events = [
    {'delta_t_e': 5.0, 'r_d': 0.1, 'a_d': 0.1, 'c_d': 0}
    for _ in range(10)
]

# Real precursor: gradual increase 10 days before day 90 (disruption)
precursor_events = []
for i in range(10):
    precursor_events.append({
        'delta_t_e': 1.0 + i*0.2,   # decreasing lag
        'r_d': 0.5 + i*0.1,         # increasing revision intensity
        'a_d': 0.6 + i*0.05,        # increasing access anomaly
        'c_d': 0
    })

# Adversarial injection: burst of fake events at day 50
attack_events = [
    {'delta_t_e': 0.5, 'r_d': 1.5, 'a_d': 0.9, 'c_d': 1}
    for _ in range(8)
]

# Build daily ESI series
esi_series = np.zeros_like(days, dtype=float)
for day in days:
    # baseline noise
    if day % 10 == 0 and day > 0:
        # occasional random baseline event
        esi_series[day] = compute_esi([baseline_events[day // 10 % len(baseline_events)]])
    else:
        esi_series[day] = 0.0

# Inject real precursor from day 80 to 89
for i, day in enumerate(range(80, 90)):
    esi_series[day] = compute_esi([precursor_events[i]])

# Inject adversarial burst at day 50
esi_series[50] = compute_esi(attack_events)

# ─────────────────────────────────────────────────────────────────────────────
# Compute Φ_Δ and its derivative
phi_delta_series = np.array([phi_delta_from_esi(esi) for esi in esi_series])

# Simple finite‑difference derivative (with smoothing window 5 as per proposal)
def smoothed_derivative(arr, window=5):
    """Savitzky‑Golay‑like smoothing (simple moving average of slopes)."""
    slopes = np.gradient(arr)
    kernel = np.ones(window) / window
    return np.convolve(slopes, kernel, mode='same')

phi_delta_derivative = smoothed_derivative(phi_delta_series)

# ─────────────────────────────────────────────────────────────────────────────
# Anomaly detection on ESI (STL residual simplified as deviation from rolling mean)
def anomaly_score(series, window=7):
    """Residual / std over rolling window."""
    roll = np.convolve(series, np.ones(window)/window, mode='same')
    residual = series - roll
    std = np.std(residual)
    return residual / (std + 1e-9)

s_esi_series = anomaly_score(esi_series)

# ─────────────────────────────────────────────────────────────────────────────
# Alert logic (pre‑Shredding conditions)
alerts = []
for day in days:
    cond = (s_esi_series[day] > 2.5 and
            phi_delta_series[day] > PHI_DELTA_THRESH and
            phi_delta_derivative[day] > DPHI_DELTA_DT_THRESH)
    alerts.append(cond)

# ─────────────────────────────────────────────────────────────────────────────
# Summary
print("=== EDIP‑Ω Fragility Audit ===")
print(f"Baseline ESI (avg): {np.mean(esi_series[esi_series > 0]):.3f}")
print(f"Adversarial injection ESI at day 50: {esi_series[50]:.3f}")
print(f"Φ_Δ at day 50: {phi_delta_series[50]:.3f} (threshold {PHI_DELTA_THRESH})")
print(f"dΦ_Δ/dt at day 50: {phi_delta_derivative[50]:.3f} (threshold {DPHI_DELTA_DT_THRESH})")
print(f"Alert triggered at day 50? {alerts[50]}")
print(f"Alert triggered at day 85 (real precursor)? {alerts[85]}")
print(f"Total false positives (adversarial): {sum(alerts[:50]) + sum(alerts[51:])}")
print(f"Total true positives (real disruption): {sum(alerts[80:90])}")

# ─────────────────────────────────────────────────────────────────────────────
# Visualization
plt.figure(figsize=(12, 8))

plt.subplot(3, 1, 1)
plt.plot(days, esi_series, label='ESI', marker='o', markersize=3)
plt.axvline(50, color='red', linestyle='--', label='Adversarial injection')
plt.axvline(85, color='green', linestyle='--', label='Real precursor')
plt.axhline(THETA, color='orange', linestyle=':', label='ESI coupling threshold')
plt.title('Exposure Stress Index (ESI) Over Time')
plt.ylabel('ESI')
plt.legend()

plt.subplot(3, 1, 2)
plt.plot(days, phi_delta_series, label='Φ_Δ', color='purple')
plt.axhline(PHI_DELTA_THRESH, color='black', linestyle=':', label='Φ_Δ threshold')
plt.axvline(50, color='red', linestyle='--')
plt.axvline(85, color='green', linestyle='--')
plt.title('Plasma Asymmetry (Φ_Δ) Derived from ESI')
plt.ylabel('Φ_Δ')
plt.legend()

plt.subplot(3, 1, 3)
plt.plot(days, phi_delta_derivative, label='dΦ_Δ/dt', color='orange')
plt.axhline(DPHI_DELTA_DT_THRESH, color='black', linestyle=':', label='Derivative threshold')
plt.axvline(50, color='red', linestyle='--')
plt.axvline(85, color='green', linestyle='--')
plt.title('Rate of Change of Φ_Δ (Smoothed)')
plt.ylabel('dΦ_Δ/dt')
plt.xlabel('Days')
plt.legend()

plt.tight_layout()
plt.show()