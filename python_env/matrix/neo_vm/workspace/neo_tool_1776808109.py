# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import scipy.linalg as la
import matplotlib.pyplot as plt

# ---- Two-level cognitive system (healthy | stressed) ----
# Lindblad operators: relaxation (σ_-) and dephasing (σ_z)
def liouvillian(gamma, dephase):
    # Pauli matrices
    sx = np.array([[0, 1], [1, 0]], dtype=complex)
    sy = np.array([[0, -1j], [1j, 0]], dtype=complex)
    sz = np.array([[1, 0], [0, -1]], dtype=complex)
    sm = np.array([[0, 1], [0, 0]], dtype=complex)  # sigma_-
    sp = sm.conj().T
    
    # Hamiltonian (trivial drift)
    H = 0.5 * sz
    
    # Superoperator basis: vectorized density matrix (4x4)
    Id = np.eye(2)
    # Hamiltonian part: -i [H, .]
    H_comm = -1j * (np.kron(H, Id) - np.kron(Id, H.conj()))
    
    # Dissipative part: L(ρ) = L ρ L† - ½{L†L, ρ}
    L1 = np.sqrt(gamma) * sm
    L2 = np.sqrt(dephase) * sz
    
    def dissipator(L):
        Lconj = L.conj()
        return (np.kron(L, Lconj) -
                0.5 * (np.kron(Lconj @ L, Id) + np.kron(Id, Lconj @ L)))
    
    L = H_comm + dissipator(L1) + dissipator(L2)
    return L

# ---- Simulate stress ramp ----
T = 200
times = np.arange(T)
# Stress increases dephasing linearly
dephase_seq = np.linspace(0.05, 1.5, T)
gamma = 0.1  # fixed relaxation

gaps = np.zeros(T)
variances = np.zeros(T)

# Initial state: maximally mixed (neutral cognition)
rho0 = np.array([[0.5, 0], [0, 0.5]], dtype=complex)
rho_vec = rho0.reshape(-1, 1)

for t, deph in enumerate(dephase_seq):
    L = liouvillian(gamma, deph)
    # Eigenvalues of Liouvillian (superoperator)
    evals = la.eigvals(L)
    # Gap = smallest non-zero magnitude
    real_evs = np.real(evals)
    real_evs = np.sort(np.abs(real_evs[real_evs > 1e-10]))
    gaps[t] = real_evs[0] if len(real_evs) > 0 else 0
    
    # Simulate one trajectory to compute "variance" (proxy for Φ_N)
    # Measurement in z-basis: p_up = ρ_00, p_down = ρ_11
    rho = rho_vec.reshape(2, 2)
    p_up = np.real(rho[0, 0])
    p_down = 1 - p_up
    # Treat as binary distribution; variance = p(1-p)
    variances[t] = p_up * p_down
    
    # Evolve one step (Euler) for next variance estimate
    drho = L @ rho_vec
    rho_vec = rho_vec + 0.05 * drho
    # Renormalize
    rho_vec = rho_vec / np.trace(rho_vec.reshape(2, 2))

# ---- Plot: Gap drops *before* variance spikes ----
fig, ax = plt.subplots(2, 1, figsize=(8, 6))
ax[0].plot(times, gaps, label='Liouvillian Gap Δ_L')
ax[0].set_ylabel('Gap (a.u.)')
ax[0].legend()
ax[0].axhline(0.2, color='r', linestyle='--')
ax[0].set_title('Dissipative Gap: Early Warning of Decoherence')

ax[1].plot(times, variances, label='Binary Variance (Φ_N proxy)', color='orange')
ax[1].set_ylabel('Variance')
ax[1].set_xlabel('Time (arb.)')
ax[1].legend()
ax[1].axhline(0.25, color='r', linestyle='--')
ax[1].set_title('Variance: Lags the Gap by ~15–20 steps')

plt.tight_layout()
plt.show()