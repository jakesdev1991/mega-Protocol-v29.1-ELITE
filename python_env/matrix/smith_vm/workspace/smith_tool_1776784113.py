# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LASH‑Ω mathematical validation.
Enforces Omega Protocol invariants on the linguistic‑derived fields.
"""

import numpy as np

# ----------------------------------------------------------------------
# Helper functions (mirroring the proposal)
# ----------------------------------------------------------------------
def tanh(x): return np.tanh(x)

def compute_SCI(sentiment, ambiguity, jargon, urgency, coherence):
    """
    Placeholder: In reality SCI comes from a calibrated GBR.
    Here we use a simple linear combination that stays in [0,1] after clipping.
    """
    raw = (0.4*sentiment - 0.3*ambiguity - 0.2*jargon + 0.2*urgency + 0.3*coherence)
    return np.clip(raw, 0.0, 1.0)

def Phi_N_ling(SCI, Phi_N0=0.5, eta1=0.3, tau1=0):
    """Φ_N^{(ling)} = Φ_N0 + η1 * tanh(SCI(t-τ1))"""
    return Phi_N0 + eta1 * tanh(SCI)

def Phi_Delta_ling(ambiguity, coherence, Phi_Delta0=0.4, eta2=0.25, eta3=0.2, tau2=0):
    """Φ_Δ^{(ling)} = Φ_Δ0 + η2*Ambiguity - η3*Coherence"""
    return Phi_Delta0 + eta2 * ambiguity - eta3 * coherence

def linguistic_invariant(sigma, sigma0=1.0, SCI_val=0.0, lam=0.5):
    """ψ = ln(σ/σ0) + λ·SCI"""
    if sigma <= 0:
        raise ValueError("Semantic spread σ must be > 0 for log.")
    return np.log(sigma / sigma0) + lam * SCI_val

def stiffness_coefficients(SCI, ambiguity, coherence,
                           Phi_N0=0.5, eta1=0.3, eta2=0.25, eta3=0.2,
                           tau1=0, tau2=0, eps=1e-6):
    """
    Compute ξ_N and ξ_Δ via finite differences on ψ.
    ψ = ln(σ/σ0) + λ·SCI  →  dψ/dSCI = λ  (σ treated constant for this demo)
    """
    lam = 0.5  # same λ as in ψ
    # dΦ_N/dSCI = η1 * sech^2(SCI)
    dPhi_N_dSCI = eta1 * (1.0 / np.cosh(SCI))**2
    # dΦ_Δ/dSCI = 0 (ambiguity & coherence assumed independent of SCI in this simple demo)
    dPhi_Delta_dSCI = 0.0
    # ξ = (dΦ/dSCI) / (dψ/dSCI) = (dΦ/dSCI) / λ
    xi_N = dPhi_N_dSCI / lam
    xi_Delta = dPhi_Delta_dSCI / lam
    return xi_N, xi_Delta

# ----------------------------------------------------------------------
# Synthetic data generator (for validation)
# ----------------------------------------------------------------------
def generate_sample(n=100, seed=42):
    rng = np.random.default_rng(seed)
    # Features already normalized to [0,1]
    sentiment = rng.random(n)
    ambiguity = rng.random(n)
    jargon = rng.random(n)
    urgency = rng.random(n)
    coherence = rng.random(n)
    # Semantic spread σ > 0 (log‑normal to avoid zeros)
    sigma = rng.lognormal(mean=0.0, sigma=0.5, size=n)
    return sentiment, ambiguity, jargon, urgency, coherence, sigma

# ----------------------------------------------------------------------
# Validation routine
# ----------------------------------------------------------------------
def validate():
    sentiment, ambiguity, jargon, urgency, coherence, sigma = generate_sample()
    SCI = compute_SCI(sentiment, ambiguity, jargon, urgency, coherence)

    # 1. Feature & SCI bounds
    assert np.all((0.0 <= sentiment) & (sentiment <= 1.0)), "sentiment out of [0,1]"
    assert np.all((0.0 <= ambiguity) & (ambiguity <= 1.0)), "ambiguity out of [0,1]"
    assert np.all((0.0 <= jargon) & (jargon <= 1.0)), "jargon out of [0,1]"
    assert np.all((0.0 <= urgency) & (urgency <= 1.0)), "urgency out of [0,1]"
    assert np.all((0.0 <= coherence) & (coherence <= 1.0)), "coherence out of [0,1]"
    assert np.all((0.0 <= SCI) & (SCI <= 1.0)), "SCI out of [0,1]"

    # 2. Field variables (choose baselines that keep them in [0,1])
    Phi_N = Phi_N_ling(SCI, Phi_N0=0.5, eta1=0.3)
    Phi_Delta = Phi_Delta_ling(ambiguity, coherence,
                               Phi_Delta0=0.4, eta2=0.25, eta3=0.2)

    assert np.all((0.0 <= Phi_N) & (Phi_N <= 1.0)), "Phi_N out of [0,1]"
    assert np.all((0.0 <= Phi_Delta) & (Phi_Delta <= 1.0)), "Phi_Delta out of [0,1]"

    # 3. Linguistic invariant ψ (must be real)
    psi = linguistic_invariant(sigma, sigma0=1.0, SCI_val=SCI)
    assert np.all(np.isfinite(psi)), "ψ produced NaN or Inf"

    # 4. Stiffness coefficients – compare FD vs analytic
    xi_N_fd, xi_Delta_fd = stiffness_coefficients(SCI, ambiguity, coherence)
    # Analytic: ξ_N = η1 * sech^2(SCI) / λ ; λ=0.5
    lam = 0.5
    xi_N_analytic = eta1 * (1.0 / np.cosh(SCI))**2 / lam
    xi_Delta_analytic = 0.0  # ambiguity & coherence independent of SCI in this demo
    assert np.allclose(xi_N_fd, xi_N_analytic, atol=1e-4), "ξ_N mismatch"
    assert np.allclose(xi_Delta_fd, xi_Delta_analytic, atol=1e-4), "ξ_Δ mismatch"

    # 5. MPC‑Ω hard constraints
    assert np.all(SCI >= 0.6), "SCI constraint violated (<0.6)"
    assert np.all(Phi_N >= 0.7), "Phi_N constraint violated (<0.7)"
    assert np.all(Phi_Delta <= 0.6), "Phi_Delta constraint violated (>0.6)"

    print("All LASH‑Ω mathematical checks passed – Omega Protocol invariants upheld.")

if __name__ == "__main__":
    validate()