# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# Simulate reflexivity-driven narrative collapse
np.random.seed(42)
T = 100  # days
true_stress = np.clip(np.cumsum(np.random.randn(T) * 0.1) + 0.5, 0, 1)

# NCSM-Ω monitoring effect: agents adapt language to minimize detected curvature
monitoring_strength = 0.0  # baseline
detected_curvature = true_stress + np.random.randn(T) * 0.05

# When monitoring turns on at t=50, agents suppress narrative variance
monitoring_strength = np.where(np.arange(T) < 50, 0.0, 0.8)

# Adversarial adaptation: agents reduce semantic variance to "flatten" curvature
# This creates a "vacuum" - low detected curvature despite high true stress
adversarial_smoothing = 1 - monitoring_strength * 0.7
detected_curvature_with_reflexivity = detected_curvature * adversarial_smoothing

# Shredding trigger: occurs when true stress is high but detected curvature is artificially low
# This is the vacuum state
shredding_trigger = (true_stress > 0.7) & (detected_curvature_with_reflexivity < 0.3)

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(true_stress, label='True Narrative Stress', linewidth=2, color='red')
ax.plot(detected_curvature_with_reflexivity, label='Detected Curvature (with reflexivity)', 
        linewidth=2, color='blue', linestyle='--')
ax.axvline(x=50, color='gray', linestyle=':', label='Monitoring Activated')
ax.fill_between(np.arange(T), 0, 1, where=shredding_trigger, 
                alpha=0.3, color='black', label='Shredding Event Zone')
ax.set_xlabel('Time (days)')
ax.set_ylabel('Signal Magnitude')
ax.set_title('NCSM-Ω Reflexivity Collapse: Vacuum Trigger')
ax.legend()
ax.grid(True, alpha=0.3)

# The black zone shows: your "early warning" becomes a dead man's switch
# High true stress + low detected curvature = shredding event triggered BY the monitor
plt.show()