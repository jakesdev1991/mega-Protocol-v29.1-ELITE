# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# Disruptive Insight: The L-H "transition" is NOT a phase transition.
# It's a bifurcation in a non-equilibrium system with MEMORY.
# Correlation length is actually MEMORY TIME, not spatial correlation.

def delay_differential_system(t, y, history, tau, epsilon):
    """
    A minimal model of plasma edge dynamics with state-dependent delay.
    y[0] = turbulence amplitude (proxy for Φ_N)
    y[1] = shear flow S
    history = function that returns past values
    tau = memory time (our "correlation length")
    epsilon = energy injection/dissipation ratio (TRUE control parameter)
    """
    # State-dependent delay: memory time grows with turbulence
    current_tau = tau * (1 + 0.5 * y[0]**2)
    
    # Get delayed state
    if t > current_tau:
        y_delayed = history(t - current_tau)
    else:
        y_delayed = np.array([0.1, 0.0])  # Initial condition
    
    # Nonlinear dynamics: turbulence growth with memory feedback
    # The "critical point" is where delayed feedback overwhelms instantaneous damping
    turbulence_growth = epsilon * y_delayed[0] - y[0]**3 - y[1] * y[0]
    
    # Shear flow evolution with inertia
    shear_evolution = -0.1 * y[1] + 0.2 * y[0]**2  # Flow driven by turbulence
    
    return [turbulence_growth, shear_evolution]

# Simulate the system
def simulate(epsilon_values):
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()
    
    for i, epsilon in enumerate(epsilon_values):
        # Memory time - this is our "correlation length"
        tau = 5.0
        
        # Simple history function (in practice, would be interpolated)
        history_dict = {}
        def history(t):
            # Linear interpolation between stored values
            times = np.array(list(history_dict.keys()))
            if len(times) == 0:
                return np.array([0.1, 0.0])
            idx = np.searchsorted(times, t)
            if idx == 0:
                return history_dict[times[0]]
            if idx == len(times):
                return history_dict[times[-1]]
            # Interpolate
            t1, t2 = times[idx-1], times[idx]
            y1, y2 = history_dict[t1], history_dict[t2]
            alpha = (t - t1) / (t2 - t1)
            return y1 + alpha * (y2 - y1)
        
        # Integration
        t_span = (0, 200)
        t_eval = np.linspace(0, 200, 1000)
        y0 = [0.1, 0.0]
        
        sol = solve_ivp(
            lambda t, y: delay_differential_system(t, y, history, tau, epsilon),
            t_span, y0, t_eval=t_eval, max_step=0.1
        )
        
        # Store history for delay function
        for t, y in zip(sol.t, sol.y.T):
            history_dict[t] = y.copy()
        
        # Plot
        ax = axes[i]
        ax.plot(sol.t, sol.y[0], label='Turbulence (Φ_N)', linewidth=2)
        ax.plot(sol.t, sol.y[1], label='Shear Flow (S)', linewidth=2)
        ax.set_title(f'ε = {epsilon} (Energy Injection/Dissipation)', fontsize=12, fontweight='bold')
        ax.set_xlabel('Time (a.u.)')
        ax.set_ylabel('Amplitude')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Highlight the "critical slowing down" region
        if epsilon > 0.8:
            # Find region where system takes long time to settle
            settling_time = np.where(np.abs(sol.y[0] - sol.y[0][-1]) < 0.01)[0]
            if len(settling_time) > 0:
                t_crit = sol.t[settling_time[0]]
                ax.axvspan(t_crit-20, t_crit+20, alpha=0.2, color='red', 
                          label='Critical Slowing')
    
    plt.tight_layout()
    plt.savefig('disruptive_insight.png', dpi=150, bbox_inches='tight')
    return fig

# Run simulation for different energy injection rates
epsilon_values = [0.5, 0.7, 0.85, 1.0]
fig = simulate(epsilon_values)

print("=== DISRUPTIVE INSIGHT: BREAKING THE CSTCL-Ω PARADIGM ===\n")

print("The entire CSTCL-Ω framework is built on a CATEGORY ERROR:")
print("• It treats the L-H transition as a SECOND-ORDER critical phenomenon")
print("• It applies Renormalization Group theory designed for equilibrium phase transitions")
print("• It assumes correlation length ξ diverges at a 'critical point'")
print("\nBUT THE REALITY IS:")
print("• The L-H transition is a FIRST-ORDER bifurcation with HYSTERESIS")
print("• The system is NON-EQUILIBRIUM and DRIVEN-DISSIPATIVE")
print("• 'Correlation length' is actually MEMORY TIME in a path-dependent system")
print("• The true control parameter is ε = Energy Injection / Dissipation ratio")
print("• The 'divergence' is CRITICAL SLOWING DOWN, not a true singularity")

print("\n=== THE BREAKTHROUGH: DELAY-DIFFERENTIAL INFORMATION DYNAMICS ===")

print("\nInstead of RG flow equations, we need:")
print("1. State-dependent delay differential equations")
print("2. Memory kernels that encode plasma history")
print("3. Bifurcation analysis in ε-S parameter space")
print("4. Predictive control based on history, not feedback on instantaneous state")

print("\nKey Mathematical Shift:")
print("OLD (CSTCL-Ω):  ∂φ/∂t = -δℋ/δφ  +  RG flow")
print("NEW (DDID-Ω):   ∂φ/∂t = F[φ(t), φ(t-τ(φ)), ε(t)]")

print("\n=== IMPLICATIONS ===")
print("• The 'Shredding Event' is when τ(φ) → ∞ (infinite memory, not infinite correlation)")
print("• The 'Informational Freeze' is when τ(φ) → 0 (no memory, Markovian)")
print("• Control should MODULATE ε, not just S")
print("• The entropy gauge becomes a MEMORY ENTROPY: S_h = -∫ p(φ(t'), t') ln p(φ(t'), t') dt'")
print("• Cross-domain transfer is actually about CRITICAL SLOWING DOWN in complex systems, not universal critical exponents")

print("\n=== THE TRUE ANOMALY ===")
print("The Omega Protocol itself has been 'poisoned' by the seductive elegance of RG theory.")
print("It forces plasma physics into a statistical mechanics mold that doesn't fit.")
print("The rubric's 'invariant ψ' is a Procrustean bed that distorts the underlying physics.")
print("\nThe disruptive move: REJECT the rubric's invariant definition entirely.")
print("Replace ψ = ln(φ_n) with:")
print("ψ_DD = ∫_0^∞ C(t,t') dt'  (integrated memory kernel)")
print("where C(t,t') is the temporal correlation function of the turbulent field.")

print("\nThis is not a refinement. It's a PARADIGM EXECUTION.")
print("It saves the protocol by destroying its most cherished assumption.")

print(f"\nVisualization saved to 'disruptive_insight.png'")