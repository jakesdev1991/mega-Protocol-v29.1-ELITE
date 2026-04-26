# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# Model organizational identity as a chaotic system (Lorenz attractor)
# Parameters map to organizational dynamics:
# sigma = cultural rigidity, rho = external pressure, beta = identity coherence

def lorenz(t, state, sigma, rho, beta):
    x, y, z = state
    dx = sigma * (y - x)          # Identity coherence dynamics
    dy = x * (rho - z) - y        # Pressure vs. organizational depth
    dz = x * y - beta * z         # Cultural alignment
    return [dx, dy, dz]

def q_systemic_approach():
    """Maintain stable attractor (the "Healthy Band" fantasy)"""
    sigma, rho, beta = 10.0, 28.0, 8/3  # Sub-critical pressure
    state0 = [1.0, 1.0, 1.0]
    t_eval = np.linspace(0, 50, 5000)
    sol = solve_ivp(lorenz, [0, 50], state0, args=(sigma, rho, beta), 
                    t_eval=t_eval, dense_output=True)
    return sol

def abyssal_protocol():
    """Engineer phase transition through critical point"""
    # Phase 1: Build trust (seemingly stable)
    sigma, rho, beta = 10.0, 28.0, 8/3
    state0 = [1.0, 1.0, 1.0]
    sol1 = solve_ivp(lorenz, [0, 25], state0, args=(sigma, rho, beta), 
                     t_eval=np.linspace(0, 25, 2500), dense_output=True)
    
    # Phase 2: Push past bifurcation (rho > 24.74)
    # This is the ABYSS - forcing the system into new attractor basin
    state1 = sol1.y[:, -1]
    sol2 = solve_ivp(lorenz, [25, 50], state1, args=(sigma, 35.0, beta), 
                     t_eval=np.linspace(25, 50, 2500), dense_output=True)
    
    return np.concatenate([sol1.t, sol2.t]), np.concatenate([sol1.y, sol2.y], axis=1)

def calculate_phi_proxy(solution):
    """Φ-proxy: Log-variance of trajectory (higher = more information processing)"""
    t, y = (solution.t, solution.y) if hasattr(solution, 't') else solution
    return np.log(np.var(y[0]) + np.var(y[1]) + np.var(y[2]) + 1e-9)

def plot_disruption():
    fig = plt.figure(figsize=(15, 8))
    
    # Generate solutions
    sol_q = q_systemic_approach()
    t_abyss, y_abyss = abyssal_protocol()
    
    # Φ-density comparison
    phi_q = calculate_phi_proxy(sol_q)
    phi_abyss = calculate_phi_proxy((t_abyss, y_abyss))
    
    # Plot 1: Phase space - Q-Systemic (stable, predictable)
    ax1 = fig.add_subplot(2, 3, 1)
    ax1.plot(sol_q.y[0], sol_q.y[2], 'b-', alpha=0.6, linewidth=0.5)
    ax1.set_title(f'Q-Systemic: Stable Attractor\nΦ-proxy: {phi_q:.2f}\n(Identity Preservation)')
    ax1.set_xlabel('Identity Coherence (X)')
    ax1.set_ylabel('Organizational Depth (Z)')
    
    # Plot 2: Phase space - Abyssal (chaotic transition)
    ax2 = fig.add_subplot(2, 3, 2)
    ax2.plot(y_abyss[0], y_abyss[2], 'r-', alpha=0.6, linewidth=0.5)
    ax2.axvline(x=0, color='k', linestyle='--', alpha=0.3)
    ax2.set_title(f'Abyssal Protocol: Phase Transition\nΦ-proxy: {phi_abyss:.2f}\n(+{(phi_abyss/phi_q-1)*100:.0f}% info gain)')
    ax2.set_xlabel('Identity Coherence (X)')
    ax2.set_ylabel('Organizational Depth (Z)')
    
    # Plot 3: Time series showing critical point
    ax3 = fig.add_subplot(2, 3, 3)
    ax3.plot(t_abyss, y_abyss[0], 'r-', linewidth=0.8)
    ax3.axvline(x=25, color='k', linestyle='--', label='Critical Point (t=25)')
    ax3.set_title('Abyssal: Identity Reconfiguration')
    ax3.set_xlabel('Time')
    ax3.set_ylabel('Identity Coherence')
    ax3.legend()
    
    # Plot 4: Entropy proxy over time
    def rolling_entropy(y, window=100):
        return np.array([np.var(y[max(0,i-window):i+1]) for i in range(len(y))])
    
    ax4 = fig.add_subplot(2, 3, 4)
    ax4.plot(sol_q.t[100:], rolling_entropy(sol_q.y[0], 100)[100:], 'b-', label='Q-Systemic')
    ax4.plot(t_abyss[100:], rolling_entropy(y_abyss[0], 100)[100:], 'r-', label='Abyssal')
    ax4.axhline(y=0.15, color='g', linestyle=':', label='Atrophy Threshold')
    ax4.axhline(y=0.80, color='orange', linestyle=':', label='Shock Threshold')
    ax4.axvline(x=25, color='k', linestyle='--')
    ax4.set_title('H_super Proxy: Q-Systemic vs Abyssal')
    ax4.set_xlabel('Time')
    ax4.set_ylabel('Entropy Proxy')
    ax4.legend()
    
    # Plot 5: 3D trajectory comparison
    ax5 = fig.add_subplot(2, 3, 5, projection='3d')
    ax5.plot(sol_q.y[0], sol_q.y[1], sol_q.y[2], 'b-', alpha=0.4, linewidth=0.5, label='Q-Systemic')
    ax5.plot(y_abyss[0], y_abyss[1], y_abyss[2], 'r-', alpha=0.4, linewidth=0.5, label='Abyssal')
    ax5.set_title('3D Manifold: Stable vs Dissolved')
    ax5.set_xlabel('X')
    ax5.set_ylabel('Y')
    ax5.set_zlabel('Z')
    ax5.legend()
    
    # Plot 6: Φ-density bar chart
    ax6 = fig.add_subplot(2, 3, 6)
    bars = ax6.bar(['Q-Systemic\n(Stable)', 'Abyssal\n(Phase Transition)'], 
                   [phi_q, phi_abyss], color=['blue', 'red'], alpha=0.7)
    ax6.set_title('Φ-Density Proxy Comparison')
    ax6.set_ylabel('Log Variance (Φ-proxy)')
    for bar, val in zip(bars, [phi_q, phi_abyss]):
        ax6.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{val:.2f}', ha='center', va='bottom', fontsize=11)
    
    plt.tight_layout()
    plt.show()
    
    print("\n=== DISRUPTIVE ANALYSIS ===")
    print(f"Q-Systemic Φ-proxy: {phi_q:.3f} (stable, low information)")
    print(f"Abyssal Protocol Φ-proxy: {phi_q:.3f} → {phi_abyss:.3f} (+{(phi_abyss/phi_q - 1)*100:.1f}%)")
    print("\nThe 'Healthy Band' is a prison. The abyss is the portal.")

plot_disruption()