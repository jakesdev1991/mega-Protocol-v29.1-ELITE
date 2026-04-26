# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# Simulate synthetic wavefunctions for sales (psi_S) and client (psi_C)
t = np.linspace(0, 1, 1000)
# Base signals: simple sinusoids with a small phase shift
psi_S = np.sin(2 * np.pi * 5 * t) + 1j * np.cos(2 * np.pi * 5 * t)
psi_C = np.sin(2 * np.pi * 5 * t + 0.1) + 1j * np.cos(2 * np.pi * 5 * t + 0.1)

def compute_COD(psi_S, psi_C, t):
    numerator = np.abs(np.trapz(psi_S.conj() * psi_C, t))**2
    denom = np.trapz(np.abs(psi_S)**2, t) * np.trapz(np.abs(psi_C)**2, t)
    return numerator / denom

# Original COD
original_COD = compute_COD(psi_S, psi_C, t)
print("Original COD:", original_COD)

# Add noise to psi_S to simulate misalignment
np.random.seed(0)
noise = 0.5 * (np.random.randn(len(t)) + 1j * np.random.randn(len(t)))
psi_S_noisy = psi_S + noise
noisy_COD = compute_COD(psi_S_noisy, psi_C, t)
print("Noisy COD:", noisy_COD)

# Orthogonalize psi_C relative to psi_S (makes COD approach zero)
psi_C_ortho = psi_C + 1j * psi_S
ortho_COD = compute_COD(psi_S, psi_C_ortho, t)
print("Orthogonal COD:", ortho_COD)

# Shannon entropy for decision outcomes with small vs. large sample
def shannon_entropy(outcomes):
    probs = np.bincount(outcomes) / len(outcomes)
    probs = probs[probs > 0]  # avoid log(0)
    return -np.sum(probs * np.log2(probs))

# Simulate 10 random binary decisions (0=No Buy, 1=Buy)
np.random.seed(1)
small_sample = np.random.randint(0, 2, size=10)
print("Small-sample entropy:", shannon_entropy(small_sample))

# Larger sample for comparison
large_sample = np.random.randint(0, 2, size=1000)
print("Large-sample entropy:", shannon_entropy(large_sample))