# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# ────────── CONFIG ──────────
n = 17               # TOE dimension
tol = 1e-9           # Zero threshold
np.random.seed(0)

# ────────── CONSTRUCT A TOE MATRIX WITH CONTROLLABLE NULLSPACE ──────────
# Start with random matrix, then inject linear dependencies to enlarge nullspace.
T = np.random.randn(n, n)
# Make the last 5 rows linear combos of the first 12 → rank ≤ 12, nullspace ≥ 5
for i in range(12, n):
    T[i, :] = sum(np.random.rand() * T[j, :] for j in range(3))

# ────────── SVD → EXPOSE NULLSPACE ──────────
U, s, Vh = np.linalg.svd(T)
null_mask = s < tol
null_dim = null_mask.sum()
null_basis = Vh[null_mask].T  # shape (n, null_dim)

print(f"TOE rank (Φ_N) = {np.linalg.matrix_rank(T, tol=tol)}")
print(f"Nullspace dim (Φ_Δ) = {null_dim}")
print(f"Asymmetry bound (Φ_Δ < 0.5·Φ_N) satisfied? {null_dim < 0.5 * np.linalg.matrix_rank(T, tol=tol)}")

# ────────── ENCODE PAYLOAD IN NULLSPACE ──────────
# Random payload vector
payload = np.random.randn(n)
# Project onto nullspace → hidden vector
coeffs = null_basis.T @ payload
hidden = null_basis @ coeffs

# Verify stealth: T·hidden ≈ 0 (undetectable by Omega dynamics)
print(f"T·hidden ≈ 0? {np.allclose(T @ hidden, np.zeros(n), atol=1e-6)}")
print(f"Hidden vector norm (energy) = {np.linalg.norm(hidden):.3e}")

# ────────── DEMONSTRATE BOUND VIOLATION ──────────
# Increase nullspace dimension by adding more linear dependencies
T2 = T.copy()
T2[15, :] = T2[0, :] - T2[1, :]  # another dependency
U2, s2, Vh2 = np.linalg.svd(T2)
null_dim2 = (s2 < tol).sum()
phi_n2 = np.linalg.matrix_rank(T2, tol=tol)
print(f"\nAfter injecting extra dependency:")
print(f"New nullspace dim = {null_dim2}, rank = {phi_n2}")
print(f"Asymmetry bound violated? {null_dim2 >= 0.5 * phi_n2}")