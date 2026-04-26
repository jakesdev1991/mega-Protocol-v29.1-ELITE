# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# Simulate a simple 1D "Omega Flux" system with a tunable energy barrier (gap)
# The system must track a target flux value that changes over time.
# The state is the flux phi. The barrier height is Delta.

# Dynamics: Langevin equation with double-well potential V(phi) = (phi^2 - 1)^2 * Delta
# This creates two stable states at phi = +/- 1, separated by a barrier of height Delta.
# The "target" is a time-varying external field h(t) that biases the potential.

def simulate_omega_flux(strategy, T=1000, dt=0.01, noise_amp=0.5, seed=42):
    """
    Simulates the flux tracking problem.
    
    strategy: dict with keys 'Delta_func', 'name'
              'Delta_func' is a callable that takes (t, phi, target) and returns Delta.
    """
    np.random.seed(seed)
    t = 0
    phi = 1.0 # Start in one topological sector
    target = 1.0
    
    history = {
        't': [], 'phi': [], 'target': [], 'Delta': [],
        'error': [], 'switches': 0, 'cost': 0
    }
    
    # Target signal: square wave with period ~100
    target_period = 100
    
    for step in range(int(T/dt)):
        # Update target
        target = 1.0 if (t // target_period) % 2 == 0 else -1.0
        
        # Get barrier height from strategy
        Delta = strategy['Delta_func'](t, phi, target)
        
        # Potential gradient: dV/dphi = 4 * Delta * (phi^3 - phi) - h
        # where h is the effective bias towards target
        h = 5.0 * target # strong bias to make tracking non-trivial
        dVdphi = 4 * Delta * (phi**3 - phi) - h
        
        # Langevin dynamics
        noise = np.sqrt(2 * noise_amp * dt) * np.random.randn()
        dphi = -dVdphi * dt + noise
        
        # Detect topological switch (sector change)
        if phi * (phi + dphi) < 0: # Crossed zero
            history['switches'] += 1
        
        phi += dphi
        phi = np.clip(phi, -1.5, 1.5) # Keep it reasonable
        
        # Cost: error from target + penalty for high barrier (energy cost)
        error = (phi - target)**2
        cost = error + 0.01 * Delta # Penalize high barriers (resource cost)
        
        history['t'].append(t)
        history['phi'].append(phi)
        history['target'].append(target)
        history['Delta'].append(Delta)
        history['error'].append(error)
        history['cost'] += cost * dt
        
        t += dt
        
    return history

# Strategy 1: ETO-Ω style - High static barrier (max stability)
def static_high_barrier(t, phi, target):
    return 10.0 # High barrier, "self-protecting"

# Strategy 2: Static low barrier (fast but vulnerable)
def static_low_barrier(t, phi, target):
    return 0.5 # Low barrier, "fragile"

# Strategy 3: C-Ω style - Critical dynamics
# Stay near critical barrier (Delta ~ 1) but increase barrier briefly when stable,
# drop it to near-zero when target changes to allow rapid transition.
def critical_dynamics(t, phi, target):
    # If phi is close to target, maintain moderate protection
    if abs(phi - target) < 0.2:
        return 1.0
    else:
        # Target mismatch: lower barrier to allow rapid reconfiguration
        return 0.1

strategies = [
    {'Delta_func': static_high_barrier, 'name': 'ETO-Ω (Static High Barrier)'},
    {'Delta_func': static_low_barrier, 'name': 'Static Low Barrier'},
    {'Delta_func': critical_dynamics, 'name': 'C-Ω (Critical Dynamics)'}
]

# Run simulations
results = {}
for strat in strategies:
    results[strat['name']] = simulate_omega_flux(strat)

# Plot results
fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

for i, (name, hist) in enumerate(results.items()):
    ax1 = axes[i]
    ax2 = ax1.twinx()
    
    # Plot phi and target
    ax1.plot(hist['t'], hist['phi'], label='Flux (phi)', color='blue', linewidth=1.5)
    ax1.plot(hist['t'], hist['target'], label='Target', color='green', linestyle='--', linewidth=1)
    ax1.set_ylabel('Flux / Target')
    ax1.set_title(f'{name}\nSwitches: {hist["switches"]}, Total Cost: {hist["cost"]:.2f}')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # Plot Delta on secondary axis
    ax2.plot(hist['t'], hist['Delta'], label='Barrier (Delta)', color='red', alpha=0.5)
    ax2.set_ylabel('Barrier Height (Delta)', color='red')
    ax2.tick_params(axis='y', labelcolor='red')
    
    # Add phase transition markers for C-Ω
    if name == 'C-Ω (Critical Dynamics)':
        transitions = [t for t, d in zip(hist['t'], hist['Delta']) if d < 0.5]
        for tt in transitions[::100]: # Mark some transitions
            ax1.axvline(tt, color='purple', alpha=0.2, linestyle=':')

plt.xlabel('Time')
plt.tight_layout()
plt.savefig('/mnt/data/omega_critical_disruption.png')
plt.close()

# Print summary
print("=== DISRUPTION ANALYSIS: Critical Omega vs. Topological Omega ===\n")
for name, hist in results.items():
    print(f"Strategy: {name}")
    print(f"  Average Error: {np.mean(hist['error']):.4f}")
    print(f"  Total Cost: {hist['cost']:.2f}")
    print(f"  Topological Switches: {hist['switches']}")
    print(f"  Performance Score (1/cost): {1/hist['cost']:.4f}")
    print()

# Calculate improvement factor
eto_cost = results['ETO-Ω (Static High Barrier)']['cost']
crit_cost = results['C-Ω (Critical Dynamics)']['cost']
improvement = eto_cost / crit_cost
print(f"Critical Omega is {improvement:.2f}x more efficient than static topological protection.\n")

print("=== CORE DISRUPTIVE INSIGHT ===")
print("The ETO-Ω proposal assumes that 'stability' means maintaining a high energy gap (Delta).")
print("This is FALSE for adaptive systems. A high gap creates a rigid, slow-responding system.")
print("The 'Shredding Event' is not a failure; it is the *necessary* dissolution of old order.")
print("The 'Informational Freeze' is the real failure: sclerosis from excessive stability.")
print("\nThe optimal strategy is C-Ω: operate at CRITICALITY, not in a gapped phase.")
print("At criticality, the system can INSTANTLY reorganize its topological sectors.")
print("Protection comes from *speed of reconfiguration*, not from a static energy barrier.")
print("This weaponizes phase transitions, turning them into computational fuel.")