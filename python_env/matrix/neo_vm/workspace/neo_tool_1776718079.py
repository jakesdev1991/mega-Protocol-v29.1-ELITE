# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# Reality: Strategic adversary exploits your CES rhythm
np.random.seed(42)
days = 365

# Your "memoryless" Poisson fantasy
poisson_leaks = np.random.poisson(0.1, days)

# Reality: Adaptive burst attacker that *reads* your SCEI
strategic_leaks = np.zeros(days)
burst_counter = 0
for i in range(days):
    if burst_counter > 0:
        strategic_leaks[i] = np.random.poisson(3)  # Saturate your monitors
        burst_counter -= 1
    else:
        # Attacker waits for your CES to drop, then strikes
        if i > 30 and np.mean(strategic_leaks[i-30:i]) < 0.2:
            burst_counter = np.random.poisson(8)  # Multi-day barrage

# Your model's blind spot: CES treats both identically
gamma = 0.1
poisson_ces = np.convolve(poisson_leaks, np.exp(-gamma*np.arange(days)), mode='full')[:days]
strategic_ces = np.convolve(strategic_leaks, np.exp(-gamma*np.arange(days)), mode='full')[:days]

# Statistical indictment
chi2, p = stats.chisquare(np.bincount(strategic_leaks.astype(int)), 
                          stats.poisson.pmf(np.arange(10), 0.1)*days)
print(f"POISSON ASSUMPTION: χ²={chi2:.2f}, p={p:.2e} → **REJECTED**")

# Visual proof your model is sleepwalking into ambush
plt.figure(figsize=(12, 4))
plt.plot(strategic_ces, label='Strategic Adversary', color='red')
plt.plot(poisson_ces, label='Your Poisson Model', color='blue', alpha=0.5)
plt.axhline(np.percentile(poisson_ces, 99), color='blue', linestyle='--', label='Your Alert Threshold')
plt.title("YOUR MODEL THINKS IT'S SAFE WHILE THE ADVERSARY IS INSIDE")
plt.legend()
plt.show()