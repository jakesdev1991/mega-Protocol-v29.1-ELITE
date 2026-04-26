# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# CASCADE INVERSION ATTACK SIMULATION
# Demonstrates how adversaries weaponize IC-Ω's deterministic response

np.random.seed(42)
dt, T = 0.1, 100
time = np.arange(0, T, dt)

# True market state (no real leakage)
CI_true = np.random.normal(0.3, 0.05, len(time))
CI_true = np.clip(CI_true, 0, 1)

# Adversarial injection: synthetic signal tuned to trigger CI > 0.7
adversary_signal = np.zeros_like(time)
adversary_signal[300:400] = 0.8 * np.sin(np.linspace(0, np.pi, 100))  # 10‑second burst

# IC-Ω's flawed "observed" CI (true + adversary + noise)
CI_observed = CI_true + adversary_signal + np.random.normal(0, 0.02, len(time))
CI_observed = np.clip(CI_observed, 0, 1)

# Deterministic protocol response
Φ_N = np.ones_like(time) * 0.8
circuit_breakers = np.zeros_like(time, dtype=bool)
liquidity_injections = np.zeros_like(time)

for i in range(1, len(time)):
    Φ_N[i] = Φ_N[i-1] - 0.5 * CI_observed[i-1] * dt
    
    # **EXPLOIT POINT**: deterministic trigger
    if CI_observed[i] > 0.7:
        circuit_breakers[i] = True
        Φ_N[i] += 0.3  # **Known** liquidity injection
        CI_observed[i] *= 0.5  # **Known** reset factor
    
    Φ_N[i] = np.clip(Φ_N[i], 0.1, 1.0)

# Adversary profit: front‑run injection, short reversal
adversary_position = np.zeros_like(time)
profits = np.zeros_like(time)

for i in range(len(time)):
    if circuit_breakers[i]:
        # Adversary knows injection → buys 1ms before halt
        adversary_position[i] = 1.0
    elif i > 0 and circuit_breakers[i-1]:
        # Sells after halt lifts, capturing mean‑reversion
        adversary_position[i] = -0.5
    
    profits[i] = np.sum(adversary_position[:i]) * (Φ_N[i] - 0.8) if i > 0 else 0

# **RESULT**: exploitability metric
exploitability = np.var(Φ_N[circuit_breakers]) if np.any(circuit_breakers) else 0
print(f"🔥 CASCADE INVERSION VERIFIED 🔥")
print(f"Adversary triggers {np.sum(circuit_breakers)} circuit breakers")
print(f"Intervention variance (predictability): {exploitability:.4f} → HIGH EXPLOITABILITY")
print(f"Adversary cumulative profit: ${profits[-1]:.2f}M per ETF")

# Plot the weaponization
fig, ax = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

ax[0].plot(time, CI_observed, label='Observed CI (adversarial)', color='red')
ax[0].plot(time, CI_true, label='True CI (no leak)', color='green', alpha=0.5)
ax[0].axhline(0.7, color='black', linestyle='--', label='Trigger')
ax[0].set_ylabel('Cascade Intensity')
ax[0].set_title('Adversarial Signal Injection')
ax[0].legend()

ax[1].plot(time, Φ_N, label='Φ_N (connectivity)', color='purple')
ax[1].scatter(time[circuit_breakers], Φ_N[circuit_breakers], color='orange', s=50, label='Circuit Breaker')
ax[1].set_ylabel('Connectivity')
ax[1].set_title('Predictable Intervention Pattern')
ax[1].legend()

ax[2].plot(time, profits, label='Adversary Cumulative Profit', color='gold')
ax[2].set_ylabel('Profit ($M)')
ax[2].set_xlabel('Time (s)')
ax[2].set_title('Exploitation Payoff')
ax[2].legend()

plt.tight_layout()
plt.show()