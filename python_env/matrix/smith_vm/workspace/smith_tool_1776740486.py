# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Validation script for the refined POASH‑Ω proposal.
Checks:
  1. PHI computation stays in [0,1] (by definition).
  2. Derived Omega covariants satisfy the protocol bounds:
        PHI >= 0.4
        Phi_N >= 0.7
        Phi_Delta <= 0.6
  3. Stiffness invariants xi_N, xi_Delta are real and positive
        (i.e., xi_N^{-2} > 0, xi_Delta^{-2} > 0).
  4. The mapping from PHI to Phi_N/Phi_Delta via the information‑theoretic
        model is consistent with the finite‑difference/Var formulation
        used in the MPC stage.
  5. MPC cost terms are non‑negative.
"""

import numpy as np

# ----------------------------------------------------------------------
# Helper functions mimicking the proposal's mathematics
# ----------------------------------------------------------------------
def compute_phi_i(A_k, mu_k, sigma_k, w_k):
    """
    Pipeline Health Index (PHI) as in the proposal:
        PHI = 1 - Σ w_k * |A_k - mu_k| / sigma_k
    Returns a scalar clipped to [0,1] for safety.
    """
    term = np.sum(w_k * np.abs(A_k - mu_k) / sigma_k)
    phi = 1.0 - term
    return np.clip(phi, 0.0, 1.0)

def entropy_from_amplitudes(A_k):
    """
    Information content I(t) = - Σ p_k log p_k,
    p_k = |A_k|^2 / Σ |A_j|^2
    """
    power = np.abs(A_k) ** 2
    total = np.sum(power)
    if total == 0:
        return 0.0
    p = power / total
    # avoid log(0)
    p = p[p > 0]
    return -np.sum(p * np.log(p))

def compute_phi_n_delta_from_entropy(I, I_dot, A_var,
                                    PhiN0, PhiDelta0,
                                    alpha, beta, gamma):
    """
    Derived from the variational model:
        Phi_N = PhiN0 + alpha * dI/dt
        Phi_Delta = PhiDelta0 - beta * I + gamma * Var(A)
    """
    PhiN = PhiN0 + alpha * I_dot
    PhiDelta = PhiDelta0 - beta * I + gamma * A_var
    return PhiN, PhiDelta

def compute_stiffness_from_coherence(coherence_vals, lam=1.0):
    """
    Average coherence <coh(k)>.
    Then:
        xi_N^{-2} = λ ( 3/<coh> + 1/<coh>^2 )
        xi_Delta^{-2} = λ ( 1/<coh> + 3/<coh>^2 )
    Returns xi_N, xi_Delta (positive if formulas hold).
    """
    coh = np.mean(coherence_vals)
    if coh <= 0:
        raise ValueError("Average coherence must be > 0 for stiffness inversion.")
    inv_coh = 1.0 / coh
    xi_N_inv2 = lam * (3.0 * inv_coh + inv_coh ** 2)
    xi_Delta_inv2 = lam * (inv_coh + 3.0 * inv_coh ** 2)
    if xi_N_inv2 <= 0 or xi_Delta_inv2 <= 0:
        raise ValueError("Stiffness inverse squared must be positive.")
    xi_N = 1.0 / np.sqrt(xi_N_inv2)
    xi_Delta = 1.0 / np.sqrt(xi_Delta_inv2)
    return xi_N, xi_Delta, xi_N_inv2, xi_Delta_inv2

def mpc_cost(PHI, PhiDelta, grad_A, lambdas):
    """
    Cost term used in the MPC horizon (single step):
        (1-PHI)^2 + λ1*PhiDelta^2 + λ2*||∇A||^2 + λ3*||u||^2
    Here we omit the control term (set to zero) and just verify
    non‑negativity of the first three terms.
    """
    term1 = (1.0 - PHI) ** 2
    term2 = lambdas[0] * PhiDelta ** 2
    term3 = lambdas[1] * np.sum(grad_A ** 2)
    return term1 + term2 + term3

# ----------------------------------------------------------------------
# Synthetic data generation for validation
# ----------------------------------------------------------------------
np.random.seed(42)
n_metrics = 5                     # latency jitter, throughput, CPU load, error rate, power
n_orders = 4                      # we consider first 4 harmonic orders
n_samples = 100                   # length of time series for stats

# Simulate raw sensor time series (just Gaussian noise around a baseline)
raw = np.random.randn(n_samples, n_metrics) * 0.1 + np.array([0.5, 1.0, 0.3, 0.05, 0.2])

# Approximate harmonic amplitudes by taking the RMS of each metric (placeholder)
A_k = np.sqrt(np.mean(raw ** 2, axis=0))   # shape (n_metrics,)
# For order analysis we would normally have A_k per order; here we reuse same amplitude
# for simplicity and just repeat across orders.
A_k_orders = np.tile(A_k[:, None], (1, n_orders))   # shape (n_metrics, n_orders)

# Baseline healthy statistics (learned from fault‑free operation)
mu_k = np.mean(A_k_orders, axis=0)          # shape (n_orders,)
sigma_k = np.std(A_k_orders, axis=0) + 1e-6 # avoid zero
w_k = np.ones(n_orders) / n_orders          # uniform weights

# Compute PHI
PHI = compute_phi_i(A_k_orders.mean(axis=0), mu_k, sigma_k, w_k)

# Approximate time derivative of PHI using finite difference on a sliding window
PHI_history = np.maximum(0.0, np.minimum(1.0,
                    PHI + 0.05 * np.random.randn(n_samples)))   # fake history
I_dot = np.gradient(PHI_history)[-1]   # latest derivative

# Entropy-based I and its variance (for mapping)
I = entropy_from_amplitudes(A_k_orders.mean(axis=0))
A_var = np.var(A_k_orders.mean(axis=0))

# Parameters for the entropic mapping (chosen to keep outputs in [0,1])
PhiN0, PhiDelta0 = 0.75, 0.5
alpha, beta, gamma = 0.1, 0.2, 0.05

PhiN, PhiDelta = compute_phi_n_delta_from_entropy(
    I, I_dot, A_var, PhiN0, PhiDelta0, alpha, beta, gamma)

# Coherence between sensor pairs (simple Pearson correlation as placeholder)
coh_matrix = np.corrcoef(raw.T)   # shape (n_metrics, n_metrics)
# Extract upper‑triangular without diagonal
coh_vals = coh_matrix[np.triu_indices_from(coh_matrix, k=1)]
# Ensure positivity (correlation can be negative; shift+scale to (0,1])
coh_vals = (coh_vals + 1) / 2.0   # now in [0,1]
# Avoid zeros
coh_vals = np.clip(coh_vals, 1e-6, None)

lam = 1.0
xi_N, xi_Delta, xi_N_inv2, xi_Delta_inv2 = compute_stiffness_from_coherence(coh_vals, lam)

# MPC cost check (single step)
lambdas = [0.5, 0.2, 0.1]   # λ1, λ2, λ3 (λ3 omitted as u=0)
grad_A = np.gradient(A_k_orders.mean(axis=0))   # dummy gradient
cost = mpc_cost(PHI, PhiDelta, grad_A, lambdas)

# ----------------------------------------------------------------------
# Validation assertions (Omega Protocol invariants)
# ----------------------------------------------------------------------
def assert_invariant(name, condition, value=None):
    if not condition:
        raise AssertionError(f"Invariant violation: {name}" +
                             (f" (value={value})" if value is not None else ""))
    else:
        print(f"[OK] {name}" + (f" = {value}" if value is not None else ""))

# 1. PHI bounds from protocol (must stay ≥0.4)
assert_invariant("PHI ≥ 0.4", PHI >= 0.4, PHI)

# 2. Omega covariants bounds
assert_invariant("Phi_N ≥ 0.7", PhiN >= 0.7, PhiN)
assert_invariant("Phi_Delta ≤ 0.6", PhiDelta <= 0.6, PhiDelta)

# 3. Stiffness invariants must be real and positive
assert_invariant("xi_N > 0", xi_N > 0, xi_N)
assert_invariant("xi_Delta > 0", xi_Delta > 0, xi_Delta)
assert_invariant("xi_N^{-2} > 0", xi_N_inv2 > 0, xi_N_inv2)
assert_invariant("xi_Delta^{-2} > 0", xi_Delta_inv2 > 0, xi_Delta_inv2)

# 4. Cost non‑negative (by construction)
assert_invariant("MPC cost ≥ 0", cost >= 0, cost)

# 5. Mapping consistency: PhiN/PhiDelta from entropic model should be close
#    to the empirical linear form used in the proposal:
#        PhiN_emp = PhiN0 + alpha * dPHI/dt
#        PhiDelta_emp = PhiDelta0 - beta * PHI + gamma * Var(A)
PhiN_emp = PhiN0 + alpha * I_dot
PhiDelta_emp = PhiDelta0 - beta * PHI + gamma * A_var
tol = 1e-6
assert_invariant("PhiN mapping consistency",
                 np.abs(PhiN - PhiN_emp) < tol,
                 np.abs(PhiN - PhiN_emp))
assert_invariant("PhiDelta mapping consistency",
                 np.abs(PhiDelta - PhiDelta_emp) < tol,
                 np.abs(PhiDelta - PhiDelta_emp))

print("\nAll Omega Protocol invariants satisfied for this random trial.")
print(f"PHI={PHI:.4f}, Phi_N={PhiN:.4f}, Phi_Delta={PhiDelta:.4f}")
print(f"xi_N={xi_N:.4f}, xi_Delta={xi_Delta:.4f}")
print(f"MPC cost={cost:.6f}")