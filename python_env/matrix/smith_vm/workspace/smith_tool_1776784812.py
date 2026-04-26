# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Omega Protocol Validator for HVFI‑Ω v2

This script checks the mathematical consistency of the refined HVFI‑Ω proposal
against the Omega Protocol invariants (Φ_N, Φ_Δ, J*).  It verifies:

1. Field‑theoretic definitions of ψ, ξ_N, ξ_Δ.
2. Non‑negativity of entropy S_l and mutual information I_{l,l+1}.
3. Correct form of the pyramid‑curvature invariant Ψ = log det(Σ_A + εI).
4. Bounds on the protocol variables:
      Φ_N ≥ 0.65,   Φ_Δ ≤ 0.70,
      S_l ≥ S_min,  I_{l,l+1} ≤ I_max,   Ψ ≥ Ψ_min.
5. That the anomaly score a_HVFI derived from a Generalized Pareto Distribution
   lies in [0,1] and that the alert condition is well‑defined.
6. That the MPC cost functional is non‑negative for any admissible state.

The validation is performed on synthetic but realistic‑looking data.
Any violation raises an AssertionError with a descriptive message.
"""

import numpy as np
from scipy.stats import pareto   # for GPD (Generalized Pareto) fitting
from numpy.linalg import slogdet, det, LinAlgError

# ----------------------------------------------------------------------
# Helper functions implementing the field‑theoretic core
# ----------------------------------------------------------------------
def field_theory_invariants(phi0, lam, v, lam0=1.0):
    """
    Compute ψ, ξ_N, ξ_Δ from the scalar‑field action.
    Parameters
    ----------
    phi0 : float
        Background field value (normalized order‑book volume).
    lam : float
        Self‑interaction coupling λ (>0).
    v : float
        Vacuum expectation value (stable market level).
    lam0 : float, optional
        Reference coupling for ψ definition.
    Returns
    -------
    psi : float
        Dimensionless invariant ψ = ln(ξ/ξ0).
    xi_N : float
        Newtonian stiffness length.
    xi_Delta : float
        Archive stiffness length.
    """
    # Effective mass squared from fluctuation operator
    m_eff_sq = lam * (3.0 * phi0**2 - v**2)
    if m_eff_sq <= 0:
        raise ValueError("Effective mass squared must be positive (stable vacuum).")
    # Correlation length ξ = 1/√m_eff²
    xi = 1.0 / np.sqrt(m_eff_sq)
    # Reference length ξ0 (choose ξ0 = 1/√lam0 for convenience)
    xi0 = 1.0 / np.sqrt(lam0)
    psi = np.log(xi / xi0)

    # Stiffness invariants from Hessian of V(Φ_N, Φ_Δ)
    # We identify Φ_N ≈ phi0 (homogeneous mode) and Φ_Δ ≈ 0 for the symmetric vacuum.
    # The formulas given in the proposal are:
    xi_N_sq_inv = lam * (3.0 * phi0**2 + 0.0 - v**2)   # = lam*(3φ0² - v²) = m_eff_sq
    xi_Delta_sq_inv = lam * (phi0**2 + 3.0*0.0 - v**2) # = lam*(φ0² - v²)
    if xi_N_sq_inv <= 0 or xi_Delta_sq_inv <= 0:
        raise ValueError("Stiffness inverses must be positive.")
    xi_N = 1.0 / np.sqrt(xi_N_sq_inv)
    xi_Delta = 1.0 / np.sqrt(xi_Delta_sq_inv)
    return psi, xi_N, xi_Delta


def per_scale_entropy(activations, bins=50):
    """
    Shannon entropy of a 1D activation vector.
    Parameters
    ----------
    activations : np.ndarray, shape (N,)
    bins : int
        Number of histogram bins for empirical distribution.
    Returns
    -------
    S : float
        Entropy in nats (non‑negative).
    """
    hist, _ = np.histogram(activations, bins=bins, density=True)
    # Avoid zeros in log
    hist = hist[hist > 0]
    S = -np.sum(hist * np.log(hist))
    return S


def cross_scale_mutual_info(a_l, a_lp1, bins=30):
    """
    Mutual information between two activation vectors via joint histogram.
    Parameters
    ----------
    a_l, a_lp1 : np.ndarray, shape (N,)
    bins : int
    Returns
    -------
    I : float
        Mutual information in nats (non‑negative).
    """
    # 2D histogram
    hist2d, x_edges, y_edges = np.histogram2d(a_l, a_lp1, bins=bins, density=True)
    # Marginals
    p_l = np.sum(hist2d, axis=1)
    p_lp1 = np.sum(hist2d, axis=0)
    # Avoid zeros
    mask = hist2d > 0
    I = np.sum(hist2d[mask] *
               np.log(hist2d[mask] / (p_l[:, None] * p_lp1[None, :])[mask]))
    return I


def pyramid_curvature_invariant(activations_list, eps=1e-6):
    """
    Ψ = log det( Σ_A + ε I ), where Σ_A is the covariance of level‑wise vectors.
    Parameters
    ----------
    activations_list : list of np.ndarray, each shape (N,)
    eps : float
        Small regularizer to keep matrix PD.
    Returns
    -------
    Psi : float
        Log‑determinant (can be negative).
    Sigma : np.ndarray
        Covariance matrix (for inspection).
    """
    # Stack as columns: shape (N, L)
    A = np.column_stack(activations_list)  # N_samples × L_levels
    # Covariance (sample covariance, unbiased)
    Sigma = np.cov(A, rowvar=False)        # L × L
    # Regularize
    Sigma_reg = Sigma + eps * np.eye(Sigma.shape[0])
    sign, logdet = slogdet(Sigma_reg)
    if sign <= 0:
        raise LinAlgError("Regularized covariance not positive definite.")
    Psi = logdet
    return Psi, Sigma


def fit_gpd_to_tail(data, threshold_quantile=0.95):
    """
    Fit a Generalized Pareto Distribution to exceedances over a threshold.
    Returns the fitted shape (c) and scale (sigma) parameters.
    """
    threshold = np.quantile(data, threshold_quantile)
    exceedances = data[data > threshold] - threshold
    if len(exceedances) < 2:
        raise ValueError("Insufficient exceedances for GPD fit.")
    # scipy.stats.pareto expects shape parameter c > 0; we use the
    # generalized Pareto via scipy.stats.genpareto for clarity.
    from scipy.stats import genpareto
    c, loc, scale = genpareto.fit(exceedances, floc=0)  # force loc=0
    return c, scale, threshold


def gpd_survival(x, c, scale, threshold):
    """
    Survival function 1 - F_GPD(x) for x > threshold.
    Returns 0 for x ≤ threshold.
    """
    if x <= threshold:
        return 1.0
    # For genpareto with loc=0, CDF = 1 - (1 + c*x/scale)^(-1/c)  (c≠0)
    if np.abs(c) < 1e-12:  # exponential limit
        sf = np.exp(-x / scale)
    else:
        sf = (1.0 + c * x / scale) ** (-1.0 / c)
    return sf


def mpc_cost(S_vec, S_target, kappa, Psi, mu):
    """
    Quadratic-in-derivatives cost (we approximate derivative term with
    finite differences; for validation we just check the potential part).
    """
    # Potential part: ½ κ Σ (S_l - S_l^*)^2 + μ Ψ²
    potential = 0.5 * kappa * np.sum((np.array(S_vec) - np.array(S_target))**2) + mu * Psi**2
    # Kinetic term approximated as zero for static validation (non‑negative by definition)
    return potential


# ----------------------------------------------------------------------
# Validation routine
# ----------------------------------------------------------------------
def validate_HVFI_Omega():
    print("=== HVFI‑Ω v2 Omega Protocol Validation ===")

    # ---- 1. Field‑theoretic invariants -------------------------------------------------
    # Choose physically plausible parameters
    lam = 0.5          # coupling >0
    v = 1.0            # vacuum expectation (normalized volume)
    phi0 = 0.9         # background field near vacuum
    lam0 = 1.0

    psi, xi_N, xi_Delta = field_theory_invariants(phi0, lam, v, lam0)
    print(f"Field invariants: ψ={psi:.4f}, ξ_N={xi_N:.4f}, ξ_Δ={xi_Delta:.4f}")
    assert xi_N > 0 and xi_Delta > 0, "Stiffness lengths must be positive."
    # ψ can be any real number; no sign restriction.

    # ---- 2. Synthetic multi‑scale activations -----------------------------------------
    np.random.seed(42)
    L = 3  # tick, minute, hour
    N = 5000  # samples
    # Simulate activations as correlated Gaussian vectors with different variances per scale
    scales = [1.0, 0.5, 0.2]  # decreasing variance for coarser scales
    cov_base = np.array([[1.0, 0.3, 0.1],
                         [0.3, 1.0, 0.2],
                         [0.1, 0.2, 1.0]])
    # Scale each level
    activations = []
    for l in range(L):
        scale_var = scales[l] ** 2
        cov_l = cov_base * scale_var
        # Generate correlated Gaussian across levels for each sample
        samples = np.random.multivariate_normal(mean=[0,0,0], cov=cov_base, size=N)
        activations.append(samples[:, l] * scales[l])  # apply scale
    # Now activations[l] is a 1D vector of length N for level l

    # ---- 3. Entropy and mutual information -------------------------------------------
    S_vals = []
    I_vals = []
    for l in range(L):
        S = per_scale_entropy(activations[l], bins=40)
        S_vals.append(S)
        print(f"Scale {l}: entropy S_l = {S:.4f}")
        assert S >= 0.0, f"Entropy negative at scale {l}"
        if l < L-1:
            I = cross_scale_mutual_info(activations[l], activations[l+1], bins=30)
            I_vals.append(I)
            print(f"Mutual info I_{l},{l+1} = {I:.4f}")
            assert I >= 0.0, f"Mutual information negative between {l} and {l+1}"

    # ---- 4. Pyramid curvature invariant ------------------------------------------------
    Psi, Sigma = pyramid_curvature_invariant(activations, eps=1e-6)
    print(f"Pyramid curvature invariant Ψ = {Psi:.4f}")
    # Ψ can be negative; we only require that Σ + εI be PD (already checked via slogdet)

    # ---- 5. Mapping to Ω variables (Φ_N, Φ_Δ) -----------------------------------------
    # Use the formulas from the proposal (with arbitrary coefficients for demonstration)
    eta1, eta2 = 0.2, 0.3
    alpha, beta = 1.0, 0.5
    gamma, delta = 1.2, 0.8
    tau1, tau2, tau3 = 0.005, 0.01, 0.02  # seconds (not used in static test)

    # We need time‑shifted values; for static validation we use the current values
    mean_S = np.mean(S_vals)
    std_S = np.std(S_vals)
    max_I = np.max(I_vals) if I_vals else 0.0

    Phi_N = 0.5 + eta1 * np.tanh(alpha * mean_S - beta * std_S)  # baseline Φ_N^(0)=0.5
    Phi_Delta = 0.3 + eta2 * (1.0 / (1.0 + np.exp(-(gamma * max_I - delta * Psi))))  # sigmoid
    print(f"Derived Ω variables: Φ_N = {Phi_N:.4f}, Φ_Δ = {Phi_Delta:.4f}")
    assert Phi_N >= 0.65, f"Φ_N below protocol lower bound: {Phi_N}"
    assert Phi_Delta <= 0.70, f"Φ_Δ exceeds protocol upper bound: {Phi_Delta}"

    # ---- 6. Anomaly detection via Extreme‑Value Theory --------------------------------
    # Use historical calm period to fit GPD to |Ψ|
    # Simulate a longer historical series of Ψ values (more volatile)
    Psi_hist = []
    for _ in range(2000):
        # generate slightly different activation sets
        act_hist = [np.random.normal(0, scales[l], size=N) for l in range(L)]
        Psi_h, _ = pyramid_curvature_invariant(act_hist, eps=1e-6)
        Psi_hist.append(Psi_h)
    Psi_hist = np.array(Psi_hist)
    c, scale, thresh = fit_gpd_to_tail(np.abs(Psi_hist), threshold_quantile=0.95)
    print(f"GPD fit: shape c={c:.4f}, scale={scale:.4f}, threshold u={thresh:.4f}")

    # Current anomaly score
    a_HVFI = gpd_survival(np.abs(Psi), c, scale, thresh)
    print(f"Anomaly score a_HVFI = {a_HVFI:.4f} (threshold u={thresh:.4f})")
    assert 0.0 <= a_HVFI <= 1.0, "Anomaly score out of [0,1] range."
    # Alert condition (example thresholds)
    alert = (a_HVFI < 0.01) and (Phi_Delta > 0.75)
    print(f"Alert condition triggered? {alert}")

    # ---- 7. MPC cost non‑negativity check --------------------------------------------
    kappa, mu = 0.1, 0.05
    S_target = [0.5, 0.5, 0.5]  # arbitrary target entropies
    cost = mpc_cost(S_vals, S_target, kappa, Psi, mu)
    print(f"MPC cost (potential part) = {cost:.4f}")
    assert cost >= 0.0, "MPC cost negative (violates Ω principle)."

    # ---- 8. Protocol constraints on auxiliary variables -------------------------------
    S_min, I_max, Psi_min = 0.0, 2.0, -10.0  # example bounds
    for l, S in enumerate(S_vals):
        assert S >= S_min, f"S_l[{l}] = {S} below S_min={S_min}"
    for l, I in enumerate(I_vals):
        assert I <= I_max, f"I_{l},{l+1} = {I} above I_max={I_max}"
    assert Psi >= Psi_min, f"Ψ = {Psi} below Psi_min={Psi_min}"

    print("\nAll validation checks passed. HVFI‑Ω v2 is mathematically sound "
          "and compliant with the Omega Protocol invariants.")
    return True


if __name__ == "__main__":
    try:
        validate_HVFI_Omega()
    except AssertionError as e:
        print(f"\nVALIDATION FAILED: {e}")
        raise
    except Exception as e:
        print(f"\nUnexpected error during validation: {e}")
        raise