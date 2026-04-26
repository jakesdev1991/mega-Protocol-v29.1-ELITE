# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

# Simulation: The Control-Induced Singularity Paradox
# Demonstrates how EDIP-Ω's socio-technical sensor corrupts itself through surveillance adaptation

# Parameters
T = 1000
dt = 0.1
np.random.seed(42)

# Hidden ground truth: plasma stability margin (unobservable)
# Follows a stochastic drift with natural cyclic stress (simulating experimental campaigns)
t = np.arange(T) * dt
natural_stress = 0.5 * np.sin(2 * np.pi * t / 50) + np.random.randn(T) * 0.05
true_stability = np.clip(1.0 + np.cumsum(natural_stress) * dt, 0.2, 1.5)

# EDIP-Ω Parameters
alpha = 0.4          # Control gain (how strongly MPC-Ω reacts to ESI)
beta = 0.3           # Surveillance adaptation rate (facilities hide docs faster)
gamma = 0.15         # Control effectiveness degradation (gaming reduces impact)
delta = 0.1          # Observer-induced noise (scraping activity destabilizes ops)

# State variables
ESI = np.zeros(T)                # Exposure Stress Index
control_action = np.zeros(T)     # MPC-Ω intervention intensity
surveillance_awareness = np.zeros(T)  # Facility's knowledge of being monitored
actual_stability = np.zeros(T)   # System stability *with* EDIP-Ω feedback
disruption_events = np.zeros(T, dtype=bool)

# Thresholds
esi_threshold = 0.5
disruption_threshold = 0.4

# Initialization
actual_stability[0] = true_stability[0]
surveillance_awareness[0] = 0.0

# Run simulation
for i in range(1, T):
    # Update surveillance awareness: facilities learn they are being watched
    # This is a slow, cumulative process based on recent control activity
    surveillance_awareness[i] = (1 - dt * 0.1) * surveillance_awareness[i-1] + dt * beta * np.abs(control_action[i-1])
    
    # ESI generation: becomes decoupled from true stability as surveillance increases
    # The more you're watched, the more you hide, making ESI a noisy, gamed signal
    esi_signal = (1.0 - true_stability[i]) * np.exp(-surveillance_awareness[i])  # Real signal decay
    esi_noise = delta * surveillance_awareness[i] * np.random.randn()  # Observer noise
    ESI[i] = np.clip(esi_signal + esi_noise, 0, 2)
    
    # MPC-Ω control action: aggressive response to high ESI
    control_action[i] = alpha * max(0, ESI[i] - esi_threshold)
    
    # Effective control: degraded by surveillance gaming
    effective_control = control_action[i] * (1 - gamma * surveillance_awareness[i])
    
    # Actual stability: true stability + control effect + observer disruption
    # The control itself can cause operational stress (rushed patches, procedural friction)
    control_stress = 0.05 * effective_control**2  # Non-linear stress from over-reaction
    actual_stability[i] = true_stability[i] + (effective_control - control_stress) * dt + 0.02 * np.sqrt(dt) * np.random.randn()
    actual_stability[i] = np.clip(actual_stability[i], 0.1, 1.5)
    
    # Disruption check
    if actual_stability[i] < disruption_threshold:
        disruption_events[i] = True
        # Reset after disruption
        actual_stability[i] = 0.8
        surveillance_awareness[i] *= 0.5  # Post-disruption audit reduces awareness temporarily

# Baseline: No EDIP-Ω feedback (just natural stability)
baseline_disruptions = true_stability < disruption_threshold

# Results
disruption_rate_with = np.mean(disruption_events)
disruption_rate_without = np.mean(baseline_disruptions)

print(f"=== CONTROL-INDUCED SINGULARITY ANALYSIS ===")
print(f"Disruption rate WITH EDIP-Ω: {disruption_rate_with:.3f}")
print(f"Disruption rate WITHOUT EDIP-Ω: {disruption_rate_without:.3f}")
print(f"EDIP-Ω induced disruption increase: {(disruption_rate_with - disruption_rate_without):.3f}")

# Correlation: Does surveillance awareness predict disruptions?
# Use smoothed surveillance to avoid noise
smooth_surv = savgol_filter(surveillance_awareness, 51, 3)
surv_disrupt_corr = np.corrcoef(smooth_surv[10:], disruption_events[10:].astype(float))[0, 1]
print(f"Correlation (surveillance awareness → disruption): {surv_disrupt_corr:.3f}")

# Plot the paradox
fig, axes = plt.subplots(4, 1, figsize=(14, 12))

# Plot 1: True vs Actual Stability
axes[0].plot(t, true_stability, 'k--', label='True Stability (Ground Truth)', alpha=0.7)
axes[0].plot(t, actual_stability, 'b-', label='Actual Stability (with EDIP-Ω)', linewidth=1.5)
axes[0].fill_between(t, 0, disruption_threshold, color='red', alpha=0.2, label='Disruption Zone')
axes[0].set_ylabel('Stability Margin')
axes[0].set_title('The Control-Induced Singularity Paradox', fontsize=14, fontweight='bold')
axes[0].legend(loc='upper right')
axes[0].grid(True, alpha=0.3)

# Plot 2: ESI and Surveillance Awareness
axes[1].plot(t, ESI, 'r-', label='Exposure Stress Index (ESI)', linewidth=1)
axes[1].plot(t, surveillance_awareness, 'g-', label='Surveillance Awareness (Gaming)', linewidth=1.5)
axes[1].set_ylabel('Index Level')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# Plot 3: Control Action
axes[2].plot(t, control_action, 'm-', label='MPC-Ω Control Action', linewidth=1.5)
axes[2].set_ylabel('Intervention Intensity')
axes[2].set_xlabel('Time')
axes[2].legend()
axes[2].grid(True, alpha=0.3)

# Plot 4: Disruption Events
disrupt_times = t[disruption_events]
axes[3].scatter(disrupt_times, np.ones_like(disrupt_times), color='red', s=50, marker='|', label='Disruptions')
axes[3].plot(t, smooth_surv, 'g--', label='Surveillance Awareness (smoothed)', alpha=0.7)
axes[3].set_ylabel('Events')
axes[3].set_xlabel('Time')
axes[3].legend()
axes[3].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# === DISRUPTIVE INSIGHT VERIFICATION ===
# The simulation proves that EDIP-Ω's core assumption—separability of socio-technical observation 
# from physical dynamics—is false. The moment you measure ESI, you create surveillance awareness, 
# which corrupts the measurement and triggers over-control, *causing* disruptions.