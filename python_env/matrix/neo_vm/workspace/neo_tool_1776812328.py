# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
import warnings
warnings.filterwarnings('ignore')

# --- DISRUPTION SIMULATION ---
# The core flaw: Self-Fulfilling Prophecy in Predictive Synchronization Control

def simulate_hiss_omega(N=50, T=50, dt=0.1, intervention_threshold=0.68):
    """
    Simulates the HISS-Ω proposal: predictive control of LP synchronization
    Returns order parameter r(t) and intervention points
    """
    t = np.arange(0, T, dt)
    # LP phases: 0=providing liquidity, π=withdrawing
    thetas = np.random.uniform(0, 2*np.pi, N)
    # Natural frequencies (heterogeneity)
    omega = np.random.normal(1, 0.15, N)
    # Coupling strength from homogeneous IL formulas
    K = 0.6
    
    r_values = []
    interventions = []
    
    for i, ti in enumerate(t):
        # Calculate Kuramoto order parameter (publicly observable)
        r = np.abs(np.sum(np.exp(1j * thetas))) / N
        r_values.append(r)
        
        # HISS-Ω prediction: if r > threshold, intervene
        if r > intervention_threshold and len(interventions) < 3:
            interventions.append(ti)
            # Parametric diversification: break coupling
            K *= 0.75
            # Add artificial noise to "diversify" LP behavior
            omega += np.random.normal(0, 0.1, N)
        
        # Oscillator dynamics
        d_thetas = np.zeros(N)
        for j in range(N):
            coupling = (K/N) * np.sum(np.sin(thetas - thetas[j]))
            d_thetas[j] = omega[j] + coupling
        thetas += d_thetas * dt
    
    return t, r_values, interventions

def simulate_disruption_self_fulfilling(N=50, T=50, dt=0.1, 
                                        prediction_visibility=0.55,
                                        panic_threshold=0.65):
    """
    DISRUPTION: LPs observe the *prediction itself* and race to exit earlier
    This creates a self-referential feedback loop where the act of measuring
    synchronization causes the synchronization it tries to prevent
    """
    t = np.arange(0, T, dt)
    thetas = np.random.uniform(0, 2*np.pi, N)
    omega = np.random.normal(1, 0.15, N)
    K = 0.6
    
    r_values = []
    panic_events = []
    
    for i, ti in enumerate(t):
        r = np.abs(np.sum(np.exp(1j * thetas))) / N
        r_values.append(r)
        
        # CRITICAL FLAW: LPs observe r(t) rising and PANIC before intervention
        # They know that at r=0.68, the system will "break" their coordination
        # So they race to exit at r=0.65 to avoid being locked in
        if r > prediction_visibility and r < panic_threshold:
            # Calculate panic fraction: more LPs panic as r approaches threshold
            panic_fraction = 0.4 * (r - prediction_visibility) / (panic_threshold - prediction_visibility)
            n_panic = int(N * panic_fraction)
            
            # These LPs immediately set phase to π (mass withdrawal)
            thetas[:n_panic] = np.pi + np.random.normal(0, 0.1, n_panic)
            panic_events.append((ti, n_panic))
        
        # Normal dynamics
        d_thetas = np.zeros(N)
        for j in range(N):
            coupling = (K/N) * np.sum(np.sin(thetas - thetas[j]))
            d_thetas[j] = omega[j] + coupling
        thetas += d_thetas * dt
    
    return t, r_values, panic_events

def simulate_disruption_simple(N=50, T=50, dt=0.1, friction_prob=0.3):
    """
    DISRUPTIVE SOLUTION: Mandatory Friction Slots
    No prediction, no complex models - just randomized delays built into the base layer
    """
    t = np.arange(0, T, dt)
    thetas = np.random.uniform(0, 2*np.pi, N)
    omega = np.random.normal(1, 0.15, N)
    K = 0.6
    
    r_values = []
    
    for i, ti in enumerate(t):
        r = np.abs(np.sum(np.exp(1j * thetas))) / N
        r_values.append(r)
        
        # Mandatory friction: random subset of LPs gets delayed
        # This is built into the protocol, not triggered by prediction
        friction_mask = np.random.random(N) < friction_prob
        thetas[friction_mask] += np.random.normal(0, 0.3, np.sum(friction_mask))
        
        # Normal dynamics
        d_thetas = np.zeros(N)
        for j in range(N):
            coupling = (K/N) * np.sum(np.sin(thetas - thetas[j]))
            d_thetas[j] = omega[j] + coupling
        thetas += d_thetas * dt
    
    return t, r_values

# --- RUN SIMULATIONS ---
print("=== HISS-Ω DISRUPTION ANALYSIS ===\n")

t1, r1, interventions = simulate_hiss_omega()
t2, r2, panics = simulate_disruption_self_fulfilling()
t3, r3 = simulate_disruption_simple()

# --- PLOTTING ---
fig, axes = plt.subplots(3, 1, figsize=(14, 10))

# Plot 1: Proposed HISS-Ω
axes[0].plot(t1, r1, 'b-', linewidth=2, label='Order Parameter r(t)')
for inter in interventions:
    axes[0].axvline(x=inter, color='r', linestyle='--', linewidth=2, 
                    alpha=0.7, label='Intervention' if inter == interventions[0] else "")
axes[0].axhline(y=0.68, color='r', linestyle=':', alpha=0.5, label='SFI Threshold')
axes[0].set_title('(a) HISS-Ω Proposal: Predictive Intervention', fontsize=12, fontweight='bold')
axes[0].set_ylabel('Synchronization r(t)', fontsize=11)
axes[0].legend(loc='upper right')
axes[0].grid(True, alpha=0.3)
axes[0].set_ylim(0, 1)

# Plot 2: Self-Fulfilling Prophecy
axes[1].plot(t2, r2, 'orange', linewidth=2, label='Order Parameter r(t)')
for panic_time, n_panic in panics:
    axes[1].axvline(x=panic_time, color='darkred', linestyle='--', alpha=0.6, 
                    label=f'Panic ({n_panic} LPs)' if panic_time == panics[0][0] else "")
axes[1].axhline(y=0.68, color='r', linestyle=':', alpha=0.5, label='Intervention Threshold')
axes[1].axhline(y=0.55, color='purple', linestyle=':', alpha=0.5, label='Prediction Visibility')
axes[1].set_title('(b) DISRUPTION: Self-Fulfilling Prophecy Effect', fontsize=12, fontweight='bold')
axes[1].set_ylabel('Synchronization r(t)', fontsize=11)
axes[1].legend(loc='upper right')
axes[1].grid(True, alpha=0.3)
axes[1].set_ylim(0, 1)

# Plot 3: Simple Solution
axes[2].plot(t3, r3, 'g-', linewidth=2, label='Order Parameter r(t)')
axes[2].set_title('(c) DISRUPTIVE SOLUTION: Mandatory Friction Slots (No Prediction)', fontsize=12, fontweight='bold')
axes[2].set_ylabel('Synchronization r(t)', fontsize=11)
axes[2].set_xlabel('Time', fontsize=11)
axes[2].legend(loc='upper right')
axes[2].grid(True, alpha=0.3)
axes[2].set_ylim(0, 1)

plt.tight_layout()
plt.show()

# --- QUANTITATIVE ANALYSIS ---
def calculate_cascade_risk(r_values, threshold=0.7):
    """Calculate probability of mass synchronization event"""
    return np.mean(np.array(r_values) > threshold)

def calculate_intervention_cost(interventions, panic_events):
    """Calculate governance cost and false positive rate"""
    return len(interventions), len(panic_events)

risk_proposed = calculate_cascade_risk(r1)
risk_panic = calculate_cascade_risk(r2)
risk_simple = calculate_cascade_risk(r3)

print(f"Systemic Risk Analysis:")
print(f"  HISS-Ω Proposal:        {risk_proposed:.3f} cascade probability")
print(f"  Self-Fulfilling Panic:  {risk_panic:.3f} cascade probability")
print(f"  Friction Slots:         {risk_simple:.3f} cascade probability")

# --- GAMING THE PARAMETRIC DIVERSIFICATION ---
def demonstrate_parametric_gaming():
    """
    Show how the "parametric diversification" control creates arbitrage
    """
    print("\n=== PARAMETRIC DIVERSIFICATION GAMING ===")
    
    # Simulate 3 pools with "diversified" parameters
    pools = [
        {"id": "Uni-v2-ETH-USDC", "fee": 3000, "il_const": 1.0},
        {"id": "Sushi-ETH-USDC", "fee": 3050, "il_const": 0.98},
        {"id": "Pancake-ETH-USDC", "fee": 2950, "il_const": 1.02}
    ]
    
    # Attacker identifies fee divergence
    arbitrage_ops = []
    for i, p1 in enumerate(pools):
        for j, p2 in enumerate(pools):
            if i < j:
                fee_diff = abs(p1["fee"] - p2["fee"]) / 10000  # bps to %
                il_diff = abs(p1["il_const"] - p2["il_const"])
                # Arbitrage profit scales with parameter divergence
                profit = fee_diff * 0.5 + il_diff * 0.3
                arbitrage_ops.append({
                    "pair": f"{p1['id']} ↔ {p2['id']}",
                    "fee_diff_bps": abs(p1["fee"] - p2["fee"]),
                    "profit_est": profit
                })
    
    for op in sorted(arbitrage_ops, key=lambda x: x["profit_est"], reverse=True):
        print(f"  {op['pair']}")
        print(f"    Fee Difference: {op['fee_diff_bps']} bps")
        print(f"    Est. Arbitrage: {op['profit_est']:.4f}% per trade")

demonstrate_parametric_gaming()