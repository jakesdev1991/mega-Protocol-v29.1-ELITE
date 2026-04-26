# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

def is_positive_definite(matrix, tol=1e-8):
    """Check if a symmetric matrix is positive definite."""
    # Ensure symmetry (should be, but just in case)
    matrix = (matrix + matrix.T) / 2
    eigenvalues = np.linalg.eigvalsh(matrix)
    return np.all(eigenvalues > tol)

def generate_random_spd(n, min_eig=0.1, max_eig=10.0):
    """Generate a random symmetric positive definite matrix."""
    # Generate random orthogonal matrix
    Q, _ = np.linalg.qr(np.random.randn(n, n))
    # Generate random eigenvalues in [min_eig, max_eig]
    eigvals = np.random.uniform(min_eig, max_eig, n)
    # Construct SPD matrix: Q @ diag(eigvals) @ Q.T
    return Q @ np.diag(eigvals) @ Q.T

def main():
    # Parameters from Omega Protocol / SOUL-M v2.0
    epsilon = 1e-6
    xi_N = 0.95  # Informational horizon (not directly used in math check)
    n_dim = 3    # 3D manifold (lat, lon, t)
    
    # Generate a random base infrastructure metric g0 (SPD)
    # We'll control the minimum eigenvalue to test edge cases
    min_eig_g0 = 0.5  # Typical value; we'll also test lower values later
    g0 = generate_random_spd(n_dim, min_eig=min_eig_g0, max_eig=5.0)
    
    print(f"Base metric g0 (min eigenvalue: {np.min(np.linalg.eigvalsh(g0)):.4f})")
    print(f"g0 =\n{g0}\n")
    
    # Test ranges
    rho_vals = np.linspace(0.0, 1.0, 101)      # Demand density [0,1]
    beta_vals = np.linspace(0.01, 0.1, 10)     # Demand sensitivity [0.01, 0.1]
    phi_N_vals = np.linspace(0.0, 1.0, 11)     # Newtonian density [0,1]
    
    # Store results for original and fixed psi
    results_original = {
        'min_eig': float('inf'),
        'violations': 0,
        'worst_case': None
    }
    results_fixed = {
        'min_eig': float('inf'),
        'violations': 0,
        'worst_case': None
    }
    
    # Sweep over parameters
    for rho in rho_vals:
        for beta in beta_vals:
            for phi_N in phi_N_vals:
                # Original psi: psi = ln(phi_N * rho + epsilon)
                arg_original = phi_N * rho + epsilon
                # Avoid log(0) - but epsilon ensures arg_original >= epsilon > 0
                psi_original = np.log(arg_original)
                
                # Fixed psi: psi = ln((phi_N * rho + epsilon) / epsilon) = ln(phi_N * rho / epsilon + 1)
                # This ensures psi >= 0 for all rho >= 0
                psi_fixed = np.log((phi_N * rho) / epsilon + 1.0)
                
                # Construct metrics
                g_original = g0 + beta * psi_original * np.eye(n_dim)
                g_fixed = g0 + beta * psi_fixed * np.eye(n_dim)
                
                # Check positive definiteness
                is_pd_original = is_positive_definite(g_original)
                is_pd_fixed = is_positive_definite(g_fixed)
                
                # Track minimum eigenvalue for original
                eigs_original = np.linalg.eigvalsh(g_original)
                min_eig_original = np.min(eigs_original)
                if min_eig_original < results_original['min_eig']:
                    results_original['min_eig'] = min_eig_original
                    results_original['worst_case'] = (rho, beta, phi_N, psi_original)
                
                # Track minimum eigenvalue for fixed
                eigs_fixed = np.linalg.eigvalsh(g_fixed)
                min_eig_fixed = np.min(eigs_fixed)
                if min_eig_fixed < results_fixed['min_eig']:
                    results_fixed['min_eig'] = min_eig_fixed
                    results_fixed['worst_case'] = (rho, beta, phi_N, psi_fixed)
                
                # Count violations (eigenvalue <= 0)
                if not is_pd_original:
                    results_original['violations'] += 1
                if not is_pd_fixed:
                    results_fixed['violations'] += 1
    
    # Print results for original psi
    print("=" * 60)
    print("RESULTS FOR ORIGINAL PSI: ψ(ρ) = ln(φ_N·ρ + ε)")
    print("=" * 60)
    print(f"Minimum eigenvalue observed: {results_original['min_eig']:.6f}")
    print(f"Number of PD violations: {results_original['violations']} / {len(rho_vals)*len(beta_vals)*len(phi_N_vals)}")
    if results_original['worst_case']:
        rho_w, beta_w, phi_N_w, psi_w = results_original['worst_case']
        print(f"Worst case: ρ={rho_w:.3f}, β={beta_w:.3f}, φ_N={phi_N_w:.3f}, ψ={psi_w:.3f}")
        print(f"  → This corresponds to argument = φ_N·ρ + ε = {phi_N_w*rho_w + epsilon:.6f}")
    print()
    
    # Print results for fixed psi
    print("=" * 60)
    print("RESULTS FOR FIXED PSI: ψ(ρ) = ln((φ_N·ρ)/ε + 1)  [Non-negative by construction]")
    print("=" * 60)
    print(f"Minimum eigenvalue observed: {results_fixed['min_eig']:.6f}")
    print(f"Number of PD violations: {results_fixed['violations']} / {len(rho_vals)*len(beta_vals)*len(phi_N_vals)}")
    if results_fixed['worst_case']:
        rho_w, beta_w, phi_N_w, psi_w = results_fixed['worst_case']
        print(f"Worst case: ρ={rho_w:.3f}, β={beta_w:.3f}, φ_N={phi_N_w:.3f}, ψ={psi_w:.3f}")
    print()
    
    # Critical analysis
    print("=" * 60)
    print("CRITICAL ANALYSIS")
    print("=" * 60)
    if results_original['violations'] > 0:
        print("❌ ORIGINAL FORMULA FAILS:")
        print("   - The metric loses positive definiteness for low demand scenarios")
        print("   - This occurs when φ_N·ρ is small (near zero), making ψ(ρ) large negative")
        print("   - Violations happen even with realistic infrastructure (min_eig(g0)=0.5)")
        print("   - This violates INV-001 (Metric Non-Degeneracy) by construction")
        print()
        print("   Root cause: ψ(ρ) can be negative → perturbation is negative definite")
        print("   → g = g0 + (negative definite) may not be PD")
    else:
        print("✅ ORIGINAL FORMULA PASSES (unexpected - check parameters)")
    
    if results_fixed['violations'] == 0:
        print("✅ FIXED FORMULA GUARANTEES PD BY CONSTRUCTION:")
        print("   - ψ(ρ) ≥ 0 for all ρ ≥ 0, φ_N ≥ 0")
        print("   - Perturbation β·ψ(ρ)·I is positive semi-definite (PSD)")
        print("   - g0 (PD) + PSD = PD → INV-001 satisfied for all valid inputs")
        print("   - No post-hoc correction needed for metric non-degeneracy")
    else:
        print("❌ FIXED FORMULA FAILS (unexpected - check implementation)")
    
    print()
    print("Shredding Event Note:")
    print("   - With fixed ψ, shredding event (triggered at φ_N·ρ > ξ_N) is")
    print("     NO LONGER NEEDED FOR INV-001 ENFORCEMENT")
    print("   - Shredding may still serve other purposes (e.g., bounding Φ_Δ,")
    print("     preventing metric explosion in extreme demand), but")
    print("     metric non-degeneracy is now invariant-safe by construction")
    print()
    
    # Additional test: What if infrastructure is very weak?
    print("=" * 60)
    print("EDGE CASE: WEAK INFRASTRUCTURE (min_eig(g0) = 0.05)")
    print("=" * 60)
    g0_weak = generate_random_spd(n_dim, min_eig=0.05, max_eig=2.0)
    min_eig_g0_weak = np.min(np.linalg.eigvalsh(g0_weak))
    print(f"Weak g0 min eigenvalue: {min_eig_g0_weak:.4f}")
    
    # Re-test original formula with weak infrastructure
    violations_weak = 0
    worst_case_weak = None
    min_eig_weak = float('inf')
    
    for rho in [0.0]:  # Worst case at rho=0
        for beta in beta_vals:
            for phi_N in phi_N_vals:
                psi_original = np.log(phi_N * rho + epsilon)
                g_weak = g0_weak + beta * psi_original * np.eye(n_dim)
                if not is_positive_definite(g_weak):
                    violations_weak += 1
                    eigs = np.linalg.eigvalsh(g_weak)
                    min_eig = np.min(eigs)
                    if min_eig < min_eig_weak:
                        min_eig_weak = min_eig
                        worst_case_weak = (rho, beta, phi_N, psi_original)
    
    print(f"Original formula violations with weak g0: {violations_weak} / {len(beta_vals)*len(phi_N_vals)}")
    if worst_case_weak:
        rho_w, beta_w, phi_N_w, psi_w = worst_case_weak
        print(f"Worst case: ρ={rho_w}, β={beta_w:.3f}, φ_N={phi_N_w:.3f}, ψ={psi_w:.3f}")
        print(f"  → Min eigenvalue: {min_eig_weak:.6f}")
    
    # Test fixed formula with weak infrastructure
    violations_weak_fixed = 0
    for rho in [0.0]:
        for beta in beta_vals:
            for phi_N in phi_N_vals:
                psi_fixed = np.log((phi_N * rho) / epsilon + 1.0)
                g_weak = g0_weak + beta * psi_fixed * np.eye(n_dim)
                if not is_positive_definite(g_weak):
                    violations_weak_fixed += 1
    
    print(f"Fixed formula violations with weak g0: {violations_weak_fixed} / {len(beta_vals)*len(phi_N_vals)}")
    if violations_weak_fixed == 0:
        print("✅ Fixed formula maintains PD even with weak infrastructure")
    else:
        print("❌ Fixed formula fails (unexpected)")

if __name__ == "__main__":
    main()