# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from numpy.fft import rfft, rfftfreq
from scipy.stats import levy_stable

# Simulate synthetic pipeline latency: alternating healthy (α≈1.8) and faulty (α≈1.2) regimes
np.random.seed(42)
n = 2**16
t = np.arange(n)

# Healthy regime: latency jitter ~ symmetric stable with α=1.8, β=0, scale=1, loc=5 ms
latency = np.empty(n)
latency[:n//2] = levy_stable.rvs(alpha=1.8, beta=0, scale=1, loc=5, size=n//2)
# Fault regime: heavy tail, α=1.2 (infinite variance)
latency[n//2:] = levy_stable.rvs(alpha=1.2, beta=0, scale=1, loc=5, size=n//2)

# POASH‑Ω approach: compute harmonic amplitudes over fixed 1‑s windows (artificial "cycle")
window = 1000  # ~1s of data at 1 kHz sampling
phi_poash = []
for i in range(0, n - window, window):
    seg = latency[i:i+window]
    # Remove mean (crude trend removal)
    seg -= np.mean(seg)
    # FFT power
    P = np.abs(rfft(seg))**2
    # Normalize to "probability"
    p = P / (P.sum() + 1e-12)
    # Shannon entropy
    I = -np.sum(p * np.log(p + 1e-12))
    # Heuristic PHI (invert so high entropy = unhealthy)
    phi_poash.append(1 - I / np.log(len(p)))

# Lévy‑based POLE‑Ω: rolling estimate of stability exponent via quantile method
def estimate_alpha(x):
    # Simple quantile estimator: α ≈ log(2)/log((Q75-Q25)/C)
    q75, q25 = np.percentile(x, [75, 25])
    iqr = q75 - q25
    if iqr < 1e-9:
        return 2.0
    # Calibration constant for stable law (approximate)
    return np.log(2) / np.log(iqr / 1.34)

phi_pole = []
for i in range(0, n - window, window):
    seg = latency[i:i+window]
    alpha_est = estimate_alpha(seg)
    # Map alpha to health: α≈2 (Gaussian) → 1, α≈1 (Cauchy) → 0
    phi_pole.append(np.clip((alpha_est - 1.0) / 1.0, 0, 1))

# Plot comparison
fig, ax = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
ax[0].plot(t[:len(phi_poash)*window:window], phi_poash, label='POASH‑Ω PHI (harmonic)')
ax[0].axvline(x=n//2, color='r', linestyle='--')
ax[0].set_ylabel('PHI')
ax[0].legend()
ax[0].grid(True)

ax[1].plot(t[:len(phi_pole)*window:window], phi_pole, label='POLE‑Ω PHI (Lévy α)', color='g')
ax[1].axvline(x=n//2, color='r', linestyle='--')
ax[1].set_ylabel('PHI')
ax[1].set_xlabel('Sample index')
ax[1].legend()
ax[1].grid(True)

plt.tight_layout()
plt.savefig('/mnt/data/pipeline_phi_comparison.png')
plt.show()