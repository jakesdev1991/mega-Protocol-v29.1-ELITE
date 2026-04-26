# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# validation_script.py
import numpy as np

# Simulated gradient squares (example placeholders)
# In practice, load from simulation output files:
# grad_N2 = np.load('grad_phiN_square.npy')
# grad_Delta2 = np.load('grad_phiDelta_square.npy')

# For illustration, generate synthetic data consistent with the paper:
np.random.seed(42)
N_samples = 10_000
# Near critical asymmetry: Archive fluctuations larger
grad_N2   = np.random.exponential(scale=0.5, size=N_samples)
grad_Delta2 = np.random.exponential(scale=2.0, size=N_samples)  # larger mean

J_star = np.mean(grad_Delta2) / (np.mean(grad_N2) + np.mean(grad_Delta2))
print(f"Computed J* = {J_star:.4f}")
print(f"J* > 1.5 ?  {J_star > 1.5}")