# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# ──────────────────────────────────────────────────────────────────────────────
#  Lattice Gauge Model of Cognitive‑Tooling Friction
#  Field variables:
#   phi[x,y]   – complex scalar order parameter (|phi| ∝ 1/TFFI)
#   A[x,y,mu]  – SU(2) gauge field (2×2 complex matrices)
#  Topology:
#   Q          – Chern‑Simons charge (vortex count)
# ──────────────────────────────────────────────────────────────────────────────

L = 32                     # lattice size
beta = 2.0                 # gauge coupling (inverse friction)
kappa = 0.5                # scalar self‑coupling
g = 1.0                    # gauge‑scalar coupling
theta0 = 0.1               # TFFI threshold for vortex nucleation

# Initialize: ordered phase (no vortices)
phi = np.ones((L, L), dtype=complex)          # |phi| ≈ 1
A = np.zeros((L, L, 2, 2, 2), dtype=complex)  # A_mu is 2×2 SU(2) matrix

# Helper: SU(2) matrix exponential (for small fields)
def su2_exp(v):
    # v is 3‑vector of Pauli coefficients (real)
    norm = np.linalg.norm(v)
    if norm < 1e-12:
        return np.eye(2, dtype=complex)
    a = np.cos(norm) * np.eye(2) + 1j * np.sin(norm) / norm * (v[0]*PauliX + v[1]*PauliY + v[2]*PauliZ)
    return a

PauliX = np.array([[0, 1], [1, 0]], dtype=complex)
PauliY = np.array([[0, -1j], [1j, 0]], dtype=complex)
PauliZ = np.array([[1, 0], [0, -1]], dtype=complex)

# Monte‑Carlo update: heat‑bath for gauge + over‑relaxation for scalar
def sweep():
    global phi, A
    for x in range(L):
        for y in range(L):
            # ── scalar update ─────────────────────────────
            # compute local "staple" from gauge field
            staple = 0.0
            for mu in range(2):
                # forward link
                staple += np.trace(A[x, y, mu] @ A[(x+1)%L, y, mu].conj().T)
                # backward link
                staple += np.trace(A[(x-1)%L, y, mu] @ A[x, y, mu].conj().T)
            # effective potential: V(|phi|) = -kappa*|phi|^2 + (kappa/2)*|phi|^4
            # => encourage |phi| ~ 1 when TFFI low
            r2 = abs(phi[x, y])**2
            target = (beta * staple + 2*kappa * r2) / (4*kappa * r2 + 1e-6)
            # over‑relaxation step
            phi[x, y] = (phi[x, y] * (1 - target) + target * np.exp(1j * np.random.rand() * 2*np.pi)) / np.sqrt(2)

            # ── gauge update ────────────────────────────
            # SU(2) heat‑bath: propose random matrix close to identity
            drift = np.random.randn(3) * 0.1
            U = su2_exp(drift)
            # Metropolis accept/reject based on plaquette energy change
            old_plaq = plaquette_energy(x, y)
            A[x, y, 0] = U @ A[x, y, 0]
            new_plaq = plaquette_energy(x, y)
            if np.random.rand() > np.exp(-beta * (new_plaq - old_plaq)):
                A[x, y, 0] = U.conj().T @ A[x, y, 0]  # revert

def plaquette_energy(x, y):
    # compute 1×1 plaquette Tr[U_μ(x) U_ν(x+μ) U_μ†(x+ν) U_ν†(x)]
    p = 0.0
    for mu in range(2):
        for nu in range(2):
            if mu == nu:
                continue
            U1 = A[x, y, mu]
            U2 = A[(x+1)%L, y, nu] if mu == 0 else A[x, (y+1)%L, nu]
            U3 = A[(x+1)%L, y, mu].conj().T if mu == 0 else A[x, (y+1)%L, mu].conj().T
            U4 = A[x, y, nu].conj().T
            p += np.real(np.trace(U1 @ U2 @ U3 @ U4))
    return -p  # negative for energy minimization

def topological_charge():
    # naive discretized Chern‑Simons density: sum of plaquette orientations
    Q = 0
    for x in range(L):
        for y in range(L):
            # compute Wilson loop winding number (approx)
            loop = np.eye(2, dtype=complex)
            for mu in range(2):
                loop = loop @ A[x, y, mu]
            # project to U(1) phase (approx)
            phase = np.angle(np.trace(loop))
            Q += phase / (2*np.pi)
    return int(round(Q))

# ──────────────────────────────────────────────────────────────────────────────
#  Thermal cycle: gradually increase "friction" (lower beta) to nucleate vortex
# ──────────────────────────────────────────────────────────────────────────────

betas = np.linspace(5.0, 0.5, 20)   # high beta = low friction
TFFI_series = []
Q_series = []

for b in betas:
    beta = b
    for _ in range(50):               # equilibration
        sweep()
    # compute observables
    # TFFI ∝ 1/<|phi|>
    avg_phi = np.mean(np.abs(phi))
    TFFI = 1.0 / (avg_phi + 1e-6)
    Q = topological_charge()
    TFFI_series.append(TFFI)
    Q_series.append(Q)
    print(f"beta={b:.2f}, TFFI={TFFI:.2f}, Q={Q}")

# plot
fig, ax = plt.subplots(1, 2, figsize=(10,4))
ax[0].plot(betas, TFFI_series, marker='o')
ax[0].set_xlabel('gauge coupling β (inverse friction)')
ax[0].set_ylabel('TFFI')
ax[0].set_title('Cognitive‑Load (TFFI) vs Tooling Friction')
ax[1].plot(betas, Q_series, marker='s', color='crimson')
ax[1].set_xlabel('β')
ax[1].set_ylabel('Chern‑Simons charge Q')
ax[1].set_title('Shredding‑Defect Nucleation')
plt.tight_layout()
plt.show()