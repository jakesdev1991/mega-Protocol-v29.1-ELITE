# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# --- Parameters ---
np.random.seed(42)
N = 200  # number of spatial points
L = 10.0
x = np.linspace(-L/2, L/2, N)
dx = x[1] - x[0]

# --- Define a conformal factor psi(x) that is very negative in a region ---
psi = np.where(np.abs(x) < 1.0, -10.0, 0.0)  # deep well near origin

# --- Metric determinant (Minkowski signature det(eta) = -1) ---
det_g = -np.exp(8 * psi)  # det(g) = -e^{8 psi}
print("Metric determinant range: [{:.3e}, {:.3e}]".format(det_g.min(), det_g.max()))

# --- Construct two *orthogonal* complex scalar fields ---
# Start with random complex fields
psi_S = np.random.randn(N) + 1j * np.random.randn(N)
psi_C = np.random.randn(N) + 1j * np.random.randn(N)

# Orthogonalize psi_C with respect to psi_S using Gram-Schmidt
# Weight by sqrt(-g) for the inner product as defined in COD
sqrt_neg_g = np.sqrt(-det_g)
psi_S_weighted = psi_S * sqrt_neg_g
psi_C_weighted = psi_C * sqrt_neg_g

# Projection coefficient
proj = np.vdot(psi_C_weighted, psi_S_weighted) / np.vdot(psi_S_weighted, psi_S_weighted)
psi_C_ortho_weighted = psi_C_weighted - proj * psi_S_weighted

# Convert back to unweighted fields
psi_C_ortho = psi_C_ortho_weighted / sqrt_neg_g

# --- Compute COD ---
num = np.abs(np.trapz(psi_S.conj() * psi_C_ortho * sqrt_neg_g, x))**2
denom = (np.trapz(np.abs(psi_S)**2 * sqrt_neg_g, x) *
         np.trapz(np.abs(psi_C_ortho)**2 * sqrt_neg_g, x))
COD = num / denom if denom != 0 else np.nan
print("Chain Overlap Density (COD) = {:.6f}".format(COD))

# --- Demonstrate that COD can be zero while det(g) is nowhere zero (except at -infty) ---
# Here det_g is extremely small but *finite* in the well, yet COD is essentially zero.
print("det(g) in the well = {:.3e} (finite but tiny)".format(det_g[N//2]))

# --- Show that the "drag" term is a gauge artifact ---
# Compute gradient of psi and the term coefficient
dpsi_dx = np.gradient(psi, dx)
# The coefficient in the EOM: -2 * exp(-2*psi) * dpsi_dx * dpsi_S_dx
dpsi_S_dx = np.gradient(psi_S, dx)
drag_coeff = -2 * np.exp(-2 * psi) * dpsi_dx * dpsi_S_dx
print("Max magnitude of 'drag' term coefficient = {:.3e}".format(np.max(np.abs(drag_coeff))))
print("Note: sign of psi does not appear; only its gradient matters.")

# --- Eigenvalues of a naive Resonant Decoupling Operator ---
# Approximate the operator as a matrix exponential of a small random perturbation
M = np.random.randn(5, 5) + 1j * np.random.randn(5, 5)
M = (M + M.conj().T) / 2  # make it Hermitian for the sake of argument
# The operator exp(-i * M * dt) with dt = 1
dt = 1.0
eigvals = np.linalg.eigvals(-1j * M * dt)
print("Eigenvalues of the decoupling operator (magnitude):")
print(np.abs(eigvals))
print("Largest magnitude = {:.3f} (often > 1 => amplification, not stabilization)".format(np.max(np.abs(eigvals))))