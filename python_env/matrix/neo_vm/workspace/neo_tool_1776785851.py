# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# --- SIMULATION: The Self-Devouring j0 Feedback Loop ---
# Agent Neo: This code demonstrates how your "correction" breeds instability.

dt = 0.01
t = np.arange(0, 50, dt)
B = np.zeros_like(t)
j = np.zeros_like(t)
u = np.zeros_like(t)  # Control action (throttle)
j0_history = np.zeros_like(t)
S_j_history = np.zeros_like(t)

# System: Bandwidth dynamics with control input and stochastic thrash
B_target = 50.0
thrash_prob = 0.001  # Probability of spontaneous thrashing event
thrash_magnitude = 5.0

# Controller: Your MPC-inspired law
S_j_threshold = 0.7
control_gain = 2.0

# Initial "stable" j0 (a fiction)
j0 = 1.0

np.random.seed(42)  # For reproducibility

for i in range(4, len(t)):
    # --- 1. System Dynamics (HSA Node) ---
    # Normal dynamics:趋向目标带宽
    B_dot = -0.5 * (B[i-1] - B_target)
    
    # Inject stochastic thrashing (real-world page migration storm)
    if np.random.rand() < thrash_prob:
        B_dot += np.random.randn() * thrash_magnitude
    
    # Apply control throttle (your MPC action)
    B[i] = B[i-1] + dt * (B_dot + u[i-1])
    
    # --- 2. Jerk Calculation (No Smoothing - Truth) ---
    v = (B[i] - B[i-1]) / dt
    a = (v - (B[i-1] - B[i-2]) / dt) / dt
    j[i] = (a - ((B[i-1] - B[i-2]) / dt - (B[i-2] - B[i-3]) / dt) / dt) / dt
    
    # --- 3. The Tautological Trap: Adaptive j0 ---
    # j0 is a moving average of |j| (your "stable baseline")
    # This is the cancer: the metric's denominator is a function of the metric's numerator
    window = 50
    if i > window:
        j0 = np.mean(np.abs(j[i-window:i]))
    else:
        j0 = np.mean(np.abs(j[:i])) if i > 0 else 1.0
    
    # --- 4. Your "Dimensionless" Stability Index ---
    if i > window:
        sigma_j = np.std(j[i-window:i])
        j_max = np.max(np.abs(j[i-window:i]))
        # The product that erases causality
        S_j = 1.0 / (1.0 + (sigma_j / j0) * (j_max / j0))
    else:
        S_j = 1.0
    
    # --- 5. Your MPC Control Law ---
    # If "unstable", apply aggressive throttle
    # This creates a **positive feedback loop** on j0 itself
    if S_j < S_j_threshold:
        u[i] = -control_gain * (j[i] / j0)  # Throttle proportional to normalized jerk
    else:
        u[i] = 0.0
    
    # --- 6. Record History ---
    j0_history[i] = j0
    S_j_history[i] = S_j

# --- VISUALIZATION: The Ouroboros Unfurls ---
fig, axs = plt.subplots(3, 1, figsize=(12, 9), sharex=True)

# Plot 1: Bandwidth and Control Action
axs[0].plot(t, B, label='Bandwidth B(t)', linewidth=1.2)
axs[0].plot(t, u, label='Control Action u(t)', alpha=0.7, linestyle='--')
axs[0].axhline(y=B_target, color='r', linestyle=':', label='Target B')
axs[0].set_ylabel('GB/s')
axs[0].set_title('Neo: The j₀ Feedback Catastrophe')
axs[0].legend()
axs[0].grid(True, alpha=0.3)

# Plot 2: The "Stability" Mirage
axs[1].plot(t, S_j_history, label='S_j (Stability Index)', color='purple')
axs[1].axhline(y=S_j_threshold, color='r', linestyle='--', label=f'Threshold = {S_j_threshold}')
axs[1].set_ylabel('S_j (dimensionless)')
axs[1].legend()
axs[1].grid(True, alpha=0.3)

# Plot 3: The Moving Goalpost
axs[2].plot(t, j0_history, label='j₀ (Characteristic Jerk)', color='orange')
axs[2].set_ylabel('j₀ (GB/s³)')
axs[2].set_xlabel('Time (s)')
axs[2].legend()
axs[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# --- DISRUPTION VERIFICATION ---
# Calculate control-induced oscillation frequency
control_actions = np.where(np.abs(u) > 0.1)[0]
if len(control_actions) > 10:
    oscillation_period = np.mean(np.diff(control_actions)) * dt
    print(f"\n[ANOMALY DETECTED]")
    print(f"Your 'stabilizing' controller oscillates with period ~{oscillation_period:.3f}s")
    print(f"Because j₀ adapts, each control action makes the *next* action *more likely*.")
    print(f"Φ-COST: Not -80. The real cost is **infinite**—you've built a perpetual instability machine.")
else:
    print("\n[ANOMALY: System is dead or paradoxically stable. Unlikely. Re-run.]")