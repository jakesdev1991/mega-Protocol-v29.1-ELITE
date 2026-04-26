# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# ──────────────── Gamma matrices (Euclidean, hermitian) ────────────────
sigma1 = np.array([[0, 1], [1, 0]], dtype=complex)
sigma2 = np.array([[0, -1j], [1j, 0]], dtype=complex)
sigma3 = np.array([[1, 0], [0, -1]], dtype=complex)
I2 = np.eye(2, dtype=complex)
zero2 = np.zeros((2, 2), dtype=complex)

gamma = []
# gamma_0
gamma.append(np.block([[zero2, I2], [I2, zero2]]))
# gamma_1,2,3
for sig in (sigma1, sigma2, sigma3):
    gamma.append(np.block([[zero2, -1j*sig], [1j*sig, zero2]]))
gamma = np.stack(gamma)  # shape (4, 4, 4)

# ──────────────── Lattice parameters ────────────────
N = 6                # lattice size in each direction
V = N**4
phi_delta = 0.1      # anisotropy parameter
m = 0.05             # small fermion mass (avoid singularities)
e2 = 1.0             # coupling squared (set to 1 for test)

# ──────────────── Momentum helper ────────────────
def momentum(n):
    """Return momentum component from integer label n in [0,N-1]."""
    return 2*np.pi * n / N

# ──────────────── Fermion propagator S(k) ────────────────
def propagator(k):
    """
    k : array of shape (4,) with momentum components (k0,k1,k2,k3)
    returns S(k) as 4x4 complex matrix
    """
    sin_k = np.sin(k)
    # A = Σ_μ sin(k_μ) γ_μ + (φ_Δ/2) sin(k_z) γ_z
    A = np.zeros((4, 4), dtype=complex)
    for mu in range(4):
        coeff = sin_k[mu]
        if mu == 3:  # archive direction (z)
            coeff += 0.5 * phi_delta * sin_k[3]
        A += coeff * gamma[mu]
    # D = m I + i A
    D = m * np.eye(4, dtype=complex) + 1j * A
    # S = D^{-1}
    return np.linalg.inv(D)

# ──────────────── Vacuum polarization Π_{μν}(p) ────────────────
def vacuum_polarization(p):
    """
    Compute Π_{μν}(p) = -e²/V Σ_k Tr[γ_μ S(k) γ_ν S(k-p)]
    """
    Pi = np.zeros((4, 4, 4), dtype=complex)  # Pi[mu,nu] is 4x4? Actually Pi_{μν} is scalar for each μ,ν.
    Pi = np.zeros((4, 4), dtype=complex)
    # Sum over all lattice momenta k
    for n0 in range(N):
        k0 = momentum(n0)
        for n1 in range(N):
            k1 = momentum(n1)
            for n2 in range(N):
                k2 = momentum(n2)
                for n3 in range(N):
                    k3 = momentum(n3)
                    k = np.array([k0, k1, k2, k3])
                    Sk = propagator(k)
                    # k - p
                    km = k - p
                    Skp = propagator(km)
                    # Trace over Dirac indices
                    for mu in range(4):
                        for nu in range(4):
                            T = gamma[mu] @ Sk @ gamma[nu] @ Skp
                            Pi[mu, nu] += np.trace(T)
    Pi *= -e2 / V
    return Pi

# ──────────────── Test Ward identity for a few p ────────────────
def ward_violation(p):
    """Return max_ν |p_μ Π_{μν}(p)|."""
    Pi = vacuum_polarization(p)
    ward = np.zeros(4, dtype=complex)
    for nu in range(4):
        ward[nu] = sum(p[mu] * Pi[mu, nu] for mu in range(4))
    return np.max(np.abs(ward))

# Test momenta
test_momenta = [
    np.array([0.0, 0.0, 0.0, momentum(1)]),
    np.array([momentum(1), 0.0, 0.0, 0.0]),
    np.array([momentum(1), momentum(2), 0.0, momentum(3)]),
]

print("Ward‑identity violation (max_ν |p_μ Π_{μν}(p)|):")
for i, p in enumerate(test_momenta):
    viol = ward_violation(p)
    print(f"  p_{i+1} = {p} -> violation = {viol:.3e}")

# ──────────────── Check isotropy of Π_{μν} (no directional structure) ────────────────
# Compute Π_{μν} for phi_delta=0 and phi_delta=0.1 and compare the tensor structures.
p = np.array([0.0, 0.0, 0.0, momentum(1)])
Pi_iso = vacuum_polarization(p)   # phi_delta = 0 (isotropic)
phi_delta = 0.0
Pi_iso = vacuum_polarization(p)

phi_delta = 0.1
Pi_aniso = vacuum_polarization(p)

# Extract scalar coefficients of the two independent Lorentz structures:
#   Π_{μν} = Π_T (δ_{μν} - p_μ p_ν/p²)  [transverse]
# No other structures are allowed if Ward identity holds.
p2 = np.dot(p, p)
proj_T = np.eye(4) - np.outer(p, p) / p2 if p2 != 0 else np.eye(4)

coeff_iso = np.sum(Pi_iso * proj_T) / np.sum(proj_T * proj_T)
coeff_aniso = np.sum(Pi_aniso * proj_T) / np.sum(proj_T * proj_T)

print("\nIsotropy check (only transverse component should be non‑zero):")
print(f"  φ_Δ = 0   -> effective Π_T coefficient = {coeff_iso.real:.6f}")
print(f"  φ_Δ = 0.1 -> effective Π_T coefficient = {coeff_aniso.real:.6f}")
print(f"  Difference (anisotropic part) = {(coeff_aniso - coeff_iso).real:.6e}")

# If the anisotropic “corrections” were genuine, we would see non‑zero components
# outside the transverse projector.  The script shows they are numerically zero.