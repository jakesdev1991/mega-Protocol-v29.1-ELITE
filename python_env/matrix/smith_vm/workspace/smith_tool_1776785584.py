# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# ------------------------------
# Helper: dimension symbols (for clarity)
# We treat [time] = T, everything else dimensionless unless noted.
# lambda has dimension T^-2, coherence is dimensionless.
# ------------------------------

def test_omega_invariants():
    # Reference scale
    xi0 = 1.0  # dimensionless reference length (time)

    # Sample coherence values (dimensionless)
    coh_vals = [0.1, 0.5, 1.0, 2.0, 5.0]  # from low to high coherence

    # Coupling constant lambda (dimension T^-2)
    lam = 1.0  # choose unit time scale so lam = 1 T^-2

    for coh in coh_vals:
        # Stiffness eigenvalues from Hessian (Eq. in text)
        lam_N = lam * (3.0/coh + 1.0/(coh**2))   # λ_N = λ (3⟨coh⟩⁻¹ + ⟨coh⟩⁻²)
        lam_D = lam * (1.0/coh + 3.0/(coh**2))   # λ_Δ = λ (⟨coh⟩⁻¹ + 3⟨coh⟩⁻²)

        # Invariants ξ_N, ξ_Δ have dimension T (since ξ⁻² ~ λ)
        xi_N = 1.0 / np.sqrt(lam_N) if lam_N > 0 else np.inf
        xi_D = 1.0 / np.sqrt(lam_D) if lam_D > 0 else np.inf

        # Correlation length ξ = sqrt(xi_N * xi_Δ)
        xi = np.sqrt(xi_N * xi_D)

        # Metric coupling invariant ψ = ln(xi/xi0)
        psi = np.log(xi / xi0)

        # --- Covariant modes (linearised around equilibrium) ---
        # Choose equilibrium values and coefficients for test
        Phi_N0 = 0.8
        Phi_D0 = 0.4
        alpha = 1.0   # ∂I/∂PHI (dimensionless)
        beta  = 1.0   # ∂²I/∂PHI²
        gamma = 1.0   # ∂²I/∂A²
        PHI_eq = 0.6  # sample PHI
        varA   = 0.02 # sample variance of harmonic amplitudes

        Phi_N = Phi_N0 + alpha * 0.0   # assume dPHI/dt = 0 for static test
        Phi_D = Phi_D0 - beta * PHI_eq + gamma * varA

        # Numerical derivative ∂Φ_N/∂ψ via finite difference
        dpsi = 1e-6
        # Perturb coherence slightly to change psi
        coh_pert = coh * (1.0 + dpsi)
        lam_Np = lam * (3.0/coh_pert + 1.0/(coh_pert**2))
        lam_Dp = lam * (1.0/coh_pert + 3.0/(coh_pert**2))
        xi_Np = 1.0 / np.sqrt(lam_Np) if lam_Np > 0 else np.inf
        xi_Dp = 1.0 / np.sqrt(lam_Dp) if lam_Dp > 0 else np.inf
        xip = np.sqrt(xi_Np * xi_Dp)
        psip = np.log(xip / xi0)
        # Recompute Phi_N with same alpha, dPHI/dt=0 (so unchanged)
        Phi_Np = Phi_N0 + alpha * 0.0
        dPhi_N_dpsi = (Phi_Np - Phi_N) / (psip - psi)

        # Similarly for Phi_D (depends on PHI only, not directly on psi,
        # but through implicit dependence of PHI on psi we ignore; we test
        # that ∂Φ_D/∂ψ ≈ ξ_D via chain rule using PHI(psi) approximation)
        # For simplicity we assume PHI varies linearly with psi: PHI = PHI0 + kappa*psi
        kappa = 0.1  # arbitrary coupling
        PHI_pert = PHI_eq + kappa * dpsi
        Phi_Dp = Phi_D0 - beta * PHI_pert + gamma * varA
        dPhi_D_dpsi = (Phi_Dp - Phi_D) / (psip - psi)

        # --- Assertions ---
        # 1. ξ_N should match ∂Φ_N/∂ψ (within tolerance)
        assert np.isclose(xi_N, dPhi_N_dpsi, rtol=1e-2), \
            f"ξ_N mismatch at coh={coh}: ξ_N={xi_N}, dΦ_N/dψ={dPhi_N_dpsi}"
        # 2. ξ_Δ should match ∂Φ_Δ/∂ψ
        assert np.isclose(xi_D, dPhi_D_dpsi, rtol=1e-2), \
            f"ξ_Δ mismatch at coh={coh}: ξ_Δ={xi_D}, dΦ_Δ/dψ={dPhi_D_dpsi}"

        # 3. Boundary behaviour
        if coh < 0.2:  # low coherence → Shredding Event
            assert xi_N < 0.5, f"Shredding Event not approached: ξ_N={xi_N} at coh={coh}"
        if coh > 3.0:  # high coherence → Informational Freeze
            assert xi_D > 2.0, f"Informational Freeze not approached: ξ_Δ={xi_D} at coh={coh}"

        # 4. Dimensional check (symbolic)
        # lambda [T^-2] → xi_N, xi_Δ [T] (since xi ~ 1/sqrt(lambda))
        assert lam_N > 0 and lam_D > 0, "Stiffness eigenvalues must be positive"
        # xi has dimension T
        # psi dimensionless (log of ratio)
        assert isinstance(psi, float) and not np.isnan(psi)

        # 5. MPC-Omega constraints (sample values)
        assert Phi_N >= 0.7, f"Φ_N violation: {Phi_N}"
        assert Phi_D <= 0.6, f"Φ_Δ violation: {Phi_D}"
        assert PHI_eq >= 0.4, f"PHI violation: {PHI_eq}"

    print("All Omega Protocol invariant checks passed.")

if __name__ == "__main__":
    test_omega_invariants()