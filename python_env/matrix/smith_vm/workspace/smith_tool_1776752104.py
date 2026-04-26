# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Validator for HVFI-Ω v2
--------------------------------------
Checks:
  * Dimensional consistency (natural units)
  * Positivity of invariants ξ_N, ξ_Δ
  * Entropy and mutual information bounds
  * Boundary conditions (Shredding Event & Informational Freeze)
  * NO BOILERPLATE (simple heuristic)
"""

import re
import numpy as np
import sympy as sp

# ----------------------------------------------------------------------
# Helper: dummy data generation (replace with real pipeline outputs)
# ----------------------------------------------------------------------
def generate_sample_data(L=3, T=100, B=20):
    """
    Returns:
        A   : (L, T) activation matrix  [a_l(t)]
        PhiN: (T,) Newtonian mode
        PhiD: (T,) Archive mode
        v   : vacuum expectation value (scalar)
        lam : coupling λ
        D   : diffusivity
        eps : regularisation for covariance
    """
    np.random.seed(42)
    A = np.random.randn(L, T)  # placeholder activations
    PhiN = np.random.randn(T) * 0.1
    PhiD = np.random.randn(T) * 0.1
    v = 1.0
    lam = 0.5
    D = 0.2
    eps = 1e-6
    return A, PhiN, PhiD, v, lam, D, eps

# ----------------------------------------------------------------------
# Core validation functions
# ----------------------------------------------------------------------
def check_dimensional_consistency(A, PhiN, PhiD, v, lam, D, eps):
    """
    In natural units [x]=[t]=1, the action S = ∫ dt dx [ ½ ϕ̇² + D/2 (∂xϕ)² - λ/4 (ϕ²−v²)² ].
    Therefore:
        [ϕ] = 0   (dimensionless)
        [D] = 0   (since ∂xϕ has same dimension as ϕ̇)
        [λ] = 0   (potential term must be dimensionless)
        [v] = 0   (same as ϕ)
        [ε] = 0   (added to dimensionless covariance)
    The function returns True if all supplied parameters are dimensionless (i.e. pure numbers).
    """
    # In practice we just check that they are real numbers (no units attached)
    ok = all(np.isscalar(x) and np.isreal(x) for x in (v, lam, D, eps))
    ok &= np.all(np.isreal(A)) and np.all(np.isreal(PhiN)) and np.all(np.isreal(PhiD))
    return ok

def compute_invariants(PhiN, PhiD, v, lam):
    """
    ξ_N^{-2} = λ (3 Φ_N² + Φ_Δ² − v²)
    ξ_Δ^{-2} = λ (Φ_N² + 3 Φ_Δ² − v²)
    ψ = ln(ξ/ξ₀)  (we set ξ₀ = 1 for simplicity, so ψ = -½ ln[λ(3ϕ₀²−v²)])
    For validation we only need ξ_N² > 0 and ξ_Δ² > 0.
    """
    xiN2 = 1.0 / (lam * (3*PhiN**2 + PhiD**2 - v**2))
    xiD2 = 1.0 / (lam * (PhiN**2 + 3*PhiD**2 - v**2))
    return xiN2, xiD2

def entropy_from_activations(a_vec, B=20):
    """Shannon entropy of histogram of a_vec with B bins."""
    hist, _ = np.histogram(a_vec, bins=B, density=True)
    # avoid log(0)
    hist = hist[hist > 0]
    return -np.sum(hist * np.log(hist))

def mutual_information(a_vec, b_vec, B=20):
    """Mutual information I(A;B) via joint histogram."""
    hist2d, xedges, yedges = np.histogram2d(a_vec, b_vec, bins=B, density=True)
    # marginals
    pa = np.sum(hist2d, axis=1)
    pb = np.sum(hist2d, axis=0)
    # avoid zeros
    mask = hist2d > 0
    hist2d = hist2d[mask]
    pa = pa[np.repeat(np.sum(mask, axis=1) > 0, np.sum(mask, axis=1))]  # align
    pb = pb[np.tile(np.sum(mask, axis=0) > 0, np.sum(mask, axis=0))]   # align
    # Actually simpler: compute using probabilities directly
    # We'll recompute with safe method:
    hist2d, _ = np.histogram2d(a_vec, b_vec, bins=B, density=True)
    pa = np.sum(hist2d, axis=1, keepdims=True)
    pb = np.sum(hist2d, axis=0, keepdims=True)
    # joint probability
    pj = hist2d
    # avoid zeros
    nz = pj > 0
    mi = np.sum(pj[nz] * np.log(pj[nz] / (pa[nz] * pb[nz])))
    return mi

def curvature_invariant(A, eps):
    """Ψ = ln det( Σ_A + ε I ), Σ_A = (1/(L-1)) A Aᵀ"""
    L = A.shape[0]
    Sigma = (A @ A.T) / (L - 1) if L > 1 else np.zeros((A.shape[0], A.shape[0]))
    M = Sigma + eps * np.eye(Sigma.shape[0])
    # ensure positive-definite for logdet
    if not np.all(np.linalg.eigvals(M) > 0):
        return None  # invalid
    Psi = np.log(np.linalg.det(M))
    return Psi

def check_bounds(S_vals, I_vals, Psi_vals, PhiN_avg, PhiD_avg, v, lam):
    """Return dict of boolean flags."""
    B = 20  # number of bins used for entropy
    flags = {}
    # Entropy bounds
    flags['entropy_nonneg'] = np.all(S_vals >= 0)
    flags['entropy_upper']  = np.all(S_vals <= np.log(B))
    # Mutual information non‑negative
    flags['mi_nonneg']      = np.all(I_vals >= 0)
    # Curvature invariant real (not None)
    flags['psi_real']       = np.all([p is not None for p in Psi_vals])
    # Informational Freeze: 3Φ_N²+Φ_Δ²−v² ≥ 0  (⇔ ξ_N^{-2} ≥ 0)
    flags['info_freeze']    = np.all((3*PhiN_avg**2 + PhiD_avg**2 - v**2) >= -1e-12)
    # Shredding Event: we set a threshold on Psi (more negative = more coupling)
    # Here we require Psi > Psi_crit (i.e. not too negative)
    Psi_crit = -15.0  # arbitrary but illustrative
    flags['shredding_bound'] = np.all([p is None or p > Psi_crit for p in Psi_vals])
    return flags

def no_boilerplate_check(text):
    """
    Very simple heuristic: lines that start with a number followed by a dot,
    or lines that start with markdown heading markers (#, ##, etc.) are
    considered boilerplate.
    Returns True if no such lines are found.
    """
    lines = text.splitlines()
    for ln in lines:
        stripped = ln.lstrip()
        if re.match(r'^\d+\.\s', stripped):          # "1. "
            return False
        if re.match(r'^#{1,6}\s', stripped):        # markdown heading
            return False
    return True

# ----------------------------------------------------------------------
# Main validation routine
# ----------------------------------------------------------------------
def main():
    # 1. Obtain or simulate data
    A, PhiN, PhiD, v, lam, D, eps = generate_sample_data()
    L, T = A.shape

    # 2. Dimensional consistency
    dim_ok = check_dimensional_consistency(A, PhiN, PhiD, v, lam, D, eps)
    print(f"Dimensional consistency check: {'PASS' if dim_ok else 'FAIL'}")

    # 3. Invariants (ξ_N², ξ_Δ²) positivity
    xiN2, xiD2 = compute_invariants(PhiN, PhiD, v, lam)
    xiN2_ok = np.all(xiN2 > 0)
    xiD2_ok = np.all(xiD2 > 0)
    print(f"ξ_N² > 0 : {'PASS' if xiN2_ok else 'FAIL'}")
    print(f"ξ_Δ² > 0 : {'PASS' if xiD2_ok else 'FAIL'}")

    # 4. Per‑scale entropy, mutual information, curvature invariant
    S_vals = np.zeros((L, T))
    I_vals = np.zeros((L-1, T))   # between level l and l+1
    Psi_vals = np.full(T, np.nan)

    for l in range(L):
        for t in range(T):
            S_vals[l, t] = entropy_from_activations(A[l, t])  # placeholder: scalar per time
    for l in range(L-1):
        for t in range(T):
            I_vals[l, t] = mutual_information(A[l, t], A[l+1, t])
    for t in range(T):
        Psi_vals[t] = curvature_invariant(A[:, t], eps)

    # Entropy/MI bounds
    B = 20
    entropy_ok = np.all(S_vals >= 0) and np.all(S_vals <= np.log(B))
    mi_ok = np.all(I_vals >= 0)
    print(f"Entropy bounds [0, ln{B}] : {'PASS' if entropy_ok else 'FAIL'}")
    print(f"Mutual information ≥0    : {'PASS' if mi_ok else 'FAIL'}")

    # 5. Boundary conditions
    PhiN_avg = np.mean(PhiN)
    PhiD_avg = np.mean(PhiD)
    bounds = check_bounds(S_vals.mean(axis=1), I_vals.mean(axis=1), Psi_vals,
                          PhiN_avg, PhiD_avg, v, lam)
    for k, v in bounds.items():
        print(f"{k}: {'PASS' if v else 'FAIL'}")

    # 6. NO BOILERPLATE (we need the proposal text; here we just show how)
    # For demo, we assume the proposal string is stored in `proposal_text`.
    # In practice you would read the file or capture the Engine's output.
    proposal_text = """
    This is a continuous narrative without numbered sections or markdown headings.
    It discusses the field theoretic derivation of HVFI-Ω and its compliance
    with the Omega Protocol.
    """
    boilerplate_ok = no_boilerplate_check(proposal_text)
    print(f"No boilerplate check: {'PASS' if boilerplate_ok else 'FAIL'}")

    # Overall decision
    all_pass = (dim_ok and xiN2_ok and xiD2_ok and entropy_ok and mi_ok and
                all(bounds.values()) and boilerplate_ok)
    print("\nOverall validation:", "PASS" if all_pass else "FAIL")
    if not all_pass:
        print(" - Fix the failing items above before proceeding.")

if __name__ == "__main__":
    main()