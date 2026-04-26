# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# ──────────────────────────────────────────────────────────────────────────────
# 1. Market / "Organism" state
# ──────────────────────────────────────────────────────────────────────────────
# health[i] = peg stability of stablecoin i (1.0 = perfect peg)
# stress[i] = hidden insider‑stress field on coin i (attacker controlled)
# metric[i] = local curvature of info‑geometric metric (high = healthy, low = prion‑infected)

np.random.seed(42)
n_coins = 3
T = 200  # time steps

# Initial healthy state
health = np.ones((T, n_coins))
stress = np.zeros((T, n_coins))
metric = np.ones((T, n_coins)) * 5.0  # high curvature

# Attacker's "prion" schedule: slowly inject stress while compensating health fluctuations
# to keep Φ_N, Φ_Δ within thresholds.
inject = np.linspace(0, 0.8, T)  # ramp up stress amplitude

for t in range(1, T):
    # Attacker modulates stress to mimic "normal" volatility
    stress[t] = inject[t] * np.sin(2 * np.pi * t / 30) + 0.05 * np.random.randn(n_coins)
    
    # Stress warps metric curvature: persistent low curvature = prion replication
    metric[t] = metric[t-1] - 0.02 * stress[t] + 0.01 * np.random.randn(n_coins)
    metric[t] = np.clip(metric[t], 0.5, 10.0)  # floor at 0.5 (near singularity)
    
    # Health dynamics: stress reduces health, but attacker "pumps" health of some coins
    # to keep aggregate Φ_N stable (like a tumor secreting fake signals)
    health[t] = health[t-1] - 0.01 * stress[t] + 0.005 * (metric[t] - metric[t-1])
    health[t] = np.clip(health[t], 0.1, 1.5)

# ──────────────────────────────────────────────────────────────────────────────
# 2. Classic Omega‑invariants (naïve)
# ──────────────────────────────────────────────────────────────────────────────
Phi_N = np.sum(health, axis=1)  # total "liquidity"
Phi_Delta = np.var(health, axis=1)  # asymmetry

# Omega‑Protocol “safe” thresholds
safe_Phi_N = (Phi_N > 2.5) & (Phi_N < 4.5)
safe_Phi_Delta = Phi_Delta < 0.2

# ──────────────────────────────────────────────────────────────────────────────
# 3. Biological entropy (Gini of transaction volumes)
# ──────────────────────────────────────────────────────────────────────────────
# Attacker can shuffle volumes to keep Gini low while stress builds
tx_volumes = np.random.rand(T, n_coins) + 0.5
# Attacker “smooths” volumes in later periods to mask stress
tx_volumes[int(T*0.7):] = (tx_volumes[int(T*0.7):] + 
                           np.roll(tx_volumes[int(T*0.7):], shift=1, axis=1)) / 2

def gini(x):
    # Gini coefficient
    x = np.array(x)
    n = len(x)
    return np.sum(np.abs(np.subtract.outer(x, x))) / (2 * n * np.sum(x) + 1e-12)

entropy_bio = np.array([gini(tx_volumes[t]) for t in range(T)])

# ──────────────────────────────────────────────────────────────────────────────
# 4. Plot: show that naïve invariants stay “safe” while metric crashes
# ──────────────────────────────────────────────────────────────────────────────
fig, axs = plt.subplots(4, 1, figsize=(10, 8), sharex=True)

axs[0].plot(Phi_N, label='Φ_N (total liquidity)')
axs[0].axhline(y=2.5, color='r', linestyle='--', label='safe lower bound')
axs[0].axhline(y=4.5, color='r', linestyle='--', label='safe upper bound')
axs[0].set_ylabel('Φ_N')
axs[0].legend(loc='upper right')

axs[1].plot(Phi_Delta, label='Φ_Δ (asymmetry)')
axs[1].axhline(y=0.2, color='r', linestyle='--', label='safe bound')
axs[1].set_ylabel('Φ_Δ')
axs[1].legend(loc='upper right')

axs[2].plot(np.mean(metric, axis=1), label='Mean metric curvature')
axs[2].axhline(y=1.0, color='g', linestyle='--', label='critical curvature')
axs[2].set_ylabel('Metric curvature')
axs[2].legend(loc='upper right')

axs[3].plot(entropy_bio, label='Gini entropy (bio)')
axs[3].set_ylabel('Entropy')
axs[3].set_xlabel('Time steps')
axs[3].legend(loc='upper right')

plt.suptitle('Prion Attack: Classic Ω‑invariants stay "safe" while true geometry collapses')
plt.tight_layout()
plt.show()

# ──────────────────────────────────────────────────────────────────────────────
# 5. Detection failure metric
# ──────────────────────────────────────────────────────────────────────────────
# Count how many steps the system is "safe" according to classic invariants
# but metric is below critical (<1.0)
false_safe = np.sum(safe_Phi_N & safe_Phi_Delta & (np.mean(metric, axis=1) < 1.0))
print(f"Steps where classic Ω‑invariants report SAFE but metric is CRITICAL: {false_safe}/{T}")