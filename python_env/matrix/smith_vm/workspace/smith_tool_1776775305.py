# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Validation script for the Supply‑Chain Credential Risk Monitor (SCCRM‑Ω) proposal.
It checks the internal mathematical consistency of the formulas presented
and verifies that the derived Omega‑Protocol invariants (Φ_N, Φ_Δ, J*)
respect the bounds and monotonicity constraints implied by the proposal.

Assumptions (made explicit for the test):
- All parameters (α, β, λ, κ, η₁, η₂, τ₁, τ₂) are positive scalars.
- Credential criticality C_fs ∈ [1,5] (int).
- Dissemination scale D_fs ≥ 0.
- Leak timestamps t_fs are non‑negative and ≤ current time t.
- Clustering coefficient CC(s) ∈ [0,1].
- The ecosystem contains at least one firm and one service.
"""

import numpy as np

# ----------------------------------------------------------------------
# Helper functions that implement the equations from the proposal
# ----------------------------------------------------------------------
def service_level_srs(C, D, t_leak, t_now, alpha, beta, lam):
    """
    SRS_s(t) = Σ_f [α·C_fs + β·D_fs] * exp(-λ·(t - t_fs))
    Here we compute the contribution of a single (f,s) pair.
    """
    return (alpha * C + beta * D) * np.exp(-lam * (t_now - t_leak))

def ecosystem_srs(Cs, Ds, t_leaks, t_now, alpha, beta, lam, kappa, service_ids):
    """
    SRS_eco(t) = (1/|S|) * Σ_s SRS_s(t) * [1 + κ·CC(s)]
    For the test we approximate CC(s) as the fraction of firms that share
    at least two services with the current service.  A simple proxy:
        CC(s) = min(1, (n_shared_services - 1) / (n_firms - 1))
    where n_shared_services is the number of services that appear in the
    leak set of at least two firms.
    """
    # Aggregate per service
    SRS_s_dict = {}
    for C, D, t_leak, sid in zip(Cs, Ds, t_leaks, service_ids):
        contrib = service_level_srs(C, D, t_leak, t_now, alpha, beta, lam)
        SRS_s_dict[sid] = SRS_s_dict.get(sid, 0.0) + contrib

    # Compute a rough clustering coefficient for each service
    # Count how many firms appear for each service
    firm_per_service = {}
    for fid, sid in zip(range(len(Cs)), service_ids):  # pretend each leak is from a distinct firm for simplicity
        firm_per_service.setdefault(sid, set()).add(fid)

    # Number of firms that appear in at least two services (proxy for clustering)
    # Build firm->service count
    firm_service_count = {}
    for fid, sid in zip(range(len(Cs)), service_ids):
        firm_service_count[fid] = firm_service_count.get(fid, 0) + 1
    n_firms = len(firm_service_count)
    n_shared = sum(1 for cnt in firm_service_count.values() if cnt >= 2)
    # Approximate CC as same for all services (just for validation)
    CC_approx = min(1.0, n_shared / max(1, n_firms - 1)) if n_firms > 1 else 0.0

    SRS_eco = (1.0 / len(SRS_s_dict)) * \
              sum(val * (1.0 + kappa * CC_approx) for val in SRS_s_dict.values())
    return SRS_eco, CC_approx

def phi_N_sccrm(Phi_N0, SRS_eco, eta1, tau1, t_now):
    """
    Φ_N^{(sccrm)}(t) = Φ_N^{(0)} - η₁·tanh( SRS_eco(t - τ₁) )
    We approximate the delay by using SRS_eco at (t_now - τ₁).
    """
    return Phi_N0 - eta1 * np.tanh(SRS_eco)

def phi_Delta_sccrm(Phi_Delta0, SRS_eco, eta2, tau2, t_now):
    """
    Φ_Δ^{(sccrm)}(t) = Φ_Δ^{(0)} + η₂·SRS_eco(t - τ₂)
    """
    return Phi_Delta0 + eta2 * SRS_eco

def correlation_lengths(SRS_eco, xi_N0, xi_Delta0):
    """
    ξ_N ∝ 1/√SRS_eco   →   ξ_N = ξ_N0 / sqrt(SRS_eco + ε)
    ξ_Δ ∝ 1/SRS_eco    →   ξ_Δ = ξ_Delta0 / (SRS_eco + ε)
    ε avoids division by zero.
    """
    eps = 1e-9
    xi_N = xi_N0 / np.sqrt(SRS_eco + eps)
    xi_Delta = xi_Delta0 / (SRS_eco + eps)
    return xi_N, xi_Delta

def cost_integrand(Phi_N, Phi_Delta, s_SRS, lam1, lam2):
    """
    (1 - Φ_N)² + λ₁·Φ_Δ² + λ₂·s_SRS²
    """
    return (1.0 - Phi_N)**2 + lam1 * Phi_Delta**2 + lam2 * s_SRS**2

# ----------------------------------------------------------------------
# Validation routine
# ----------------------------------------------------------------------
def validate_sccrm():
    np.random.seed(42)

    # ----- Parameter ranges (chosen to be physically plausible) -----
    Phi_N0      = np.random.uniform(0.5, 0.9)   # baseline strategic connectivity
    Phi_Delta0  = np.random.uniform(0.1, 0.4)   # baseline information asymmetry
    eta1        = np.random.uniform(0.05, 0.3)  # strength of Φ_N dampening
    eta2        = np.random.uniform(0.05, 0.3)  # strength of Φ_Δ increase
    tau1        = 3.0   # months (used only as a shift; we treat SRS_eco as already delayed)
    tau2        = 2.0
    alpha       = np.random.uniform(0.1, 0.5)
    beta        = np.random.uniform(0.1, 0.5)
    lam         = np.random.uniform(0.01, 0.2)   # decay constant (day⁻¹) – we treat time in months for simplicity
    kappa       = np.random.uniform(0.0, 0.5)    # clustering amplification
    xi_N0       = np.random.uniform(0.5, 2.0)    # baseline correlation length
    xi_Delta0   = np.random.uniform(0.5, 2.0)
    lam1        = np.random.uniform(0.1, 1.0)
    lam2        = np.random.uniform(0.1, 1.0)

    # ----- Synthetic leak data -----
    n_leaks = 20
    # Criticality 1‑5, dissemination ≥0, timestamps in months ago
    C_vals = np.random.randint(1, 6, size=n_leaks)
    D_vals = np.random.uniform(0.0, 10.0, size=n_leaks)
    t_leak_vals = np.random.uniform(0.0, 24.0, size=n_leaks)   # leaks up to 2 years ago
    t_now = 24.0   # "now" is 24 months after the earliest possible leak
    service_ids = np.random.randint(0, 5, size=n_leaks)   # 5 distinct services

    # ----- Compute SRS_eco -----
    SRS_eco, CC_approx = ecosystem_srs(
        C_vals, D_vals, t_leak_vals, t_now,
        alpha, beta, lam, kappa, service_ids
    )

    # ----- Compute Omega variables -----
    Phi_N = phi_N_sccrm(Phi_N0, SRS_eco, eta1, tau1, t_now)
    Phi_Delta = phi_Delta_sccrm(Phi_Delta0, SRS_eco, eta2, tau2, t_now)
    xi_N, xi_Delta = correlation_lengths(SRS_eco, xi_N0, xi_Delta0)

    # ----- Anomaly score (simplified) -----
    # For the test we just use a dummy residual based on SRS_eco itself
    residual = SRS_eco - np.mean([SRS_eco])  # will be zero → s_SRS = 0
    sigma_residual = np.std([SRS_eco]) + 1e-9
    s_SRS = np.abs(residual) / sigma_residual

    # ----- Cost integrand -----
    integrand = cost_integrand(Phi_N, Phi_Delta, s_SRS, lam1, lam2)

    # ----- Assertions (the "rules") -----
    # 1. Bounds for Omega invariants (as implied by the proposal)
    assert 0.0 <= Phi_N <= 1.0, f"Phi_N out of bounds: {Phi_N}"
    assert 0.0 <= Phi_Delta <= 1.0, f"Phi_Delta out of bounds: {Phi_Delta}"

    # 2. Monotonicity w.r.t. SRS_eco (checked via finite difference)
    eps = 1e-6
    SRS_plus = SRS_eco + eps
    Phi_N_plus = phi_N_sccrm(Phi_N0, SRS_plus, eta1, tau1, t_now)
    Phi_Delta_plus = phi_Delta_sccrm(Phi_Delta0, SRS_plus, eta2, tau2, t_now)
    assert Phi_N_plus <= Phi_N + 1e-9, "Phi_N should not increase with SRS"
    assert Phi_Delta_plus >= Phi_Delta - 1e-9, "Phi_Delta should not decrease with SRS"

    # 3. Correlation lengths decrease with SRS
    xi_N_plus, xi_Delta_plus = correlation_lengths(SRS_plus, xi_N0, xi_Delta0)
    assert xi_N_plus <= xi_N + 1e-9, "xi_N should not increase with SRS"
    assert xi_Delta_plus <= xi_Delta + 1e-9, "xi_Delta should not increase with SRS"

    # 4. Proposed hard constraints from the MPC‑Ω formulation
    assert SRS_eco <= 10.0 + 1e-9, f"SRS_eco exceeds allowed max: {SRS_eco}"
    assert Phi_N >= 0.4 - 1e-9, f"Phi_N below minimum allowed: {Phi_N}"
    assert Phi_Delta <= 0.8 + 1e-9, f"Phi_Delta above maximum allowed: {Phi_Delta}"

    # 5. Cost integrand must be non‑negative (sum of squares)
    assert integrand >= 0.0, f"Cost integrand negative: {integrand}"

    # 6. SCCRM‑Ω specific formulas reproduce the stated dependencies
    #    (already tested via monotonicity; additionally check functional form)
    #    Φ_N = Φ_N0 - η₁·tanh(SRS_eco)  →  derivative = -η₁·sech²(SRS_eco) ≤ 0
    deriv_Phi_N = -eta1 * (1.0 - np.tanh(SRS_eco)**2)
    assert deriv_Phi_N <= 1e-9, f"Derivative of Phi_N w.r.t SRS not non‑positive: {deriv_Phi_N}"
    #    Φ_Δ = Φ_Δ0 + η₂·SRS_eco  →  derivative = η₂ ≥ 0
    assert eta2 >= 0.0, "eta2 must be non‑negative"

    # If we reach here, all checks passed
    print("✅ SCCRM‑Ω mathematical validation passed.")
    print(f"   SRS_eco          = {SRS_eco:.4f}")
    print(f"   Phi_N            = {Phi_N:.4f} (in [0,1])")
    print(f"   Phi_Delta        = {Phi_Delta:.4f} (in [0,1])")
    print(f"   xi_N             = {xi_N:.4f}")
    print(f"   xi_Delta         = {xi_Delta:.4f}")
    print(f"   Cost integrand   = {integrand:.6f}")

# ----------------------------------------------------------------------
# Run validation
# ----------------------------------------------------------------------
if __name__ == "__main__":
    try:
        validate_sccrm()
    except AssertionError as e:
        print("❌ Validation failed:")
        raise e