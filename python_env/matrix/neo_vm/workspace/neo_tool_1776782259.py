# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# Minimal 2D lattice (4x4) with periodic boundary conditions
L = 4
# Gauge field: random U(1) phases on links
np.random.seed(0)
U = np.exp(1j * np.random.rand(2, L, L) * 2*np.pi)  # U_mu(x)

# Naive orthogonal decomposition:
# "N" = symmetric part (average with neighbor)
# "Delta" = antisymmetric part (difference with neighbor)
def decompose(U):
    U_N = np.zeros_like(U, dtype=complex)
    U_Delta = np.zeros_like(U, dtype=complex)
    for mu in range(2):
        # neighbor in +mu direction (periodic)
        Up = np.roll(U[mu], -1, axis=mu)
        # symmetric (connectivity) mode
        U_N[mu] = 0.5 * (U[mu] + Up)
        # antisymmetric (archive) mode
        U_Delta[mu] = 0.5 * (U[mu] - Up)
    return U_N, U_Delta

U_N, U_Delta = decompose(U)

# Compute the fermion loop (polarization) via random vector estimator
# Pi_{mu,nu}(q) = < Tr[ V_mu(q) V_nu(-q) ] >, V_mu = sum_x exp(i q·x) J_mu(x)
def polarization_current(U, mu, q):
    # Simplified: J_mu(x) ~ U_mu(x) - U_mu(x)^\dagger
    J = U[mu] - np.conj(U[mu])
    # Fourier transform
    phase = np.exp(1j * (q[0]*np.arange(L)[:, None] + q[1]*np.arange(L)[None, :]))
    return np.sum(J * phase)

def compute_pi_at_q(q):
    Pi = np.zeros((2,2), dtype=complex)
    for mu in range(2):
        for nu in range(2):
            V_mu = polarization_current(U, mu, q)
            V_nu = polarization_current(U, nu, -q)
            Pi[mu,nu] = V_mu * V_nu
    return Pi

# Zero momentum
q0 = np.array([0,0])
Pi_total = compute_pi_at_q(q0)

# Now compute contributions from N and Delta sectors separately
Pi_N = np.zeros((2,2), dtype=complex)
Pi_Delta = np.zeros((2,2), dtype=complex)
for mu in range(2):
    for nu in range(2):
        V_mu_N = polarization_current(U_N, mu, q0)
        V_nu_N = polarization_current(U_N, nu, q0)
        V_mu_D = polarization_current(U_Delta, mu, q0)
        V_nu_D = polarization_current(U_Delta, nu, q0)
        Pi_N[mu,nu] = V_mu_N * V_nu_N
        Pi_Delta[mu,nu] = V_mu_D * V_nu_D

print("Total Pi(0) matrix:\n", Pi_total)
print("Pi_N(0) matrix:\n", Pi_N)
print("Pi_Delta(0) matrix:\n", Pi_Delta)
print("Trace(Pi_Delta):", np.trace(Pi_Delta).real)

# Ward identity check: q_mu * Pi_{mu,nu} should vanish
q_test = np.array([1, 0])  # non-zero momentum
Pi_q = compute_pi_at_q(q_test)
ward = q_test[0] * Pi_q[0,:] + q_test[1] * Pi_q[1,:]
print("Ward identity violation (should be ~0):", ward)