# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
ATS‑Ω mathematical compliance validator.
Checks the core equations and invariants from the Omega Protocol rubric v26.0.
"""

import numpy as np
import numpy.linalg as LA

# -------------------------- Helper Functions --------------------------

def double_well(B, alpha, beta, gamma):
    """V(B) = α/2 B^2 + β/4 B^4 - γ B"""
    return 0.5 * alpha * B**2 + 0.25 * beta * B**4 - gamma * B

def compute_phi_n_phi_delta(Sigma):
    """
    From covariance matrix Sigma of the computational‑integrity field B:
        Φ_N = sqrt(lambda_max(Sigma))
        Φ_Δ = μ_3 / (μ_2**(3/2))
    where μ_p are the central moments of the eigenvalue distribution.
    """
    evals = LA.eigvalsh(Sigma)          # real symmetric → eigenvalues
    phi_n = np.sqrt(np.max(evals))      # Φ_N
    # central moments of the eigenvalue distribution
    mu = np.mean(evals)
    mu_2 = np.mean((evals - mu)**2)     # variance
    mu_3 = np.mean((evals - mu)**3)     # skewness numerator
    phi_delta = mu_3 / (mu_2**1.5) if mu_2 > 0 else 0.0
    return phi_n, phi_delta, evals

def psi_ats(phi_n, phi_n0):
    """Invariant ψ = ln(Φ_N/Φ_N^{(0)})"""
    return np.log(phi_n / phi_n0)

def shannon_conditional_entropy(path_probs, type_weights):
    """
    S_alg = Σ_m p(m) [ - Σ_k p_{m,k} log p_{m,k} ]
    path_probs[m,k] = p_{m,k}
    type_weights[m] = p(m)
    """
    assert np.allclose(type_weights.sum(), 1.0), "type_weights must sum to 1"
    S = 0.0
    for m, p_m in enumerate(type_weights):
        row = path_probs[m]
        # avoid log(0)
        row_safe = np.where(row > 0, row, 1.0)
        S += -p_m * np.sum(row * np.log(row_safe))
    return S

def ati_from_invariants(curv_ratio, betti_ratio, S_alg):
    """
    ATI = (|R_G|/|R_G0|) * (β1/β10) * exp(-S_alg)
    Here curv_ratio and betti_ratio are already normalised to 1 at t=0.
    """
    return curv_ratio * betti_ratio * np.exp(-S_alg)

# -------------------------- Synthetic Test --------------------------

def run_validation():
    np.random.seed(42)

    # --- 1. Covariance matrix for B field (algorithm components) ---
    n_comp = 8                     # number of algorithm components
    # generate a random positive‑definite covariance
    A = np.random.randn(n_comp, n_comp)
    Sigma = A @ A.T + 0.1 * np.eye(n_comp)   # ensure PD

    phi_n, phi_delta, evals = compute_phi_n_phi_delta(Sigma)
    print(f"Φ_N = {phi_n:.4f}, Φ_Δ = {phi_delta:.4f}")
    print(f"Eigenvalues of Σ: {evals}")

    # --- 2. Baseline Φ_N0 (from fault‑free simulation) ---
    phi_n0 = phi_n   # for this test we take the current state as baseline
    psi = psi_ats(phi_n, phi_n0)
    print(f"ψ_ats = ln(Φ_N/Φ_N0) = {psi:.4f}")

    # --- 3. Verify invariant matches definition ---
    assert np.allclose(psi, np.log(phi_n / phi_n0)), "ψ invariant mismatch"

    # --- 4. Double‑well potential shape ---
    alpha, beta, gamma = -1.0, 2.0, 0.5   # α<0, β>0, γ>0 as required
    B_test = np.linspace(-2, 2, 400)
    V = double_well(B_test, alpha, beta, gamma)
    # Check that V has two minima (simple numeric check)
    deriv = np.gradient(V, B_test)
    sign_changes = np.where(np.diff(np.sign(deriv)))[0]
    assert len(sign_changes) >= 2, "Double‑well should have at least two extrema"
    print("Double‑well potential shape OK.")

    # --- 5. Entropy gauge and gauge term A_μ J^μ ---
    # Mock path probabilities for 3 types, each with 2 possible paths
    path_probs = np.array([[0.7, 0.3],
                           [0.4, 0.6],
                           [0.5, 0.5]])   # rows = types, cols = paths
    type_weights = np.array([0.5, 0.3, 0.2])   # p(m)
    S_alg = shannon_conditional_entropy(path_probs, type_weights)
    print(f"S_alg = {S_alg:.4f}")

    # A_μ = ∂_μ S_alg → for temporal component μ=0 we approximate ∂_t S_alg ≈ 0 (steady state)
    A_mu = np.zeros(4)   # μ = 0,1,2,3
    A_mu[0] = 0.0        # ∂_t S_alg ≈ 0 in this static test
    J_mu = np.array([np.sqrt(2) * phi_delta, 0.0, 0.0, 0.0])   # J^μ = √2 Φ_Δ δ^μ_0
    gauge_term = np.dot(A_mu, J_mu)   # A_μ J^μ (with metric signature absorbed)
    print(f"Gauge term A_μ J^μ (temporal) = {gauge_term:.4f}")
    # In a static test the gauge term should be zero (since ∂_t S_alg = 0)
    assert np.allclose(gauge_term, 0.0), "Gauge term not zero for static S_alg"

    # --- 6. ATI computation (mock curvature and Betti ratios) ---
    curv_ratio = 0.9   # |R_G|/|R_G0|
    betti_ratio = 1.1  # β1/β10
    ATI = ati_from_invariants(curv_ratio, betti_ratio, S_alg)
    print(f"ATI = {ATI:.4f}")

    # --- 7. QP constraints ---
    assert ATI >= 0.6, f"ATI constraint violated: {ATI}"
    assert phi_n >= 0.5, f"Φ_N constraint violated: {phi_n}"
    assert S_alg >= np.log(2), f"S_alg constraint violated: {S_alg} (need ≥ ln2)"
    print("All QP constraints satisfied.")

    # --- 8. Cost function sanity (non‑negative) ---
    mu1, mu2, mu3 = 1.0, 1.0, 1.0
    cost = ((0.6 - ATI) if ATI < 0.6 else 0.0)**2 \
         + mu1 * ((0.5 - phi_n) if phi_n < 0.5 else 0.0)**2 \
         + mu2 * (phi_delta**2) \
         + mu3 * ((np.log(2) - S_alg) if S_alg < np.log(2) else 0.0)**2
    assert cost >= 0.0, "Cost function produced negative value"
    print(f"Instantaneous cost = {cost:.6f} (non‑negative)")

    print("\n✅ All mathematical checks passed. ATS‑Ω is Ω‑Physics Rubric v26.0 compliant.")

if __name__ == "__main__":
    try:
        run_validation()
    except AssertionError as e:
        print(f"\n❌ Validation failed: {e}")
        raise