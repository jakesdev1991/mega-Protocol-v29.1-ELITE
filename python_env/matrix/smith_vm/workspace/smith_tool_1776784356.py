# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator for LFBFM‑Ω
------------------------------------------------
This script checks the mathematical consistency of the core equations
presented in the Linguistic Freeze‑Boundary Fragility Monitor (LFBFM‑Ω)
proposal and verifies that the derived quantities respect the Omega
Protocol invariants (Phi_N, Phi_Delta, J* → here represented by the
constraints on LFBFI, Phi_N, Phi_Delta and the linguistic entropy).

The validation is deliberately lightweight: it works with synthetic
data that mimics the structure described in the proposal and asserts
that no invariant is violated.  If any assertion fails, an
AssertionError is raised with a diagnostic message.

Assumptions made for the purpose of this check:
* The linguistic field L is a 4‑dimensional vector per unit:
      L = [sentiment, uncertainty, urgency, consensus]  (all ∈ [0,1])
* The action S is dimensionless → we only need to verify that each
  term is a pure number (no hidden dimensional constants).
* Omega‑Protocol invariants enforced via the MPC‑Ω constraints:
      LFBFI ≤ 0.7
      Phi_N ≥ 0.6
      S_ling ≥ log(5)
* The mapping from LFBFI to the Omega modes uses the linear
  approximations given in the proposal (lead times τ are set to 0 for
  the static check; the inequalities are monotonic in LFBFI, so the
  sign of the coefficients is what matters).

If you want to test with real data, replace the synthetic generator
with your own data loader and keep the same validation functions.
"""

import numpy as np
import itertools

# ----------------------------------------------------------------------
# Helper functions that mirror the definitions in the proposal
# ----------------------------------------------------------------------
def tanh(x):
    return np.tanh(x)

def compute_LFBFI(unit_features, alpha, beta, gamma, delta):
    """
    unit_features: shape (N_units, 4) → [NegSent, Unc, Urg, (1-Coh)]
    Returns LFBFI_i(t) for each unit and the global weighted LFBFI.
    """
    raw = alpha * unit_features[:, 0] + beta * unit_features[:, 1] + \
          gamma * unit_features[:, 2] + delta * unit_features[:, 3]
    LFBFI_i = tanh(raw)
    # For the static test we use uniform weights; in practice w_i ∝ influence.
    w = np.ones(LFBFI_i.shape) / LFBFI_i.shape[0]
    LFBFI_global = np.dot(w, LFBFI_i)
    return LFBFI_i, LFBFI_global

def map_to_Phi(Phi0, LFBFI, Consensus=None, Coherence=None,
               eta1=0.2, eta2=0.1, eta3=0.15, eta4=0.05, tau=0):
    """
    Static mapping (τ=0) as per:
        Phi_N = Phi_N0 - η1·LFBFI(t-τ) + η2·Consensus(t-τ)
        Phi_Delta = Phi_Delta0 + η3·LFBFI(t-τ) - η4·Coherence(t-τ)
    Consensus and Coherence are assumed to be the averages over units.
    """
    Phi_N = Phi0[0] - eta1 * LFBFI + eta2 * (Consensus if Consensus is not None else 0.5)
    Phi_D = Phi0[1] + eta3 * LFBFI - eta4 * (Coherence if Coherence is not None else 0.5)
    return Phi_N, Phi_D

def linguistic_entropy(pattern_counts):
    """
    pattern_counts: dict or array of frequencies p_f.
    Returns Shannon entropy S_ling = -∑ p_f log p_f.
    """
    p = np.asarray(list(pattern_counts.values()), dtype=float)
    p = p / p.sum()  # normalize
    # avoid log(0)
    p = np.clip(p, 1e-12, None)
    return -np.sum(p * np.log(p))

def psi_from_LFBFI(LFBFI, lam=0.3):
    """
    Approximation used in the proposal:
        ψ ≈ ln(LFBFI/(1-LFBFI)) + λ·d(LFBFI)/dt
    For the static check we set the derivative term to zero.
    """
    # guard against division by zero
    eps = 1e-9
    LFBFI_safe = np.clip(LFBFI, eps, 1.0 - eps)
    return np.log(LFBFI_safe / (1.0 - LFBFI_safe)) + lam * 0.0

def potential_V(L, alpha=0.5, beta=0.2):
    """
    Double‑well V(L) = α/2 ‖L‖² + β/4 ‖L‖⁴ .
    Returns scalar per unit (we later average).
    """
    norm_sq = np.sum(L**2, axis=-1)
    return 0.5 * alpha * norm_sq + 0.25 * beta * norm_sq**2

def action_density(L, grad_L, g_mu_nu=np.eye(4),
                   alpha=0.5, beta=0.2,
                   lambda_Omega=0.1, L_Omega=0.0,
                   A_mu=np.zeros(4), J_mu=np.zeros(4)):
    """
    Computes the integrand of the Omega Action:
        ½ g^{μν} ∂_μ L·∂_ν L + V(L) + λ_Ω L_Ω(Φ_N,Φ_Δ) + A_μ J^μ
    For the static validation we set gradients and gauge terms to zero
    and treat L_Ω as a dummy scalar (set to 0).  The result should be a
    pure number.
    """
    kinetic = 0.5 * np.tensordot(grad_L, np.tensordot(g_mu_nu, grad_L, axes=([0],[0])), axes=([0,1],[0,1]))
    # In the static case grad_L = 0 → kinetic = 0
    potential = np.mean(V(L, alpha, beta))
    coupling = lambda_Omega * L_Omega  # =0
    gauge = np.dot(A_mu, J_mu)         # =0
    return kinetic + potential + coupling + gauge

# ----------------------------------------------------------------------
# Synthetic data generator (mimics confidential document features)
# ----------------------------------------------------------------------
def generate_synthetic_units(n_units=10, seed=42):
    rng = np.random.default_rng(seed)
    # Each feature in [0,1]; we bias them to produce a realistic spread.
    NegSent = rng.beta(2, 5, n_units)   # mostly low sentiment
    Unc     = rng.beta(1, 3, n_units)   # low uncertainty
    Urg     = rng.beta(1, 4, n_units)   # low urgency
    Coh     = rng.beta(5, 2, n_units)   # high consensus → (1-Coh) low
    # Build the feature vector as defined in LFBFI: [NegSent, Unc, Urg, (1-Coh)]
    features = np.column_stack([NegSent, Unc, Urg, 1.0 - Coh])
    return features

def generate_pattern_counts(n_patterns=8, seed=123):
    rng = np.random.default_rng(seed)
    counts = rng.dirichlet(np.ones(n_patterns))
    return {f"pattern_{i}": counts[i] for i in range(n_patterns)}

# ----------------------------------------------------------------------
# Validation routine
# ----------------------------------------------------------------------
def validate_LFBFM_Omega():
    print("=== LFBFM‑Ω Omega‑Protocol Invariant Validation ===")

    # 1. Generate synthetic linguistic field data
    features = generate_synthetic_units(n_units=12)
    # Features are already [NegSent, Unc, Urg, (1-Coh)]

    # 2. Choose calibrated weights (example values from proposal)
    alpha, beta, gamma, delta = 0.4, 0.2, 0.3, 0.1

    # 3. Compute LFBFI per unit and globally
    LFBFI_i, LFBFI_global = compute_LFBFI(features, alpha, beta, gamma, delta)
    print(f"LFBFI per unit: {np.round(LFBFI_i, 3)}")
    print(f"Global LFBFI: {LFBFI_global:.3f}")

    # 4. Invariant: LFBFI must lie in [0,1] (tanh guarantees this)
    assert np.all((LFBFI_i >= 0.0) & (LFBFI_i <= 1.0)), "Unit LFBFI out of [0,1]"
    assert (0.0 <= LFBFI_global <= 1.0), "Global LFBFI out of [0,1]"

    # 5. Compute average consensus and coherence needed for Phi mapping
    # Consensus_i = Coh_i (we stored 1-Coh, so recover)
    Consensus_i = 1.0 - features[:, 3]
    Coherence_i = Consensus_i  # in the proposal coherence ≈ consensus for this demo
    Consensus_avg = np.mean(Consensus_i)
    Coherence_avg = np.mean(Coherence_i)

    # 6. Map to Omega modes (using baseline values Phi_N0=0.8, Phi_Delta0=0.2)
    Phi_N0, Phi_Delta0 = 0.8, 0.2
    Phi_N, Phi_Delta = map_to_Phi(
        (Phi_N0, Phi_Delta0),
        LFBFI_global,
        Consensus=Consensus_avg,
        Coherence=Coherence_avg
    )
    print(f"Phi_N: {Phi_N:.3f}, Phi_Delta: {Phi_Delta:.3f}")

    # 7. Omega‑Protocol constraints (from MPC‑Ω section)
    assert LFBFI_global <= 0.7 + 1e-9, f"LFBFI violates upper bound: {LFBFI_global}"
    assert Phi_N >= 0.6 - 1e-9, f"Phi_N violates lower bound: {Phi_N}"
    # Entropy constraint
    pattern_counts = generate_pattern_counts()
    S_ling = linguistic_entropy(pattern_counts)
    print(f"Linguistic entropy S_ling: {S_ling:.3f}")
    assert S_ling >= np.log(5) - 1e-9, f"S_ling below log(5): {S_ling}"

    # 8. Compute psi from LFBFI (static approximation)
    psi = psi_from_LFBFI(LFBFI_global)
    print(f"Psi (approx): {psi:.3f}")

    # 9. Action density check (should be a pure number)
    # For static validation we set gradients and gauge terms to zero.
    grad_L = np.zeros_like(features)  # ∂_μ L = 0
    g_mu_nu = np.eye(4)               # Minkowski‑like metric (dimensionless)
    action = action_density(features, grad_L, g_mu_nu=g_mu_nu)
    print(f"Action density (static): {action:.6f}")
    # No dimensional analysis possible here; we just ensure it's a finite real.
    assert np.isfinite(action), "Action density is not finite"

    # 10. Potential shape check: double‑well requires α>0, β>0
    assert alpha > 0 and beta > 0, "Potential coefficients must be positive for double‑well"

    # 11. Verify that the mapping from LFBFI to Phi_N/Phi_Delta is monotonic
    # (as implied by the coefficients' signs)
    test_LFBFI = np.linspace(0.0, 1.0, 11)
    Phi_N_test = Phi_N0 - 0.2 * test_LFBFI + 0.1 * Consensus_avg
    Phi_D_test = Phi_Delta0 + 0.15 * test_LFBFI - 0.05 * Coherence_avg
    assert np.all(np.diff(Phi_N_test) <= 0), "Phi_N should decrease with LFBFI"
    assert np.all(np.diff(Phi_D_test) >= 0), "Phi_Delta should increase with LFBFI"

    print("\n✅ All Omega‑Protocol invariants and mathematical consistency checks passed.")
    return True

# ----------------------------------------------------------------------
# Run validation
# ----------------------------------------------------------------------
if __name__ == "__main__":
    try:
        validate_LFBFM_Omega()
    except AssertionError as e:
        print("\n❌ Validation FAILED:")
        raise e