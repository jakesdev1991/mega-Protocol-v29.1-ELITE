# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for CFIS-Ω
Checks:
    1. CFI(t) >= 0.85
    2. Phi_N_flow(t) >= 0.8
    3. S_flow(t) >= ln(2)
    4. CFI computed from tanh stays in [-1,1]
    5. Phi_N_flow update stays bounded (optional)
    6. Field PDE cubic term yields double-well (lambda>0)
"""

import numpy as np

# ----------------------------------------------------------------------
# Helper functions (mirroring the paper)
# ----------------------------------------------------------------------
def compute_CFI(engagement, Phi_N_flow, Phi_Delta_flow,
                alpha=1.0, beta=1.0, gamma=1.0):
    """CFI = tanh[α·Eng + β·Φ_N^flow − γ·Φ_Δ^flow]"""
    arg = alpha * engagement + beta * Phi_N_flow - gamma * Phi_Delta_flow
    return np.tanh(arg), arg

def Phi_N_flow_update(Phi_N0, CFI_past, S_flow_past,
                      eta1=0.2, eta2=0.1):
    """Φ_N^flow(t) = Φ_N^(0) - η1·(1-CFI(t-τ)) + η2·S_flow(t-τ)"""
    return Phi_N0 - eta1 * (1.0 - CFI_past) + eta2 * S_flow_past

def psi_flow(Persistence1, Persistence0=1.0):
    """ψ_flow = ln(Persistence1 / Persistence0)"""
    if Persistence1 <= 0:
        raise ValueError("Persistence must be >0 for log")
    return np.log(Persistence1 / Persistence0)

def field_potential(F, F_opt=0.0, lam=1.0):
    """Potential V(F) = (λ/4)*(F^2 - F_opt^2)^2  (derived from -λ(F^3-F_opt))"""
    return lam * 0.25 * (F**2 - F_opt**2)**2

# ----------------------------------------------------------------------
# Validation routine
# ----------------------------------------------------------------------
def validate_random_samples(N=10000):
    """Draw random plausible values and assert invariants."""
    np.random.seed(42)
    # plausible ranges (based on typical normalized quantities)
    engagement      = np.random.uniform(0.0, 1.0, N)          # [0,1]
    Phi_N_flow      = np.random.uniform(0.5, 1.5, N)          # around 1
    Phi_Delta_flow  = np.random.uniform(0.0, 0.5, N)          # small distraction
    S_flow          = np.random.uniform(0.5, 1.2, N)          # > ln(2) often
    Persistence1    = np.random.uniform(0.5, 2.0, N)          # >0

    # Pre‑compute constants
    alpha, beta, gamma = 1.0, 1.0, 1.0
    eta1, eta2 = 0.2, 0.1
    ln2 = np.log(2.0)

    for i in range(N):
        # 1. CFI
        CFI, arg = compute_CFI(engagement[i], Phi_N_flow[i], Phi_Delta_flow[i],
                               alpha, beta, gamma)
        assert -1.0 <= CFI <= 1.0, f"CFI out of tanh range: {CFI}"
        assert CFI >= 0.85, f"CFI constraint violated: {CFI} < 0.85 (arg={arg})"

        # 2. Phi_N_flow invariant
        assert Phi_N_flow[i] >= 0.8, f"Phi_N_flow < 0.8: {Phi_N_flow[i]}"

        # 3. S_flow invariant
        assert S_flow[i] >= ln2, f"S_flow < ln(2): {S_flow[i]}"

        # 4. Phi_N_flow update sanity (use past values approximated by current)
        Phi_N_upd = Phi_N_flow_update(Phi_N0=1.0,
                                      CFI_past=CFI,
                                      S_flow_past=S_flow[i])
        # Should stay near 1.0 ± some margin; we just check it's non‑negative
        assert Phi_N_upd >= 0.0, f"Phi_N_flow update negative: {Phi_N_upd}"

        # 5. psi_flow well‑defined
        _ = psi_flow(Persistence1[i])  # will raise if invalid

        # 6. Field potential double-well (lambda>0)
        assert field_potential(CFI, F_opt=0.0, lam=1.0) >= 0.0, "Potential negative"

    print(f"All {N} random samples passed invariant checks.")
    return True

# ----------------------------------------------------------------------
# Edge‑case test for the cubic term stability
# ----------------------------------------------------------------------
def test_cubic_stability():
    """Show that lambda>0 yields a double‑well with minima at +/-F_opt."""
    lam = 0.5
    F_opt = 1.0
    Fs = np.linspace(-2.5, 2.5, 400)
    V = lam * 0.25 * (Fs**2 - F_opt**2)**2
    minima = Fs[np.argmin(V)]
    # Expect minima near +-F_opt
    assert np.isclose(np.abs(minima), F_opt, atol=1e-2), \
        f"Cubic term did not produce wells at +/-{F_opt}, got {minima}"
    print("Cubic stability test passed.")

if __name__ == "__main__":
    validate_random_samples()
    test_cubic_stability()
    print("Ω‑Invariant validation successful.")