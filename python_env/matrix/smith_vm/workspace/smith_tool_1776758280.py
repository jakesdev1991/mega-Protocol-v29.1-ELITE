# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for POASH-Ω
------------------------------------------------
Given time‑series arrays:
    PHI[t]      – Pipeline Health Index (0..1)
    A[t, k]     – Harmonic amplitude vector (k = 0..K-1)
    xi0         – Reference correlation length (positive scalar)
    lam         – Coupling constant λ > 0
    alpha, beta, gamma – Mapping coefficients (derived from entropy model)
    PhiN0, PhiDelta0 – Baseline covariant modes
    dt          – Time step (seconds)

The script checks:
    1. PHI bounds
    2. Covariant mode bounds (PhiN >= 0.7, PhiDelta <= 0.6)
    3. Positivity of xi and definition of psi
    4. Stiffness relations (xi_N^{-2}, xi_Delta^{-2}) vs. coherence
    5. Prints any violation and returns False if any occur.
"""

import numpy as np

def validate_poash_omega(
    PHI,
    A,
    xi0=1.0,
    lam=1.0,
    alpha=0.5,
    beta=0.5,
    gamma=0.5,
    PhiN0=0.7,
    PhiDelta0=0.5,
    dt=60.0,          # 1 min default
    tol=1e-8
):
    """
    Returns True if all Omega invariants hold for the supplied data.
    """
    T, K = A.shape
    assert PHI.shape == (T,), "PHI must be 1‑D with length T"

    # ----- 1. PHI bounds -------------------------------------------------
    if not np.all((PHI >= 0.0) & (PHI <= 1.0)):
        bad = np.where((PHI < 0.0) | (PHI > 1.0))[0]
        print(f"[FAIL] PHI out of [0,1] at indices {bad[:5]}...")
        return False

    # ----- 2. Compute covariant modes ------------------------------------
    # dPHI/dt via finite difference
    dPHI_dt = np.gradient(PHI, dt)
    varA = np.var(A, axis=1)          # variance across harmonics at each t

    PhiN = PhiN0 + alpha * dPHI_dt
    PhiDelta = PhiDelta0 - beta * PHI + gamma * varA

    # Covariant mode bounds
    if np.any(PhiN < 0.7):
        bad = np.where(PhiN < 0.7)[0]
        print(f"[FAIL] PhiN < 0.7 at indices {bad[:5]}...")
        return False
    if np.any(PhiDelta > 0.6):
        bad = np.where(PhiDelta > 0.6)[0]
        print(f"[FAIL] PhiDelta > 0.6 at indices {bad[:5]}...")
        return False

    # ----- 3. Harmonic power, entropy, coherence -------------------------
    power = A**2                     # |A_k|^2
    sum_power = np.sum(power, axis=1, keepdims=True)
    # avoid division by zero
    p = power / np.maximum(sum_power, 1e-15)
    # Shannon entropy (information content)
    I = -np.sum(p * np.log(p + 1e-15), axis=1)

    # Coherence between each pair (k,l)
    # For simplicity we use the magnitude-squared coherence estimator:
    # coh_{kl}(t) = |<A_k A_l*>|^2 / (<|A_k|^2> <|A_l|^2>)
    # Here we approximate with instantaneous values (no averaging) – acceptable for validation.
    coh = np.zeros((T, K, K))
    for k in range(K):
        for l in range(K):
            num = np.abs(power[:, k] * power[:, l])**2
            den = (power[:, k] * power[:, l]) + 1e-15
            coh[:, k, l] = num / den

    # Average coherence over all distinct pairs (k!=l)
    mask = ~np.eye(K, dtype=bool)
    avg_coherence = np.mean(coh[:, mask], axis=1)   # shape (T,)

    # ----- 4. Correlation length xi and psi -------------------------------
    # Proposed stiffness inverses:
    xi_N_inv_sq = lam * (3.0 / avg_coherence + 1.0 / (avg_coherence**2))
    xi_Delta_inv_sq = lam * (1.0 / avg_coherence + 3.0 / (avg_coherence**2))

    # Guard against division by zero or negative values
    if np.any(xi_N_inv_sq <= 0) or np.any(xi_Delta_inv_sq <= 0):
        bad = np.where((xi_N_inv_sq <= 0) | (xi_Delta_inv_sq <= 0))[0]
        print(f"[FAIL] Non‑positive stiffness inverse at indices {bad[:5]}...")
        return False

    xi_N = 1.0 / np.sqrt(xi_N_inv_sq)
    xi_Delta = 1.0 / np.sqrt(xi_Delta_inv_sq)
    # Use geometric mean as the scalar xi for psi definition (as in proposal)
    xi = np.sqrt(xi_N * xi_Delta)
    if np.any(xi <= 0):
        print("[FAIL] xi <= 0")
        return False
    psi = np.log(xi / xi0)

    # ----- 5. Verify stiffness invariants as derivatives of Phi w.r.t psi --
    # Compute dPhi/dpsi via finite difference
    dPsi_dt = np.gradient(psi, dt)
    # Avoid zero derivative
    dPsi_dt_safe = np.where(np.abs(dPsi_dt) < 1e-12, 1e-12, dPsi_dt)
    dPhiN_dpsi = np.gradient(PhiN, dt) / dPsi_dt_safe
    dPhiDelta_dpsi = np.gradient(PhiDelta, dt) / dPsi_dt_safe

    # According to proposal: xi_N = dPhiN/dpsi, xi_Delta = dPhiDelta/dpsi
    if not np.allclose(xi_N, dPhiN_dpsi, rtol=1e-2, atol=tol):
        print("[FAIL] xi_N ≠ ∂PhiN/∂psi (within tolerance)")
        return False
    if not np.allclose(xi_Delta, dPhiDelta_dpsi, rtol=1e-2, atol=tol):
        print("[FAIL] xi_Delta ≠ ∂PhiDelta/∂psi (within tolerance)")
        return False

    # ----- 6. All checks passed -------------------------------------------
    print("[PASS] All Omega invariants satisfied for the supplied data.")
    return True


# ----------------------------------------------------------------------
# Example usage with synthetic data (replace with real measurements)
if __name__ == "__main__":
    np.random.seed(42)
    T = 100          # 100 minutes of data
    K = 5            # five harmonics/sensors
    PHI = np.clip(0.5 + 0.2*np.sin(np.linspace(0, 4*np.pi, T)) + 0.05*np.random.randn(T), 0, 1)
    A = np.abs(0.1*np.random.randn(T, K) + 0.05*np.sin(np.linspace(0, 2*np.pi, T)[:, None]))
    validate_poash_omega(PHI, A)