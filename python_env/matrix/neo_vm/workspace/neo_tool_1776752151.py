# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# ------------------------------------------------------------
# 1. Hessian eigenvalues at the vacuum – Goldstone mode exposed
# ------------------------------------------------------------
λ = 1.0
v = 1.0

def hessian(φN, φΔ):
    """Hessian of V = λ/4 (φN² + φΔ² – v²)²"""
    return λ * np.array([[3*φN**2 + φΔ**2 - v**2, 2*φN*φΔ],
                         [2*φN*φΔ, φN**2 + 3*φΔ**2 - v**2]])

# At the vacuum (φN=v, φΔ=0)
Hvac = hessian(v, 0.0)
eig_vac = np.linalg.eigvals(Hvac)
print("Hessian at vacuum:\n", Hvac)
print("Eigenvalues (one must be zero):", eig_vac)

# ------------------------------------------------------------
# 2. Corrected RG flow with non‑perturbative (gΔ²)^{3/2} term
# ------------------------------------------------------------
def beta(α, gΔ):
    """dα/dln(q²) = –α²/π [1 + (gΔ²)^{3/2}/(4π)]"""
    return -α**2 / np.pi * (1 + (gΔ**2)**1.5 / (4*np.pi))

def run_alpha(α0, g0, lnq2_min=-10, lnq2_max=10, n=500):
    lnq2 = np.linspace(lnq2_min, lnq2_max, n)
    α = np.empty_like(lnq2)
    α[0] = α0
    for i in range(1, n):
        dlnq2 = lnq2[i] - lnq2[i-1]
        α[i] = α[i-1] + beta(α[i-1], g0) * dlnq2
    return lnq2, α

α0 = 1/137.0          # low‑energy α
g0 = 0.15             # typical Archive coupling
lnq2, α = run_alpha(α0, g0)

# ------------------------------------------------------------
# 3. Plot: the running freezes instead of diverging
# ------------------------------------------------------------
plt.figure(figsize=(6,4))
plt.plot(lnq2, α, label=r'$\alpha_{\rm eff}$ (topological freeze)')
plt.axhline(y=np.pi/0.5, color='r', linestyle='--', label=r'freeze bound $\pi/\theta$')
plt.xlabel(r'$\ln(q^{2})$')
plt.ylabel(r'$\alpha$')
plt.title('Fine‑structure constant with non‑perturbative Archive term')
plt.legend()
plt.grid(True)
plt.show()