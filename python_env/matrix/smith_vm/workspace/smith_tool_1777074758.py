# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from scipy.linalg import cholesky, LinAlgError

def is_positive_definite(matrix):
    """
    Check if a matrix is positive definite by attempting Cholesky decomposition.
    Returns True if PD, False otherwise.
    """
    try:
        cholesky(matrix, lower=True)
        return True
    except LinAlgError:
        return False

def test_isotropic_metric():
    """
    Test the isotropic metric form: g = g0 + β * ρ * I
    where g0 is PD, β >= 0, ρ in [0, 1]
    Should always be PD.
    """
    np.random.seed(42)
    n = 3  # dimension
    
    # Generate random SPD matrix for g0
    A = np.random.randn(n, n)
    g0 = A @ A.T + n * np.eye(n)  # Ensure SPD with margin
    
    # Test multiple β and ρ values
    for β in [0.0, 0.1, 0.5, 1.0, 2.0]:
        for ρ in [0.0, 0.25, 0.5, 0.75, 1.0]:
            perturbation = β * ρ * np.eye(n)
            g = g0 + perturbation
            
            if not is_positive_definite(g):
                return False, f"Isotropic form failed: β={β}, ρ={ρ}, min eig={np.min(np.linalg.eigvals(g)):.6f}"
    
    return True, "Isotropic form: All tests passed (g remains PD)"

def test_anisotropic_metric():
    """
    Test the anisotropic metric form: g = g0 + α * H_ρ
    where H_ρ is the Hessian of demand density ρ.
    Construct counterexample where H_ρ is negative definite.
    """
    n = 2
    
    # Base metric: identity (SPD)
    g0 = np.eye(n)
    
    # Demand density: ρ(x,y) = -(x^2 + y^2)  [downward parabola]
    # Hessian: [[-2, 0], [0, -2]] (negative definite)
    H_ρ = np.array([[-2.0, 0.0],
                    [0.0, -2.0]])
    
    # Test α values
    for α in [0.1, 0.3, 0.4, 0.5, 0.6, 1.0]:
        perturbation = α * H_ρ
        g = g0 + perturbation
        
        # Check eigenvalues
        eigvals = np.linalg.eigvals(g)
        min_eig = np.min(eigvals)
        
        if min_eig <= 0:
            return False, f"Anisotropic form failed: α={α}, min eig={min_eig:.6f}, g=\n{g}"
    
    # This point should never be reached for the counterexample
    return True, "Anisotropic form: Unexpectedly passed all tests (should fail for α>0.5)"

def validate_metric_non_degeneracy():
    """
    Validate the core invariant INV-001: Metric Non-Degeneracy (det(g) > 0)
    by testing both metric formulations.
    """
    print("=" * 60)
    print("OMEGA PROTOCOL INVARIANT VALIDATION: INV-001")
    print("Metric Non-Degeneracy: det(g) > 0 ∀x, t")
    print("=" * 60)
    
    # Test isotropic form (Section 3.3)
    iso_pass, iso_msg = test_isotropic_metric()
    print(f"\n[ISOTROPIC FORM] g_ij = g0_ij + β·ρ(x)·δ_ij")
    print(f"  Result: {'PASS' if iso_pass else 'FAIL'}")
    print(f"  Details: {iso_msg}")
    
    # Test anisotropic form (Section 2.3)
    ani_pass, ani_msg = test_anisotropic_metric()
    print(f"\n[ANISOTROPIC FORM] g_ij = g0_ij + α·∂²ρ/∂x^i∂x^j")
    print(f"  Result: {'PASS' if ani_pass else 'FAIL'}")
    print(f"  Details: {ani_msg}")
    
    # Overall verdict for INV-001
    if iso_pass and not ani_pass:
        print("\n" + "!" * 60)
        print("CRITICAL INCONSISTENCY DETECTED:")
        print("  - Isotropic form (Section 3.3) preserves PD → supports INV-001")
        print("  - Anisotropic form (Section 2.3) can violate PD → breaks INV-001")
        print("  - PROPOSAL USES BOTH FORMS WITHOUT RESOLUTION → INV-001 UNENFORCEABLE")
        print("!" * 60)
        return False
    elif ani_pass:
        print("\n[WARNING] Anisotropic form unexpectedly passed - check counterexample")
        return False
    else:
        print("\n[ERROR] Both forms failed - fundamental issue with metric construction")
        return False

def enforce_invariant_001(g0, rho_func, alpha=0.1, method="isotropic"):
    """
    Enforce INV-001 by constructing metric safely.
    
    Parameters:
    - g0: base metric (must be SPD)
    - rho_func: function returning demand density ρ at point x (scalar)
    - alpha: perturbation coefficient
    - method: "isotropic" or "anisotropic_safe" (with PSD projection)
    
    Returns:
    - g: metric tensor guaranteed to be SPD (if possible)
    - status: "success" or "fallback_to_g0"
    """
    # Verify g0 is SPD
    if not is_positive_definite(g0):
        raise ValueError("Base metric g0 must be SPD")
    
    n = g0.shape[0]
    
    if method == "isotropic":
        # Isotropic form: guaranteed PD if g0 SPD and alpha*rho >= 0
        rho = rho_func()  # scalar demand density
        if alpha * rho < 0:
            return g0, "fallback_to_g0 (negative perturbation)"
        g = g0 + alpha * rho * np.eye(n)
        return g, "success"
    
    elif method == "anisotropic_safe":
        # Anisotropic form with safety projection to nearest PSD
        rho = rho_func()
        # Compute Hessian numerically (simplified for demo)
        # In practice, would use automatic differentiation or finite differences
        eps = 1e-4
        H = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                # Central difference for second partial
                x_plus = np.zeros(n); x_plus[i] = eps
                x_minus = np.zeros(n); x_minus[i] = -eps
                y_plus = np.zeros(n); y_plus[j] = eps
                y_minus = np.zeros(n); y_minus[j] = -eps
                
                f_xxyy = (rho_func(x_plus + y_plus) - rho_func(x_plus + y_minus) 
                         - rho_func(x_minus + y_plus) + rho_func(x_minus + y_minus)) / (4 * eps**2)
                H[i, j] = f_xxyy
        
        # Project Hessian to nearest PSD matrix (via eigenvalue clipping)
        evals, evecs = np.linalg.eigh(H)
        evals_clipped = np.maximum(evals, 0)  # Set negative eigenvalues to zero
        H_psd = evecs @ np.diag(evals_clipped) @ evecs.T
        
        g = g0 + alpha * H_psd
        # Final check (should always pass due to projection)
        if is_positive_definite(g):
            return g, "success (anisotropic with PSD projection)"
        else:
            return g0, "fallback_to_g0 (projection failed)"
    
    else:
        raise ValueError("Method must be 'isotropic' or 'anisotropic_safe'")

# Example usage of enforcement
if __name__ == "__main__":
    # Validate the mathematical inconsistency
    invariant_holds = validate_metric_non_degeneracy()
    
    print("\n" + "=" * 60)
    print("ENFORCEMENT DEMONSTRATION")
    print("=" * 60)
    
    # Setup: 2D base metric (identity)
    g0_base = np.eye(2)
    
    # Demand density function: ρ(x,y) = exp(-(x^2+y^2)) [Gaussian peak]
    def rho_gaussian():
        # In real system, this would depend on position x
        # For demo, return fixed value at origin
        return 1.0  # max density at center
    
    # Test unsafe anisotropic method (as in proposal)
    print("\n[UNSAFE ENFORCEMENT - AS IN PROPOSAL]")
    try:
        g_unsafe, status = enforce_invariant_001(
            g0_base, rho_gaussian, alpha=0.6, method="anisotropic_safe"  # Note: proposal doesn't do PSD projection
        )
        print(f"  Status: {status}")
        print(f"  Matrix:\n{g_unsafe}")
        print(f"  Is PD? {is_positive_definite(g_unsafe)}")
        if not is_positive_definite(g_unsafe):
            print("  → INV-001 VIOLATION RISK DETECTED")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Test safe isotropic method
    print("\n[SAFE ENFORCEMENT - ISOTROPIC FORM]")
    g_safe, status = enforce_invariant_001(
        g0_base, rho_gaussian, alpha=0.2, method="isotropic"
    )
    print(f"  Status: {status}")
    print(f"  Matrix:\n{g_safe}")
    print(f"  Is PD? {is_positive_definite(g_safe)}")
    
    # Test unsafe anisotropic WITHOUT correction (proposal's actual method)
    print("\n[UNSAFE ENFORCEMENT - PROPOSAL'S ACTUAL METHOD]")
    print("  (No PSD projection - uses raw Hessian)")
    rho_val = rho_gaussian()
    H_raw = np.array([[-2.0, 0.0], [0.0, -2.0]])  # Hessian of -ρ at origin (for demo)
    g_unsafe_raw = g0_base + 0.6 * H_raw
    print(f"  Alpha=0.6, Hessian=\n{H_raw}")
    print(f"  Resulting g=\n{g_unsafe_raw}")
    print(f"  Is PD? {is_positive_definite(g_unsafe_raw)}")
    if not is_positive_definite(g_unsafe_raw):
        print("  → INV-001 VIOLATION: det(g) = {np.linalg.det(g_unsafe_raw):.6f} ≤ 0")
    
    print("\n" + "=" * 60)
    print("CONCLUSION")
    print("=" * 60)
    if not invariant_holds:
        print("✗ PROPOSAL FAILS INV-001 VALIDATION")
        print("  Root cause: Unverified anisotropic metric perturbation")
        print("  Required fix: Use isotropic form OR add PSD projection to anisotropic form")
    else:
        print("✓ PROPOSAL PASSES INV-001 VALIDATION")