# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# Simulate HISS-Ω vulnerability: Sybil manipulation of Kuramoto order parameter
# Assumptions: 100 legitimate LPs, adversary controls N_sybil addresses

np.random.seed(42)
blocks = np.arange(0, 50)
legitimate_LPs = 100

# Legitimate LPs: random phases, low natural synchronization
theta_legit = np.random.uniform(0, 2*np.pi, legitimate_LPs)

# Adversary injects Sybil "withdrawal intents" at block 20
sybil_attack_block = 20
N_sybil = 5000  # 50x Sybil amplification

# Kuramoto order parameter calculation
def compute_r(thetas):
    return np.abs(np.sum(np.exp(1j * thetas))) / len(thetas)

r_history = []
for block in blocks:
    if block < sybil_attack_block:
        # Normal operation: r ~ 0.1 (desynchronized)
        theta_current = theta_legit
    else:
        # Sybil attack: all Sybils submit identical withdrawal intents
        # This simulates 5000 fake oscillators with phase = π (mass exit)
        theta_sybil = np.full(N_sybil, np.pi)
        theta_current = np.concatenate([theta_legit, theta_sybil])
    
    r = compute_r(theta_current)
    r_history.append(r)

# Plot
plt.figure(figsize=(10, 6))
plt.axvline(x=sybil_attack_block, color='red', linestyle='--', label='Sybil Attack')
plt.plot(blocks, r_history, linewidth=2)
plt.xlabel('Block Number')
plt.ylabel('Kuramoto Order Parameter r(t)')
plt.title('HISS-Ω Vulnerability: Sybil Attack Spoofing Synchronization')
plt.legend()
plt.grid(True)
plt.show()

# Calculate false positive impact
baseline_r = np.mean(r_history[:sybil_attack_block])
attack_r = np.mean(r_history[sybil_attack_block:])
print(f"Baseline r(t): {baseline_r:.3f}")
print(f"Attack r(t): {attack_r:.3f}")
print(f"False Synchronization Amplification: {attack_r/baseline_r:.1f}x")
print(f"SFI would trigger at >0.68. Attack pushes r(t) to {attack_r:.3f} → FALSE ALARM")