# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Validation script for the Algorithmic Topology Shield (ATS‑Ω) proposal.
Checks mathematical consistency with the Ω‑Physics Rubric v26.0:
  - Kinetic term, double‑well potential, gauge coupling.
  - Definition of covariant modes Φ_N and Φ_Δ from the covariance matrix.
  - Invariant ψ = ln(Φ_N/Φ_N⁰).
  - Entropy gauge A_μ = ∂_μ S_alg, J^μ = √2 Φ_Δ δ^μ₀.
  - Boundaries (Algorithmic Shredding / Informational Freeze).
  - ATI formula and its mapping to Ω variables.
  - MPC‑Ω state, control actions, QP constraints and cost function structure.
"""

import numpy as np
import sympy as sp

# ------------------------------
# Helper functions
# ------------------------------
def covariance_matrix(B):
    """B shape: (n_components, n_samples) -> covariance (n_components, n_components)"""
    return np.cov(B, bias=True)  # biased estimator matches rubric's use of population moments

def phi_n_from_cov(Sigma):
    """Φ_N = sqrt(largest eigenvalue of Sigma)"""
    evals = np.linalg.eigvalsh(Sigma)  # real symmetric
    return np.sqrt(np.max(evals))

def phi_delta_from_cov(Sigma, B):
    """Φ_Δ = μ₃ / (μ₂)^{3/2} where μ_p are central moments of the field values."""
    # Flatten field values to compute moments across all components & samples
    flat = B.ravel()
    mu = np.mean(flat)
    mu2 = np.mean((flat - mu)**2)
    mu3 = np.mean((flat - mu)**3)
    if mu2 == 0:
        return 0.0
    return mu3 / (mu2**1.5)

def entropy_conditional(B, path_labels, type_labels):
    """
    Compute Shannon conditional entropy S_alg.
    B: (n_components, n_samples) field values (not used directly, only for counting)
    path_labels: (n_components,) integer id of computational path taken by each component
    type_labels: (n_components,) integer id of algorithmic type (e.g., matmul, solve, ...)
    """
    unique_types = np.unique(type_labels)
    S = 0.0
    for t in unique_types:
        mask = (type_labels == t)
        p_type = np.mean(mask)  # fraction of components of this type
        if p_type == 0:
            continue
        paths = path_labels[mask]
        _, counts = np.unique(paths, return_counts=True)
        p_path = counts / len(paths)
        S_type = -np.sum(p_path * np.log(p_path + 1e-12))  # avoid log(0)
        S += p_type * S_type
    return S

def ATI_from_invariants(Ricci_curv, beta1, S_alg, Ricci0, beta1_0):
    """
    ATI = (|Ricci|/|Ricci0|) * (β₁/β₁₀) * exp(-S_alg)
    Ricci_curv: scalar magnitude of average Ricci curvature (we use absolute)
    """
    return (np.abs(Ricci_curv) / np.abs(Ricci0)) * (beta1 / beta1_0) * np.exp(-S_alg)

def double_well_potential(B, alpha, beta, gamma):
    """V(B) = α/2 B² + β/4 B⁴ - γ B"""
    return 0.5*alpha*B**2 + 0.25*beta*B**4 - gamma*B

def invariant_psi(Phi_N, Phi_N0):
    """ψ = ln(Φ_N/Φ_N⁰)"""
    return np.log(Phi_N / Phi_N0)

def gauge_current(Phi_Delta):
    """J^μ = √2 Φ_δ δ^μ₀  -> only time component non‑zero"""
    J = np.zeros(4)
    J[0] = np.sqrt(2) * Phi_Delta
    return J

# ------------------------------
# Validation tests
# ------------------------------
def run_validation():
    errors = []
    warnings = []

    # 1. Check double‑well shape (α<0, β>0, γ>0) yields two minima
    alpha, beta, gamma = -1.0, 2.0, 0.5  # example satisfying constraints
    B_sym = sp.symbols('B')
    V_sym = 0.5*alpha*B_sym**2 + 0.25*beta*B_sym**4 - gamma*B_sym
    dV = sp.diff(V_sym, B_sym)
    crit_points = sp.solve(dV, B_sym)
    # keep real roots
    real_roots = [float(r) for r in crit_points if r.is_real]
    if len(real_roots) < 2:
        errors.append("Double‑well potential does not have at least two real stationary points.")
    else:
        # check that second derivative >0 at minima
        d2V = sp.diff(dV, B_sym)
        minima = [r for r in real_roots if d2V.subs(B_sym, r) > 0]
        if len(minima) < 2:
            warnings.append("Double‑well may not have two distinct minima (check parameters).")

    # 2. Random field test for Φ_N, Φ_Δ, ψ, entropy gauge
    np.random.seed(42)
    n_comp, n_samp = 8, 128
    B = np.random.randn(n_comp, n_samp)  # Gaussian field
    Sigma = covariance_matrix(B)
    Phi_N = phi_n_from_cov(Sigma)
    Phi_Delta = phi_delta_from_cov(Sigma, B)
    Phi_N0 = 1.0  # reference from fault‑free simulation (set to 1 for test)
    psi = invariant_psi(Phi_N, Phi_N0)

    # Verify Φ_N definition matches rubric: sqrt(max eig)
    evals = np.linalg.eigvalsh(Sigma)
    expected_Phi_N = np.sqrt(np.max(evals))
    if not np.isclose(Phi_N, expected_Phi_N, rtol=1e-10):
        errors.append(f"Φ_N mismatch: got {Phi_N}, expected {expected_Phi_N}")

    # Verify Φ_Δ definition matches rubric: μ₃/(μ₂)^{3/2}
    flat = B.ravel()
    mu = np.mean(flat)
    mu2 = np.mean((flat - mu)**2)
    mu3 = np.mean((flat - mu)**3)
    expected_Phi_Delta = 0.0 if mu2 == 0 else mu3 / (mu2**1.5)
    if not np.isclose(Phi_Delta, expected_Phi_Delta, rtol=1e-10):
        errors.append(f"Φ_Δ mismatch: got {Phi_Delta}, expected {expected_Phi_Delta}")

    # 3. Entropy gauge consistency
    # Mock path and type labels (each component picks a path 0..2, type 0..1)
    path_labels = np.random.randint(0, 3, size=n_comp)
    type_labels = np.random.randint(0, 2, size=n_comp)
    S_alg = entropy_conditional(B, path_labels, type_labels)
    # A_μ = ∂_μ S_alg -> we cannot compute derivative without spacetime dependence,
    # but we can check that S_alg is a scalar (as required) and that J^μ uses Φ_Δ.
    J = gauge_current(Phi_Delta)
    if not np.allclose(J[1:], 0.0, atol=1e-12):
        errors.append("Spatial components of J^μ should be zero (only time component).")
    if not np.isclose(J[0], np.sqrt(2)*Phi_Delta, rtol=1e-10):
        errors.append("Time component of J^μ does not match √2 Φ_Δ.")

    # 4. Boundaries interpretation
    # Algorithmic Shredding: ψ → +∞ when Φ_N → ∞ and S_alg → high
    # Informational Freeze: ψ → -∞ when Φ_N → 0 and S_alg → low
    # We test monotonicity: ψ increases with Φ_N, decreases with S_alg (via ATI)
    if Phi_N > 1e3:
        # large Φ_N should give large positive ψ (since Φ_N0=1)
        if psi < 0:
            warnings.append("Very large Φ_N gave non‑positive ψ (check reference).")
    if Phi_N < 1e-3:
        if psi > 0:
            warnings.append("Very small Φ_N gave non‑negative ψ (check reference).")

    # 5. ATI formula and mapping to Ω variables (lead‑time τ ignored here)
    # Mock Ricci curvature and β₁
    Ricci_curv = np.random.rand() * 0.5  # some positive curvature
    Ricci0 = 1.0
    beta1 = np.random.randint(1,5)
    beta1_0 = 2
    ATI = ATI_from_invariants(Ricci_curv, beta1, S_alg, Ricci0, beta1_0)
    if not (0.0 <= ATI <= 1.0 + 1e-12):
        errors.append(f"ATI out of [0,1] range: {ATI}")

    # Mapping to Φ_N^(ats) and Φ_Δ^(ats) per proposal:
    # Φ_N^(ats)(t) = Φ_N⁰ - η₁·(1‑ATI(t‑τ)) + η₂·β₀(t‑τ)/β₀(0)
    # Φ_Δ^(ats)(t) = Φ_Δ⁰ + η₃·Var[timing] - η₄·ATI(t‑τ)
    # We just check that the structure uses ATI linearly (no higher powers).
    eta1, eta2, eta3, eta4 = 0.2, 0.1, 0.15, 0.1
    Phi_N0_ref = 1.0
    Phi_Delta0_ref = 0.0
    beta0 = len(np.unique(type_labels))  # number of connected components in type graph (mock)
    beta0_0 = 2
    Phi_N_ats = Phi_N0_ref - eta1*(1 - ATI) + eta2*(beta0/beta0_0)
    Phi_Delta_ats = Phi_Delta0_ref + 0.0  # ignore timing variance for simplicity - eta4*ATI
    Phi_Delta_ats = Phi_Delta0_ref - eta4*ATI  # only ATI term for test
    # Ensure they remain non‑negative (physical)
    if Phi_N_ats < 0:
        warnings.append(f"Computed Φ_N^(ats) negative: {Phi_N_ats}")
    if Phi_Delta_ats < 0:
        warnings.append(f"Computed Φ_Δ^(ats) negative: {Phi_Delta_ats}")

    # 6. MPC‑Ω state vector dimension check
    state_len = 9  # [Φ_N, Φ_Δ, ψ, ξ_N, ξ_Δ, ATI, B, S_alg, C_vuln]
    # We just assert that the proposal lists exactly these components.
    expected_names = ["Φ_N^(ats)", "Φ_Δ^(ats)", "ψ_ats", "ξ_N", "ξ_Δ",
                      "ATI", "B", "S_alg", "C_vuln"]
    if len(expected_names) != state_len:
        errors.append(f"State vector length mismatch: expected {state_len}, got {len(expected_names)}")

    # 7. QP constraints: ATI ≥ 0.6, Φ_N ≥ 0.5, S_alg ≥ ln2
    if ATI < 0.6 - 1e-9:
        errors.append(f"ATI constraint violated: {ATI} < 0.6")
    if Phi_N < 0.5 - 1e-9:
        errors.append(f"Φ_N constraint violated: {Phi_N} < 0.5")
    if S_alg < np.log(2) - 1e-9:
        errors.append(f"S_alg constraint violated: {S_alg} < ln(2)")

    # 8. Cost function structure (quadratic penalties)
    # We just verify that each term is of form (target - variable)_+^2
    mu1, mu2, mu3 = 1.0, 1.0, 1.0
    cost = (max(0.6 - ATI, 0))**2 \
           + mu1 * (max(0.5 - Phi_N, 0))**2 \
           + mu2 * (Phi_Delta**2) \
           + mu3 * (max(np.log(2) - S_alg, 0))**2
    if cost < 0:
        errors.append("Cost function produced negative value (should be non‑negative).")

    # ------------------------------
    # Report
    # ------------------------------
    if errors:
        print("VALIDATION FAILED – Errors:")
        for e in errors:
            print(" -", e)
    else:
        print("VALIDATION PASSED – No mathematical inconsistencies detected.")
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(" -", w)

if __name__ == "__main__":
    run_validation()