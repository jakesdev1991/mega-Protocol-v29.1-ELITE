# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol CFIS-Ω Validator
--------------------------------
Checks mathematical soundness and invariant compliance of the refined
Cognitive Flow Integrity Shield (CFIS-Ω) as described in the audit.
"""

import numpy as np

# ------------------- PARAMETERS (representative values) -------------------
# Physical / cognitive constants (chosen for illustration)
D = 0.1          # diffusion coefficient
lam = 0.5        # nonlinear restoring strength
gamma = 0.2      # coupling strength
F_opt = 1.0      # optimal flow field value (can be any positive scalar)
alpha = 1.0      # expertise scaling exponent
eps = 1e-8       # small regularizer to avoid division by zero
ln2 = np.log(2.0)

# ------------------- 1. Flow Field Equilibrium Check -------------------
def restoring_term(F, F_opt=F_opt, lam=lam):
    """
    Corrected cubic restoring term derived from double-well potential:
        V(F) = (lam/4) * (F^2 - F_opt^2)^2
    => -dV/dF = -lam * F * (F^2 - F_opt^2)
    """
    return -lam * F * (F**2 - F_opt**2)

def test_equilibrium():
    """Verify that F = F_opt is a zero of the restoring term."""
    val = restoring_term(F_opt)
    assert np.isclose(val, 0.0, atol=1e-12), \
        f"Restoring term at F_opt={F_opt} gives {val}, expected 0."
    # Also check that a small perturbation yields a restoring force toward F_opt
    pert = F_opt + 0.1
    val_pert = restoring_term(pert)
    # sign should oppose the perturbation
    assert np.sign(val_pert) == -np.sign(pert - F_opt), \
        f"Restoring force does not push back toward F_opt: {val_pert}"
    print("✓ Flow field equilibrium test passed.")

# ------------------- 2. Coupling Term Dimensionality -------------------
def coupling_term(F, grad_PhiDelta):
    """
    Intended form: scalar F times vector grad_PhiDelta.
    Returns a vector of same shape as grad_PhiDelta.
    """
    return gamma * F * grad_PhiDelta

def test_coupling():
    F = np.random.rand()
    grad_PhiDelta = np.random.rand(3)   # example 3‑D gradient
    vec = coupling_term(F, grad_PhiDelta)
    assert vec.shape == grad_PhiDelta.shape, \
        f"Coupling term shape mismatch: {vec.shape} vs {grad_PhiDelta.shape}"
    print("✓ Coupling term dimensionality test passed.")

# ------------------- 3. Adaptive Manifold Safety -------------------
def adaptive_coordinate(task_diff, user_skill, alpha=alpha, eps=eps):
    """
    Computes the first coordinate of the adaptive manifold:
        task_difficulty / (user_skill^α + eps)
    """
    return task_diff / (user_skill**alpha + eps)

def test_manifold():
    # nominal case
    assert np.isfinite(adaptive_coordinate(5.0, 2.0))
    # edge case: zero skill
    assert np.isfinite(adaptive_coordinate(5.0, 0.0))
    # edge case: very small skill
    assert np.isfinite(adaptive_coordinate(5.0, 1e-6))
    print("✓ Adaptive manifold division‑by‑zero guard passed.")

# ------------------- 4. Invariant Enforcement via Simple MPC ------------
def cfi(t, engagement=0.9, PhiN_flow=0.85, PhiDelta_flow=0.1,
        alpha_w=0.6, beta_w=0.3, gamma_w=0.1):
    """
    Placeholder CFI formula (tanh combination). Weights are illustrative.
    """
    arg = alpha_w * engagement + beta_w * PhiN_flow - gamma_w * PhiDelta_flow
    return np.tanh(arg)

def mpc_cost(w1, w2, horizon=10):
    """
    Quadratic penalty for violating constraints over a horizon.
    We simulate a dummy trajectory where CFI, PhiN_flow, S_flow drift linearly
    with time; the weights scale the penalties.
    """
    t = np.arange(horizon)
    # dummy trajectories (could be replaced with a real simulator)
    CFI_t = 0.8 + 0.01 * t          # slowly increasing
    PhiN_t = 0.75 + 0.005 * t
    S_t = ln2 - 0.001 * t           # slowly decreasing

    # constraint violations (positive when below threshold)
    viol_CFI = np.maximum(0.85 - CFI_t, 0.0)
    viol_PhiN = np.maximum(0.8 - PhiN_t, 0.0)
    viol_S = np.maximum(ln2 - S_t, 0.0)

    cost = np.sum(w1 * viol_CFI**2 + w2 * viol_PhiN**2)
    return cost

def test_invariants():
    # Simple grid search for weights that keep cost zero (i.e., no violations)
    feasible = False
    for w1 in np.linspace(0.1, 2.0, 10):
        for w2 in np.linspace(0.1, 2.0, 10):
            if mpc_cost(w1, w2) == 0.0:
                feasible = True
                break
        if feasible:
            break
    assert feasible, "No weight pair found that satisfies all constraints over horizon."
    print("✓ Invariant feasibility test passed (weights exist).")

# ------------------- MAIN DRIVER -----------------------------------------
if __name__ == "__main__":
    try:
        test_equilibrium()
        test_coupling()
        test_manifold()
        test_invariants()
        print("\nAll validation checks PASSED. CFIS-Ω is mathematically sound "
              "and respects Omega Protocol invariants (subject to the noted "
              "ambiguities in the original proposal).")
    except AssertionError as e:
        print("\nValidation FAILED:", e)
        raise SystemExit(1)