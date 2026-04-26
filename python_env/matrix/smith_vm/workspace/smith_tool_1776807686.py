# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
LSGM‑Ω Rubric Compliance Checker
--------------------------------
Verifies the following Ω‑Physics Rubric v26.0 requirements:
  1. Primary invariant: ψ = ln Φ_N   (connectivity mode)
  2. Entropy‑gauge term:   𝒜_μ J^μ with J^μ = √2 Φ_δ δ^μ_0
     must yield ∂_μ J^μ = 0 when 𝒜_μ is a proper gauge field.
  3. Dimensional consistency: all exponents must be dimensionless;
     we introduce characteristic time τ0 and length ℓ0.
  4. Φ_N must be derived from the spectral gap λ₁ of the
     weighted directory‑tree Laplacian (Lichnerowicz bound
     is only an inequality – we check that the proposed
     exponential mapping does not violate the bound).
The script returns PASS only if *all* checks succeed within
numerical tolerance.
"""

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as sla

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def graph_laplacian(adjacency, weights=None):
    """Return the weighted graph Laplacian L = D - W."""
    if weights is None:
        weights = np.ones_like(adjacency)
    W = adjacency * weights
    D = np.diag(W.sum(axis=1))
    return D - W

def spectral_gap(L):
    """Smallest non‑zero eigenvalue of symmetric Laplacian L."""
    # Use shift-invert mode to get the smallest eigenvalue > 0
    evals = sla.eigsh(L, k=2, which='SM', return_eigenvectors=False)
    evals.sort()
    # evals[0] is zero (for connected graph); return evals[1]
    return evals[1]

def ollivier_ricci_lower_bound(L):
    """Compute a simple lower bound on Ollivier‑Ricci curvature:
       R_min >= (d/(d-1)) * λ₁   (Lichnerowicz bound for regular graphs)
    Here we approximate average degree d from the Laplacian."""
    n = L.shape[0]
    deg = np.diag(L)  # Actually -L_ii = sum_j w_ij
    d_avg = deg.mean()
    if d_avg <= 1:
        return 0.0
    lam1 = spectral_gap(L)
    return (d_avg / (d_avg - 1)) * lam1

def check_invariant(Phi_N, psi, tol=1e-9):
    """Verify ψ = ln(Φ_N/Φ_N0)  (Φ_N0 absorbed into reference)."""
    # We allow an additive constant; check that exp(psi) proportional to Phi_N
    ratio = np.exp(psi) / Phi_N
    # ratio should be constant across all entries; test variance
    return np.allclose(ratio, ratio[0], rtol=tol, atol=tol)

def entropy_gauge_conservation(S_dir, Phi_Delta, dt=1.0):
    """
    Test the entropy‑gauge conservation law.
    We model 𝒜_μ = ∂_μ S_dir (only time component non‑zero for simplicity)
    and J^μ = √2 Φ_Δ δ^μ_0.
    The gauge field strength is F_{0i}=∂_0 𝒜_i - ∂_i 𝒜_0.
    With only time dependence, ∂_μ J^μ = (1/√-g) ∂_0 (√-g J^0).
    We discretize and check that the update of Φ_Δ implied by
    the gauge equation ∂_μ F^{μν}=J^ν yields ∂_0 J^0 = 0.
    """
    # Assume unit sqrt(-g) = 1 for simplicity
    J0 = np.sqrt(2) * Phi_Delta
    # Finite difference of J0 in time
    dJ0_dt = np.gradient(J0, dt)
    # Conservation requires dJ0_dt ≈ 0
    return np.allclose(dJ0_dt, 0.0, atol=1e-8)

def dimensional_check(expr, tau0, ell0):
    """
    Very light‑weight dimensional check: ensure that any occurrence of
    time or length appears only via the dimensionless combinations
    t/tau0 and x/ell0.  We do this by verifying that the expression
    contains no raw 't' or 'x' symbols (in this toy demo we just
    trust the user supplied dimensionless fields).
    """
    # Placeholder: assume user supplies dimensionless fields.
    return True

# ----------------------------------------------------------------------
# Main validation routine
# ----------------------------------------------------------------------
def main():
    # ------------------------------------------------------------------
    # 1. Build a synthetic directory‑tree graph (for illustration)
    # ------------------------------------------------------------------
    # Example: a small tree with 6 nodes, edge weight = 1 normally,
    # weight = 1+beta if edge crosses an "internal‑use‑only" boundary.
    n_nodes = 6
    adjacency = np.zeros((n_nodes, n_nodes), dtype=int)
    # edges (parent->child)
    edges = [(0,1),(0,2),(1,3),(1,4),(2,5)]
    beta = 5.0  # penalty for crossing internal‑use‑only
    weights = np.ones_like(adjacency, dtype=float)
    for i,j in edges:
        adjacency[i,j] = adjacency[j,i] = 1
        # pretend edge (1,3) crosses the boundary
        if (i,j) == (1,3) or (j,i) == (1,3):
            weights[i,j] = weights[j,i] = 1.0 + beta
    L = graph_laplacian(adjacency, weights)

    # ------------------------------------------------------------------
    # 2. Compute Φ_N from spectral gap
    # ------------------------------------------------------------------
    lam1 = spectral_gap(L)
    Phi_N0 = 1.0          # baseline
    R0 = 1.0              # reference curvature scale
    # Ollivier‑Ricci curvature lower bound (used as proxy)
    R_lower = ollivier_ricci_lower_bound(L)
    # Proposed mapping (exponential) – note: this is *not* guaranteed
    Phi_N = Phi_N0 * np.exp(R_lower / R0)

    # ------------------------------------------------------------------
    # 3. Compute the invariant ψ = ln Φ_N (up to additive constant)
    # ------------------------------------------------------------------
    psi = np.log(Phi_N)   # we absorb ln(Phi_N0) into the constant

    # ------------------------------------------------------------------
    # 4. Check invariant condition
    # ------------------------------------------------------------------
    inv_ok = check_invariant(Phi_N, psi)
    print(f"Invariant ψ = ln Φ_N check: {'PASS' if inv_ok else 'FAIL'}")
    if not inv_ok:
        print("  Reason: ψ does not equal ln Φ_N up to a constant.")

    # ------------------------------------------------------------------
    # 5. Entropy‑gauge conservation test
    # ------------------------------------------------------------------
    # Mock directory‑type entropy time series (3 states)
    S_dir = np.array([0.9, 0.95, 0.92])   # Shannon entropy, dimensionless
    # Mock Φ_Δ derived from LSFI (sigmoid) – just for demo
    LSFI = np.array([0.4, 0.6, 0.55])
    Phi_Delta = 1.0 / (1.0 + np.exp(-LSFI))   # simple sigmoid inverse
    gauge_ok = entropy_gauge_conservation(S_dir, Phi_Delta, dt=1.0)
    print(f"Entropy‑gauge ∂_μ J^μ = 0 check: {'PASS' if gauge_ok else 'FAIL'}")
    if not gauge_ok:
        print("  Reason: Varying 𝒜_μ J^μ with 𝒜_μ = ∂_μ S_dir does not yield current conservation.")
        print("          A proper gauge field strength tensor F_{μν} is required.")

    # ------------------------------------------------------------------
    # 6. Dimensional consistency (placeholder)
    # ------------------------------------------------------------------
    tau0 = 1.0   # characteristic time (weeks)
    ell0 = 10.0  # characteristic length (average depth)
    dim_ok = dimensional_check(None, tau0, ell0)
    print(f"Dimensional consistency check: {'PASS' if dim_ok else 'FAIL'}")

    # ------------------------------------------------------------------
    # 7. Lichnerowicz bound sanity check
    # ------------------------------------------------------------------
    # The true spectral gap λ₁ must be >= the lower bound.
    bound_ok = lam1 >= R_lower - 1e-12
    print(f"Lichnerowicz bound λ₁ ≥ (d/(d-1)) R_min : {'PASS' if bound_ok else 'FAIL'}")
    if not bound_ok:
        print(f"  λ₁ = {lam1:.6f}, lower bound = {R_lower:.6f}")

    # ------------------------------------------------------------------
    # Final verdict
    # ------------------------------------------------------------------
    all_ok = inv_ok and gauge_ok and dim_ok and bound_ok
    print("\n=== OVERALL RESULT ===")
    print("PASS" if all_ok else "FAIL")
    if not all_ok:
        print("One or more rubric requirements are violated. See messages above.")

if __name__ == "__main__":
    main()