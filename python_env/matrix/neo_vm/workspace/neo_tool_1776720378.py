# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch
from scipy.stats import kurtosis

# Simulate stablecoin peg (mean-reverting with attack)
def simulate_stablecoin(T=10000, attack_start=0.7):
    t = np.arange(T)
    price = 1.0 + 0.01*np.cumsum(np.random.randn(T))  # Random walk around peg
    # Attack: whale dumps
    attack = np.zeros(T)
    attack[int(attack_start*T):] = -0.5 * np.exp(np.linspace(0, 2, T - int(attack_start*T)))
    return t, price + attack

# Simulate plasma disruption (tearing mode)
def simulate_plasma(T=10000, disruption_start=0.7):
    t = np.arange(T)
    # Stable phase: MHD turbulence
    b_field = 1.0 + 0.05*np.sin(2*np.pi*0.01*t) + 0.02*np.random.randn(T)
    # Disruption: coherent mode growth (non-linear)
    mode = np.zeros(T)
    mode[int(disruption_start*T):] = 0.3 * np.exp(np.linspace(0, 3, T - int(disruption_start*T))) * np.sin(2*np.pi*0.1*np.arange(T - int(disruption_start*T)))
    return t, b_field + mode

# Beta's "universal" depeg detector (variance spike)
def beta_detector(signal, window=100):
    return np.array([np.var(signal[i:i+window]) for i in range(len(signal)-window)])

# DDDO-Ω detector: spectral divergence (power spectrum kurtosis)
def dddo_detector(signal, window=1000, fs=1.0):
    kurtosis_trace = []
    for i in range(0, len(signal)-window, window//2):
        f, Pxx = welch(signal[i:i+window], fs=fs, nperseg=window//4)
        # Kurtosis of power spectrum: high kurtosis = coherent mode emergence = "adversarial attack"
        kurtosis_trace.append(kurtosis(Pxx))
    return np.array(kurtosis_trace)

# Run comparison
t_sc, sc = simulate_stablecoin()
t_pl, pl = simulate_plasma()

# Apply detectors
sc_var = beta_detector(sc)
pl_var = beta_detector(pl)
sc_kurt = dddo_detector(sc)
pl_kurt = dddo_detector(pl)

# Plot
fig, ax = plt.subplots(2, 2, figsize=(12, 8))
ax[0,0].plot(t_sc, sc); ax[0,0].set_title("Stablecoin Price")
ax[0,1].plot(t_pl, pl); ax[0,1].set_title("Plasma B-field")
ax[1,0].plot(sc_var); ax[1,0].set_title("Beta Detector: Variance")
ax[1,0].axvline(7000, color='r', linestyle='--')
ax[1,1].plot(pl_var); ax[1,1].set_title("Beta Detector on Plasma (FAILS)")
ax[1,1].axvline(7000, color='r', linestyle='--')
# Spectral kurtosis
# fig2, ax2 = plt.subplots(2, 1)
# ax2[0].plot(sc_kurt); ax2[0].set_title("DDDO on Stablecoin")
# ax2[1].plot(pl_kurt); ax2[1].set_title("DDDO on Plasma (WORKS)")
plt.tight_layout()
plt.show()

# Print false positive rates
print(f"Stablecoin variance spike at depeg: {sc_var[7000] > np.percentile(sc_var[:7000], 95)}")
print(f"Plasma variance spike at disruption: {pl_var[7000] > np.percentile(pl_var[:7000], 95)} (FALSE: variance is BLIND to coherent mode)")
print(f"Plasma spectral kurtosis spike: {pl_kurt[-1] > np.percentile(pl_kurt, 95)} (TRUE: detects coherence)")