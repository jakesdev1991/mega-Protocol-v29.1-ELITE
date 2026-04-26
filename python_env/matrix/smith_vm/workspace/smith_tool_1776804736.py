# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TCM-Ω Mathematical & Ω‑Protocol Compliance Validator
-----------------------------------------------------
Checks:
  * CTOI definition and bounds
  * Φ_N = CTOI  (chosen convention)
  * Φ_Δ = Std[log(xi/xi0)]
  * ψ = ln(Φ_N), ψ_Δ = ln(Φ_Δ)
  * Entropy gauge S >= ln(3)
  * Hard QP constraints: CTOI >= 0.6, Φ_N >= 0.6, S >= ln(3)
  * Quadratic cost function
  * Numerical tolerance for invariant checks
"""

import numpy as np

# ------------------- USER‑CONFIGURABLE PARAMETERS -------------------
# Baselines (healthy population) – should be obtained from control data
W0 = 1.0          # |<W_p(0)>|
Delta0 = 1.0      # Δ0
Xi0    = 1.0      # ξ0
tau_pred = 2.0    # weeks (prediction horizon – used only for shifting if needed)
mu1 = mu2 = mu3 = 1.0   # cost weights
tol = 1e-9        # tolerance for invariant equality
# --------------------------------------------------------------------

def safe_log(x):
    """Log that returns -inf for non‑positive inputs (to be caught by constraints)."""
    return np.where(x > 0, np.log(x), -np.inf)

def compute_ctoi(W_loop, Delta, Xi):
    """
    CTOI = (|<W_p>|/|<W_p0>|) * (Δ/Δ0) * (ξ/ξ0)
    All inputs are assumed to be 1‑D arrays of same length (time steps).
    """
    W_norm = np.abs(W_loop) / W0
    D_norm = Delta / Delta0
    X_norm = Xi    / Xi0
    return W_norm * D_norm * X_norm

def compute_phi_n(ctoi):
    """Φ_N = CTOI (chosen convention)."""
    return ctoi

def compute_phi_delta(xi):
    """
    Φ_Δ = Std[ log( ξ_i / ξ0 ) ] across agents at each time step.
    xi: shape (n_time, n_agents)
    """
    log_ratio = np.log(xi / Xi0 + 1e-15)   # avoid log(0)
    return np.std(log_ratio, axis=1)

def compute_entropy(c_tilde):
    """
    Shannon entropy of the normalized agent‑response distribution.
    c_tilde: shape (n_time, n_agents, dim) – we collapse the dim by norm.
    """
    norms = np.linalg.norm(c_tilde, axis=2)          # (n_time, n_agents)
    p = norms / (np.sum(norms, axis=1, keepdims=True) + 1e-15)
    # Avoid log(0)
    S = -np.sum(p * np.log(p + 1e-15), axis=1)
    return S

def compute_psi(phi_n):
    """Ω‑invariant ψ = ln(Φ_N)."""
    return safe_log(phi_n)

def compute_psi_delta(phi_delta):
    """Ω‑invariant ψ_Δ = ln(Φ_Δ)."""
    return safe_log(phi_delta)

def hard_constraints_passed(ctoi, phi_n, entropy):
    """Return bool and a dict of which constraints fail."""
    fails = {}
    if np.any(ctoi < 0.6 - tol):
        fails['CTOI'] = ctoi[ctoi < 0.6]
    if np.any(phi_n < 0.6 - tol):
        fails['Phi_N'] = phi_n[phi_n < 0.6]
    if np.any(entropy < np.log(3) - tol):
        fails['Entropy'] = entropy[entropy < np.log(3)]
    passed = len(fails) == 0
    return passed, fails

def quadratic_cost(ctoi, phi_n, phi_delta, entropy):
    """
    J = ∫ [ (0.6-CTOI)_+^2 + μ1(0.6-Φ_N)_+^2 + μ2 Φ_Δ^2 + μ3 (ln3 - S)_+^2 ] dt
    We approximate the integral by a simple sum (Δt = 1).
    """
    term1 = np.maximum(0.6 - ctoi, 0.0)**2
    term2 = mu1 * np.maximum(0.6 - phi_n, 0.0)**2
    term3 = mu2 * phi_delta**2
    term4 = mu3 * np.maximum(np.log(3) - entropy, 0.0)**2
    return np.sum(term1 + term2 + term3 + term4)

def validate_tcm_omega(W_loop, Delta, Xi, h_stress, c_tilde):
    """
    Main validation routine.
    Returns a dict with all computed quantities and test results.
    """
    # --- Core observables ---
    ctoi = compute_ctoi(W_loop, Delta, Xi)
    phi_n = compute_phi_n(ctoi)                 # Φ_N = CTOI
    phi_delta = compute_phi_delta(Xi)           # Φ_Δ
    entropy = compute_entropy(c_tilde)

    # --- Ω‑invariants ---
    psi = compute_psi(phi_n)
    psi_delta = compute_psi_delta(phi_delta)

    # --- Invariant checks ---
    psi_ok = np.allclose(psi, safe_log(phi_n), atol=tol, rtol=0)
    psi_delta_ok = np.allclose(psi_delta, safe_log(phi_delta), atol=tol, rtol=0)

    # --- Hard constraints ---
    constraints_ok, fails = hard_constraints_passed(ctoi, phi_n, entropy)

    # --- Cost ---
    cost = quadratic_cost(ctoi, phi_n, phi_delta, entropy)

    # Assemble results
    results = {
        'CTOI': ctoi,
        'Phi_N': phi_n,
        'Phi_Δ': phi_delta,
        'S_cognitive': entropy,
        'ψ': psi,
        'ψ_Δ': psi_delta,
        'Invariant ψ OK': psi_ok,
        'Invariant ψ_Δ OK': psi_delta_ok,
        'Hard constraints OK': constraints_ok,
        'Constraint failures': fails,
        'Quadratic cost': cost
    }
    return results

# ------------------- Example usage with synthetic data -------------------
if __name__ == "__main__":
    np.random.seed(42)
    n_steps = 50
    n_agents = 20

    # Simulate healthy baselines with small noise
    W_loop = np.ones(n_steps) + 0.05*np.random.randn(n_steps)
    Delta  = np.ones(n_steps) + 0.02*np.random.randn(n_steps)
    Xi     = np.ones((n_steps, n_agents)) + 0.03*np.random.randn((n_steps, n_agents))
    h_stress = np.random.randn(n_steps, 3)   # dummy stressor vector
    c_tilde = np.random.randn(n_steps, n_agents, 4)   # 4‑dim response per agent

    out = validate_tcm_omega(W_loop, Delta, Xi, h_stress, c_tilde)

    print("\n=== TCM‑Ω Validation Report ===")
    for k, v in out.items():
        if isinstance(v, np.ndarray):
            print(f"{k:20}: shape={v.shape}, min={v.min():.4f}, max={v.max():.4f}")
        else:
            print(f"{k:20}: {v}")
    # --------------------------------------------------------------------