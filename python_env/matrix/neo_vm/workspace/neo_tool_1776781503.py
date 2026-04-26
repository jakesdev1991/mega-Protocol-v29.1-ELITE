# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

def entanglement_metric(Pi_delta, h_tilde, M0_a, r):
    """
    Dynamical metric tensor G_ij for (Φ_N, Φ_Δ) space.
    Pi_delta: Archive polarization
    h_tilde: dimensionless Yukawa coupling ~ h0*Lambda
    M0_a: Archive mass in lattice units
    r: Wilson parameter
    """
    # Diagonal terms: Engine's result
    G_NN = 1.0 # Normalized free theory norm
    
    # G_DeltaDelta is the renormalized propagator denominator.
    # Shredding occurs as this -> 0.
    G_DeltaDelta = 1.0 - Pi_delta
    
    # OFF-DIAGONAL: Entanglement from Wilson-term mixing.
    # This is the disruption: grows as the gap closes and is enhanced by Wilson breaking.
    # The Wilson term introduces a momentum-dependent vertex ~ (r/a) sin(p_mu a) that doesn't vanish at p->0
    # when contracted with Archive loops, leading to a non-perturbative mixing term.
    # This term is *not* captured by naive diagram projection.
    # It scales as h_tilde^2 * (r / (M0_a + 1e-12)) * Pi_delta / (1 - Pi_delta)
    # The division by (1-Pi_delta) is the critical non-linear feedback: mixing diverges *with* the shredding.
    epsilon = h_tilde**2 * (r / (M0_a + 0.01)) * Pi_delta / (1 - Pi_delta + 1e-12)
    
    G = np.array([[G_NN, epsilon],
                  [epsilon, G_DeltaDelta]])
    return G, epsilon

def simulate_shredding():
    # Parameters: choose M0 light relative to cutoff to expose the flaw
    h_tilde = 0.8  # Strong coupling
    M0_a = 0.1       # Light Archive mass (flaw: decoupling fails)
    r = 1.0          # Wilson term active
    Pi_delta_initial = 0.01
    
    Pi_vals = np.linspace(Pi_delta_initial, 0.99, 500) # Drive towards shredding
    
    cond_nums = []
    epsilons = []
    eigenvals_0 = []
    eigenvals_1 = []
    
    breakdown_point = None
    
    for Pi in Pi_vals:
        G, eps = entanglement_metric(Pi, h_tilde, M0_a, r)
        
        # Check for metric breakdown: non-positive-definite or ill-conditioned
        evals = np.linalg.eigvals(G)
        evals_real = np.real(evals)
        min_eig = np.min(evals_real)
        
        # Condition number: ratio of eigenvalues. Diverges at shredding.
        if min_eig > 1e-10:
            cond_num = np.max(evals_real) / min_eig
        else:
            cond_num = np.inf
            if breakdown_point is None:
                breakdown_point = Pi
        
        cond_nums.append(cond_num)
        epsilons.append(eps)
        eigenvals_0.append(evals_real[0])
        eigenvals_1.append(evals_real[1])
    
    # Plot the catastrophe
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    
    axes[0,0].plot(Pi_vals, epsilons, 'r-', linewidth=2)
    axes[0,0].set_title('Entanglement Mixing ε')
    axes[0,0].set_xlabel('Π_Δ(0)')
    axes[0,0].set_ylabel('ε')
    axes[0,0].axvline(x=breakdown_point, color='k', linestyle='--', label='Breakdown')
    axes[0,0].legend()
    
    axes[0,1].semilogy(Pi_vals, cond_nums, 'b-', linewidth=2)
    axes[0,1].set_title('Condition Number of Metric G')
    axes[0,1].set_xlabel('Π_Δ(0)')
    axes[0,1].set_ylabel('κ(G)')
    axes[0,1].axvline(x=breakdown_point, color='k', linestyle='--')
    
    axes[1,0].plot(Pi_vals, eigenvals_0, 'g-', label='λ₀', linewidth=2)
    axes[1,0].plot(Pi_vals, eigenvals_1, 'm-', label='λ₁', linewidth=2)
    axes[1,0].set_title('Eigenvalues of G (Metric)')
    axes[1,0].set_xlabel('Π_Δ(0)')
    axes[1,0].set_ylabel('Eigenvalue')
    axes[1,0].axvline(x=breakdown_point, color='k', linestyle='--')
    axes[1,0].legend()
    axes[1,0].axhline(y=0, color='gray', linewidth=0.5)
    
    # Show the determinant (product of eigenvalues) -> 0
    det_vals = np.array(eigenvals_0) * np.array(eigenvals_1)
    axes[1,1].semilogy(Pi_vals, det_vals, 'c-', linewidth=2)
    axes[1,1].set_title('Metric Determinant')
    axes[1,1].set_xlabel('Π_Δ(0)')
    axes[1,1].set_ylabel('det(G)')
    axes[1,1].axvline(x=breakdown_point, color='k', linestyle='--')
    
    plt.tight_layout()
    plt.savefig('/tmp/shredding_catastrophe.png')
    print(f"Breakdown occurs at Π_Δ(0) = {breakdown_point:.4f}, not at 1.0")
    print("The metric becomes ill-conditioned and non-invertible *prematurely*.")
    print("This is the geometric Shredding: the coordinate basis collapses before the singularity.")
    return breakdown_point, Pi_vals, epsilons, cond_nums

# Execute the disruption
breakdown, Pi_vals, epsilons, cond_nums = simulate_shredding()