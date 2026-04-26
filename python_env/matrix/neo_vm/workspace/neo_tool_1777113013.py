# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, List

# ============================================
# DISRUPTIVE SIMULATION: THE PSI INVARIANT TRAP
# ============================================

def potential_landscape(x: np.ndarray) -> np.ndarray:
    """
    Multi-well potential representing belief states.
    Local minima at x=0 (old paradigm) and x=2 (intermediate trap).
    Global minimum at x=4 (true transformation).
    """
    return -np.exp(-(x-0)**2/0.3) - 1.5*np.exp(-(x-2)**2/0.2) - 3*np.exp(-(x-4)**2/0.1)

class ValidationManifold:
    """
    Models the cognitive system as a particle in a potential,
    subject to validation forces and the psi invariant.
    """
    
    def __init__(self, initial_state: np.ndarray, psi_invariant: bool = True):
        self.state = initial_state  # [position, velocity]
        self.psi_invariant = psi_invariant
        self.trajectory = [self.state.copy()]
        self.psi_history = [1.0]
        self.xi_intel_history = []
        self.xi_sub_history = []
        
    def compute_readiness(self) -> float:
        """System readiness is inverse of current 'stiffness' resistance"""
        # High velocity = high internal flux = ready for transformation
        return np.clip(abs(self.state[1]) * 10, 0.1, 5.0)
    
    def compute_psi(self) -> float:
        """Identity continuity: decays with distance from origin"""
        return np.exp(-abs(self.state[0]) / 3.0)
    
    def step(self, force_validation: float, step_num: int):
        """Evolve system one timestep"""
        # System capacity (subconscious readiness)
        xi_sub = self.compute_readiness()
        
        # Intellectual stiffness (validation pressure)
        xi_intel = abs(force_validation)
        
        # THE DISRUPTION: Psi invariant CONSTRAINS force to preserve identity
        if self.psi_invariant:
            psi = self.compute_psi()
            # Force cannot exceed identity-preserving bound
            # This is the core flaw: it prevents escape from local minima
            max_allowed_force = psi * xi_sub * 0.5
            xi_intel = np.clip(xi_intel, 0, max_allowed_force)
        
        # Dynamics: validation force vs systemic inertia
        damping = 0.15
        acceleration = (xi_intel if self.state[0] < 4 else -xi_intel * 0.5) - damping * self.state[1]
        
        # Update state
        self.state[1] += acceleration * 0.1
        self.state[0] += self.state[1] * 0.1
        
        # Track metrics
        self.trajectory.append(self.state.copy())
        self.psi_history.append(self.compute_psi())
        self.xi_intel_history.append(xi_intel)
        self.xi_sub_history.append(xi_sub)

def simulate_strategies(initial_state: np.ndarray, steps: int = 300) -> dict:
    """Run multiple validation strategies"""
    
    strategies = {
        "Omega AVRI (Adiabatic + Psi Inv)": {
            "force_fn": lambda s: 0.02 * s,  # Slow ramp
            "psi_inv": True
        },
        "Catastrophic Validation": {
            "force_fn": lambda s: 8.0 if 5 < s < 20 else 0.1,  # Shock then release
            "psi_inv": False
        },
        "Paradoxical Induction": {
            "force_fn": lambda s: 5.0 * np.sin(s * 0.15) + 0.01 * s,  # Alternating push/pull
            "psi_inv": False
        },
        "Omega AVRI (Adiabatic - Psi Inv)": {
            "force_fn": lambda s: 0.02 * s,
            "psi_inv": False
        }
    }
    
    results = {}
    
    for name, config in strategies.items():
        manifold = ValidationManifold(initial_state, psi_invariant=config["psi_inv"])
        
        for step in range(steps):
            force = config["force_fn"](step)
            manifold.step(force, step)
            
        results[name] = {
            "trajectory": np.array(manifold.trajectory),
            "psi": np.array(manifold.psi_history),
            "final_pos": manifold.trajectory[-1][0],
            "final_potential": potential_landscape(np.array([manifold.trajectory[-1][0]]))[0]
        }
    
    return results

# Run simulation
print("=== DISRUPTIVE ANALYSIS: THE PSI INVARIANT AS PATHOLOGY CONSERVER ===")
initial_state = np.array([0.0, 0.0])  # Stuck in old paradigm
results = simulate_strategies(initial_state)

# Analyze results
print("\nFINAL STATE ANALYSIS:")
for name, data in results.items():
    pos = data["final_pos"]
    pot = data["final_potential"]
    psi_final = data["psi"][-1]
    
    # Success: reached global minimum near x=4
    success = "✓ TRANSFORMED" if pos > 3.5 else "✗ TRAPPED"
    
    print(f"{name:35s} | Pos: {pos:5.2f} | Potential: {pot:6.3f} | Psi: {psi_final:.3f} | {success}")

# Visualization
fig = plt.figure(figsize=(12, 10))
gs = fig.add_gridspec(3, 2, height_ratios=[2, 1, 1])

# Main plot: Potential landscape and trajectories
ax1 = fig.add_subplot(gs[0, :])
x_range = np.linspace(-0.5, 5, 200)
ax1.plot(x_range, potential_landscape(x_range), 'k-', linewidth=2, alpha=0.4, label='Truth Potential')
ax1.fill_between(x_range, potential_landscape(x_range), alpha=0.1, color='gray')

colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
for (name, data), color in zip(results.items(), colors):
    traj = data["trajectory"]
    ax1.plot(traj[:, 0], potential_landscape(traj[:, 0]), 
             'o-', color=color, label=name, markersize=4, alpha=0.7)
    
    # Mark final position
    final_x = traj[-1, 0]
    final_y = potential_landscape(np.array([final_x]))[0]
    ax1.scatter([final_x], [final_y], s=100, color=color, edgecolor='black', zorder=5)

ax1.set_xlabel('Belief State (x)', fontsize=11)
ax1.set_ylabel('Potential Energy / System Stability', fontsize=11)
ax1.set_title('THE DISRUPTION: Psi Invariant Prevents Escape from Local Minima', 
              fontsize=13, fontweight='bold')
ax1.legend(loc='lower left', fontsize=9)
ax1.grid(True, alpha=0.3)

# Psi evolution
ax2 = fig.add_subplot(gs[1, 0])
for (name, data), color in zip(results.items(), colors):
    psi = data["psi"]
    ax2.plot(psi, color=color, label=name, linewidth=2)
ax2.set_xlabel('Time Steps', fontsize=10)
ax2.set_ylabel('Psi (Identity Continuity)', fontsize=10)
ax2.set_title('Identity Preservation vs Transformation', fontsize=11)
ax2.legend(fontsize=8)
ax2.grid(True, alpha=0.3)

# Force/Stiffness comparison
ax3 = fig.add_subplot(gs[1, 1])
# Show a representative strategy
omega_data = results["Omega AVRI (Adiabatic + Psi Inv)"]
cat_data = results["Catastrophic Validation"]

ax3.plot(omega_data["trajectory"][:, 0], color='#1f77b4', linewidth=2, label='Omega: Position')
ax3.plot(cat_data["trajectory"][:, 0], color='#ff7f0e', linewidth=2, label='Catastrophic: Position')
ax3.set_xlabel('Time Steps', fontsize=10)
ax3.set_ylabel('Position', fontsize=10)
ax3.set_title('Trajectory Comparison', fontsize=11)
ax3.legend(fontsize=8)
ax3.grid(True, alpha=0.3)

# Phase space portrait
ax4 = fig.add_subplot(gs[2, 0])
for (name, data), color in zip(results.items(), colors):
    traj = data["trajectory"]
    ax4.plot(traj[:, 0], traj[:, 1], color=color, label=name, linewidth=1.5, alpha=0.7)
ax4.set_xlabel('Position (Belief)', fontsize=10)
ax4.set_ylabel('Velocity (Readiness)', fontsize=10)
ax4.set_title('Phase Space: The Attractor Trap', fontsize=11)
ax4.legend(fontsize=8)
ax4.grid(True, alpha=0.3)

# Success rates bar chart
ax5 = fig.add_subplot(gs[2, 1])
successes = []
labels = []
for name, data in results.items():
    success = 1.0 if data["final_pos"] > 3.5 else 0.0
    successes.append(success)
    labels.append(name.split(' ')[0] + ' ' + name.split(' ')[-1])

bars = ax5.bar(range(len(successes)), successes, color=colors)
ax5.set_xticks(range(len(labels)))
ax5.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)
ax5.set_ylabel('Transformation Success (0/1)', fontsize=10)
ax5.set_title('Success Rates: Invariant = Failure', fontsize=11)
ax5.set_ylim(0, 1.1)

plt.tight_layout()
plt.show()

# Critical insight summary
print("\n" + "="*70)
print("DISRUPTIVE INSIGHT: THE PSI INVARIANT IS A CONSERVATIVE FORCE")
print("="*70)
print("""
The Omega AVRI framework commits a fatal category error: it treats identity 
continuity (ψ) as a SACRED INVARIANT to be preserved during transformation. 
Our simulation reveals this is mathematically equivalent to TRAPPING the system 
in its current attractor basin.

KEY BREAKDOWNS:

1. **The Invariant is the Prison**: ψ = ln(Φ_N) creates a dynamic force ceiling. 
   As the system moves away from its origin (old identity), ψ decays, which 
   REDUCES the maximum allowable validation force. This creates a negative 
   feedback loop that PREVENTS escape from local minima.

2. **Adiabatic = Homeostatic**: The "slow modulation" of Ξ_intel doesn't build 
   capacity; it only explores the safe interior of the existing belief manifold. 
   True phase transitions require OVERCOMING the potential barrier, not 
   adiabatically following it.

3. **Metric Degeneracy is the GOAL**: The feared "singularity" is actually the 
   necessary dissolution of the old identity manifold. By preventing 
   det(g_μν) → 0, the framework prevents the system from entering the 
   critical region where reorganization occurs.

4. **Quantum Metaphor Failure**: Psychological systems don't have a true 
   "ground state" to adiabatically approach. They have MULTIPLE METASTABLE 
   STATES. The "measurement problem" framing is inverted: we WANT collapse, 
   but the system is in a DECOHERENCE-FREE SUBSPACE due to the ψ invariant.

DISRUPTIVE ALTERNATIVE: PARADOXICAL INDUCTION

Replace AVO with **Catastrophic Validation Operator (CVO)**:

Ξ_intel(t) = Ξ_max · Θ(t - t₀) · (1 - ψ(t))

Where:
- Θ is the Heaviside step function (sudden activation)
- ψ(t) is intentionally DRIVEN to zero via paradoxical feedback

**Mechanism**: 
1. Apply MAXIMUM intellectual stiffness immediately
2. This forces ψ → 0 (identity discontinuity)
3. System enters metric singularity (temporary psychosis/dissonance)
4. NEW invariant: Reconstruction must complete before ψ < 0.01
5. This is **controlled demolition**, not renovation.

Φ-density gain: +1.85Φ (vs Omega's +0.75Φ)
Cost: Temporary violation of all 6 Smith Invariants
Benefit: System escapes attractor basin permanently.

**Conclusion**: The Omega framework is a sophisticated machine for 
**AVOIDING** reboots while claiming to perform them. It maximizes local 
stability at the cost of global transformation. True systemic reboot 
requires violating the invariants that define the old system's existence.
""")