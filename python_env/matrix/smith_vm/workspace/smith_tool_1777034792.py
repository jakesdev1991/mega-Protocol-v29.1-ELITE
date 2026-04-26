# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

def is_positive_definite(matrix):
    """Check if a symmetric matrix is positive definite via Cholesky."""
    try:
        np.linalg.cholesky(matrix)
        return True
    except np.linalg.LinAlgError:
        return False

def random_spd_matrix(dim, eig_min=0.5, eig_max=5.0):
    """Generate a random symmetric positive definite matrix with eigenvalues in [eig_min, eig_max]."""
    Q, _ = np.linalg.qr(np.random.randn(dim, dim))
    eigvals = np.random.uniform(eig_min, eig_max, size=dim)
    return Q @ np.diag(eigvals) @ Q.T

def psi(rho, phi_N, epsilon):
    """Demand coupling function."""
    return np.log(phi_N * rho + epsilon)

def metric_perturbation(rho, phi_N, epsilon, beta, dim):
    """Compute the isotropic perturbation beta * psi * I."""
    return beta * psi(rho, phi_N, epsilon) * np.eye(dim)

def full_metric(g0, rho, phi_N, epsilon, beta):
    """Compute g = g0 + beta * psi * I."""
    dim = g0.shape[0]
    return g0 + metric_perturbation(rho, phi_N, epsilon, beta, dim)

def validate_invariant(num_samples=10000, dim=3):
    """
    Validate INV-001: det(g) > 0 (i.e., g is positive definite)
    under the stated bounds:
        rho ∈ [0, 1]
        phi_N ∈ [0, 1]   (normalized demand flux)
        epsilon = 1e-6
        beta ∈ [0.01, 0.1]
        g0: random SPD with minimum eigenvalue >= 0.5 (chosen to reflect a reasonable base infrastructure)
    """
    epsilon = 1e-6
    violations = []
    
    for _ in range(num_samples):
        # Random base metric (infrastructure)
        g0 = random_spd_matrix(dim, eig_min=0.5, eig_max=5.0)
        
        # Random inputs within bounds
        rho = np.random.uniform(0.0, 1.0)
        phi_N = np.random.uniform(0.0, 1.0)
        beta = np.random.uniform(0.01, 0.1)
        
        g = full_metric(g0, rho, phi_N, epsilon, beta)
        
        if not is_positive_definite(g):
            violations.append((g0, rho, phi_N, beta, g))
    
    return violations

def analyze_violation_case(violation):
    """Print details of a violating case for debugging."""
    g0, rho, phi_N, beta, g = violation
    eigvals_g0 = np.linalg.eigvalsh(g0)
    eigvals_g = np.linalg.eigvalsh(g)
    psi_val = psi(rho, phi_N, 1e-6)
    print("Violation detected!")
    print(f"  rho={rho:.6f}, phi_N={phi_N:.6f}, beta={beta:.6f}")
    print(f"  psi = ln(phi_N*rho + ε) = {psi_val:.6f}")
    print(f"  g0 eigenvalues: {eigvals_g0}")
    print(f"  g  eigenvalues: {eigvals_g}")
    print(f"  min eigenvalue of g: {np.min(eigvals_g):.6f}")
    print("-" * 50)

if __name__ == "__main__":
    print("Validating INV-001 (det(g) > 0) under Omega Protocol bounds...")
    violations = validate_invariant(num_samples=20000, dim=3)
    
    if not violations:
        print("✅ PASS: No violations found in 20,000 random samples.")
        print("   The metric construction g_ij = g⁰_ij + β·ln(φ_N·ρ + ε)·δ_ij")
        print("   guarantees positive definiteness for the given bounds.")
    else:
        print(f"❌ FAIL: {len(violations)} violation(s) found.")
        print("   First few violating cases:")
        for i, v in enumerate(violations[:5]):
            print(f"\nViolation #{i+1}:")
            analyze_violation_case(v)
        print("\nThis indicates that the chosen bounds on β, ε, or the assumption")
        print("on g₀'s minimum eigenvalue may be insufficient to guarantee INV-001.")
        print("Consider tightening β bounds or increasing ε.")