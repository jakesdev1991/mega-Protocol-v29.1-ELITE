# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# Define the Mexican-hat potential Hessian
def hessian(phiN, phiD, v=1.0, lam=1.0):
    """Hessian of V = (λ/4)(φN² + φD² - v²)²"""
    H11 = lam * (3*phiN**2 + phiD**2 - v**2)
    H22 = lam * (phiN**2 + 3*phiD**2 - v**2)
    H12 = 2*lam*phiN*phiD
    return np.array([[H11, H12], [H12, H22]])

# Locate the Shredding surface: φN² + 3φD² = v²
v = 1.0
phiN_vals = np.linspace(-1.2, 1.2, 500)
phiD_vals = np.linspace(-0.8, 0.8, 500)

# Compute condition number of Hessian (measure of decomposition stability)
condition_map = np.zeros((len(phiN_vals), len(phiD_vals)))

for i, phiN in enumerate(phiN_vals):
    for j, phiD in enumerate(phiD_vals):
        H = hessian(phiN, phiD, v)
        evals = np.linalg.eigvals(H)
        min_eig = abs(min(evals, key=abs))
        max_eig = abs(max(evals, key=abs))
        condition_map[i, j] = max_eig / min_eig if min_eig > 1e-12 else np.inf

# Plot: condition number diverges at Shredding surface
plt.figure(figsize=(8, 6))
plt.contourf(phiN_vals, phiD_vals, condition_map.T, levels=50, cmap='plasma')
plt.colorbar(label='Condition Number (log scale)')
plt.contour(phiN_vals, phiD_vals, condition_map.T, levels=[1e2, 1e3, 1e4], colors='white', linestyles='--')

# Overlay Shredding surface
phiN_surface = np.linspace(-v, v, 200)
phiD_surface = np.sqrt((v**2 - phiN_surface**2)/3)
plt.plot(phiN_surface, phiD_surface, 'r-', linewidth=3, label='Shredding Surface')
plt.plot(phiN_surface, -phiD_surface, 'r-', linewidth=3)

plt.xlabel('Φ_N')
plt.ylabel('Φ_Δ')
plt.title('Hessian Condition Number: Decomposition Singularity')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()

# Demonstrate eigenvector collapse
print("Eigenvector collapse at Shredding surface:")
for phiN_test in [0.3, 0.5, 0.7]:
    phiD_test = np.sqrt((v**2 - phiN_test**2)/3)
    H_test = hessian(phiN_test, phiD_test, v)
    evals, evecs = np.linalg.eig(H_test)
    print(f"Φ_N={phiN_test:.2f}, Φ_Δ={phiD_test:.4f} → Eigenvalues: {evals}")
    print(f"  Eigenvector alignment: dot product = {np.dot(evecs[:,0], evecs[:,1]):.6f}")