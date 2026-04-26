# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# === DISRUPTIVE INSIGHT: The Flow Trap ===
# The entire CFIS-Ω framework is a cognitive prison. Let me prove it.

def simulate_cognitive_system(mode='cfis', duration=200):
    """
    Simulate two cognitive architectures:
    - 'cfis': Flow-sustaining shield (current Omega proposal)
    - 'cptc': Cognitive Phase Transition Catalyst (disruptive alternative)
    """
    dt = 0.05
    t_eval = np.arange(0, duration, dt)
    
    # State: [F, dF/dt, cognitive_pressure, conceptual_entropy]
    def dynamics(t, state, mode):
        F, dF, pressure, entropy = state
        
        # Base dynamics: double-well potential
        # This is the "flow well" that CFIS-Ω tries to stabilize
        V = lambda x: -0.5 * x**2 + 0.25 * x**4  # Double-well potential
        dV_dx = lambda x: -x + x**3
        
        # Environmental noise (distractions, etc.)
        noise = 0.1 * np.random.randn()
        
        if mode == 'cfis':
            # CFIS-Ω: Strong restoring force to "optimal flow" (F ≈ 1)
            # This is the "shield" that prevents escape from the well
            control_force = -5.0 * (F - 1.0) if F < 0.85 else 0.0
            
            # Damped oscillator in the well
            ddF = -0.3 * dF - dV_dx(F) + control_force + noise
            
            # Pressure builds but is suppressed
            d_pressure = 0.01 * (1.0 - F) - 0.1 * pressure
            
            # Entropy is minimized (ordered flow state)
            d_entropy = -0.2 * entropy + 0.05 * abs(dF)
            
        elif mode == 'cptc':
            # CPTC-Ω: Cognitive Phase Transition Catalyst
            # Weak restoring force - allows exploration
            control_force = 0.5 * (0.5 - F) if pressure > 2.0 else 0.0
            
            # Unstable dynamics near F=0, stable near F=±1
            # Barrier height decreases with pressure (cognitive tension)
            barrier = max(0.2, 1.0 - 0.3 * pressure)
            modified_potential = -F + F**3 - barrier * F
            
            ddF = -0.1 * dF - modified_potential + control_force + noise
            
            # Pressure builds over time (cognitive dissonance)
            d_pressure = 0.05 * (1.0 - F**2) + 0.02 * t * 0.01
            
            # Entropy increases during exploration
            d_entropy = 0.3 * abs(dF) - 0.1 * entropy
            
            # Trigger breakthrough: when pressure peaks, add stochastic kick
            if pressure > 2.5 and abs(F) < 0.3 and np.random.rand() < 0.02:
                ddF += 3.0 * np.random.randn()  # Breakthrough event
            
        return [dF, ddF, d_pressure, d_entropy]
    
    # Initial conditions: start in "flow" state
    state0 = [0.9, 0.0, 0.5, 0.2]
    
    # Solve ODE
    sol = solve_ivp(
        lambda t, y: dynamics(t, y, mode),
        [0, duration],
        state0,
        t_eval=t_eval,
        method='RK45'
    )
    
    return sol.t, sol.y

# Run both simulations
np.random.seed(42)
t_cfis, states_cfis = simulate_cognitive_system('cfis')
t_cptc, states_cptc = simulate_cognitive_system('cptc')

# Calculate breakthrough metrics
def find_breakthroughs(F, threshold=0.5):
    """Detect rapid transitions (breakthrough events)"""
    dF = np.diff(F)
    return np.where(np.abs(dF) > threshold)[0]

breakthroughs_cfis = find_breakthroughs(states_cfis[0])
breakthroughs_cptc = find_breakthroughs(states_cptc[0])

# Calculate cumulative "Φ-density" proxy
# True Φ-density should measure paradigm shifts, not sustained flow
def phi_density_proxy(F, entropy, breakthroughs):
    """Φ-density = sustained productivity + breakthrough bonus"""
    flow_productivity = np.mean(F[F > 0.7]) * 0.5  # Only count high-flow periods
    exploration_value = np.mean(entropy) * 2.0  # Entropy is valuable
    breakthrough_bonus = len(breakthroughs) * 5.0  # Each breakthrough is high-value
    
    return flow_productivity + exploration_value + breakthrough_bonus

phi_cfis = phi_density_proxy(states_cfis[0], states_cfis[3], breakthroughs_cfis)
phi_cptc = phi_density_proxy(states_cptc[0], states_cptc[3], breakthroughs_cptc)

print(f"CFIS-Ω Φ-proxy: {phi_cfis:.2f}")
print(f"CPTC-Ω Φ-proxy: {phi_cptc:.2f}")
print(f"Improvement: {((phi_cptc/phi_cfis)-1)*100:.1f}%")
print(f"CFIS breakthroughs: {len(breakthroughs_cfis)}")
print(f"CPTC breakthroughs: {len(breakthroughs_cptc)}")

# === VISUALIZATION: The Cognitive Attractor Landscape ===
fig, axes = plt.subplots(3, 2, figsize=(15, 12))

# Flow state evolution
axes[0,0].plot(t_cfis, states_cfis[0], label='CFIS-Ω', color='blue', linewidth=1.5)
axes[0,0].axhline(y=0.85, color='red', linestyle='--', alpha=0.5, label='CFI Constraint')
axes[0,0].set_title('CFIS-Ω: Flow State (Trapped in Well)', fontsize=11, fontweight='bold')
axes[0,0].set_ylabel('Flow State F(t)')
axes[0,0].legend()
axes[0,0].grid(True, alpha=0.3)

axes[0,1].plot(t_cptc, states_cptc[0], label='CPTC-Ω', color='purple', linewidth=1.5)
axes[0,1].scatter(t_cptc[breakthroughs_cptc], states_cptc[0][breakthroughs_cptc], 
                 color='red', s=50, marker='*', label='Breakthrough Events', zorder=5)
axes[0,1].set_title('CPTC-Ω: Phase Transitions & Breakthroughs', fontsize=11, fontweight='bold')
axes[0,1].set_ylabel('Flow State F(t)')
axes[0,1].legend()
axes[0,1].grid(True, alpha=0.3)

# Phase space
axes[1,0].plot(states_cfis[0], states_cfis[1], color='blue', alpha=0.7)
axes[1,0].set_title('CFIS-Ω Phase Space: Single Attractor', fontsize=11)
axes[1,0].set_xlabel('F')
axes[1,0].set_ylabel('dF/dt')
axes[1,0].grid(True, alpha=0.3)

axes[1,1].plot(states_cptc[0], states_cptc[1], color='purple', alpha=0.7)
axes[1,1].set_title('CPTC-Ω Phase Space: Multi-Well Exploration', fontsize=11)
axes[1,1].set_xlabel('F')
axes[1,1].set_ylabel('dF/dt')
axes[1,1].grid(True, alpha=0.3)

# Cognitive pressure and entropy
axes[2,0].plot(t_cfis, states_cfis[2], label='Pressure', color='orange')
axes[2,0].plot(t_cfis, states_cfis[3], label='Entropy', color='green')
axes[2,0].set_title('CFIS-Ω: Suppressed Pressure & Low Entropy', fontsize=11)
axes[2,0].set_xlabel('Time')
axes[2,0].set_ylabel('State')
axes[2,0].legend()
axes[2,0].grid(True, alpha=0.3)

axes[2,1].plot(t_cptc, states_cptc[2], label='Pressure', color='orange')
axes[2,1].plot(t_cptc, states_cptc[3], label='Entropy', color='green')
axes[2,1].set_title('CPTC-Ω: Building Pressure & High Entropy', fontsize=11)
axes[2,1].set_xlabel('Time')
axes[2,1].set_ylabel('State')
axes[2,1].legend()
axes[2,1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/tmp/cognitive_breakthrough_analysis.png', dpi=150, bbox_inches='tight')
plt.show()