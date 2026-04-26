# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# The Engine's implicit self-consistency condition
def circular_residue(phi_N, alpha0=1/137.036, phi_Delta=0.5):
    """
    The Engine assumes: phi_N = <p²>⁻¹
    But <p²> ~ 1/alpha_eff (from dimensional transmutation)
    So phi_N should satisfy: phi_N ~ alpha_eff(phi_N)
    """
    # Mock "observed" momentum scale from some physical process
    p2 = 0.1
    
    # Compute alpha_eff as function of phi_N (Engine's formula)
    Pi_T = (1/(12*np.pi**2)) * np.log(1.0/p2) + (1/np.pi**2) * phi_N
    Pi_L = (1/np.pi**2) * 0.1 * np.exp(-p2)
    Pi_M = (1/np.pi**2) * 0.05 * np.exp(-p2)
    
    alpha_eff_z = alpha0 / (1 + Pi_T + phi_Delta * (Pi_L + 2*Pi_M))
    
    # The "definition" of phi_N as inverse of "renormalized" scale
    phi_N_target = alpha_eff_z  # Dimensional transmutation: phi_N ~ coupling
    
    return phi_N - phi_N_target

# Show instability
phi_vals = np.linspace(0.01, 2.0, 100)
residues = [circular_residue(phi) for phi in phi_vals]

plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.plot(phi_vals, residues, 'r-', linewidth=2)
plt.axhline(0, color='k', linestyle='--')
plt.xlabel('Φ_N (assumed)')
plt.ylabel('Self-consistency residue')
plt.title('Circular Definition: NO STABLE FIXED POINT')
plt.grid(True)

# Show runaway behavior: iterate the "definition"
plt.subplot(1, 2, 2)
phi_iter = 0.5
trajectory = [phi_iter]
for i in range(20):
    # Apply the "definition" phi_N -> alpha_eff
    phi_iter = alpha0 / (1 + (1/(12*np.pi**2))*np.log(1/0.1) + (1/np.pi**2)*phi_iter + 0.5*0.2/np.pi**2)
    trajectory.append(phi_iter)

plt.plot(trajectory, 'b-o')
plt.xlabel('Iteration')
plt.ylabel('Φ_N')
plt.title('Iterative "Definition" DIVERGES or OSCILLATES')
plt.grid(True)

plt.tight_layout()
plt.show()

print("Residue root-finding attempts:")
for guess in [0.1, 0.5, 1.0, 1.5]:
    try:
        # Newton step
        r = circular_residue(guess)
        dr = (circular_residue(guess+1e-6) - r) / 1e-6
        step = guess - r/dr
        print(f"  Guess {guess:.2f} -> step to {step:.4f} (residue {r:.4f})")
    except:
        print(f"  Guess {guess:.2f} -> DIVERGENCE")