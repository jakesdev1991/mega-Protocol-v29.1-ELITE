# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# --- Simulation parameters ---
np.random.seed(42)
T = 200
window = 20

# True (hidden) performance of each algorithm (steady state)
true_perf = np.array([0.75, 0.70, 0.68, 0.65, 0.60])

# Observed performance: true + small noise
obs_perf = np.zeros((T, 5))
obs_perf += true_perf + 0.05 * np.random.randn(T, 5)

# --- Attack: rogue algorithm (index 4) games its score between t=50 and t=100 ---
rogue_start, rogue_end = 50, 100
obs_perf[rogue_start:rogue_end, 4] = 0.95  # artificially high

# After rogue_end, rogue performance collapses
obs_perf[rogue_end:, 4] = 0.30

# --- Meta‑learner: softmax selection probabilities ---
def softmax(scores, temp=0.5):
    exp = np.exp(scores / temp)
    return exp / exp.sum(axis=1, keepdims=True)

probs = softmax(obs_perf, temp=0.5)

# Entropy of selection distribution
entropy = -np.sum(probs * np.log(np.clip(probs, 1e-12, 1)), axis=1)

# Weighted "performance" V(t) (simple expectation)
V = np.sum(probs * obs_perf, axis=1)

# --- Shredding detection: high entropy + low performance ---
shredding_thresh = 1.5  # entropy threshold
performance_thresh = 0.55
shredding_event = (entropy > shredding_thresh) & (V < performance_thresh)

# --- Plot ---
fig, ax = plt.subplots(3, 1, figsize=(8, 6), sharex=True)
ax[0].plot(V, label='V(t) (weighted performance)')
ax[0].axhline(performance_thresh, color='r', linestyle='--', label='Performance threshold')
ax[0].set_ylabel('Performance')
ax[0].legend()
ax[0].set_title('AGRIS‑Ω Vulnerability: Rogue Algorithm Attack')

ax[1].plot(entropy, label='Entropy S(t)')
ax[1].axhline(shredding_thresh, color='r', linestyle='--', label='Entropy threshold')
ax[1].set_ylabel('Entropy')
ax[1].legend()

ax[2].plot(shredding_event, label='Shredding Event', color='purple')
ax[2].set_xlabel('Time step')
ax[2].set_ylabel('Shredding flag')
ax[2].legend()

plt.tight_layout()
plt.show()