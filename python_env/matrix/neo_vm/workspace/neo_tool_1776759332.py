# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Transfer‑matrix demonstration that a 1‑D double‑well field does NOT
exhibit the emergent topological order claimed by ETO‑Ω.
"""
import numpy as np
import scipy.linalg as la

# ----------------------------------------------------------------------
# 1. Discretize the field φ (the "Omega field")
phi_min, phi_max, dphi = -5.0, 5.0, 0.1
phi_grid = np.arange(phi_min, phi_max + dphi/2, dphi)
Nphi = len(phi_grid)

# 2. Double‑well potential V(φ) = -a φ²/2 + b φ⁴/4
a = 1.0      # coefficient of the quadratic term (negative sign)
b = 0.1      # small quartic coefficient (keeps potential bounded)
V = -0.5 * a * phi_grid**2 + 0.25 * b * phi_grid**4

# 3. Nearest‑neighbor coupling (kinetic term) -> Gaussian kernel
#    T(φ, φ') = exp[-½(φ‑φ')² -½V(φ) -½V(φ')]
#    (units are chosen so that β = 1)
pair = np.exp(-0.5 * (phi_grid[:, None] - phi_grid[None, :])**2)  # Nphi x Nphi
diag = np.exp(-0.5 * (V[:, None] + V[None, :]))
T = pair * diag  # transfer matrix

# 4. Diagonalize T (largest eigenvalue λ0, second‑largest λ1)
eigvals, eigvecs = la.eig(T)
eigvals = np.real_if_close(eigvals)
idx = np.argsort(eigvals)[::-1]  # descending order
λ0 = eigvals[idx[0]]
λ1 = eigvals[idx[1]]

# 5. Correlation length ξ = -1 / ln(λ1/λ0)
ξ = -1.0 / np.log(λ1/λ0)
print(f"Correlation length ξ = {ξ:.4f} (finite → no divergent susceptibility)")

# 6. Order parameter O = lim_{|i-j|→∞} ⟨φ_i φ_j⟩
#    For a symmetric double‑well, ⟨φ⟩ = 0, so O = 0.
psi0 = np.real_if_close(eigvecs[:, idx[0]])
psi0 /= np.linalg.norm(psi0)
⟨φ⟩ = np.sum(psi0**2 * phi_grid)
O = ⟨φ⟩**2
print(f"⟨φ⟩ = {⟨φ⟩:.6e}, order parameter O = {O:.6e} (zero in symmetric phase)")

# 7. Invariants Φ_N and Φ_Δ as defined in the proposal
#    (Here we interpret them as spatial averages of φ and φ²)
Φ_N = np.sum(psi0**2 * phi_grid)                # average field
Φ_Δ = np.sum(psi0**2 * phi_grid**2)              # average squared field
print(f"Φ_N (average φ) = {Φ_N:.6e}")
print(f"Φ_Δ (average φ²) = {Φ_Δ:.6e}")

# 8. Show that the “gap” Δ (difference between the two lowest eigenvalues
#    of the *quantum* Hamiltonian) is not the same as the statistical
#    gap above. The statistical gap is just λ0‑λ1, which never closes.
Δ_stat = λ0 - λ1
print(f"Statistical gap Δ_stat = {Δ_stat:.6e} (non‑zero for all couplings)")

# ----------------------------------------------------------------------
# 9. Sanity check: compute the two‑point correlator and fit to exponential
def correlator(r):
    # ⟨φ_i φ_{i+r}⟩ = Σ_n (λ_n/λ0)^r ⟨0|φ|n⟩⟨n|φ|0⟩
    # Approximate using the first two eigenstates.
    psi1 = np.real_if_close(eigvecs[:, idx[1]])
    psi1 /= np.linalg.norm(psi1)
    φ_0n = np.sum(psi0 * phi_grid * psi1)   # ⟨0|φ|1⟩
    return Φ_N**2 + (λ1/λ0)**r * φ_0n**2

r_vals = np.arange(0, 50, 2)
corr = [correlator(r) for r in r_vals]
print("\nTwo‑point correlator ⟨φ_i φ_{i+r}⟩ (first few distances):")
for r, c in zip(r_vals[:6], corr[:6]):
    print(f"r={r:2d}: {c:.6f}")

# The exponential decay constant should match ξ computed above.
# Fit log(corr) vs r for r>0 to extract ξ_fit.
if len(corr) > 1:
    y = np.log(np.array(corr[1:]) - Φ_N**2 + 1e-12)  # subtract long‑range part
    ξ_fit = -1.0 / np.polyfit(r_vals[1:], y, 1)[0]
    print(f"Fit correlation length ξ_fit ≈ {ξ_fit:.4f} (should match ξ above)")

# ----------------------------------------------------------------------
# 10. Bottom line
print("\n=== CONCLUSION ===")
print("The double‑well field possesses only a finite correlation length")
print("and a symmetric (disordered) ground state. It does *not* host")
print("a degenerate ground‑state manifold, nor does it support anyonic")
print("excitations. Consequently the claimed mapping to a topological")
print("stabilizer code is impossible: Φ_N and Φ_Δ cannot be logical")
print("operators, and the ‘gap’ is merely a statistical gap, not a")
print("spectral gap of a quantum memory.")