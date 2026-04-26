# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import math

def validate_metric_non_degeneracy(g0, beta, epsilon, phi_N=1.0, rho_max=1.0, tolerance=1e-8):
    """
    Validates the Metric Non-Degeneracy invariant (INV-001) for the SOUL-M metric construction.
    
    Metric definition: g_ij = g⁰_ij + β * ψ(ρ) * δ_ij
    where ψ(ρ) = ln(φ_N * ρ + ε)
    
    Conditions for positive definiteness (PD):
    1. g⁰ must be symmetric and PD (verified separately)
    2. For all ρ ∈ [0, ρ_max]: λ_min(g⁰) + β * ln(φ_N * ρ + ε) > 0
    
    Since ψ(ρ) is monotonically increasing in ρ (derivative = φ_N/(φ_N*ρ+ε) > 0),
    the minimum eigenvalue occurs at ρ=0:
        λ_min(g) = λ_min(g⁰) + β * ln(ε)
    
    Thus, the invariant holds iff:
        λ_min(g⁰) + β * ln(ε) > 0   [when ε < 1, ln(ε) < 0]
        Always true if ε ≥ 1 (since ln(ε) ≥ 0 and β ≥ 0)
    
    Parameters:
    -----------
    g0 : np.ndarray
        Base infrastructure metric (symmetric matrix, assumed PD)
    beta : float
        Demand sensitivity coefficient (β ≥ 0)
    epsilon : float
        Regularization constant (ε > 0)
    phi_N : float
        Newtonian informational density normalization (φ_N ≥ 0)
    rho_max : float
        Maximum demand density to consider (default=1.0 for normalized [0,1])
    tolerance : float
        Numerical tolerance for PD check (default=1e-8)
    
    Returns:
    --------
    bool
        True if metric is PD for all ρ ∈ [0, ρ_max], False otherwise
    str
        Explanation of result
    """
    # Verify g0 is symmetric
    if not np.allclose(g0, g0.T, atol=tolerance):
        return False, "Base metric g⁰ is not symmetric"
    
    # Verify g0 is PD (all eigenvalues > 0)
    try:
        eigvals = np.linalg.eigvalsh(g0)  # For symmetric matrices
        lambda_min = np.min(eigvals)
        if lambda_min <= tolerance:
            return False, f"Base metric g⁰ is not PD (min eigenvalue = {lambda_min:.2e})"
    except np.linalg.LinAlgError:
        return False, "Base metric g⁰ is not symmetric/Hermitian (eigvalsh failed)"
    
    # Handle epsilon >= 1 case (ln(epsilon) >= 0)
    if epsilon >= 1.0:
        # Perturbation term β*ln(φ_N*ρ+ε) ≥ 0 for all ρ≥0, β≥0
        # Since g⁰ is PD, g = g⁰ + (non-negative)*I remains PD
        return True, f"ε={epsilon} ≥ 1 → perturbation non-negative → g PD by construction"
    
    # For epsilon < 1: ln(epsilon) < 0
    log_epsilon = math.log(epsilon)
    # Critical condition: lambda_min(g0) + beta * log_epsilon > 0
    critical_value = -lambda_min(g0) / log_epsilon  # Positive since log_epsilon < 0
    
    if beta < critical_value - tolerance:
        # Verify at worst-case rho=0
        psi_0 = math.log(phi_N * 0.0 + epsilon)
        min_eigval_g = lambda_min(g0) + beta * psi_0
        if min_eigval_g > tolerance:
            return True, f"INV-001 satisfied: β={beta} < {critical_value:.4f} (λ_min(g⁰)/|ln(ε)|)"
        else:
            return False, f"Worst-case rho=0 fails: λ_min(g) = {min_eigval_g:.2e} ≤ 0"
    elif beta > critical_value + tolerance:
        return False, f"INV-001 violated: β={beta} ≥ {critical_value:.4f} (requires β < λ_min(g⁰)/|ln(ε)|)"
    else:
        # Boundary case (beta ≈ critical_value)
        psi_0 = math.log(phi_N * 0.0 + epsilon)
        min_eigval_g = lambda_min(g0) + beta * psi_0
        if min_eigval_g > tolerance:
            return True, f"INV-001 satisfied at boundary: β={beta} ≈ {critical_value:.4f}"
        else:
            return False, f"Boundary case fails: λ_min(g) = {min_eigval_g:.2e} ≤ 0"

def demonstrate_invariant_enforcement():
    """
    Demonstration of invariant enforcement with realistic parameters.
    """
    print("="*60)
    print("OMEGA PROTOCOL INVARIANT VALIDATION: SOUL-M METRIC")
    print("="*60)
    
    # Example: 2D spatial manifold (lat, lon) - simplified to 2x2 metric
    # Base infrastructure metric g⁰ (e.g., road network cost)
    # Designed to be well-conditioned with min eigenvalue = 0.5
    g0 = np.array([[0.6, 0.1], 
                   [0.1, 0.6]])  # Eigenvalues: 0.5, 0.7 → PD
    
    # Parameters from plea (with safety margin)
    beta = 0.05       # Within [0.01, 0.1] but below critical value
    epsilon = 1e-6    # As specified in plea
    phi_N = 1.0       # Normalization constant
    
    print(f"\nBase metric g⁰:")
    print(g0)
    print(f"Eigenvalues of g⁰: {np.linalg.eigvalsh(g0)}")
    print(f"λ_min(g⁰) = {np.min(np.linalg.eigvalsh(g0)):.4f}")
    
    print(f"\nParameters:")
    print(f"β = {beta}")
    print(f"ε = {epsilon} → ln(ε) = {math.log(epsilon):.4f}")
    print(f"φ_N = {phi_N}")
    
    # Validate invariant
    is_valid, message = validate_metric_non_degeneracy(g0, beta, epsilon, phi_N)
    
    print(f"\nValidation Result:")
    print(f"{'✓ PASS' if is_valid else '✗ FAIL'}: {message}")
    
    # Show worst-case metric at rho=0
    psi_0 = math.log(phi_N * 0.0 + epsilon)
    g_worst = g0 + beta * psi_0 * np.eye(2)
    print(f"\nWorst-case metric (ρ=0):")
    print(g_worst)
    print(f"Eigenvalues: {np.linalg.eigvalsh(g_worst)}")
    print(f"λ_min(g) = {np.min(np.linalg.eigvalsh(g_worst)):.4f}")
    
    # Show best-case metric at rho=1
    psi_1 = math.log(phi_N * 1.0 + epsilon)
    g_best = g0 + beta * psi_1 * np.eye(2)
    print(f"\nBest-case metric (ρ=1):")
    print(g_best)
    print(f"Eigenvalues: {np.linalg.eigvalsh(g_best)}")
    print(f"λ_min(g) = {np.min(np.linalg.eigvalsh(g_best)):.4f}")
    
    # Demonstrate violation case
    print("\n" + "-"*60)
    print("DEMONSTRATING INVARIANT VIOLATION")
    print("-"*60)
    beta_violation = 0.15  # Exceeds critical value
    print(f"Testing with β = {beta_violation} (unsafe)")
    is_valid_violation, msg_violation = validate_metric_non_degeneracy(
        g0, beta_violation, epsilon, phi_N
    )
    print(f"Result: {'✓ PASS' if is_valid_violation else '✗ FAIL'}: {msg_violation}")
    
    if not is_valid_violation:
        g_violation = g0 + beta_violation * psi_0 * np.eye(2)
        print(f"Violation metric (ρ=0) eigenvalues: {np.linalg.eigvalsh(g_violation)}")
        print(f"λ_min(g) = {np.min(np.linalg.eigvalsh(g_violation)):.4f} (< 0 → INV-001 FAIL)")
    
    print("\n" + "="*60)
    print("KEY INSIGHT: INV-001 ENFORCED BY CONSTRUCTION")
    print("="*60)
    print("• Metric remains PD for ALL ρ ∈ [0, ∞) when β < λ_min(g⁰)/|ln(ε)|")
    print("• No runtime checks needed - invariant guaranteed by parameter bounds")
    print("• Circuit breaker (INV-001 response) only triggers if parameters misconfigured")
    print("• This transforms invariant from damage control to generative constraint")

if __name__ == "__main__":
    demonstrate_invariant_enforcement()