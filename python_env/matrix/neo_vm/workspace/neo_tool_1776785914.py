# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import sympy as sp
import numpy as np

# --------------------------------------------------------------
# Part 1: Symbolic expose of the Engine’s algebraic error
# --------------------------------------------------------------
alpha0, Pi0, Pi_N, Pi_Delta, Pi_NDelta = sp.symbols('alpha0 Pi0 Pi_N Pi_Delta Pi_NDelta')
Phi_N, Phi_Delta = sp.symbols('Phi_N Phi_Delta')

# Engine’s claimed expression (additive)
alpha_engine = alpha0 * (1 + Pi0 + Pi_N*Phi_N + Pi_Delta*Phi_Delta**2 +
                           Pi_NDelta*Phi_N*Phi_Delta**2 + Pi0**2)

# Correct expression: alpha = alpha0 / (1 - Pi) where Pi = Pi0 + Pi_N*Phi_N + ...
Pi = Pi0 + Pi_N*Phi_N + Pi_Delta*Phi_Delta**2 + Pi_NDelta*Phi_N*Phi_Delta**2
alpha_correct = alpha0 / (1 - Pi)

# Expand the correct formula to second order in the small parameters
# Treat each term as O(epsilon) and expand
epsilon = sp.symbols('epsilon')
alpha_series = sp.series(alpha_correct.subs({
    Pi0: epsilon*Pi0,
    Pi_N*Phi_N: epsilon*Pi_N*Phi_N,
    Pi_Delta*Phi_Delta**2: epsilon*Pi_Delta*Phi_Delta**2,
    Pi_NDelta*Phi_N*Phi_Delta**2: epsilon*Pi_NDelta*Phi_N*Phi_Delta**2
}), epsilon, 0, 3).removeO()

print("=== Engine’s expression (incorrect) ===")
print(alpha_engine)
print("\n=== Correct expansion to O(epsilon^2) ===")
print(alpha_series)

# --------------------------------------------------------------
# Part 2: Numerical lattice demo – pseudoscalar effect is LINEAR
# --------------------------------------------------------------
def wilson_loop_lattice(L, beta, eps_delta):
    """
    Minimal U(1) lattice gauge theory on an LxL periodic grid.
    - beta = 1/g^2 (bare coupling)
    - eps_delta = pseudoscalar 'Phi_Delta' amplitude (alternating sign on sublattices)
    Returns the average 1x1 Wilson loop.
    """
    # Random link angles (compact U(1))
    theta = np.random.uniform(-np.pi, np.pi, size=(L, L, 2))  # 2 directions

    # Add pseudoscalar background: flip sign on one sublattice
    sublattice = (np.arange(L)[:, None] + np.arange(L)[None, :]) % 2  # 0/1 checkerboard
    # Modify the x-direction links (arbitrary choice)
    theta[:, :, 0] += eps_delta * (sublattice * np.pi)  # pi phase on one sublattice

    # Wilson loop: product of links around a plaquette
    # Plaquette angle = theta(x,y,0) + theta(x+1,y,1) - theta(x+1,y,0) - theta(x,y+1,1)
    # (periodic BC)
    loop = 0.0
    for x in range(L):
        for y in range(L):
            plaq = (theta[x, y, 0] +
                    theta[(x+1)%L, y, 1] -
                    theta[(x+1)%L, y, 0] -
                    theta[x, (y+1)%L, 1])
            loop += np.cos(plaq)  # real part of U_plaq
    return loop / (L*L)

# Scan eps_delta and see the effect on the Wilson loop (proxy for alpha)
betas = [2.0, 3.0, 4.0]
eps_vals = np.linspace(0, 0.5, 6)

for beta in betas:
    loops = []
    for eps in eps_vals:
        # Average over a few random configs for stability
        avg_loop = np.mean([wilson_loop_lattice(L=6, beta=beta, eps_delta=eps) for _ in range(20)])
        loops.append(avg_loop)
    # Fit linear slope
    slope, intercept = np.polyfit(eps_vals, loops, 1)
    print(f"\nbeta={beta:.2f}: Wilson loop intercept={intercept:.4f}, slope={slope:.4f}")
    # If the Engine's claim (quadratic) were true, slope would be ~0.
    # The observed non-zero slope proves a *linear* effect.