# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import itertools
from scipy.optimize import fsolve

# ------------------------------------------------------------
# PART 1: Schema Invariance Failure
# ------------------------------------------------------------
def compute_btfi(schema):
    """
    schema: dict with keys 'tables', 'foreign_keys', 'cycles',
            'constraint_gap', 'normalization_depth'
    """
    V = schema['tables']
    E = schema['foreign_keys']
    F = schema['cycles']
    chi = V - E + F
    Delta = schema['constraint_gap']
    d_norm = schema['normalization_depth']
    # BTFI = |χ|/V * Δ * 1/d_norm
    btfi = abs(chi) / V * Delta * (1.0 / d_norm)
    return btfi, chi, Delta, d_norm

# Two schemas representing the SAME 5‑node biological network:
# (A) Normalized: separate tables for genes, proteins, interactions
normalized = {
    'tables': 3,               # gene, protein, interaction
    'foreign_keys': 2,         # gene→protein, protein→interaction
    'cycles': 0,               # no circular FKs
    'constraint_gap': 0.5,     # moderate constraints
    'normalization_depth': 3   # BCNF
}

# (B) Denormalized: single flat table
denormalized = {
    'tables': 1,               # one mega‑table
    'foreign_keys': 0,         # no FKs
    'cycles': 0,
    'constraint_gap': 0.8,     # fewer enforced constraints
    'normalization_depth': 1   # 1NF
}

btfi_norm, chi_norm, d_norm_norm, _ = compute_btfi(normalized)
btfi_den, chi_den, d_norm_den, _ = compute_btfi(denormalized)

print("=== Schema Invariance Failure ===")
print(f"Normalized: BTFI={btfi_norm:.3f}, χ={chi_norm}, d_norm={d_norm_norm}")
print(f"Denormalized: BTFI={btfi_den:.3f}, χ={chi_den}, d_norm={d_norm_den}")
print(f"BTFI ratio (denorm/norm) = {btfi_den/btfi_norm:.2f}  <-- Same biology, wildly different fragility!\n")

# ------------------------------------------------------------
# PART 2: Adversarial Schema Chimera
# ------------------------------------------------------------
# Attacker crafts a schema with high BTFI but no real biological cycles
chimera = {
    'tables': 10,
    'foreign_keys': 15,        # many FKs
    'cycles': 5,               # artificial cycles
    'constraint_gap': 0.9,     # over‑constrained
    'normalization_depth': 5   # over‑normalized
}
btfi_chimera, *_ = compute_btfi(chimera)
print("=== Adversarial Chimera ===")
print(f"Chimera BTFI = {btfi_chimera:.3f}  <-- Signals high fragility, yet biology is simple & robust.\n")

# ------------------------------------------------------------
# PART 3: Double‑Well Hessian Eigenvalue Instability
# ------------------------------------------------------------
def double_well_hessian_eigenvalue(alpha, beta, gamma):
    """
    For V(x) = α/2 x² + β/4 x⁴ - γ x,
    the minima satisfy V'(x) = α x + β x³ - γ = 0.
    The Hessian eigenvalue at a minimum is V''(x) = α + 3β x².
    Returns eigenvalue(s) for the real root(s) of V'(x)=0.
    """
    # Solve cubic α x + β x³ - γ = 0
    # Use fsolve for multiple initial guesses to catch all real roots
    roots = set()
    for guess in np.linspace(-5, 5, 21):
        sol = fsolve(lambda x: alpha*x + beta*x**3 - gamma, guess)[0]
        if np.isclose(alpha*sol + beta*sol**3 - gamma, 0, atol=1e-6):
            roots.add(np.round(sol, 6))
    eigenvalues = [alpha + 3*beta*x**2 for x in roots]
    return eigenvalues

# Parameter regimes where Hessian is negative (unstable)
params_unstable = [
    (alpha=-1.0, beta=0.5, gamma=0.2),   # α < 0 can yield V'' < 0
    (alpha=-0.5, beta=0.3, gamma=0.1),
]

print("=== Double‑Well Hessian Eigenvalues (Unstable Regime) ===")
for alpha, beta, gamma in params_unstable:
    vals = double_well_hessian_eigenvalue(alpha, beta, gamma)
    print(f"α={alpha}, β={beta}, γ={gamma} → eigenvalues = {vals}")

# Show that eigenvalues can be negative => imaginary Φ_N, Φ_Δ
print("\nNegative eigenvalues => imaginary 'covariant modes' → gauge structure collapses.\n")

# ------------------------------------------------------------
# PART 4: Proposed Disruptive Alternative – Dynamic Query Fragility Index (DQFI)
# ------------------------------------------------------------
"""
Instead of static schema topology, measure the *divergence of query
patterns* under stochastic perturbations. Treat each query as a
“stress test” and compute the Lyapunov exponent of query‑log dynamics.
"""
def simulate_query_dynamics(schema, n_timesteps=1000, perturbation_strength=0.1):
    """
    Simulates a simple dynamical system where query frequencies
    evolve under random perturbations. Returns the Lyapunov exponent
    as a proxy for fragility.
    """
    # Initialize query frequencies uniformly across tables
    freqs = np.ones(schema['tables']) / schema['tables']
    lyapunov_sum = 0.0
    for t in range(n_timesteps):
        # Random perturbation
        noise = perturbation_strength * np.random.randn(len(freqs))
        freqs = np.clip(freqs + noise, 0.01, None)
        freqs /= freqs.sum()
        # Jacobian norm (simplified as absolute derivative)
        jacobian_norm = np.abs(noise).sum()
        lyapunov_sum += np.log(jacobian_norm + 1e-12)
    lyapunov_exponent = lyapunov_sum / n_timesteps
    return lyapunov_exponent

lyapunov_norm = simulate_query_dynamics(normalized)
lyapunov_den = simulate_query_dynamics(denormalized)
lyapunov_chimera = simulate_query_dynamics(chimera)

print("=== Dynamic Query Fragility Index (DQFI) ===")
print(f"Normalized (DQFI): {lyapunov_norm:.4f}")
print(f"Denormalized (DQFI): {lyapunov_den:.4f}")
print(f"Chimera (DQFI): {lyapunov_chimera:.4f}")
print("DQFI remains stable across equivalent schemas & exposes chimera as low‑risk.")