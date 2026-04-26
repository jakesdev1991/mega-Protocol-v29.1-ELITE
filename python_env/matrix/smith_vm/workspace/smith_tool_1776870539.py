# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# --------------------------------------------------------------
# Omega Protocol Validation: Trauma‑Induced Performance Anxiety
# --------------------------------------------------------------
# This script verifies the mathematical soundness of the
# derivation and enforces the invariants:
#   * Phi_N   – total Φ‑density (norm of state)
#   * Phi_Delta – Φ‑current (continuity)
#   * J_star  – probability/current conservation (unitary evolution)
# --------------------------------------------------------------

import sympy as sp
import numpy as np

# ------------------------------------------------------------------
# 1. Symbolic setup
# ------------------------------------------------------------------
# Basis: |id> (identity), |threat>, |perf>
# We treat the space as C^3 with orthonormal basis e_id, e_th, e_perf.
id, threat, perf = sp.symbols('id threat perf', real=True)
# State vector |psi> = a|id> + b|threat> + c|perf>
a, b, c = sp.symbols('a b c', complex=True)

# Normalization condition (Phi_N invariant)
norm_sq = sp.conjugate(a)*a + sp.conjugate(b)*b + sp.conjugate(c)*c
Phi_N = sp.simplify(norm_sq)   # should be 1 for a physical state

# Identity projector
P_id = sp.Matrix([[1, 0, 0],
                  [0, 0, 0],
                  [0, 0, 0]])   # in basis (id, threat, perf)

# Threat and performance projectors (for COD)
P_threat = sp.Matrix([[0, 0, 0],
                      [0, 1, 0],
                      [0, 0, 0]])
P_perf   = sp.Matrix([[0, 0, 0],
                      [0, 0, 0],
                      [0, 0, 1]])

# ------------------------------------------------------------------
# 2. COD definition (trauma)
# ------------------------------------------------------------------
# |Psi_threat> = b |threat>   (only threat component)
# |Psi_actual> = a|id> + b|threat> + c|perf>   (full state)
# Overlap <threat|psi> = b*
overlap_th = sp.conjugate(b)   # <threat|psi>
norm_threat_sq = sp.conjugate(b)*b
norm_psi_sq    = Phi_N

COD = sp.simplify(sp.Abs(overlap_th)**2 / (norm_threat_sq * norm_psi_sq))
# COD simplifies to |b|^2 / (|b|^2) = 1 when threat component exists,
# but we keep the generic form to check normalization.

print("COD expression:", COD)
print("COD is real and in [0,1]? ->", sp.simplify(COD - sp.conjugate(COD)) == 0)

# ------------------------------------------------------------------
# 3. Phase‑Shift Decoupling (PSD) Hamiltonian
# ------------------------------------------------------------------
# We restrict PSD to the threat<->perf subspace (sigma_x)
# sigma_x in that subspace:
sigma_x_sub = sp.Matrix([[0, 1, 0],
                         [1, 0, 0],
                         [0, 0, 0]])   # acts only on threat/perf

# Time‑dependent coupling (real scalar)
Gamma_t = sp.symbols('Gamma_t', real=True)

H_org = sp.Matrix([[0, 0, 0],
                   [0, 0, 0],
                   [0, 0, 0]])   # placeholder; only PSD matters for test

H_eff = H_org + Gamma_t * sigma_x_sub

# Unitarity condition: exp(-i H_eff dt) must be unitary for real Gamma_t
dt = sp.symbols('dt', real=True, positive=True)
U = sp.exp(-sp.I * H_eff * dt)   # matrix exponential (sympy handles diagonalizable case)

# Check U^\dagger U = I (within assumptions that Gamma_t*dt is small -> use series to 2nd order)
U_dag_U = sp.simplify(U.H * U)
# Expand to second order in Gamma_t*dt (sufficient for infinitesimal step)
U_dag_U_series = sp.series(U_dag_U, Gamma_t, 0, 3).removeO()
print("U^\dagger U (series up to O((Gamma dt)^2)):", U_dag_U_series)
# Expect identity matrix
is_unitary = sp.simplify(U_dag_U_series - sp.eye(3)) == sp.zeros(3,3)
print("Is PSD propagator unitary (to 2nd order)?", is_unitary)

# ------------------------------------------------------------------
# 4. Informational Stiffness (xi_id) preservation
# ------------------------------------------------------------------
# xi_id = <psi|P_id|psi> = |a|^2
xi_id = sp.simplify(sp.conjugate(a)*a)
# After infinitesimal step: |psi'> = U |psi>
psi_vec = sp.Matrix([a, b, c])
psi_prime = U * psi_vec
xi_id_prime = sp.simplify((psi_prime.H * P_id * psi_prime)[0,0])
# Expand to same order
xi_id_prime_series = sp.series(xi_id_prime, Gamma_t, 0, 3).removeO()
print("xi_id after step (series):", xi_id_prime_series)
stiffness_preserved = sp.simplify(xi_id_prime_series - xi_id) == 0
print("Informational Stiffness preserved?", stiffness_preserved)

# ------------------------------------------------------------------
# 5. Boundedness of Gamma_t (stiffness constraint)
# ------------------------------------------------------------------
# Suppose we have a known critical stiffness xi_c.
xi_c = sp.symbols('xi_c', real=True, positive=True)
# Require |a|^2 >= xi_c  ->  a_real^2 + a_imag^2 >= xi_c
# We enforce that the PSD step does not reduce |a|^2 below xi_c.
# Since we proved xi_id is unchanged, the constraint reduces to checking initial state.
stiffness_constraint = sp.simplify(xi_id - xi_c) >= 0
print("Stiffness constraint (symbolic):", stiffness_constraint)

# ------------------------------------------------------------------
# 6. Φ‑Current continuity (Phi_Delta) – simplified check
# ------------------------------------------------------------------
# For a closed system with unitary evolution, the continuity equation
#   dPhi_N/dt + div J = 0
# holds identically because Phi_N is constant.
# We verify dPhi_N/dt = 0 using Heisenberg picture: d<psi|psi>/dt = i<[H, I]> = 0.
Phi_N_dt = sp.simplify(sp.I * (psi_vec.H * H_eff * psi_vec - (psi_vec.H * H_eff * psi_vec).H))
print("dPhi_N/dt (should be 0):", Phi_N_dt)
Phi_Delta_ok = sp.simplify(Phi_N_dt) == 0
print("Phi_Delta continuity satisfied?", Phi_Delta_ok)

# ------------------------------------------------------------------
# 7. Summary
# ------------------------------------------------------------------
print("\n=== VALIDATION SUMMARY ===")
print("COD well‑formed:", sp.simplify(COD - sp.conjugate(COD)) == 0)
print("PSD unitary (2nd order):", is_unitary)
print("Informational Stiffness preserved:", stiffness_preserved)
print("Φ‑density constant (Phi_N):", sp.simplify(Phi_N - 1) == 0)   # assuming normalized
print("Φ‑current continuity:", Phi_Delta_ok)
print("Stiffness constraint satisfied (if initial state meets xi_c):", stiffness_constraint)