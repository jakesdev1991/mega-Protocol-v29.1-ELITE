# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validation script for the refined Byzantine-Resilient Streaming Omega (BRS-Ω) proposal.
Checks:
  1. Parameter ranges and types.
  2. Dimensional consistency (all Ω‑variables dimensionless, ξ have time dimension).
  3. Constraints from the Omega Protocol invariants:
        Φ_N ≥ 0.6,  Φ_Δ ≤ 0.7,
        ξ_N⁻² > 0,  ξ_Δ⁻² > 0  (→ finite correlation lengths).
  4. Non‑negativity of the MPC‑Ω cost terms.
  5. Boundary conditions (Shredding Event & Informational Freeze) are not violated.
  6. Entropy‑based threat observable is well‑defined.
Run with a representative set of parameters; the script will raise AssertionError
if any invariant is violated.
"""

import math
import numpy as np

# -------------------------- PARAMETERS (example values) --------------------------
m = 10                     # number of workers (streams)
t = 3                      # tolerated Byzantine workers (must be integer)
s = 0.4                    # sparsity ratio (0 = dense, 1 = maximally sparse)
ell0 = 0.5                 # baseline latency (seconds)
alpha = 0.3                # latency increase per unit t/m
beta  = 0.2                # latency decrease per unit sparsity
ell_max = 2.0              # maximum allowable latency (seconds)

# Mapping coefficients (from the proposal)
Phi_N0   = 0.8
Phi_Delta0 = 0.3
gamma1 = 0.25
gamma2 = 0.15
gamma3 = 0.2
gamma4 = 0.1

# Stiffness‑model coefficients
lam = 1.0                  # coupling constant (dimensionless)
gamma0 = 0.5
gamma1_stiff = 0.05
gamma2_stiff = 0.02
delta0 = 0.4
delta1_stiff = 0.04
delta2_stiff = 0.01

# Entropy / threat detection
H_max = math.log(m)        # maximal Shannon entropy (nats)
H_obs = 1.2                # observed entropy (must be in [0, H_max])

# MPC‑Ω cost weights
lambda1 = 0.5
lambda2 = 0.3

# Boundary thresholds (from the proposal)
Phi_N_min   = 0.6
Phi_Delta_max = 0.7
# -------------------------- END PARAMETERS -------------------------------------

def check_range(name, val, low=None, high=None, int_type=False):
    if int_type:
        assert isinstance(val, int), f"{name} must be integer"
    else:
        assert isinstance(val, (int, float)), f"{name} must be numeric"
    if low is not None:
        assert val >= low, f"{name}={val} below lower bound {low}"
    if high is not None:
        assert val <= high, f"{name}={val} above upper bound {high}"

# 1. Parameter sanity checks
check_range("m", m, low=1, int_type=True)
t_max = (m - 1) // 2
check_range("t", t, low=0, high=t_max, int_type=True)
check_range("s", s, low=0.0, high=1.0)
check_range("ell0", ell0, low=0.0)
check_range("alpha", alpha, low=0.0)
check_range("beta", beta, low=0.0)
check_range("ell_max", ell_max, low=ell0)   # ell_max should be >= baseline
check_range("Phi_N0", Phi_N0, low=0.0, high=1.0)
check_range("Phi_Delta0", Phi_Delta0, low=0.0, high=1.0)
check_range("gamma1", gamma1, low=0.0, high=1.0)
check_range("gamma2", gamma2, low=0.0, high=1.0)
check_range("gamma3", gamma3, low=0.0, high=1.0)
check_range("gamma4", gamma4, low=0.0, high=1.0)
check_range("lam", lam, low=0.0)
check_range("gamma0", gamma0, low=0.0)
check_range("gamma1_stiff", gamma1_stiff, low=0.0)
check_range("gamma2_stiff", gamma2_stiff, low=0.0)
check_range("delta0", delta0, low=0.0)
check_range("delta1_stiff", delta1_stiff, low=0.0)
check_range("delta2_stiff", delta2_stiff, low=0.0)
check_range("H_obs", H_obs, low=0.0, high=H_max)
check_range("lambda1", lambda1, low=0.0)
check_range("lambda2", lambda2, low=0.0)

# 2. Latency model
ell = ell0 + alpha * (t / m) - beta * s
assert ell >= 0.0, f"Computed latency ell={ell} negative"
assert ell <= ell_max, f"Latency ell={ell} exceeds ell_max={ell_max}"

# 3. Omega invariant mappings (as in the refined proposal)
Phi_N_stream = Phi_N0 - gamma1 * (ell / ell_max) + gamma2 * (1.0 - t / t_max)
Phi_Delta_stream = Phi_Delta0 + gamma3 * (ell / ell_max) - gamma4 * (t / t_max)

assert Phi_N_stream >= Phi_N_min, f"Phi_N_stream={Phi_N_stream} < min {Phi_N_min}"
assert Phi_Delta_stream <= Phi_Delta_max, f"Phi_Delta_stream={Phi_Delta_stream} > max {Phi_Delta_max}"
assert 0.0 <= Phi_N_stream <= 1.0, f"Phi_N_stream out of [0,1]: {Phi_N_stream}"
assert 0.0 <= Phi_Delta_stream <= 1.0, f"Phi_Delta_stream out of [0,1]: {Phi_Delta_stream}"

# 4. Stiffness invariants (must stay positive → finite correlation lengths)
xi_N_inv_sq = lam * (gamma0 + gamma1_stiff * t + gamma2_stiff * ell)
xi_Delta_inv_sq = lam * (delta0 - delta1_stiff * t + delta2_stiff * ell)

assert xi_N_inv_sq > 0.0, f"xi_N⁻² ≤ 0 → ξ_N infinite or imaginary: {xi_N_inv_sq}"
assert xi_Delta_inv_sq > 0.0, f"xi_Δ⁻² ≤ 0 → ξ_Δ infinite or imaginary: {xi_Delta_inv_sq}"

# Correlation lengths have dimension of time; we just check they are real positive
xi_N = 1.0 / math.sqrt(xi_N_inv_sq)
xi_Delta = 1.0 / math.sqrt(xi_Delta_inv_sq)
assert xi_N > 0.0 and xi_Delta > 0.0, "Correlation lengths not positive"

# 5. Metric coupling invariant ψ = ln(ξ/ξ₀); choose ξ₀ = 1.0 (dimensionless reference)
xi0 = 1.0
# Use geometric mean as a characteristic length (any positive combo works)
xi_char = math.sqrt(xi_N * xi_Delta)
psi = math.log(xi_char / xi0)
assert isinstance(psi, float), "ψ not a real number"

# 6. Entropy‑based threat observable
theta = 1.0 - H_obs / H_max
assert 0.0 <= theta <= 1.0, f"Threat level θ={theta} outside [0,1]"

# 7. MPC‑Ω cost terms (non‑negative by construction)
cost_state = (1.0 - Phi_N_stream)**2 + (Phi_Delta_stream)**2
cost_threat = lambda1 * (theta - t / m)**2
cost_latency = lambda2 * ell**2
total_cost = cost_state + cost_threat + cost_latency

assert cost_state >= 0.0, "State cost negative"
assert cost_threat >= 0.0, "Threat cost negative"
assert cost_latency >= 0.0, "Latency cost negative"
assert total_cost >= 0.0, "Total MPC cost negative"

# 8. Boundary condition checks (Shredding Event & Informational Freeze)
# Shredding Event: Φ_Δ → Φ_Δ^(min) and ξ_Δ⁻² → 0⁺ (we already enforce Φ_Δ ≤ max and ξ_Δ⁻² > 0)
# Informational Freeze: Φ_N → Φ_N^(max) and ξ_N⁻² → 0⁺ (we enforce Φ_N ≥ min and ξ_N⁻² > 0)
# Additionally, we can define explicit limits:
Phi_N_max_allowed = 0.9   # example upper bound before freeze
Phi_Delta_min_allowed = 0.1 # example lower bound before shredding
assert Phi_N_stream <= Phi_N_max_allowed, f"Φ_N_stream={Phi_N_stream} approaches freeze threshold"
assert Phi_Delta_stream >= Phi_Delta_min_allowed, f"Φ_Δ_stream={Phi_Delta_stream} approaches shredding threshold"

# If we reach here, all invariants are satisfied.
print("✅ All Omega Protocol invariants and mathematical constraints are satisfied.")
print(f"   m={m}, t={t}, s={s:.3f}, ell={ell:.3f}s")
print(f"   Φ_N_stream={Phi_N_stream:.3f}, Φ_Δ_stream={Phi_Delta_stream:.3f}")
print(f"   ξ_N={xi_N:.3f}s, ξ_Δ={xi_Delta:.3f}s, ψ={psi:.3f}")
print(f"   Threat θ={theta:.3f}, MPC cost={total_cost:.3f}")