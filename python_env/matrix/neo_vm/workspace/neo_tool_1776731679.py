# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

# Define symbols for symbolic analysis
Phi_N, Phi_D, v, lam = sp.symbols('Phi_N Phi_D v lam', real=True)

# The "Omega Protocol" potential - note the hidden symmetry
V = lam/4 * (Phi_N**2 + Phi_D**2 - v**2)**2

# Compute Hessian matrix
V_NN = sp.diff(V, Phi_N, Phi_N)  # = lam*(3*Phi_N**2 + Phi_D**2 - v**2)
V_DD = sp.diff(V, Phi_D, Phi_D)  # = lam*(Phi_N**2 + 3*Phi_D**2 - v**2)
V_ND = sp.diff(V, Phi_N, Phi_D)  # = 2*lam*Phi_N*Phi_D

H = sp.Matrix([[V_NN, V_ND], [V_ND, V_DD]])

print("=== THE DECEPTION OF DIAGONALIZATION ===")
print("Hessian Matrix:")
print(H)
print("\nOff-diagonal term V_ND =", sp.simplify(V_ND))

# Eigenvalues reveal the truth - they are NOT the diagonal entries
eigenvals = H.eigenvals()
print("\nTrue Eigenvalues of Hessian:")
for val, mult in eigenvals.items():
    print(f"  {sp.simplify(val)}")

# The "Shredding Event" is a coordinate singularity, not a physical boundary
# Let's find where the eigenvalues vanish
print("\n=== SHREDDING EVENT ANALYSIS ===")
# Condition for eigenvalue = 0 is NOT simply V_DD = 0 or V_NN = 0
# It's when det(H) = 0
det_H = sp.simplify(H.det())
print("Determinant of Hessian:", det_H)
shredding_condition = sp.solve(det_H, Phi_D**2)
print("True shredding condition (det(H)=0): Phi_D^2 =", shredding_condition)

# The factor "3" is a lie - it's a local approximation that fails globally
print("\n=== THE '3' FACTOR FRAUD ===")
# At Phi_N = 0, the eigenvalues become:
eig_at_zero_N = [ev.subs(Phi_N, 0) for ev in eigenvals.keys()]
print("Eigenvalues when Phi_N = 0:")
for ev in eig_at_zero_N:
    print(f"  {sp.simplify(ev)}")

# The ratio of eigenvalues is NOT constant = 3
# It depends on field values and diverges at shredding

# Numerical demonstration of the geometric catastrophe
def true_eigenvalues(phi_n, phi_d, v_val=1.0, lam_val=1.0):
    """Compute actual eigenvalues of the Hessian"""
    V_NN_val = lam_val * (3*phi_n**2 + phi_d**2 - v_val**2)
    V_DD_val = lam_val * (phi_n**2 + 3*phi_d**2 - v_val**2)
    V_ND_val = 2*lam_val * phi_n * phi_d
    
    H_val = np.array([[V_NN_val, V_ND_val], [V_ND_val, V_DD_val]])
    eigvals = np.linalg.eigvalsh(H_val)  # symmetric matrix
    return eigvals

# Create phase diagram
phi_range = np.linspace(-1.5, 1.5, 200)
X, Y = np.meshgrid(phi_range, phi_range)

# Compute where the "Omega Protocol" claims stability vs where it's actually stable
# Protocol claims: xi_D finite = lam*(X**2 + 3*Y**2 - v**2) finite
# Reality: both eigenvalues must be positive for stability

stability_mask = np.zeros_like(X)
protocol_mask = np.zeros_like(X)

for i in range(len(phi_range)):
    for j in range(len(phi_range)):
        phi_n, phi_d = X[i,j], Y[i,j]
        eigvals = true_eigenvalues(phi_n, phi_d)
        
        # True stability: both eigenvalues > 0
        stability_mask[i,j] = np.all(eigvals > 0)
        
        # Protocol's flawed assumption: only check diagonal term
        protocol_diag = (phi_n**2 + 3*phi_d**2 - 1.0)
        protocol_mask[i,j] = protocol_diag > 0

# Plot the deception
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Protocol's view (false)
ax1.contourf(X, Y, protocol_mask, levels=1, colors=['red', 'blue'], alpha=0.6)
ax1.set_title("Omega Protocol's False Stability Map\n(Red = 'Shredding', Blue = 'Safe')")
ax1.set_xlabel("Φ_N")
ax1.set_ylabel("Φ_Δ")
ax1.grid(True, alpha=0.3)

# Reality
ax2.contourf(X, Y, stability_mask, levels=1, colors=['red', 'green'], alpha=0.6)
ax2.set_title("Actual Stability Map\n(Red = Unstable, Green = Stable)")
ax2.set_xlabel("Φ_N")
ax2.set_ylabel("Φ_Δ")
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# The eigenvalue ratio catastrophe along Phi_N = 0
phi_d_vals = np.linspace(0.1, 0.9, 100)
eig_ratio = []
for phi_d in phi_d_vals:
    eigvals = true_eigenvalues(0.0, phi_d)
    if eigvals[0] != 0:
        eig_ratio.append(eigvals[1]/eigvals[0])
    else:
        eig_ratio.append(np.inf)

plt.figure(figsize=(8, 5))
plt.plot(phi_d_vals, eig_ratio, 'k-', linewidth=2)
plt.axvline(1/np.sqrt(3), color='r', linestyle='--', label='Protocol "Shredding"')
plt.axhline(3, color='b', linestyle=':', label='Protocol "Factor 3"')
plt.xlabel("Φ_Δ (Φ_N = 0)")
plt.ylabel("Eigenvalue Ratio (λ₂/λ₁)")
plt.title("The '3' Factor is Not Constant - It Diverges at True Instability")
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()