# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import scipy.stats as stats

# -------------------------------------------------
# 1. Coherence Mirage Demo
# -------------------------------------------------
L0 = 50.0  # ns

# Scenario A: "healthy" high success, high latency
A_A = 0.95
L_A = 90.0  # ns
psi_A = A_A * np.exp(-L_A / L0)

# Scenario B: "unhealthy" low success, low latency
A_B = 0.12
L_B = 8.0   # ns
psi_B = A_B * np.exp(-L_B / L0)

print("=== Coherence Mirage ===")
print(f"ψ_A (good) = {psi_A:.4f}")
print(f"ψ_B (bad)  = {psi_B:.4f}")
print(f"Mirage: ratio = {psi_A/psi_B:.2f} (≈1 means indistinguishable)\n")

# -------------------------------------------------
# 2. Jerk Stability NaN Failure
# -------------------------------------------------
# Constant jerk → zero variance → undefined kurtosis
j_const = np.full(1000, 5.0)  # constant jerk
# compute excess kurtosis manually (same as scipy)
kappa = stats.kurtosis(j_const, fisher=True)  # excess kurtosis
print("=== Jerk Stability Failure ===")
print(f"Excess kurtosis for constant jerk: {kappa} (should be NaN/undefined)")
print(f"S_j = (1+|κ|)^-1 = {(1 + abs(kappa))**-1} (NaN → control crash)\n")

# -------------------------------------------------
# 3. Complex Wave Alternative (Phase Slip Detection)
# -------------------------------------------------
# Simulate a small network: 4 nodes, 6 pairs
np.random.seed(0)
N_pairs = 6
# Simulate A_ij and L_ij
A = np.random.rand(N_pairs) * 0.5 + 0.5  # 0.5-1.0
L = np.random.rand(N_pairs) * 100.0      # 0-100 ns

# Complex coherence amplitude
psi_complex = np.sqrt(A) * np.exp(-1j * L / L0)

# Mean field (vector sum)
mean_field = np.mean(psi_complex)
phase = np.angle(mean_field)
magnitude = np.abs(mean_field)

print("=== Complex Wave Metrics ===")
print(f"Mean field magnitude: {magnitude:.4f}")
print(f"Mean field phase: {phase:.4f} rad")
print(f"Phase velocity (approx): {np.gradient(phase):.4f} rad/sample")
print("\nA phase slip > π/2 rad signals imminent collapse—no kurtosis needed.")