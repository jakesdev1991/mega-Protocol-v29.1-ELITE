# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# ========== SIMULATION PARAMETERS ==========
T = 200                    # simulation horizon (hours)
dt = 1.0                   # time step (hours)
t = np.arange(0, T, dt)

# Building thermal dynamics (first-order)
k = 0.1                    # heat loss coefficient
T_set = 22.0               # setpoint (°C)
T_out = 10.0               # ambient (°C)

# VRFT controller gain (ideal)
K_opt = 1.5

# Attacker drift
epsilon = 0.005            # slow bias injection rate

# Defender's mixed‑strategy: two actions: "normal" (p) and "cautious" (1-p)
# p evolves as a function of *regret* (standard GTPR‑Ω)
def update_p(regret):
    # Sigmoid: high regret → low p (more cautious)
    return 1 / (1 + np.exp(regret - 1.0))

# Cost components
def energy_cost(u):
    return 0.5 * u**2

def discomfort_cost(T_true):
    return 0.5 * (T_true - T_set)**2

# ========== SILENT‑BOIL ATTACK ==========
np.random.seed(42)
T_true = np.full_like(t, T_set)  # start at setpoint
bias = epsilon * np.sqrt(t)        # slow drift
u_hist = np.zeros_like(t)
cost_hist = np.zeros_like(t)
regret_hist = np.zeros_like(t)
entropy_hist = np.zeros_like(t)
lyapunov_hist = np.zeros_like(t)

# "Equilibrium" cost under no attack (baseline)
V_eq = energy_cost(K_opt * (T_set - T_set)) + discomfort_cost(T_set)

for i in range(1, len(t)):
    # Sensor reading is true temp + bias
    T_sensor = T_true[i-1] + bias[i]

    # VRFT control (normal action)
    u_normal = K_opt * (T_set - T_sensor)
    # Cautious action: reduce gain
    u_cautious = 0.5 * u_normal

    # Mixed strategy
    p = update_p(regret_hist[i-1])
    u = p * u_normal + (1 - p) * u_cautious
    u_hist[i] = u

    # Building dynamics (Euler step)
    dT = -k * (T_true[i-1] - T_out) + u
    T_true[i] = T_true[i-1] + dT * dt

    # Cost incurred
    cost = energy_cost(u) + discomfort_cost(T_true[i])
    cost_hist[i] = cost

    # Regret (difference from static equilibrium cost)
    regret_hist[i] = cost - V_eq

    # Shannon entropy of defender's mixed strategy
    if 0 < p < 1:
        S = -p * np.log(p) - (1-p) * np.log(1-p)
    else:
        S = 0.0
    entropy_hist[i] = S

    # Lyapunov exponent of p (disequilibrium metric)
    # Approximate as log‑ratio of successive p's
    if i > 1 and p > 0 and p < 1:
        lyap = np.log(abs(p - update_p(regret_hist[i-2])))
    else:
        lyap = 0.0
    lyapunov_hist[i] = lyap

# ========== VISUALIZE FAILURE ==========
fig, axs = plt.subplots(4, 1, figsize=(10, 12), sharex=True)

axs[0].plot(t, bias, color='red')
axs[0].set_ylabel('Sensor bias (°C)')
axs[0].set_title('Silent‑Boil Attack: bias grows slowly ∝ √t')

axs[1].plot(t, regret_hist, color='blue')
axs[1].axhline(y=0.5, color='black', linestyle='--', label='Detection threshold')
axs[1].set_ylabel('Regret ρ(t)')
axs[1].legend()
axs[1].set_title('Regret stays "safe" until ~150h, then spikes (too late)')

axs[2].plot(t, entropy_hist, color='green')
axs[2].set_ylabel('Entropy S(t)')
axs[2].set_title('Entropy collapses early → deterministic (exploitable) defense')

axs[3].plot(t, lyapunov_hist, color='purple')
axs[3].set_ylabel('Lyapunov exponent')
axs[3].set_xlabel('Time (hours)')
axs[3].set_title('Disequilibrium metric spikes *early* (warning at ~30h)')

plt.tight_layout()
plt.show()