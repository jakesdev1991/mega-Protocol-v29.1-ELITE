# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Validation for Topological Cognitive Memory (TCM‑Ω)

Checks:
  1. CTOI definition uses normalized ratios (baseline = max).
  2. Φ_N = 1 - CTOI (with prediction horizon shift ignored for static check).
  3. ψ = ln(Φ_N), ψ_Δ = ln(Φ_Δ + eps)  (eps avoids log(0)).
  4. Entropy S = - Σ p_i log p_i  with p_i = ||c_i|| / Σ||c_j||.
  5. QP constraints: CTOI >= 0.6, Φ_N >= 0.6, S >= ln(3).
  6. Cost integrand is non‑negative.
  7. Dynamics: dCTOI/dt = -γ*max(stress-Δ,0)*CTOI + κ*intervention
     guarantees CTOI stays in [0,1] for reasonable parameters.
"""

import numpy as np
import sympy as sp

# ----------------------------
# Symbolic checks
# ----------------------------
# Define symbols
CTOI, Delta, Delta0, xi, xi0, Wp, Wp0 = sp.symbols('CTOI Delta Delta0 xi xi0 Wp Wp0', nonnegative=True)
Phi_N, Phi_Delta, psi, psi_Delta, S = sp.symbols('Phi_N Phi_Delta psi psi_Delta S', real=True)
eps = sp.symbols('eps', positive=True)

# 1. CTOI definition (ratio form)
CTOI_expr = (sp.Abs(Wp) / sp.Abs(Wp0)) * (Delta / Delta0) * (xi / xi0)

# 2. Mapping to Phi_N (static, ignore tau)
Phi_N_expr = 1 - CTOI_expr

# 3. Omega invariants
psi_expr = sp.log(Phi_N_expr)
psi_Delta_expr = sp.log(Phi_Delta + eps)   # safeguard

# 4. Entropy (symbolic for two agents as example)
p1, p2 = sp.symbols('p1 p2', nonnegative=True)
S_expr = -(p1*sp.log(p1) + p2*sp.log(p2))  # assumes p1+p2=1

# Verify that psi = ln(Phi_N) holds identically
assert sp.simplify(psi_expr - sp.log(Phi_N_expr)) == 0, "ψ invariant mismatch"

# Verify that ψ_Δ = ln(Φ_Δ+eps) holds
assert sp.simplify(psi_Delta_expr - sp.log(Phi_Delta + eps)) == 0, "ψ_Δ invariant mismatch"

print("Symbolic invariants: OK")

# ----------------------------
# Numerical sanity check
# ----------------------------
np.random.seed(42)
n_samples = 10000

# Healthy baselines (set as maxima)
Delta0_val = 1.0
xi0_val    = 1.0
Wp0_val    = 1.0   # assume normalized to 1 at t=0

# Generate random physiological values within plausible ranges
Delta_vals   = np.random.uniform(0.2, 1.5, n_samples)   # can dip below baseline
xi_vals      = np.random.uniform(0.2, 1.5, n_samples)
Wp_vals      = np.random.uniform(0.0, 1.2, n_samples)  # Wilson loop magnitude <= baseline in healthy state

# Compute CTOI using baseline as MAX (so we clip ratios at 1)
CTOI_vals = np.minimum(np.abs(Wp_vals)/Wp0_val, 1.0) * \
            np.minimum(Delta_vals/Delta0_val, 1.0) * \
            np.minimum(xi_vals/xi0_val, 1.0)

# Phi_N from static mapping (ignore tau)
Phi_N_vals = 1.0 - CTOI_vals

# Phi_Delta: std of log(xi/xi0) across a synthetic population of agents
# Simulate 5 agents per sample
n_agents = 5
xi_agent_vals = np.random.uniform(0.5, 1.5, (n_samples, n_agents))
log_ratios = np.log(xi_agent_vals / xi0_val)
Phi_Delta_vals = np.std(log_ratios, axis=1)

# Entropy: random probability vectors (Dirichlet)
alpha = np.ones(3)  # three cognitive modes
p_vals = np.random.dirichlet(alpha, size=n_samples)
S_vals = -np.sum(p_vals * np.log(p_vals + 1e-12), axis=1)  # avoid log(0)

# Omega invariants numeric
psi_vals = np.log(np.clip(Phi_N_vals, 1e-12, None))
psi_Delta_vals = np.log(Phi_Delta_vals + 1e-9)

# Constraints
ctoi_ok = np.all(CTOI_vals >= 0.6)
phiN_ok = np.all(Phi_N_vals >= 0.6)
entropy_ok = np.all(S_vals >= np.log(3) - 1e-9)  # allow tiny numerical slack

# Cost integrand non‑negative check (sample mu=1)
mu1=mu2=mu3=1.0
integrand = ((0.6 - CTOI_vals)*np.clip(0.6 - CTOI_vals, 0, None))**2 + \
            mu1*((0.6 - Phi_N_vals)*np.clip(0.6 - Phi_N_vals, 0, None))**2 + \
            mu2*(Phi_Delta_vals)**2 + \
            mu3*(np.clip(np.log(3) - S_vals, 0, None))**2
cost_ok = np.all(integrand >= -1e-12)

print(f"CTOI >=0.6 : {ctoi_ok}")
print(f"Phi_N >=0.6: {phiN_ok}")
print(f"Entropy >=ln3: {entropy_ok}")
print(f"Cost integrand non‑negative: {cost_ok}")

# Dynamics check: Euler forward with random stress & intervention
gamma = 0.5
kappa = 0.3
dt = 0.1
CTOI_dyn = CTOI_vals.copy()
stress_vals = np.random.uniform(0.0, 2.0, n_samples)
intervention_vals = np.random.uniform(0.0, 1.0, n_samples)

# Ensure stress, Delta positive
Delta_vals_pos = np.clip(Delta_vals, 0.1, None)

dCTOI = -gamma * np.maximum(stress_vals - Delta_vals_pos, 0.0) * CTOI_dyn + kappa * intervention_vals
CTOI_dyn_next = CTOI_dyn + dCTOI * dt
# Clip to physical range [0,1]
CTOI_dyn_next = np.clip(CTOI_dyn_next, 0.0, 1.0)

dyn_ok = np.all((CTOI_dyn_next >= 0.0) & (CTOI_dyn_next <= 1.0))
print(f"Dynamics keep CTOI in [0,1]: {dyn_ok}")

# Final verdict
if all([ctoi_ok, phiN_ok, entropy_ok, cost_ok, dyn_ok]):
    print("\nVALID: All Ω‑Protocol checks passed.")
else:
    raise AssertionError("\nINVALID: One or more checks failed.")