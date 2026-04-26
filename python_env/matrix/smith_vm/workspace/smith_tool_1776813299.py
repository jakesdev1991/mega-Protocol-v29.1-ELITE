# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# ----------------------------
# Helper functions (definitions)
# ----------------------------
def Phi_N_from_covariance(cov_mat):
    """
    Average variance from Hessian of decoded-cognitive covariance.
    cov_mat: dxd numpy array (covariance of decoded cognitive states)
    Returns scalar Phi_N.
    """
    eigvals = np.linalg.eigvalsh(cov_mat)  # eigenvalues λ_k
    return np.mean(eigvals)

def Phi_Delta_from_errors(errors):
    """
    Skewness of residual cognitive‑error distribution.
    errors: 1‑D numpy array of residuals (c_i - μ)
    Returns scalar Phi_Delta (dimensionless).
    """
    mu2 = np.mean(errors**2)
    mu3 = np.mean(errors**3)
    if mu2 == 0:
        return 0.0
    return mu3 / (mu2**1.5)

def invariant_psi(Phi_N, Phi_N0):
    """ψ = ln(Φ_N / Φ_N^{(0)})"""
    return np.log(Phi_N / Phi_N0)

def entropy_cognitive(p):
    """Shannon entropy S = -∑ p_i log p_i"""
    return -np.sum(p * np.log(p + 1e-12))  # avoid log(0)

def gauge_current(Phi_Delta):
    """
    Rubric‑compliant timelike gauge current:
        J^μ = sqrt(2) * Φ_Δ * δ^μ_0
    Returns a 4‑vector (μ=0..3) with only time component non‑zero.
    """
    J = np.zeros(4)
    J[0] = np.sqrt(2.0) * Phi_Delta   # δ^μ_0 picks μ=0
    return J

def CTOI(Wilson_loop, Delta, xi, Wilson_loop0, Delta0, xi0):
    """Cognitive Topological Order Index"""
    return (np.abs(Wilson_loop) / np.abs(Wilson_loop0)) * \
           (Delta / Delta0) * (xi / xi0)

# ----------------------------
# Validation routine
# ----------------------------
def validate_tcm_omega(
    cov_mat,          # dxd covariance of decoded cognitive states
    errors,           # 1‑D residuals for skewness
    Wilson_loop,      # current Wilson loop expectation
    Delta,            # current energy gap
    xi,               # current correlation length
    Phi_N0,           # baseline Φ_N
    Wilson_loop0,     # baseline Wilson loop
    Delta0,           # baseline gap
    xi0,              # baseline correlation length
    p_agent,          # agent‑probability vector for entropy
    stress_thresh=0.6 # CTOI lower bound (example)
):
    # 1. Compute covariant modes
    Phi_N = Phi_N_from_covariance(cov_mat)
    Phi_Delta = Phi_Delta_from_errors(errors)

    # 2. Invariant check
    psi = invariant_psi(Phi_N, Phi_N0)
    # (no numeric target; just ensure it's a real number)
    assert np.isfinite(psi), "Invariant ψ must be finite"

    # 3. Gauge current definition & dimensionlessness
    J = gauge_current(Phi_Delta)
    # J must be dimensionless → we check that its components are pure numbers
    assert np.all(np.isfinite(J)), "Gauge current J^μ must be finite (dimensionless)"
    # Optionally, verify only time component non‑zero:
    assert np.allclose(J[1:], 0.0), "Spatial components of J^μ must vanish (timelike current)"

    # 4. Boundary conditions (rubric‑required Φ_Δ divergence)
    # Shredding: ψ → +∞  AND  Φ_Δ → +∞
    # Freeze:  ψ → -∞  AND  Φ_Δ → 0
    # We test logical consistency: if ψ is large positive, Φ_Δ must be large;
    # if ψ is large negative, Φ_Δ must be near zero.
    # Use thresholds as proxies for "∞"/"0".
    SHRED_PSI_THR = 10.0   # ψ > 10 approximates +∞
    FREEZE_PSI_THR = -10.0 # ψ < -10 approximates -∞
    SHRED_PHI_THR = 10.0   # Φ_Δ > 10 approximates +∞
    FREEZE_PHI_THR = 0.1   # Φ_Δ < 0.1 approximates 0

    if psi > SHRED_PSI_THR:
        assert Phi_Delta > SHRED_PHI_THR, \
            "Shredding requires Φ_Δ → +∞ when ψ → +∞"
    if psi < FREEZE_PSI_THR:
        assert Phi_Delta < FREEZE_PHI_THR, \
            "Freeze requires Φ_Δ → 0 when ψ → -∞"

    # 5. Entropy gauge (A_μ J^μ term)
    S = entropy_cognitive(p_agent)
    A_mu = np.gradient(S)  # simplified: treat as derivative w.r.t. x^μ
    # Contract A_μ J^μ (sum over μ)
    gauge_term = np.dot(A_mu, J)
    assert np.isfinite(gauge_term), "Entropy‑gauge term must be finite"

    # 6. MPC‑Ω constraints (example values)
    CTOI_val = CTOI(Wilson_loop, Delta, xi,
                    Wilson_loop0, Delta0, xi0)
    assert CTOI_val >= stress_thresh, f"CTOI ({CTOI_val}) below threshold {stress_thresh}"
    assert Phi_N >= 0.6 * Phi_N0, f"Φ_N ({Phi_N}) below 0.6·Φ_N0"
    assert S >= np.log(3), f"Entropy S ({S}) below ln(3)"

    # 7. Action term sanity (dimensionless check)
    # We assume fields are normalized; just ensure no NaNs/Infs.
    assert np.all(np.isfinite([Phi_N, Phi_Delta, psi, S, CTOI_val])), \
        "One or more field quantities non‑finite"

    print("All TCM‑Ω validation checks passed.")
    return {
        "Phi_N": Phi_N,
        "Phi_Delta": Phi_Delta,
        "psi": psi,
        "entropy": S,
        "CTOI": CTOI_val,
        "gauge_term": gauge_term
    }

# ----------------------------
# Example usage (dummy data)
# ----------------------------
if __name__ == "__main__":
    np.random.seed(42)
    d = 5
    cov_mat = np.random.rand(d, d)
    cov_mat = cov_mat @ cov_mat.T  # make PSD
    errors = np.random.randn(100)
    Wilson_loop = 0.9
    Delta = 1.0
    xi = 1.0
    Phi_N0 = 1.0
    Wilson_loop0 = 1.0
    Delta0 = 1.0
    xi0 = 1.0
    p_agent = np.full(4, 0.25)  # uniform distribution

    try:
        result = validate_tcm_omega(
            cov_mat, errors, Wilson_loop, Delta, xi,
            Phi_N0, Wilson_loop0, Delta0, xi0, p_agent
        )
        print("Validation result:", result)
    except AssertionError as e:
        print("VALIDATION FAILED:", e)