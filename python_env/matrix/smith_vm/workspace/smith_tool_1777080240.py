# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for QALF Proposal
Checks:
  - Φ_L = 1 - S_defects/S_max  in [0,1]
  - Φ_E = Δt_q/Δt_c            in (0,1]
  - ξ_E ≤ 0.015
  - ψ = ln(Φ_L) defined (Φ_L>0)
  - ξ_L = Δt * c / d ≤ 1
  - Net Φ = Φ_L + Φ_E - ξ_E within theoretical bounds [0,2]
  - Base Φ_density ≈ 0.89 achievable under constraints
  - Additive gains claimed (+4.8 Φ) are impossible under current definitions
"""

import numpy as np

# Constants (can be adjusted)
C = 299792458.0          # m/s, speed of light
S_MAX = 1.0              # normalize entropy to 1 for simplicity
DELTA_T_C = 10e-3        # 10 ms classical latency (example)
D = 0.025                # characteristic length ~2.5 cm (foot sole thickness)
XI_E_MAX = 0.015         # 1.5%

def phi_L(S_defects):
    return 1.0 - S_defects / S_MAX

def phi_E(delta_t_q, delta_t_c=DELTA_T_C):
    return delta_t_q / delta_t_c

def xi_L(delta_t, d=D):
    return delta_t * C / d

def net_phi(S_defects, delta_t_q, delta_t_c=DELTA_T_C, xi_E=0.0):
    return phi_L(S_defects) + phi_E(delta_t_q, delta_t_c) - xi_E

def check_invariants(S_defects, delta_t_q, delta_t_c=DELTA_T_C, xi_E=0.0, delta_t=None):
    """Return dict of pass/fail for each invariant."""
    if delta_t is None:
        delta_t = delta_t_q  # assume actuation latency equals quantum latency for simplicity
    results = {}
    # Φ_L bounds
    pl = phi_L(S_defects)
    results['Phi_L_in_[0,1]'] = 0.0 <= pl <= 1.0
    # Φ_E bounds
    pe = phi_E(delta_t_q, delta_t_c)
    results['Phi_E_in_(0,1]'] = 0.0 < pe <= 1.0
    # Entropy penalty
    results['xi_E_≤_0.015'] = xi_E <= XI_E_MAX
    # ψ defined
    results['psi_defined'] = pl > 0.0
    # ξ_L ≤ 1
    results['xi_L_≤_1'] = xi_L(delta_t) <= 1.0
    # Net Φ bounds (theoretical max 2, min 0)
    phi = net_phi(S_defects, delta_t_q, delta_t_c, xi_E)
    results['Phi_in_[0,2]'] = 0.0 <= phi <= 2.0
    # Base Φ density ~0.89 tolerance
    results['Phi_near_0.89'] = np.isclose(phi, 0.89, atol=0.02)
    return results, phi

def search_feasible_base():
    """Look for any (S_defects, Δt_q) that yields Φ≈0.89 while respecting invariants."""
    S_vals = np.linspace(0, 0.99, 200)   # S_defects/S_max
    dt_q_vals = np.linspace(0.001, DELTA_T_C, 200)  # up to classical latency
    feasible = []
    for S in S_vals:
        for dt_q in dt_q_vals:
            res, phi = check_invariants(S, dt_q, xi_E=0.01)  # use max allowed ξ_E
            if all(res.values()):
                feasible.append((S, dt_q, phi))
    return feasible

def test_claimed_gains():
    """Check if the claimed additive gains (+4.8 Φ) can be derived from the model."""
    # Max possible Φ from model = 2 (when Φ_L=1, Φ_E=1, ξ_E=0)
    max_phi_model = 2.0
    base_phi = 0.89
    claimed_total = base_phi + 4.8
    return {
        'max_phi_model': max_phi_model,
        'claimed_total_phi': claimed_total,
        'claim_exceeds_model': claimed_total > max_phi_model,
        'excess': claimed_total - max_phi_model
    }

if __name__ == "__main__":
    print("=== Omega Protocol Invariant Validation ===")
    # 1. Feasibility search for base Φ≈0.89
    feasible = search_feasible_base()
    print(f"\nFeasible (S_defects/S_max, Δt_q) pairs giving Φ≈0.89: {len(feasible)} found.")
    if feasible:
        # Show a few examples
        for S, dt_q, phi in feasible[:5]:
            print(f"  S/Smax={S:.3f}, Δt_q={dt_q*1e3:.2f} ms → Φ={phi:.3f}")
    else:
        print("  No feasible pair found under current constraints.")

    # 2. Test claimed additive gains
    gain_info = test_claimed_gains()
    print("\n=== Claimed Additive Gain Analysis ===")
    print(f"Maximum Φ achievable by the model: {gain_info['max_phi_model']:.2f}")
    print(f"Claimed total Φ (base +4.8):      {gain_info['claimed_total_phi']:.2f}")
    print(f"Claim exceeds model?              {gain_info['claim_exceeds_model']}")
    if gain_info['claim_exceeds_model']:
        print(f"Excess Φ:                         {gain_info['excess']:.2f} (impossible)")

    # 3. Random sanity check
    print("\n=== Random Sample Validation (10k points) ===")
    np.random.seed(42)
    N = 10000
    S_rand = np.random.rand(N) * 0.99          # keep < S_max
    dt_q_rand = np.random.rand(N) * DELTA_T_C
    xi_e_rand = np.random.rand(N) * XI_E_MAX
    pass_count = 0
    for i in range(N):
        res, _ = check_invariants(S_rand[i], dt_q_rand[i], xi_E=xi_e_rand[i])
        if all(res.values()):
            pass_count += 1
    print(f"Points satisfying all invariants: {pass_count}/{N} ({100*pass_count/N:.1f}%)")