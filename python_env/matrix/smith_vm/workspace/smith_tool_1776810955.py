# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Validation for QM‑Ω (Quantum Memory Shield for Distributed Cognition)
--------------------------------------------------------------------------------
This script checks that the mathematical formulation respects the Omega invariants:
    - Φ_N ∈ [0, 1]
    - Φ_Δ ∈ [-1, 1]   (or [0,1] if shifted)
    - CDI ∈ [0, 1]
    - ψ_qm finite (|R_G| > eps)
    - S_cog ≥ ln(3)
    - Hard MPC constraints: CDI ≤ 0.7, Φ_N ≥ 0.6, S_cog ≥ ln(3)
The test draws random samples for the underlying signals and verifies the
properties hold for many iterations.
"""

import numpy as np

# -------------------------- Configuration --------------------------
np.random.seed(42)          # reproducibility
N_TRIALS = 100_000          # number of random samples
M_AGENTS = 25               # as proposed in the integration
DIM_STATE = 10              # dimensionality of cognitive state vector (arbitrary)
EPS_R = 1e-12               # protection against zero curvature
LOG3 = np.log(3.0)

# Coefficients – must be non‑negative (we sample them from a reasonable range)
ALPHA, BETA, GAMMA = np.random.uniform(0, 2, size=3)
ETA1, ETA2, ETA3, ETA4 = np.random.uniform(0, 2, size=4)
LAMBDA = np.random.uniform(0, 2)
MU1, MU2, MU3 = np.random.uniform(0, 2, size=3)

# Baseline Omega values (chosen inside the admissible interval)
PHI_N0 = np.random.uniform(0.4, 0.8)
PHI_D0 = np.random.uniform(-0.5, 0.5)
PSI0   = np.random.uniform(-2, 2)

# Time‑delays (lead times) – not needed for the static check
TAU1, TAU2 = 2.0, 5.0   # hours, only used symbolically

# -------------------------- Helper Functions --------------------------
def safe_tanh(x):
    """tanh that guarantees non‑negative output (clipped at 0)."""
    return np.tanh(np.maximum(x, 0.0))

def clip01(x):
    return np.minimum(np.maximum(x, 0.0), 1.0)

def clip_pm1(x):
    return np.minimum(np.maximum(x, -1.0), 1.0)

def compute_cdi(theta, eps, rho):
    """Cognitive Decoherence Index with safeguards."""
    arg = ALPHA * theta + BETA * eps + GAMMA * rho
    return safe_tanh(arg)          # ∈ [0,1]

def compute_phi_n(cdi, theta):
    """Φ_N^{(qm)} with linear mapping and clipping."""
    val = PHI_N0 - ETA1 * cdi + ETA2 * (1.0 - theta)
    return clip01(val)

def compute_phi_delta(theta, eps):
    """Φ_Δ^{(qm)} with linear mapping and clipping."""
    val = PHI_D0 + ETA3 * theta - ETA4 * eps
    return clip_pm1(val)

def compute_psi(cdi, ricci_abs):
    """Invariant ψ from Ollivier‑Ricci curvature."""
    # Avoid log of zero or negative
    log_term = np.log(np.maximum(ricci_abs, EPS_R) / 1.0)  # R0 set to 1 for simplicity
    return log_term + LAMBDA * cdi

def compute_entropy(agent_norms):
    """S_cognitive from agent response norms."""
    # Avoid division by zero
    total = np.sum(agent_norms)
    if total <= 0:
        # All zero norms → uniform distribution over agents (max entropy)
        p = np.ones(M_AGENTS) / M_AGENTS
    else:
        p = agent_norms / total
    # Shannon entropy
    return -np.sum(p * np.log(np.maximum(p, 1e-15)))   # protect log(0)

# -------------------------- Monte‑Carlo Test --------------------------
def run_validation():
    for i in range(N_TRIALS):
        # ---- Raw signals (all non‑negative by construction) ----
        theta   = np.random.uniform(0.0, 1.0)          # decoherence ratio
        eps     = np.random.uniform(0.0, 1.0)          # average residual error
        rho     = np.random.uniform(1.0, 4.0)          # redundancy factor n/d (≥1)
        # Agent response norms – ensure at least three agents have non‑zero norm
        agent_norms = np.random.uniform(0.0, 2.0, size=M_AGENTS)
        # Force at least three agents > 0 to guarantee S_cog ≥ ln(3) possible
        if np.count_nonzero(agent_norms > 1e-6) < 3:
            idx = np.random.choice(M_AGENTS, size=3, replace=False)
            agent_norms[idx] = np.random.uniform(0.5, 2.0, size=3)

        # ---- Derived quantities ----
        cdi   = compute_cdi(theta, eps, rho)
        phi_n = compute_phi_n(cdi, theta)
        phi_d = compute_phi_delta(theta, eps)
        # Ricci curvature magnitude – sample a positive value; occasionally near zero to test EPS_R
        ricci_abs = np.random.uniform(0.0, 5.0)
        psi   = compute_psi(cdi, ricci_abs)
        s_cog = compute_entropy(agent_norms)

        # ---- Invariant checks ----
        assert 0.0 <= cdi <= 1.0, f"CDI out of bounds: {cdi}"
        assert 0.0 <= phi_n <= 1.0, f"Phi_N out of bounds: {phi_n}"
        assert -1.0 <= phi_d <= 1.0, f"Phi_Delta out of bounds: {phi_d}"
        assert np.isfinite(psi), f"Psi non‑finite (Ricci≈0): {psi}"
        assert s_cog >= LOG3 - 1e-9, f"S_cog below ln(3): {s_cog}"

        # ---- Hard MPC constraints (must be satisfied by the controller) ----
        # In a true MPC these would be enforced; here we simply verify that the
        # sampled point does not violate them – if it does, the controller would
        # need to act.
        assert cdi <= 0.7 + 1e-9, f"CDI exceeds hard limit: {cdi}"
        assert phi_n >= 0.6 - 1e-9, f"Phi_N below hard limit: {phi_n}"
        assert s_cog >= LOG3 - 1e-9, f"S_cog below hard limit: {s_cog}"

        # ---- Cost integrand non‑negativity (sanity) ----
        integrand = ((cdi - 0.6) ** 2 if cdi > 0.6 else 0.0) \
                  + MU1 * ((0.6 - phi_n) ** 2 if phi_n < 0.6 else 0.0) \
                  + MU2 * (phi_d ** 2) \
                  + MU3 * ((LOG3 - s_cog) ** 2 if s_cog < LOG3 else 0.0)
        assert integrand >= 0.0, f"Negative integrand: {integrand}"

    print(f"✅ Validation passed over {N_TRIALS:,} random trials.")
    print(f"   Sampled coefficient ranges:")
    print(f"     α,β,γ = [{ALPHA:.3f},{BETA:.3f},{GAMMA:.3f}]")
    print(f"     η₁…η₄ = [{ETA1:.3f},{ETA2:.3f},{ETA3:.3f},{ETA4:.3f}]")
    print(f"     λ     = {LAMBDA:.3f}")
    print(f"     μ₁…μ₃ = [{MU1:.3f},{MU2:.3f},{MU3:.3f}]")

if __name__ == "__main__":
    run_validation()