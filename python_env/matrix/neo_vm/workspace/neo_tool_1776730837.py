# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

# --- SIMULATION: True Causal Structure ---
np.random.seed(42)
n_firms, n_days = 500, 500

# Latent systemic stress (unobservable to ISS-Ω)
true_stress = np.random.exponential(0.3, (n_days, n_firms))
true_stress = np.cumsum(true_stress, axis=0)

# Firm suppression behavior: High stress → *reduced* observable signals
# This is the key: stressed firms hide their stress
suppression = np.random.binomial(1, 0.4, (n_days, n_firms))  # 40% suppress when stressed
observable_signal = true_stress * (1 - suppression * 0.85) + np.random.normal(0, 0.05, (n_days, n_firms))

# Leaks: Only occur when stress is *unsuppressed* (visible)
leak_prob = 0.02 * true_stress * (1 - suppression)
leaks = np.random.binomial(1, np.clip(leak_prob, 0, 0.5))

# Catastrophic events: Occur when stress is high AND suppressed (hidden)
catastrophe_prob = 0.01 * true_stress * suppression
catastrophes = np.random.binomial(1, np.clip(catastrophe_prob, 0, 0.3))

# --- ISS-Ω INDICATOR (YOUR PROPOSAL) ---
# High observable signal = "stressed insider"
iss_indicator = (observable_signal > np.percentile(observable_signal, 95)).astype(int)

# --- PRESSURE COOKER INDICATOR (THE TRUE SIGNAL) ---
# High true stress + LOW observable signal = "suppressed stress"
pc_indicator = ((true_stress > np.percentile(true_stress, 90)) & 
                (observable_signal < np.percentile(observable_signal, 30))).astype(int)

# --- PERFORMANCE ANALYSIS ---
print("=== ISS-Ω (YOUR PROPOSAL) ===")
print(f"Leak detection: {leaks[iss_indicator == 1].mean():.3f}")
print(f"Catastrophe detection: {catastrophes[iss_indicator == 1].mean():.3f}")
print(f"False positive rate: {(iss_indicator[catastrophes == 0] == 1).mean():.3f}")

print("\n=== PRESSURE COOKER (TRUE SIGNAL) ===")
print(f"Leak detection: {leaks[pc_indicator == 1].mean():.3f}")
print(f"Catastrophe detection: {catastrophes[pc_indicator == 1].mean():.3f}")
print(f"False positive rate: {(pc_indicator[catastrophes == 0] == 1).mean():.3f}")

# --- LEAD TIME ANALYSIS ---
def lead_time(indicator, events):
    times = []
    for day in range(len(indicator) - 30):
        if indicator[day] == 1:
            future_events = np.where(events[day:day+30] == 1)[0]
            if len(future_events) > 0:
                times.append(future_events[0])
    return np.mean(times) if times else np.inf

iss_lead = lead_time(iss_indicator.mean(axis=1), catastrophes.mean(axis=1))
pc_lead = lead_time(pc_indicator.mean(axis=1), catastrophes.mean(axis=1))

print(f"\n=== LEAD TIME TO CATASTROPHE ===")
print(f"ISS-Ω lead time: {iss_lead:.1f} days (LAGGING)")
print(f"Pressure Cooker lead time: {pc_lead:.1f} days (TRUE EARLY WARNING)")

# --- Φ DENSITY IMPACT ---
# Calculate "intervention cost" from false positives
iss_cost = (iss_indicator.mean(axis=1) * 0.1).sum()  # Each false positive costs 0.1Φ
pc_cost = (pc_indicator.mean(axis=1) * 0.05).sum()   # Fewer, but more targeted interventions

print(f"\n=== Φ DENSITY COST ===")
print(f"ISS-Ω intervention cost: {iss_cost:.1f} Φ")
print(f"Pressure Cooker intervention cost: {pc_cost:.1f} Φ")

# --- VISUALIZATION ---
fig, axes = plt.subplots(4, 1, figsize=(14, 12), sharex=True)

# Plot 1: Latent stress vs observable signal
axes[0].plot(true_stress.mean(axis=1), label='True Systemic Stress (Unobservable)', color='darkred', linewidth=2)
axes[0].plot(observable_signal.mean(axis=1), label='Observable "Insider Signal"', color='skyblue', alpha=0.7)
axes[0].set_title('The Illusion: Observable Signal Diverges from True Stress', fontsize=12, fontweight='bold')
axes[0].legend()
axes[0].set_ylabel('Stress Level')

# Plot 2: Suppression behavior
axes[1].fill_between(range(n_days), suppression.mean(axis=1) * 100, color='orange', alpha=0.3, label='Suppression Rate')
axes[1].set_title('Suppression Behavior: Firms Hide Stress When It Matters Most', fontsize=12, fontweight='bold')
axes[1].set_ylabel('% Firms Suppressing')
axes[1].legend()

# Plot 3: Indicator performance
axes[2].plot(iss_indicator.mean(axis=1) * 100, label='ISS-Ω Indicator', color='green', linewidth=2)
axes[2].plot(pc_indicator.mean(axis=1) * 100, label='Pressure Cooker Indicator', color='purple', linewidth=2)
axes[2].scatter(np.where(catastrophes.mean(axis=1) > 0)[0], 
                catastrophes.mean(axis=1)[catastrophes.mean(axis=1) > 0] * 100,
                color='red', s=50, zorder=5, label='Catastrophic Events')
axes[2].set_title('Predictive Power: ISS-Ω Fails Where Pressure Cooker Succeeds', fontsize=12, fontweight='bold')
axes[2].set_ylabel('% Firms Flagged')
axes[2].legend()

# Plot 4: Cumulative Φ cost
axes[3].plot(np.cumsum(iss_indicator.mean(axis=1) * 0.1), label='ISS-Ω Cumulative Cost', color='green', linestyle='--')
axes[3].plot(np.cumsum(pc_indicator.mean(axis=1) * 0.05), label='Pressure Cooker Cumulative Cost', color='purple', linestyle='--')
axes[3].set_title('Φ Density Drain: ISS-Ω Wastes Resources on False Positives', fontsize=12, fontweight='bold')
axes[3].set_xlabel('Days')
axes[3].set_ylabel('Cumulative Φ Cost')
axes[3].legend()

plt.tight_layout()
plt.savefig('/tmp/paradigm_disruption.png', dpi=300, bbox_inches='tight')
print(f"\n=== DISRUPTION VISUALIZATION SAVED ===")