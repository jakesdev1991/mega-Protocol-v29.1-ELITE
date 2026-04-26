# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# Simulate HSA node with heavy-tailed entropy bursts
np.random.seed(42)
dt = 0.01
t = np.arange(0, 10, dt)
N = len(t)

# Conservative parameters (from your "repaired" analysis)
lambda_cons = 0.01
v = 250.0
I0 = 200.0
A = 50.0
omega = 20 * np.pi  # 10 Hz

I = I0 + A * np.sin(omega * t)
dI_dt = np.gradient(I, dt)
J_cons = -lambda_cons * (3 * I**2 - v**2) * dI_dt  # GB/s⁴

# Dissipative parameters: entropy production with Pareto bursts
kappa = 2e-4  # dissipative coupling
S_baseline = 2.8  # nats/s
burst_prob = 0.02  # heavy-tailed bursts

# Entropy production rate: baseline + Pareto bursts
dS_dt = np.ones(N) * S_baseline
for i in range(N):
    if np.random.random() < burst_prob:
        dS_dt[i] += np.random.pareto(1.5) * 15.0  # α=1.5 → infinite variance

# Entropy acceleration = second derivative
d2S_dt2 = np.gradient(dS_dt, dt)

# Dissipative jerk: J_diss = -κ * d²S/dt²
J_diss = -kappa * d2S_dt2

# Total jerk
J_total = J_cons + J_diss

# "Repaired" stability criteria (conservative only)
RMS_J_cons = np.sqrt(np.mean(J_cons**2))
max_J_cons = np.max(np.abs(J_cons))
J_crit = 1.2e7
cons_stable = RMS_J_cons < J_crit and max_J_cons < 3 * RMS_J_cons

# Total jerk stability
RMS_J_total = np.sqrt(np.mean(J_total**2))
max_J_total = np.max(np.abs(J_total))
total_stable = RMS_J_total < J_crit

print("=== CONSERVATIVE ANALYSIS (Your 'Repaired' Method) ===")
print(f"RMS(J_cons): {RMS_J_cons:.2e} GB/s⁴ (< {J_crit:.2e})? {RMS_J_cons < J_crit}")
print(f"max|J_cons|: {max_J_cons:.2e} GB/s⁴ (< 3×RMS)? {max_J_cons < 3 * RMS_J_cons}")
print(f"CONSERVATIVE VERDICT: {'STABLE' if cons_stable else 'UNSTABLE'}")

print("\n=== DISSIPATIVE REALITY (What You Missed) ===")
print(f"RMS(J_total): {RMS_J_total:.2e} GB/s⁴ (< {J_crit:.2e})? {RMS_J_total < J_crit}")
print(f"max|J_total|: {max_J_total:.2e} GB/s⁴")
print(f"Peak J_diss: {np.max(np.abs(J_diss)):.2e} GB/s⁴ (entropy burst)")
print(f"DISSIPATIVE VERDICT: {'STABLE' if total_stable else 'UNSTABLE — SHREDDING IMMINENT'}")

# Visualization
fig, axs = plt.subplots(4, 1, figsize=(12, 10), sharex=True)

axs[0].plot(t, I, color='blue', linewidth=1.5)
axs[0].set_ylabel("I(t) [GB/s]")
axs[0].set_title("HSA Node: Conservative Stability Masking Dissipative Catastrophe")
axs[0].grid(True, alpha=0.3)

axs[1].plot(t, dS_dt, color='orange', linewidth=1)
axs[1].set_ylabel("dS/dt [nats/s]")
axs[1].grid(True, alpha=0.3)

axs[2].plot(t, J_cons, color='green', linewidth=1.5, label='J_cons')
axs[2].axhline(J_crit, color='black', linestyle='--', label='J_crit')
axs[2].set_ylabel("J_cons [GB/s⁴]")
axs[2].legend()
axs[2].grid(True, alpha=0.3)

axs[3].plot(t, J_total, color='red', linewidth=1.5, label='J_total')
axs[3].fill_between(t, J_total, alpha=0.3, color='red')
axs[3].axhline(J_crit, color='black', linestyle='--', label='J_crit')
axs[3].set_ylabel("J_total [GB/s⁴]")
axs[3].set_xlabel("Time [s]")
axs[3].legend()
axs[3].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()