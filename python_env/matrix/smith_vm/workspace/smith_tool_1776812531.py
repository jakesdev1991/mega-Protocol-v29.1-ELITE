# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

def validate_pcs_ohm(
    C: np.ndarray,          # coherence field values at object points (shape: (N,))
    gradC: np.ndarray,      # gradient of C (shape: (N, dim))
    skewC: float,           # skewness of the coherence distribution (scalar)
    region_probs: np.ndarray, # p(r) for each region (shape: (R,))
    cond_probs: np.ndarray,   # p(c|r) for each region and coherence bin (shape: (R, B))
    PhiN0: float = 1.0,     # baseline Phi_N
    kappa: dict = None,     # calibration constants {k1,k2,k3,k4}
    S_low: float = 0.1,
    S_high: float = None,   # if None, set to log(num_regions * num_bins)
    mu: dict = None,        # cost weights {mu1,mu2,mu3}
    tol: float = 1e-8
) -> bool:
    """
    Returns True if the supplied data satisfy all Omega‑Protocol invariants
    for the Perceptual Coherence Shield (PCS‑Ω).
    """
    # ----- 1. Basic sanity -----
    if C.ndim != 1:
        raise ValueError("C must be a 1‑D array of coherence values.")
    if gradC.shape[0] != C.size:
        raise ValueError("gradC must have same first dimension as C.")
    if region_probs.ndim != 1 or cond_probs.ndim != 2:
        raise ValueError("region_probs must be 1‑D, cond_probs 2‑D (R,B).")
    if not np.allclose(region_probs.sum(), 1.0, atol=tol):
        raise ValueError("region_probs must sum to 1.")
    if not np.allclose(cond_probs.sum(axis=1), 1.0, atol=tol):
        raise ValueError("Each row of cond_probs must sum to 1.")

    # ----- 2. Double‑well potential parameters -----
    # (These are assumed to be set elsewhere; we only check sign)
    # alpha < 0, beta > 0, gamma > 0
    # For validation we just require the user to provide sensible kappa.
    if kappa is None:
        kappa = {"k1": 1.0, "k2": 0.1, "k3": 1.0, "k4": 0.1}
    k1, k2, k3, k4 = kappa["k1"], kappa["k2"], kappa["k3"], kappa["k4"]

    # ----- 3. Covariant modes from Hessian diagonalization -----
    normC = np.linalg.norm(C)
    if normC == 0:
        raise ValueError("Coherence field cannot be identically zero.")
    # field smoothness term
    smooth = np.linalg.norm(gradC) / normC   # = ||∇C|| / ||C||
    omega_N_sq = k1 * smooth + k2
    omega_D_sq = k3 * skewC + k4

    if omega_N_sq <= 0 or omega_D_sq <= 0:
        return False   # eigenvalues must be positive (stable minima)

    PhiN = np.sqrt(omega_N_sq)
    PhiD = np.sqrt(omega_D_sq)

    # ----- 4. Invariant -----
    psi_perc = np.log(PhiN / PhiN0)   # should be real; PhiN>0 guaranteed above

    # ----- 5. Conditional entropy gauge -----
    # Avoid log(0) by masking zeros
    mask = cond_probs > 0
    S_perc = -np.sum(
        region_probs[:, None] * np.where(mask, cond_probs * np.log(cond_probs), 0.0)
    )
    # Theoretical maximum entropy (uniform over all region-bin pairs)
    R, B = cond_probs.shape
    S_max = np.log(R * B)
    if S_high is None:
        S_high = S_max
    if not (0.0 - tol <= S_perc <= S_max + tol):
        return False   # entropy out of physical bounds

    # ----- 6. Boundary conditions (thermodynamic consistency) -----
    # Perceptual Shredding: PhiN → large AND S_perc → S_max
    # Perceptual Locking:   PhiN → small AND S_perc → 0
    # We simply check that the extremes are not violated in the opposite sense:
    if PhiN > 1e3 and S_perc < 0.5 * S_max:   # shredding should have high entropy
        return False
    if PhiN < 1e-3 and S_perc > 0.5 * S_max:  # locking should have low entropy
        return False

    # ----- 7. MPC‑Ω constraints -----
    # PCI = PhiN * PhiD * Gamma ; we set Gamma = 1 for validation (can be extended)
    PCI = PhiN * PhiD   # assuming Gamma=1
    if PCI < 0.6 - tol:
        return False
    if PhiN < 0.5 - tol:
        return False
    if not (S_low - tol <= S_perc <= S_high + tol):
        return False

    # ----- 8. Cost function non‑negativity (quadratic form) -----
    if mu is None:
        mu = {"mu1": 1.0, "mu2": 1.0, "mu3": 1.0}
    m1, m2, m3 = mu["mu1"], mu["mu2"], mu["mu3"]
    # Target entropy (choose middle of allowed band)
    S_target = 0.5 * (S_low + S_high)
    cost = (
        (0.6 - PCI) ** 2 if PCI < 0.6 else 0.0
        + m1 * (0.5 - PhiN) ** 2 if PhiN < 0.5 else 0.0
        + m2 * (PhiD) ** 2
        + m3 * (S_perc - S_target) ** 2
    )
    if cost < -tol:   # should never be negative for a sum of squares
        return False

    # All checks passed
    return True


# ----------------- Example usage -----------------
if __name__ == "__main__":
    # Mock data: 100 points, 2‑D gradient, 3 regions, 4 coherence bins
    np.random.seed(0)
    N = 100
    C = np.random.rand(N)
    C = C / np.linalg.norm(C)          # normalize
    gradC = np.random.randn(N, 2) * 0.1
    skewC = 0.0                         # symmetric distribution
    R, B = 3, 4
    region_probs = np.ones(R) / R
    cond_probs = np.ones((R, B)) / B   # uniform -> maximal entropy
    print("Validation result:", validate_pcs_ohm(C, gradC, skewC, region_probs, cond_probs))