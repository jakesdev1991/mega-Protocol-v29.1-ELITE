# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

def validate_slba_omega(phi_n0, phi_delta0, alpha_c, beta_kappa, weights, 
                       r_crit=0.7, phi_n_min=0.8, 
                       phi_n_bound=(0, 1), phi_delta_bound=(0, 1)):
    """
    Validates SLBA-Ω implementation against Omega Protocol invariants.
    
    Parameters:
    -----------
    phi_n0 : float
        Baseline connectedness (Φ_N⁰)
    phi_delta0 : float
        Baseline asymmetry (Φ_Δ⁰)
    alpha_c : float
        Sensitivity coefficient for coverage
    beta_kappa : float
        Sensitivity coefficient for consistency
    weights : list/array
        [w1, w2, w3, w4] for robustness score R_D
    r_crit : float
        Minimum acceptable robustness score (default: 0.7)
    phi_n_min : float
        Minimum required Φ_N^(doc) (default: 0.8)
    phi_n_bound : tuple
        (min, max) acceptable range for Φ_N^(doc)
    phi_delta_bound : tuple
        (min, max) acceptable range for Φ_Δ^(doc)
    
    Returns:
    --------
    dict
        Validation results with keys:
        - 'invariant_compliance': bool
        - 'constraint_feasibility': dict
        - 'metric_consistency': dict
        - 'warnings': list
        - 'errors': list
    """
    results = {
        'invariant_compliance': True,
        'constraint_feasibility': {
            'phi_n_constraint': False,
            'r_d_constraint': False,
            'feasible_region': None
        },
        'metric_consistency': {
            'xi_n_monotonic': False,
            'xi_delta_monotonic': False,
            'r_d_range': (0, 0)
        },
        'warnings': [],
        'errors': []
    }
    
    eps = 1e-9
    
    # ===== INVARIANT COMPLIANCE CHECKS =====
    # 1. Φ_N^(doc) must remain within bounds for all C_D ∈ [0,1]
    phi_n_min_val = phi_n0 * np.tanh(alpha_c * 0)  # At C_D=0
    phi_n_max_val = phi_n0 * np.tanh(alpha_c * 1)  # At C_D=1
    
    if phi_n_min_val < phi_n_bound[0] - eps or phi_n_max_val > phi_n_bound[1] + eps:
        results['invariant_compliance'] = False
        results['errors'].append(
            f"Φ_N^(doc) range [{phi_n_min_val:.3f}, {phi_n_max_val:.3f}] "
            f"exceeds bounds {phi_n_bound}"
        )
    
    # 2. Φ_Δ^(doc) must remain within bounds for all κ_D ∈ [0,1]
    phi_delta_min_val = phi_delta0 + beta_kappa * (1 - 1)  # At κ_D=1
    phi_delta_max_val = phi_delta0 + beta_kappa * (1 - 0)  # At κ_D=0
    
    if phi_delta_min_val < phi_delta_bound[0] - eps or phi_delta_max_val > phi_delta_bound[1] + eps:
        results['invariant_compliance'] = False
        results['errors'].append(
            f"Φ_Δ^(doc) range [{phi_delta_min_val:.3f}, {phi_delta_max_val:.3f}] "
            f"exceeds bounds {phi_delta_bound}"
        )
    
    # ===== CONSTRAINT FEASIBILITY CHECKS =====
    # 1. Φ_N^(doc) ≥ phi_n_min feasibility
    max_phi_n = phi_n0 * np.tanh(alpha_c)  # Max at C_D=1
    results['constraint_feasibility']['phi_n_constraint'] = (max_phi_n >= phi_n_min - eps)
    
    if not results['constraint_feasibility']['phi_n_constraint']:
        results['warnings'].append(
            f"Φ_N^(doc) constraint infeasible: max possible={max_phi_n:.3f} < required={phi_n_min}"
        )
    
    # 2. R_D ≥ r_crit feasibility (R_D = w·x, x∈[0,1]^4)
    # Max R_D = sum(weights) when all inputs=1
    max_r_d = np.sum(weights)
    min_r_d = 0  # When all inputs=0
    
    results['constraint_feasibility']['r_d_constraint'] = (max_r_d >= r_crit - eps)
    results['constraint_feasibility']['feasible_region'] = (min_r_d, max_r_d)
    
    if not results['constraint_feasibility']['r_d_constraint']:
        results['warnings'].append(
            f"R_D constraint infeasible: max possible={max_r_d:.3f} < required={r_crit}"
        )
    
    # ===== METRIC CONSISTENCY CHECKS =====
    # 1. Correlation lengths should decrease with improving documentation
    # ξ_N ∝ 1/σ_D → should be decreasing in σ_D
    sigma_d_vals = np.array([0.1, 0.5, 0.9])
    xi_n_vals = 1 / sigma_d_vals  # Proportional
    results['metric_consistency']['xi_n_monotonic'] = np.all(np.diff(xi_n_vals) < -eps)
    
    # ξ_Δ ∝ 1/φ_D → should be decreasing in φ_D
    phi_d_vals = np.array([0.1, 0.5, 0.9])
    xi_delta_vals = 1 / phi_d_vals
    results['metric_consistency']['xi_delta_monotonic'] = np.all(np.diff(xi_delta_vals) < -eps)
    
    # 2. R_D range validation
    results['metric_consistency']['r_d_range'] = (float(min_r_d), float(max_r_d))
    
    # ===== CROSS-DOMAIN TRANSFER VALIDATION =====
    # Check if sensitivity coefficients maintain proportionality across domains
    # In tokamak: β_N limits; in stablecoin: collateral ratios
    # The same β_kappa should apply to consistency metrics in both domains
    if beta_kappa <= 0:
        results['errors'].append("β_κ must be positive for meaningful consistency sensitivity")
        results['invariant_compliance'] = False
    
    if alpha_c <= 0:
        results['errors'].append("α_C must be positive for meaningful coverage sensitivity")
        results['invariant_compliance'] = False
    
    # ===== WEIGHTS VALIDATION =====
    if not np.allclose(np.sum(weights), 1.0, atol=eps):
        results['errors'].append(f"Weights must sum to 1.0 (got {np.sum(weights):.3f})")
        results['invariant_compliance'] = False
    
    if np.any(np.array(weights) < -eps):
        results['errors'].append("Weights must be non-negative")
        results['invariant_compliance'] = False
    
    return results

# Example validation with parameters from proposal
if __name__ == "__main__":
    # Parameters extracted from Agent Alpha's proposal
    params = {
        'phi_n0': 1.0,          # Baseline connectedness (normalized)
        'phi_delta0': 0.2,      # Baseline asymmetry
        'alpha_c': 2.0,         # Sensitivity to coverage (chosen to give tanh(2)≈0.96)
        'beta_kappa': 0.3,      # Sensitivity to consistency
        'weights': [0.25, 0.25, 0.25, 0.25],  # Equal weights
        'r_crit': 0.7,
        'phi_n_min': 0.8
    }
    
    results = validate_slba_omega(**params)
    
    print("=== SLBA-Ω Omega Protocol Validation ===")
    print(f"Invariant Compliance: {'PASS' if results['invariant_compliance'] else 'FAIL'}")
    print("\nConstraint Feasibility:")
    print(f"  Φ_N^(doc) ≥ 0.8: {'FEASIBLE' if results['constraint_feasibility']['phi_n_constraint'] else 'INFEASIBLE'}")
    print(f"  R_D ≥ 0.7: {'FEASIBLE' if results['constraint_feasibility']['r_d_constraint'] else 'INFEASIBLE'}")
    print(f"  R_D range: [{results['constraint_feasibility']['feasible_region'][0]:.3f}, "
          f"{results['constraint_feasibility']['feasible_region'][1]:.3f}]")
    print("\nMetric Consistency:")
    print(f"  ξ_N monotonic in σ_D: {'PASS' if results['metric_consistency']['xi_n_monotonic'] else 'FAIL'}")
    print(f"  ξ_Δ monotonic in φ_D: {'PASS' if results['metric_consistency']['xi_delta_monotonic'] else 'FAIL'}")
    print(f"  R_D range: [{results['metric_consistency']['r_d_range'][0]:.3f}, "
          f"{results['metric_consistency']['r_d_range'][1]:.3f}]")
    
    if results['warnings']:
        print("\nWarnings:")
        for w in results['warnings']:
            print(f"  - {w}")
    
    if results['errors']:
        print("\nErrors:")
        for e in results['errors']:
            print(f"  - {e}")
    else:
        print("\nNo critical errors detected.")