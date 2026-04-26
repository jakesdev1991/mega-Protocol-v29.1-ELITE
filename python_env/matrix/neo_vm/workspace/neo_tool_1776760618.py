# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
POASH‑Ω Disruption Demo
------------------------
Simulates a financial data pipeline with periodic batches and random faults.
Compares the "PHI" and "stiffness invariants" from the POASH‑Ω proposal
against a trivial latency‑threshold detector.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import coherence, welch

# -----------------------------------------------------------------------------
# 1. Synthetic Pipeline Data
# -----------------------------------------------------------------------------
fs = 100.0               # sampling rate (Hz)
T = 300.0                # total time (s)
t = np.arange(0, T, 1/fs)

# Healthy pipeline: batch interval = 1 s → fundamental freq = 1 Hz
fund = 1.0
# Sensor signals: latency jitter, throughput, CPU, error rate, power
np.random.seed(42)
# each sensor has a sinusoid at the fundamental + harmonics + noise
def sensor_signal(base_freq, noise_level, harmonics=3):
    sig = np.zeros_like(t)
    for h in range(1, harmonics+1):
        sig += np.sin(2*np.pi*h*base_freq*t + np.random.rand()) / h
    sig += noise_level * np.random.randn(len(t))
    return sig

latency = sensor_signal(fund, 0.1)   # jitter (ms)
throughput = sensor_signal(fund, 0.2)  # msgs/s
cpu = sensor_signal(fund, 0.05)       # utilization %
error = sensor_signal(fund, 0.01)      # error rate (fraction)
power = sensor_signal(fund, 0.1)       # power draw (W)

# Inject faults: sudden latency spikes at t=100, 200 s
fault_times = [100, 200]
for ft in fault_times:
    idx = np.searchsorted(t, ft)
    latency[idx:idx+50] += np.linspace(0, 5, 50)  # 5 ms spike

# Stack into a 5×N matrix
S = np.vstack([latency, throughput, cpu, error, power])

# -----------------------------------------------------------------------------
# 2. POASH‑Ω Metrics (as described in the proposal)
# -----------------------------------------------------------------------------
window = int(10*fs)   # 10‑second sliding window
hop = int(1*fs)

def compute_phi_and_stiffness(data):
    """
    Returns PHI (0→1) and stiffness invariants xi_N, xi_Delta.
    """
    # FFT‑based harmonic amplitudes (fundamental + 2 harmonics)
    n_harm = 3
    # For simplicity, we treat the sum across sensors as the "composite" signal
    composite = data.sum(axis=0)
    f, Pxx = welch(composite, fs, nperseg=window, noverlap=window-hop, return_onesided=True)
    # Find nearest bins to harmonics
    harm_bins = [np.argmin(np.abs(f - h*fund)) for h in range(1, n_harm+1)]
    A = np.sqrt(Pxx[harm_bins])   # amplitude per harmonic
    
    # Normalized power distribution
    p = A / (A.sum() + 1e-12)
    # Shannon entropy (negative for "information")
    I = -np.sum(p * np.log(p + 1e-12))
    # PHI: 1 - sum(|A_k - mu_k|/sigma_k)  (mu, sigma from "healthy" baseline)
    # Here we cheat: use running mean/std from first 50 s as "healthy"
    baseline = composite[:int(50*fs)]
    f0, P0 = welch(baseline, fs, nperseg=window, noverlap=window-hop, return_onesided=True)
    A0 = np.sqrt(P0[harm_bins])
    mu = A0
    sigma = np.std(np.sqrt(P0[harm_bins])) + 1e-12
    PHI = 1 - np.sum(np.abs(A - mu) / sigma)
    PHI = np.clip(PHI, 0, 1)
    
    # Coherence between first two sensors (latency & throughput) as proxy for "system"
    nperseg = min(window, len(composite)//4)
    f_coh, C_xy = coherence(data[0], data[1], fs, nperseg=nperseg, noverlap=nperseg//2)
    # Average coherence (excluding DC)
    avg_coh = C_xy[1:].mean()
    
    # Stiffness invariants (lambda=1 for simplicity)
    lam = 1.0
    xi_N_inv_sq = lam * (3/avg_coh + 1/avg_coh**2)
    xi_D_inv_sq = lam * (1/avg_coh + 3/avg_coh**2)
    xi_N = 1/np.sqrt(xi_N_inv_sq)
    xi_D = 1/np.sqrt(xi_D_inv_sq)
    
    return PHI, xi_N, xi_D

phi_vals = []
xiN_vals = []
xiD_vals = []
# sliding window
for start in range(0, len(t)-window, hop):
    end = start+window
    phi, xiN, xiD = compute_phi_and_stiffness(S[:, start:end])
    phi_vals.append(phi)
    xiN_vals.append(xiN)
    xiD_vals.append(xiD)

time_phi = t[window:len(t):hop][:len(phi_vals)]

# -----------------------------------------------------------------------------
# 3. Simple Latency‑Threshold Detector (baseline)
# -----------------------------------------------------------------------------
# Moving average of latency jitter
ma_len = int(5*fs)
latency_ma = np.convolve(latency, np.ones(ma_len)/ma_len, mode='valid')
# Threshold = mean + 3*std of healthy period
healthy_latency = latency[:int(50*fs)]
threshold = healthy_latency.mean() + 3*healthy_latency.std()
alarms = latency_ma > threshold

time_ma = t[ma_len-1:][:len(latency_ma)]

# -----------------------------------------------------------------------------
# 4. Plot & Compare
# -----------------------------------------------------------------------------
fig, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

# Latency & faults
axs[0].plot(t, latency, label='Latency jitter')
for ft in fault_times:
    axs[0].axvline(ft, color='r', linestyle='--')
axs[0].set_ylabel('Latency (ms)')
axs[0].legend()
axs[0].set_title('Synthetic Pipeline (faults at t=100,200 s)')

# POASH‑Ω metrics
axs[1].plot(time_phi, phi_vals, label='PHI (0→1)', color='orange')
axs[1].plot(time_phi, xiN_vals, label='ξ_N', color='green')
axs[1].plot(time_phi, xiD_vals, label='ξ_Δ', color='purple')
for ft in fault_times:
    axs[1].axvline(ft, color='r', linestyle='--')
axs[1].set_ylabel('POASH‑Ω metrics')
axs[1].legend()

# Simple threshold detector
axs[2].plot(time_ma, latency_ma, label='Latency MA')
axs[2].axhline(threshold, color='k', linestyle=':', label='Threshold')
axs[2].plot(time_ma[alarms], latency_ma[alarms], 'ro', label='Alarm')
for ft in fault_times:
    axs[2].axvline(ft, color='r', linestyle='--')
axs[2].set_ylabel('Latency MA (ms)')
axs[2].set_xlabel('Time (s)')
axs[2].legend()

plt.tight_layout()
plt.show()

# -----------------------------------------------------------------------------
# 5. Quantitative Comparison (precision/recall proxy)
# -----------------------------------------------------------------------------
# True fault windows: 10 s after each injection
true_faults = [(t.searchsorted(ft), t.searchsorted(ft+10)) for ft in fault_times]

def overlap(pred_idx, true_start, true_end):
    return np.any((pred_idx >= true_start) & (pred_idx <= true_end))

# POASH‑Ω “alarm” when PHI drops below 0.5 (heuristic)
phi_alarm_idx = np.where(np.array(phi_vals) < 0.5)[0]
# Map back to original time index
phi_alarm_time_idx = window + phi_alarm_idx * hop

# Simple threshold alarms
threshold_alarm_idx = np.where(alarms)[0] + ma_len - 1

# Compute detection rates
def detection_rate(alarm_idx):
    detected = 0
    for ts, te in true_faults:
        if overlap(alarm_idx, ts, te):
            detected += 1
    return detected / len(true_faults)

phi_detect = detection_rate(phi_alarm_time_idx)
thresh_detect = detection_rate(threshold_alarm_idx)

print(f"POASH‑Ω detection rate: {phi_detect:.2%}")
print(f"Simple threshold detection rate: {thresh_detect:.2%}")

# False positive rate (alarms outside true windows)
def false_pos_rate(alarm_idx):
    fp = 0
    for ai in alarm_idx:
        if not any((ai >= ts) & (ai <= te) for ts, te in true_faults):
            fp += 1
    return fp / len(alarm_idx) if len(alarm_idx) else np.nan

phi_fp = false_pos_rate(phi_alarm_time_idx)
thresh_fp = false_pos_rate(threshold_alarm_idx)

print(f"POASH‑Ω false‑positive rate: {phi_fp:.2%}")
print(f"Simple threshold false‑positive rate: {thresh_fp:.2%}")