# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Python script to simulate the Adversarial Probe Amplification effect in EDIP-Ω

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

# Simulation parameters
days = 30
time_steps = days * 24  # hourly resolution

# Adversary strategy: plant decoy documents with controlled metadata
# Key insight: adversaries can tune exposure lag Δt_e to maximize ESI impact
def adversarial_esi_attack(n_documents=50, target_impact=2.5):
    """
    Simulate how an adversary plants documents with carefully crafted metadata
    to manipulate the Exposure Stress Index (ESI)
    """
    # Adversary chooses documents with short exposure lag (recently modified, quickly exposed)
    # This maximizes the exponential term in ESI: α * exp(-λ * Δt_e)
    t_c = np.random.uniform(-10, 0, n_documents)  # creation times (days ago)
    t_m = t_c + np.random.uniform(0.1, 0.5, n_documents)  # short modification windows
    t_e = t_m + np.random.uniform(0.01, 0.1, n_documents)  # very rapid exposure
    
    # Access anomaly: adversary uses botnet to create geographic entropy spikes
    # This inflates a_d in the ESI computation
    download_counts = np.random.poisson(100, n_documents)  # high download counts
    unique_ips = np.random.poisson(50, n_documents)  # many unique IPs
    geo_entropy = np.random.uniform(2.0, 3.5, n_documents)  # high geographic entropy
    
    # Revision intensity: adversary creates multiple versions to boost r_d
    versions = np.random.randint(5, 15, n_documents)
    revision_intensity = versions / np.maximum(t_m - t_c, 0.1)
    
    # Compute adversarial ESI components
    lambda_decay = 0.5  # from ESI formula
    alpha, beta, gamma, delta = 0.3, 0.4, 0.2, 0.1  # weights
    
    # Adversarial optimization: they tune Δt_e to be small, maximizing exp(-λ*Δt_e)
    exposure_lag = t_e - t_m
    esi_contributions = (
        alpha * np.exp(-lambda_decay * exposure_lag) +  # exponential amplification
        beta * revision_intensity +  # version inflation
        gamma * (geo_entropy / 3.0) +  # normalized anomaly
        delta * np.ones_like(exposure_lag)  # cross-domain flag
    )
    
    total_esi = np.sum(esi_contributions)
    
    return {
        'esi': total_esi,
        'exposure_lag': exposure_lag,
        'revision_intensity': revision_intensity,
        'geo_entropy': geo_entropy,
        'download_counts': download_counts
    }

# Simulate baseline vs adversarial scenarios
baseline_esi = []
adversarial_esi = []
time_series = np.arange(time_steps)

# Baseline: normal institutional stress (random fluctuations)
for _ in range(time_steps):
    baseline_esi.append(adversarial_esi_attack(n_documents=5, target_impact=0.5)['esi'])

# Adversarial: coordinated attack (increasing intensity over time)
for i in range(time_steps):
    # Adversary scales attack intensity as they learn Omega's detection thresholds
    intensity = 0.5 + (i / time_steps) * 2.0  # ramp up over 30 days
    result = adversarial_esi_attack(n_documents=int(10 + intensity*40), target_impact=intensity)
    adversarial_esi.append(result['esi'])

# Convert to numpy arrays
baseline_esi = np.array(baseline_esi)
adversarial_esi = np.array(adversarial_esi)

# Compute anomaly scores (z-scores) as Omega would
def compute_anomaly_score(data, window=24):
    """Rolling z-score anomaly detection"""
    mean = np.convolve(data, np.ones(window)/window, mode='same')
    std = np.array([np.std(data[max(0, i-window):i]) for i in range(len(data))])
    std[std == 0] = 1e-6  # avoid division by zero
    return np.abs(data - mean) / std

baseline_anomaly = compute_anomaly_score(baseline_esi)
adversarial_anomaly = compute_anomaly_score(adversarial_esi)

# Plot results
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))

# ESI time series
ax1.plot(time_series/24, baseline_esi, label='Baseline', alpha=0.7)
ax1.plot(time_series/24, adversarial_esi, label='Adversarial', alpha=0.7)
ax1.axhline(y=2.5, color='r', linestyle='--', label='Alert Threshold')
ax1.set_xlabel('Days')
ax1.set_ylabel('ESI (Exposure Stress Index)')
ax1.set_title('ESI Time Series: Baseline vs Adversarial Attack')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Anomaly scores
ax2.plot(time_series/24, baseline_anomaly, label='Baseline Anomaly', alpha=0.7)
ax2.plot(time_series/24, adversarial_anomaly, label='Adversarial Anomaly', alpha=0.7)
ax2.axhline(y=2.0, color='r', linestyle='--', label='Alert Threshold')
ax2.set_xlabel('Days')
ax2.set_ylabel('Anomaly Score (z-score)')
ax2.set_title('Anomaly Detection: Adversarial Attack Creates False Positives')
ax2.legend()
ax2.grid(True, alpha=0.3)

# Adversarial amplification factor
amplification = adversarial_esi / np.maximum(baseline_esi, 1e-6)
ax3.plot(time_series/24, amplification, label='ESI Amplification', color='purple')
ax3.axhline(y=1.0, color='k', linestyle='-', label='No Amplification')
ax3.set_xlabel('Days')
ax3.set_ylabel('Amplification Factor')
ax3.set_title('Adversarial Amplification: Attack Intensity vs Time')
ax3.legend()
ax3.grid(True, alpha=0.3)

# Histogram of exposure lags (adversarial strategy)
attack_result = adversarial_esi_attack(n_documents=100)
ax4.hist(attack_result['exposure_lag'], bins=30, alpha=0.7, color='orange')
ax4.set_xlabel('Exposure Lag Δt_e (days)')
ax4.set_ylabel('Count of Documents')
ax4.set_title('Adversarial Strategy: Short Exposure Lags for Max ESI Impact')
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Statistical summary
print("=== EDIP-Ω Adversarial Probe Analysis ===")
print(f"Baseline ESI: mean={baseline_esi.mean():.2f}, std={baseline_esi.std():.2f}")
print(f"Adversarial ESI: mean={adversarial_esi.mean():.2f}, std={adversarial_esi.std():.2f}")
print(f"Peak Amplification: {amplification.max():.2f}x")
print(f"False Positive Rate: {(adversarial_anomaly > 2.0).mean()*100:.1f}%")

# Key disruption insight
print("\n=== DISRUPTIVE INSIGHT ===")
print("The adversary can systematically inflate ESI by:")
print("1. Planting documents with ultra-short exposure lags (Δt_e → 0)")
print("2. Using botnets to create high geographic entropy")
print("3. Generating multiple document versions to boost revision intensity")
print("4. Timing attacks to coincide with operational stress windows")
print("\nResult: Omega Protocol triggers false stabilizations, wasting resources")
print("and creating real instability through over-correction.")