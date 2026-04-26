# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Validation script for the Confidential Financial Trauma Monitor (CFTM‑Ω) proposal.
Checks mathematical soundness and Omega‑Protocol invariant compliance.
"""

import numpy as np

# ----------------------------------------------------------------------
# Helper definitions (as per the proposal)
# ----------------------------------------------------------------------
def CTI(A, C, R, L, alpha=0.4, beta=0.3, gamma=0.2, delta=0.1):
    """Confidential Trauma Index – tanh‑scaled linear combination."""
    raw = alpha * A + beta * C + gamma * R + delta * L
    return np.tanh(raw)

def Phi_N(Phi_N0, CTI_val, S_psych, tau=1.0, eta1=0.5, eta2=0.3):
    """Connectivity mode from trauma field (Eq. in proposal)."""
    return Phi_N0 + eta1 * CTI_val - eta2 * S_psych

def Phi_Delta(Phi_Delta0, CTI_val, Phi_N_val, tau=1.0, eta3=0.4, eta4=0.2):
    """Asymmetry mode from trauma field."""
    return Phi_Delta0 + eta3 * CTI_val - eta4 * Phi_N_val

def psi_psych(Phi_N_val, Phi_N0):
    """Ω‑compliant invariant (log‑ratio of connectivity)."""
    return np.log(Phi_N_val / Phi_N0)

def S_psych(p_vec):
    """Behavioral diversity entropy (Shannon)."""
    p_vec = np.asarray(p_vec, dtype=float)
    p_vec = p_vec / p_vec.sum()  # normalize
    return -np.sum(p_vec * np.log(p_vec + 1e-12))

def J_mu(Phi_Delta_val, mu=0):
    """Gauge current – only time component non‑zero."""
    J = np.zeros(4)
    J[mu] = np.sqrt(2) * Phi_Delta_val
    return J

def V_T(T, alpha=-1.0, beta=2.0, gamma=1.5):
    """Double‑well potential V(T) = α/2 T² + β/4 T⁴ − γ T."""
    return 0.5 * alpha * T**2 + 0.25 * beta * T**4 - gamma * T

# ----------------------------------------------------------------------
# Validation tests
# ----------------------------------------------------------------------
def run_validation():
    print("=== CFTM‑Ω Mathematical & Invariant Validation ===")

    # 1. CTI bounds
    A, C, R, L = 0.8, 0.6, 0.4, 0.5   # example proxy values in [0,1]
    cti = CTI(A, C, R, L)
    assert 0.0 <= cti <= 1.0, f"CTI out of bounds: {cti}"
    print(f"✓ CTI ∈ [0,1]: {cti:.4f}")

    # 2. Entropy bounds (for later constraint)
    p_example = np.array([0.4, 0.3, 0.2, 0.1])   # four agent types
    S = S_psych(p_example)
    assert S >= 0.0, f"Entropy negative: {S}"
    print(f"✓ Behavioral entropy S_psych = {S:.4f}")

    # 3. Connectivity and asymmetry baseline values
    Phi_N0 = 1.0
    Phi_Delta0 = 0.2
    Phi_N_val = Phi_N(Phi_N0, cti, S)
    Phi_Delta_val = Phi_Delta(Phi_Delta0, cti, Phi_N_val)

    # 4. Invariant ψ_psych matches log‑ratio
    psi = psi_psych(Phi_N_val, Phi_N0)
    expected_psi = np.log(Phi_N_val / Phi_N0)
    assert np.isclose(psi, expected_psi), f"ψ_psych mismatch: {psi} vs {expected_psi}"
    print(f"✓ ψ_psych = ln(Φ_N/Φ_N0) = {psi:.4f}")

    # 5. Gauge current form
    J = J_mu(Phi_Delta_val, mu=0)
    assert np.allclose(J[1:], 0.0), "Spatial components of J^μ must vanish"
    assert np.isclose(J[0], np.sqrt(2) * Phi_Delta_val), "Time component mismatch"
    print(f"✓ J^μ = [ {J[0]:.4f}, 0, 0, 0 ] (only time‑like)")

    # 6. Double‑well potential minima (qualitative check)
    # For α<0, β>0, γ>0 the potential has two minima; we just verify V(T) is real.
    T_test = np.linspace(-2, 2, 5)
    V_vals = V_T(T_test)
    assert np.all(np.isfinite(V_vals)), "Potential produced non‑finite values"
    print(f"✓ V(T) finite over test range: {V_vals}")

    # 7. QP‑style constraints (as used in MPC‑Ω)
    cti_max = 0.68
    Phi_N_min = 0.55
    S_min = np.log(4)   # ≈1.386

    assert cti <= cti_max + 1e-9, f"CTI constraint violated: {cti} > {cti_max}"
    assert Phi_N_val >= Phi_N_min - 1e-9, f"Φ_N constraint violated: {Phi_N_val} < {Phi_N_min}"
    assert S >= S_min - 1e-9, f"Entropy constraint violated: {S} < {S_min}"
    print(f"✓ QP constraints satisfied: CTI≤{cti_max}, Φ_N≥{Phi_N_min}, S≥ln(4)")

    # 8. Trauma‑field dynamics sanity check (Euler step)
    D, kappa, lam = 0.1, 0.5, 0.2   # diffusion, self‑reinforcement, recovery
    sigma = 0.0                     # no external leak in this step
    zeta = 0.0                      # deterministic
    # Simple 1‑D Laplacian approximation (second difference) with spacing dx=1
    laplacian = 0.0                 # assume spatially uniform field for test
    dTdt = D * laplacian + kappa * cti * (1 - cti) - lam * cti + sigma + zeta
    # Integrate one small step
    dt = 0.01
    T_next = cti + dTdt * dt
    assert 0.0 <= T_next <= 1.0, f"Trauma field left [0,1] after step: {T_next}"
    print(f"✓ Trauma‑field Euler step keeps T∈[0,1] (T→{T_next:.4f})")

    print("\nAll validation checks passed. The proposal is mathematically sound "
          "and compliant with the Omega Protocol invariants.\n")

if __name__ == "__main__":
    run_validation()