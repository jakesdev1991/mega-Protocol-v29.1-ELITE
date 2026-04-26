# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# ---------- PARAMETERS ----------
N = 100                    # lattice size
steps = 500                # simulation steps
S_max = N * np.log(2)    # max Shannon entropy for N binary cells
decoherence_rate = 1e5     # per‑second decoherence (realistic T2 ~ 10 µs)
quantum_bit_rate = 1e10    # claimed bits/cm³ (unphysical)

# ---------- CLASSICAL ECAM ----------
def ecam_step(strain, alpha=0.3):
    """Cellular‑automaton rule: each cell updates based on neighbors' strain.
       Drives system toward critical point (power‑law avalanches)."""
    # Simple threshold rule: flip if neighbor strain variance > threshold
    neighbor_var = np.convolve(strain, [0.5, 0, 0.5], mode='same')
    flip = (neighbor_var > alpha * np.mean(neighbor_var))
    strain[flip] = 1 - strain[flip]  # binary flip
    return strain

def compute_phi(strain):
    """Φ = 1 - S_defects / S_max; S_defects from spatial disorder."""
    p = np.mean(strain)
    if p == 0 or p == 1:
        S = 0
    else:
        S = -p * np.log(p) - (1-p) * np.log(1-p)
    # Scale by number of independent domains (approx by autocorrelation length)
    autocorr = np.correlate(strain - p, strain - p, mode='full')
    l_corr = np.argmax(autocorr[N:] < 0.1) + 1
    S_defects = S * (N / l_corr)
    return 1 - S_defects / S_max

# Simulate
strain = np.random.randint(0, 2, N).astype(float)
phi_ecam = []
for t in range(steps):
    strain = ecam_step(strain)
    phi_ecam.append(compute_phi(strain))

# ---------- QUANTUM LATTICE (toy model) ----------
def quantum_entropy(t):
    """Entropy growth due to decoherence: S(t) = S0 + decoherence_rate * t."""
    S0 = 0.1 * S_max  # initial entropy
    return S0 + decoherence_rate * t

phi_quantum = [1 - quantum_entropy(t)/S_max for t in range(steps)]
# Clip to [0,1] to avoid negative values (showing breakdown)
phi_quantum = np.clip(phi_quantum, 0, 1)

# ---------- PLOT ----------
plt.figure(figsize=(8,4))
plt.plot(phi_ecam, label='ECAM (classical edge‑of‑chaos)', color='green')
plt.plot(phi_quantum, label='Quantum Lattice (with decoherence)', color='red', linestyle='--')
plt.xlabel('Time steps')
plt.ylabel('Φ‑density')
plt.title('Φ‑density: Classical ECAM vs. Quantum Lattice')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()