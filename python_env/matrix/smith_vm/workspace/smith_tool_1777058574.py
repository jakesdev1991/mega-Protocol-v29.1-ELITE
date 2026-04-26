# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from typing import Tuple, Optional, Union

def validate_invariant_001(
    g0: np.ndarray,
    phi_N: float = 1.0,
    epsilon: float = 1e-6,
    xi_N: float = 0.95,
    beta_min: float = 0.01,
    beta_max: float = 0.1,
    rho_samples: int = 1000,
    beta_samples: int = 1000
) -> Tuple[bool, Optional[dict]]:
    """
    Validate INV-001 (Metric Non-Degeneracy: det(g) > 0) for SOUL-M v2.0
    in the normal operating range (rho ∈ [0, xi_N/phi_N]).
    
    The metric is defined as: g = g0 + beta * psi(rho) * I
    where psi(rho) = ln(phi_N * rho + epsilon)
    
    Returns:
        (is_valid, failure_info)
        is_valid: True if det(g) > 0 for all (rho, beta) in domain
        failure_info: dict with details if invalid (None if valid)
    """
    # Validate g0 is symmetric and positive definite
    if not np.allclose(g0, g0.T):
        return False, {"error": "g0 must be symmetric"}
    
    eigvals = np.linalg.eigvalsh(g0)
    lambda_min_g0 = np.min(eigvals)
    if lambda_min_g0 <= 0:
        return False, {"error": "g0 must be positive definite (lambda_min <= 0)"}
    
    # Define normal operating range for rho: [0, xi_N/phi_N]
    rho_max = xi_N / phi_N
    rho_grid = np.linspace(0, rho_max, rho_samples)
    beta_grid = np.linspace(beta_min, beta_max, beta_samples)
    
    # Precompute psi(rho) for efficiency
    psi_values = np.log(phi_N * rho_grid + epsilon)
    
    # Check condition: lambda_min(g) = lambda_min(g0) + beta * psi(rho) > 0
    min_eigenvalue = lambda_min_g0  # Will be updated in loop
    failure_points = []
    
    for i, rho in enumerate(rho_grid):
        psi = psi_values[i]
        for beta in beta_grid:
            lambda_min_g = lambda_min_g0 + beta * psi
            if lambda_min_g <= 0:
                failure_points.append({
                    "rho": float(rho),
                    "beta": float(beta),
                    "psi": float(psi),
                    "lambda_min_g0": float(lambda_min_g0),
                    "lambda_min_g": float(lambda_min_g),
                    "perturbation": float(beta * psi)
                })
    
    if failure_points:
        # Return the worst failure (most negative eigenvalue)
        worst = min(failure_points, key=lambda x: x["lambda_min_g"])
        return False, {
            "failure_type": "metric_degeneracy",
            "worst_point": worst,
            "total_failures": len(failure_points),
            "failure_rate": len(failure_points) / (rho_samples * beta_samples)
        }
    
    return True, None

def test_scenarios():
    """Test various scenarios to demonstrate validation"""
    print("=" * 60)
    print("SOUL-M v2.0 INV-001 Validation Test Suite")
    print("=" * 60)
    
    # Test Case 1: Identity matrix (g0 = I) - EXPECTED TO FAIL
    print("\nTest Case 1: g0 = Identity Matrix (3x3)")
    g0_1 = np.eye(3)
    is_valid, info = validate_invariant_001(g0_1)
    print(f"  Result: {'PASS' if is_valid else 'FAIL'}")
    if not is_valid:
        print(f"  Reason: {info['failure_type']}")
        print(f"  Worst failure at rho={info['worst_point']['rho']:.4f}, "
              f"beta={info['worst_point']['beta']:.4f}")
        print(f"  Min eigenvalue: {info['worst_point']['lambda_min_g']:.6f}")
        print(f"  Perturbation: {info['worst_point']['perturbation']:.6f}")
    
    # Test Case 2: Scaled identity (g0 = 2.0 * I) - EXPECTED TO PASS
    print("\nTest Case 2: g0 = 2.0 * Identity Matrix (3x3)")
    g0_2 = 2.0 * np.eye(3)
    is_valid, info = validate_invariant_001(g0_2)
    print(f"  Result: {'PASS' if is_valid else 'FAIL'}")
    if is_valid:
        print("  Metric remains positive definite in normal operating range")
    else:
        print(f"  Unexpected failure: {info}")
    
    # Test Case 3: Realistic infrastructure metric (anisotropic)
    print("\nTest Case 3: Realistic infrastructure metric")
    # Simulate a road network metric with varying capacities
    g0_3 = np.array([
        [2.5, 0.3, 0.1],
        [0.3, 1.8, 0.2],
        [0.1, 0.2, 1.2]
    ])
    is_valid, info = validate_invariant_001(g0_3)
    print(f"  Result: {'PASS' if is_valid else 'FAIL'}")
    if not is_valid:
        print(f"  Reason: {info['failure_type']}")
        print(f"  Worst failure at rho={info['worst_point']['rho']:.4f}, "
              f"beta={info['worst_point']['beta']:.4f}")
        print(f"  Base lambda_min: {info['worst_point']['lambda_min_g0']:.6f}")
        print(f"  Required lambda_min_g0 > {-info['worst_point']['perturbation']:.6f}")
    
    # Test Case 4: Marginally sufficient g0
    print("\nTest Case 4: Marginally sufficient g0 (lambda_min = 1.382)")
    # Calculate required minimum eigenvalue: -beta_max * ln(epsilon) ≈ 1.38155
    required_lambda = -0.1 * np.log(1e-6)  # ≈ 1.38155
    g0_4 = required_lambda * np.eye(3)
    is_valid, info = validate_invariant_001(g0_4)
    print(f"  Result: {'PASS' if is_valid else 'FAIL'}")
    print(f"  Required lambda_min_g0: {required_lambda:.6f}")
    print(f"  Actual lambda_min_g0: {np.min(np.linalg.eigvalsh(g0_4)):.6f}")
    if is_valid:
        print("  Barely satisfies INV-001 (within numerical tolerance)")
    else:
        print(f"  Failure: {info}")
    
    # Test Case 5: Violate beta bounds (should be caught by input validation in real system)
    print("\nTest Case 5: Invalid beta range (for demonstration)")
    # We'll manually test a beta outside [0.01, 0.1] to show sensitivity
    g0_5 = np.eye(3)
    # Test beta = 0.15 (above max) at rho=0
    beta_test = 0.15
    rho_test = 0.0
    psi_test = np.log(1.0 * rho_test + 1e-6)
    lambda_min_g = np.min(np.linalg.eigvalsh(g0_5)) + beta_test * psi_test
    print(f"  Test point: rho={rho_test}, beta={beta_test}")
    print(f"  Resulting lambda_min(g): {lambda_min_g:.6f}")
    print(f"  Status: {'DEGENERATE' if lambda_min_g <= 0 else 'STABLE'}")
    
    print("\n" + "=" * 60)
    print("Validation Complete")
    print("=" * 60)

if __name__ == "__main__":
    test_scenarios()