# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# Omega Protocol Validator – Higher‑Order Lattice Polarization
# -----------------------------------------------------------
# Checks:
#   1. Perturbative parameters stay small (|ln| < L_max, g2/mD2 < G_max)
#   2. Poisson recovery: ∇² Φ_N + S(Φ_Δ) ≈ 0  (tol)
#   3. Entropy proxy: S_cond = -∫ ρ log ρ  ≥ 0  (discrete approximation)
#   4. No tachyonic/massless modes: m_eff > m_min, m_Δ > mD_min
# -----------------------------------------------------------

import numpy as np

class ShreddingError(RuntimeError):
    pass

def validate_configuration(Phi_N, Phi_Delta, lattice_spacing=a,
                           cutoff_Lambda=np.pi/a,
                           g=0.3,          # example coupling
                           xi_N=1.0, xi_Delta=1.0,
                           m_e=0.511e-3,   # MeV in natural units
                           L_max=5.0, G_max=0.1,
                           poisson_tol=1e-3,
                           m_eff_min=1e-6, m_delta_min=1e-6,
                           entropy_tol=0.0):
    """
    Parameters
    ----------
    Phi_N, Phi_Delta : np.ndarray
        Real‑scalar fields on a regular grid (same shape).
    a : float
        Lattice spacing (sets UV cutoff).
    Returns
    -------
    dict with diagnostic values.
    Raises ShreddingError if any invariant fails.
    """
    # ---- 1. Effective masses -------------------------------------------------
    m_eff = m_e + g * Phi_N          # m_eff = m_e + g_N Φ_N  (set g_N = g for demo)
    xi_Delta = xi_Delta              # correlation length from stiffness
    m_Delta = 1.0 / xi_Delta         # m_Δ = 1/ξ_Δ

    # Check for massless/tachyonic danger
    if np.any(m_eff <= m_eff_min):
        raise ShreddingError(f"m_eff too small/min zero: min={m_eff.min():.3e}")
    if np.any(m_Delta <= m_delta_min):
        raise ShreddingError(f"m_Δ too small/min zero: min={m_Delta.min():.3e}")

    # ---- 2. Perturbative parameters -----------------------------------------
    L = np.log(cutoff_Lambda**2 / m_eff**2)          # one‑loop log
    G = g**2 / m_Delta**2                           # two‑loop coefficient

    if np.any(np.abs(L) > L_max):
        raise ShreddingError(f"One‑loop log exceeds bound: max|L|={np.abs(L).max():.3f} > {L_max}")
    if np.any(G > G_max):
        raise ShreddingError(f"Two‑loop term exceeds bound: max G={G.max():.3f} > {G_max}")

    # ---- 3. Poisson recovery (∇² Φ_N + source ≈ 0) -------------------------
    # Simple 5‑point stencil Laplacian (periodic BC for illustration)
    laplacian = (
        np.roll(Phi_N, 1, axis=0) + np.roll(Phi_N, -1, axis=0) +
        np.roll(Phi_N, 1, axis=1) + np.roll(Phi_N, -1, axis=1) -
        4 * Phi_N
    ) / a**2

    # Source term taken as proportional to Φ_Δ (can be replaced by full kernel)
    source = Phi_Delta   # S(Φ_Δ) = Φ_Δ  (dimensionless scaling absorbed)
    poisson_resid = laplacian + source

    if np.any(np.abs(poisson_resid) > poisson_tol):
        raise ShreddingError(f"Poisson recovery violated: max|res|={np.abs(poisson_resid).max():.3e}")

    # ---- 4. Entropy proxy (Shannon conditional entropy of fluctuations) ----
    # Treat the joint PDF of (Φ_N, Φ_Δ) as a histogram; compute S = -∑ p log p
    # Small additive epsilon avoids log(0).
    joint = np.stack([Phi_N.ravel(), Phi_Delta.ravel()], axis=-1)
    hist, _ = np.histogramdd(joint, bins=20, density=True)
    p = hist.flatten()
    p = p[p > 0]                     # remove zeros
    S_cond = -np.sum(p * np.log(p))

    if S_cond < entropy_tol:
        raise ShreddingError(f"Entropy bound violated: S_cond={S_cond:.3f} < {entropy_tol}")

    # ---- Diagnostics ---------------------------------------------------------
    diag = {
        "m_eff_min": float(m_eff.min()),
        "m_eff_max": float(m_eff.max()),
        "m_Delta_min": float(m_Delta.min()),
        "m_Delta_max": float(m_Delta.max()),
        "log_one_loop_max": float(np.abs(L).max()),
        "two_loop_max": float(G.max()),
        "poisson_resid_max": float(np.abs(poisson_resid).max()),
        "entropy_cond": float(S_cond)
    }
    return diag


# ----------------------------------------------------------------------
# Example usage (replace with actual field data from the derivation)
if __name__ == "__main__":
    # Dummy fields: small fluctuations around zero
    N = 64
    a = 0.1
    Phi_N   = 0.01 * np.random.randn(N, N)
    Phi_D   = 0.01 * np.random.randn(N, N)

    try:
        result = validate_configuration(Phi_N, Phi_D, a=a)
        print("Validation PASSED. Diagnostics:")
        for k, v in result.items():
            print(f"  {k}: {v}")
    except ShreddingError as e:
        print(f"VALIDATION FAILED – Shredding detected: {e}")