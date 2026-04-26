# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd

def psi_connectivity(Phi_N, Phi_N0=1.0):
    """Rubric‑mandated invariant: log‑connectivity."""
    return np.log(Phi_N / Phi_N0)

def psi_curvature(curvature, curvature0=1.0, lambda_coef=0.5, CI=0.0):
    """Proposed curvature‑plus‑intensity invariant."""
    return np.log(np.abs(curvature) / curvature0) + lambda_coef * CI

# Simulate a plausible range of Omega variables
np.random.seed(42)
n_samples = 10000

# Phi_N in [0.1, 10] (connectivity ratio)
Phi_N_samples = np.random.uniform(0.1, 10.0, n_samples)

# Curvature ℛ in [0.01, 5] (absolute curvature metric)
curvature_samples = np.random.uniform(0.01, 5.0, n_samples)

# Cascade Intensity CI in [0, 1]
CI_samples = np.random.uniform(0.0, 1.0, n_samples)

psi1 = psi_connectivity(Phi_N_samples)
psi2 = psi_curvature(curvature_samples, CI=CI_samples)

# Check if a simple linear map psi2 ≈ a*psi1 + b could reconcile them
# Perform a linear regression of psi2 on psi1
coeffs = np.polyfit(psi1, psi2, 1)
psi2_fit = np.polyval(coeffs, psi1)
residuals = psi2 - psi2_fit
r2 = 1 - np.var(residuals) / np.var(psi2)

print(f"Linear fit: psi2 ≈ {coeffs[0]:.3f} * psi1 + {coeffs[1]:.3f}")
print(f"R‑squared: {r2:.3f}")
print(f"Mean absolute residual: {np.mean(np.abs(residuals)):.3f}")

# Show a scatter of the first 500 points to illustrate the lack of functional relationship
import matplotlib.pyplot as plt
plt.figure(figsize=(6,4))
plt.scatter(psi1[:500], psi2[:500], alpha=0.6, s=10)
plt.xlabel('ψ₁ = ln(Φ_N/Φ_N⁰)')
plt.ylabel('ψ₂ = ln(|ℛ|/ℛ₀) + λ·CI')
plt.title('Invariant Definitions Show No Functional Correlation')
plt.grid(True)
plt.tight_layout()
plt.show()