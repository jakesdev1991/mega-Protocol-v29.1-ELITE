# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# Parameters
lam = 1.0
v = 1.0

# Field grid
N = 400
phi_max = 1.5
phi_N = np.linspace(-phi_max, phi_max, N)
phi_D = np.linspace(-phi_max, phi_max, N)
PhiN, PhiD = np.meshgrid(phi_N, phi_D)

# Potential
V = (lam / 4) * (PhiN**2 + PhiD**2 - v**2)**2

# Hessian components
V_NN = lam * (3 * PhiN**2 + PhiD**2 - v**2)  # ∂²V/∂Φ_N²
V_DD = lam * (PhiN**2 + 3 * PhiD**2 - v**2)  # ∂²V/∂Φ_Δ²
V_ND = 2 * lam * PhiN * PhiD                  # ∂²V/∂Φ_N∂Φ_Δ

# Eigenvalues of Hessian
trace = V_NN + V_DD
det = V_NN * V_DD - V_ND**2
# eigenvalues = (trace ± sqrt(trace**2 - 4*det)) / 2
discriminant = trace**2 - 4 * det
# For stability, ensure discriminant is non-negative (it is for this potential)
sqrt_disc = np.sqrt(np.maximum(discriminant, 0))
eig1 = (trace - sqrt_disc) / 2
eig2 = (trace + sqrt_disc) / 2

# Zero contours for diagonal entries (Shredding surfaces)
# ∂²V/∂Φ_Δ² = 0  ->  Phi_N^2 + 3 Phi_D^2 = v^2
# ∂²V/∂Φ_N² = 0  ->  3 Phi_N^2 + Phi_D^2 = v^2

# Zero contour for eigenvalues (det = 0) -> S = v^2 or v^2/3
S = PhiN**2 + PhiD**2
det_zero_outer = np.isclose(S, v**2, atol=0.02)
det_zero_inner = np.isclose(S, v**2 / 3, atol=0.02)

# Plotting
fig, axs = plt.subplots(2, 2, figsize=(12, 10))

# Panel 1: Potential
cont = axs[0,0].contourf(PhiN, PhiD, V, levels=50, cmap='viridis')
axs[0,0].set_title('Potential V(Φ_N, Φ_Δ)')
axs[0,0].set_xlabel('Φ_N')
axs[0,0].set_ylabel('Φ_Δ')
fig.colorbar(cont, ax=axs[0,0])

# Panel 2: Zero contours of diagonal entries
axs[0,1].contour(PhiN, PhiD, V_DD, levels=[0], colors='red', linewidths=2, label='∂²V/∂Φ_Δ² = 0')
axs[0,1].contour(PhiN, PhiD, V_NN, levels=[0], colors='blue', linewidths=2, label='∂²V/∂Φ_N² = 0')
axs[0,1].set_title('Diagonal Entry Zero Contours')
axs[0,1].set_xlabel('Φ_N')
axs[0,1].set_ylabel('Φ_Δ')
axs[0,1].legend()

# Panel 3: Zero contours of eigenvalues (det = 0)
axs[1,0].contour(PhiN, PhiD, det, levels=[0], colors='green', linewidths=2, label='det(H) = 0')
axs[1,0].set_title('Eigenvalue Zero Contour (det=0)')
axs[1,0].set_xlabel('Φ_N')
axs[1,0].set_ylabel('Φ_Δ')
axs[1,0].legend()

# Panel 4: Off-diagonal magnitude
offdiag_mag = np.abs(V_ND)
cont4 = axs[1,1].contourf(PhiN, PhiD, offdiag_mag, levels=50, cmap='plasma')
axs[1,1].set_title('Off-diagonal |∂²V/∂Φ_N∂Φ_Δ|')
axs[1,1].set_xlabel('Φ_N')
axs[1,1].set_ylabel('Φ_Δ')
fig.colorbar(cont4, ax=axs[1,1])

plt.tight_layout()
plt.show()

# Print eigenvalues at a few points to illustrate
points = [
    (0.0, 0.0),          # origin (local maximum)
    (v/np.sqrt(2), v/np.sqrt(2)),  # point on vacuum manifold (Goldstone direction)
    (v, 0.0),            # point on vacuum manifold (radial direction)
    (0.5, 0.2),          # generic point inside
    (0.2, 0.5)           # generic point inside
]

for pn, pd in points:
    # Compute Hessian eigenvalues at this point
    Vnn = lam * (3 * pn**2 + pd**2 - v**2)
    Vdd = lam * (pn**2 + 3 * pd**2 - v**2)
    Vnd = 2 * lam * pn * pd
    trace_p = Vnn + Vdd
    det_p = Vnn * Vdd - Vnd**2
    disc_p = trace_p**2 - 4 * det_p
    sqrt_disc_p = np.sqrt(max(disc_p, 0))
    eig1_p = (trace_p - sqrt_disc_p) / 2
    eig2_p = (trace_p + sqrt_disc_p) / 2
    print(f"Point ({pn:.2f}, {pd:.2f}): eigenvalues = ({eig1_p:.3f}, {eig2_p:.3f}), diagonal entries = ({Vnn:.3f}, {Vdd:.3f}), off-diagonal = {Vnd:.3f}")