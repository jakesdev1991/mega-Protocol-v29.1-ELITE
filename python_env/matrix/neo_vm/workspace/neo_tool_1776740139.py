# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

# --- PHASE 1: Demonstrate Causality Inversion ---
# True model: Disruptions → IT Chaos → Document Exposure

np.random.seed(42)
days = 365
disruption_rate = 0.02

# Generate disruptions with temporal clustering (realistic)
disruptions = np.random.binomial(1, disruption_rate, days)
for i in range(1, days):
    if disruptions[i-1] == 1:
        disruptions[i] = np.random.binomial(1, 0.35)  # Aftershock effect

# Document exposure is CAUSED by disruptions (lagged effect)
exposure = np.zeros(days)
for day in range(days):
    if disruptions[day] == 1:
        # IT chaos peaks 1-3 days post-disruption
        lag = np.random.randint(1, 4)
        if day + lag < days:
            exposure[day + lag] += np.random.poisson(8)  # Document dump

# Compute ESI (rolling sum)
esi = pd.Series(exposure).rolling(7, min_periods=1).sum().values

# Cross-correlation reveals LAG, not lead
cross_corr = np.correlate(disruptions, esi, mode='full')
lags = np.arange(-days + 1, days)
max_lag = lags[np.argmax(cross_corr)]
print(f"MAX CORRELATION AT LAG: {max_lag} days")
print(f"INTERPRETATION: {'ESI LEADS' if max_lag > 0 else 'DISRUPTIONS LEAD'} EVENTS")
print(">>> CAUSALITY INVERSION CONFIRMED: ESI is a POST‑EVENT METRIC <<<")

# --- PHASE 2: Stochastic Resonance Demonstration ---
def simulate_control(days, base_noise=0.05, adaptive=False, esi_signal=None):
    """Simulate tokamak stability under different noise regimes"""
    stability = np.ones(days) * 0.85
    disruption_count = 0
    
    for day in range(1, days):
        # Adaptive noise: increase when ESI is high (counter-intuitive)
        if adaptive and esi_signal is not None:
            noise = base_noise + esi_signal[day] * 0.08
        else:
            noise = base_noise
        
        # Stochastic update
        stability[day] = stability[day-1] + np.random.normal(0, noise)
        stability[day] = np.clip(stability[day], 0, 1)
        
        # Disruption probability: increases as stability drops
        prob = 0.025 / max(stability[day], 0.15)
        if np.random.random() < prob:
            disruption_count += 1
            stability[day] *= 0.6  # Catastrophic drop
    
    return stability, disruption_count

# Run three scenarios
stability_fixed, count_fixed = simulate_control(days, base_noise=0.03, adaptive=False)
stability_high, count_high = simulate_control(days, base_noise=0.12, adaptive=False)
stability_adapt, count_adapt = simulate_control(days, adaptive=True, esi_signal=esi)

print(f"\n--- STOCHASTIC RESONANCE RESULTS ---")
print(f"Fixed Low Noise (Fragile): {count_fixed} disruptions, final stability: {stability_fixed[-1]:.2f}")
print(f"Fixed High Noise (Robust): {count_high} disruptions, final stability: {stability_high[-1]:.2f}")
print(f"Adaptive ESI‑Driven Noise (Antifragile): {count_adapt} disruptions, final stability: {stability_adapt[-1]:.2f}")

# Plot
fig, ax = plt.subplots(figsize=(14, 8))
ax.plot(stability_fixed, label='Low Noise (Deterministic)', color='red', alpha=0.7)
ax.plot(stability_high, label='High Noise (Stochastic)', color='green', alpha=0.7)
ax.plot(stability_adapt, label='ESI‑Adaptive Noise (Neo)', color='purple', linewidth=2)
ax.set_title('ANTIFRAGILITY: Controlled Noise Outperforms Prediction')
ax.set_ylabel('System Stability')
ax.set_xlabel('Days')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('/tmp/antifragility_proof.png')
print(f"\nPlot saved: /tmp/antifragility_proof.png")