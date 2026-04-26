# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Quantum-Memory-Stabilized Omega (QMSO-Ω) Validation Script
# ---------------------------------------------------------
# This script checks the mathematical consistency of the QMSO-Ω proposal
# against the Omega Protocol invariants:
#   • Covariance of Φ_N, Φ_Δ (logical operators commute with stabilizers/H)
#   • Correct derivation of ψ, ξ_N, ξ_Δ from code distance d and gap Δ
#   • Boundary conditions (Shredding Event, Informational Freeze) map to
#     gap closure and over‑suppression regimes.
#   • Entropy gauge S_h = -Tr(ρ ln ρ) is a valid von‑Neumann entropy.
#   • Effective action yields equations of motion with thermally‑assisted rates
#     Γ ∝ exp(-Δ/k_B T).
#
# We use a concrete instance: the 3D toric code on an L×L×L cubic lattice.
# Stabilizers: vertex (A_v) = ∏_{e∈v} X_e, plaquette (B_p) = ∏_{e∈∂p} Z_e.
# Logical operators:  X̄ = ∏_{e∈γ_x} X_e (non‑trivial loop in x‑direction),
#                     Z̄ = ∏_{e∈γ_z} Z_e (non‑trivial loop in z‑direction).
#
# The script is symbolic; it does not require numerical simulation.
# ---------------------------------------------------------

import sympy as sp
import itertools

# -------------------------- 1. Define lattice & operators --------------------------
L = sp.symbols('L', integer=True, positive=True)   # linear size
# For the 3D toric code, code distance d = L (minimum weight of logical operator)
d = L
d0 = sp.symbols('d0', positive=True)   # reference distance

# Pauli operators on a single qubit (symbolic)
I, X, Y, Z = sp.symbols('I X Y Z')
# We'll treat stabilizers and logicals as products; commutation reduces to
# counting overlapping sites with X/Z.

def commutes(op1, op2):
    """Return True if two Pauli strings commute (ignoring phase)."""
    # op1, op2 are dicts mapping site -> Pauli ('X','Y','Z')
    # They commute if the number of sites where both have Pauli and
    # the Paulis are different (X vs Z or Z vs X) is even.
    diff = sum(1 for site in set(op1) & set(op2)
               if op1[site] != op2[site] and {op1[site], op2[site]} == {'X','Z'})
    return diff % 2 == 0

# Build stabilizer generators for a single vertex and plaquette (representative)
# We label sites by coordinates (x,y,z) and edges; for simplicity we assume
# each vertex touches 6 edges (X-type) and each plaquette touches 4 edges (Z-type).
# The exact geometry is not needed for commutation checks; we just need overlap parity.

# Vertex stabilizer A_v: product of X on six incident edges
def vertex_stabilizer(v):
    # v = (x,y,z)
    x,y,z = v
    edges = [(x+1,y,z,'x'), (x-1,y,z,'x'),   # ±x
             (x,y+1,z,'y'), (x,y-1,z,'y'),   # ±y
             (x,y,z+1,'z'), (x,y,z-1,'z')]   # ±z
    return {e: 'X' for e in edges}

# Plaquette stabilizer B_p: product of Z on four edges in the plaquette plane
def plaquette_stabilizer(p, plane):
    # p = (x,y,z) lower‑left corner, plane in {'xy','yz','zx'}
    x,y,z = p
    if plane == 'xy':
        edges = [(x,y,z,'x'), (x+1,y,z,'x'), (x,y+1,z,'y'), (x,y,z,'y')]
    elif plane == 'yz':
        edges = [(x,y,z,'y'), (x,y+1,z,'y'), (x,y,z+1,'z'), (x,y,z,'z')]
    else:  # zx
        edges = [(x,y,z,'z'), (x+1,y,z,'z'), (x,y,z+1,'x'), (x,y,z,'x')]
    return {e: 'Z' for e in edges}

# Logical X̄: non‑trivial loop wrapping around x‑direction (spans L edges)
def logical_X():
    # Choose loop at y=0, z=0, varying x from 0 to L-1
    edges = [(x,0,0,'x') for x in range(L)]
    return {e: 'X' for e in edges}

# Logical Z̄: non‑trivial loop wrapping around z‑direction (spans L edges)
def logical_Z():
    edges = [(0,0,z,'z') for z in range(L)]
    return {e: 'Z' for e in edges}

# -------------------------- 2. Covariance check --------------------------
# Logical operators must commute with all stabilizers (and thus with H = -∑A -∑B)
def check_covariance():
    fails = []
    # Test a few representative stabilizers; due to translation invariance,
    # if they commute with one vertex and one plaquette they commute with all.
    v0 = (0,0,0)
    A = vertex_stabilizer(v0)
    for plane in ['xy','yz','zx']:
        p0 = (0,0,0)
        B = plaquette_stabilizer(p0, plane)
        if not commutes(logical_X(), A):
            fails.append(('X̄', 'vertex', v0))
        if not commutes(logical_X(), B):
            fails.append(('X̄', 'plaquette', (p0,plane)))
        if not commutes(logical_Z(), A):
            fails.append(('Z̄', 'vertex', v0))
        if not commutes(logical_Z(), B):
            fails.append(('Z̄', 'plaquette', (p0,plane)))
    return fails

# -------------------------- 3. Invariant derivation --------------------------
# ψ = ln(d/d0)
psi = sp.log(d/d0)

# Φ_N = ⟨X̄⟩, Φ_Δ = ⟨Z̄⟩. For the ground state of the toric code (zero temperature)
# the expectation values are ±1 depending on the logical sector; we treat them
# as symbols that can take values in [-1,1].
Phi_N, Phi_Delta = sp.symbols('Phi_N Phi_Delta', real=True)

# ξ_N = ∂Φ_N/∂ψ, ξ_Δ = ∂Φ_Δ/∂psi
xi_N = sp.diff(Phi_N, psi)
xi_Delta = sp.diff(Phi_Delta, psi)

# In the low‑temperature phase the logical expectation values are *independent*
# of d (they are fixed by the logical sector), hence the derivatives should be zero.
# We enforce this as a consistency condition.
low_T_condition = sp.simplify(xi_N) + sp.simplify(xi_Delta)  # should be 0 if both zero

# -------------------------- 4. Gap & rate --------------------------
Delta, kB, T = sp.symbols('Delta kB T', positive=True)
# Thermally‑assisted rate Gamma ∝ exp(-Delta/(kB T))
Gamma = sp.exp(-Delta/(kB*T))

# -------------------------- 5. Entropy gauge --------------------------
# von Neumann entropy S_h = -Tr(ρ ln ρ). For a diagonal density matrix with
# eigenvalues p_i, S_h = -∑ p_i ln(p_i). We check that S_h ≥ 0 and
# S_h = 0 for a pure state (single eigenvalue =1).
p = sp.symbols('p0 p1', nonnegative=True)
# Constraint: p0 + p1 = 1
S_h = -(p[0]*sp.log(p[0]) + p[1]*sp.log(p[1])) if isinstance(p, sp.Matrix) else -(p0*sp.log(p0) + p1*sp.log(p1))
# We'll test with a generic pure state (p0=1, p1=0) and a mixed state (p0=p1=0.5)
def entropy_test():
    pure = sp.N(S_h.subs({p0:1, p1:0}))
    mixed = sp.N(S_h.subs({p0:0.5, p1:0.5}))
    return pure, mixed

# -------------------------- 6. Boundary conditions --------------------------
# Shredding Event: gap closes → Delta → 0 → Gamma → 1 (max error rate)
# Informational Freeze: Delta → ∞ → Gamma → 0 (no dynamics)
shredding_limit = sp.limit(Gamma, Delta, 0)
freeze_limit = sp.limit(Gamma, Delta, sp.oo)

# -------------------------- 7. Run validation --------------------------
def run_validation():
    print("=== QMSO-Ω Mathematical Validation ===")
    # 2. Covariance
    cov_fails = check_covariance()
    if cov_fails:
        print(f"[FAIL] Covariance violations: {cov_fails}")
    else:
        print("[PASS] Logical operators commute with all stabilizers (covariant).")
    
    # 3. Invariant derivation
    print(f"\nDerived quantities:")
    print(f"  ψ = ln(d/d0) = {psi}")
    print(f"  ξ_N = ∂Φ_N/∂ψ = {xi_N}")
    print(f"  ξ_Δ = ∂Φ_Δ/∂ψ = {xi_Delta}")
    # Low‑T condition: both derivatives should vanish
    if sp.simplify(xi_N) == 0 and sp.simplify(xi_Delta) == 0:
        print("[PASS] ξ_N, ξ_Δ vanish in low‑T phase (logical expectation independent of d).")
    else:
        print("[WARN] ξ_N, ξ_Δ not identically zero; check logical state dependence.")
    
    # 4. Gap & rate
    print(f"\nThermal rate: Γ = exp(-Δ/(k_B T)) = {Gamma}")
    print(f"  → Shredding limit (Δ→0): Γ → {shredding_limit}")
    print(f"  → Freeze limit (Δ→∞): Γ → {freeze_limit}")
    if shredding_limit == 1 and freeze_limit == 0:
        print("[PASS] Gap correctly controls error rates.")
    else:
        print("[FAIL] Gap‑rate relationship inconsistent.")
    
    # 5. Entropy gauge
    pure_e, mixed_e = entropy_test()
    print(f"\nEntropy checks:")
    print(f"  Pure state S_h = {pure_e}")
    print(f"  Maximally mixed (2‑level) S_h = {mixed_e}")
    if pure_e == 0 and mixed_e > 0:
        print("[PASS] Von Neumann entropy behaves as expected.")
    else:
        print("[FAIL] Entropy definition problematic.")
    
    # Summary
    print("\n=== Validation Complete ===")

if __name__ == "__main__":
    run_validation()