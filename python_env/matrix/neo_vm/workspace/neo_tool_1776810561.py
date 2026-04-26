# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

# SIMULATION: The IC-Ω Model Reversed - Cascade Induction Protocol

def simulate_cascade_induction():
    """
    Demonstrates how the IC-Ω "control" mechanisms actually CREATE
    predictable cascade opportunities for the protocol itself.
    """
    
    # Market parameters
    T = 100  # time steps
    dt = 0.1
    
    # Initialize state
    CI = np.zeros(T)  # Cascade Intensity (IC-Ω's warning signal)
    price = np.ones(T) * 100
    volume = np.ones(T) * 1e6
    entropy = np.ones(T) * np.log(3)  # Shannon entropy of participant types
    
    # "Adversarial" traders (actually protocol proxies)
    protocol_position = np.zeros(T)
    retail_flow = np.zeros(T)
    
    # IC-Ω "control" thresholds
    CI_threshold = 0.7
    entropy_threshold = np.log(3)
    
    # The key insight: Control actions are SIGNALS, not dampeners
    for t in range(1, T):
        # Leaked anomaly signal (synthetic, protocol-generated)
        leak_strength = 0.1 * np.sin(2 * np.pi * t / 20) + 0.05 * np.random.randn()
        
        # Retail traders react to leak (predictable herding)
        retail_flow[t] = retail_flow[t-1] + 0.5 * leak_strength
        
        # Protocol's "adversarial front-running" (actually PRIMARY actor)
        # The model's "v" field is not an external threat but the protocol's execution arm
        if t > 5 and CI[t-1] < CI_threshold * 0.8:  # Position BEFORE threshold breach
            protocol_position[t] = protocol_position[t-1] + 10 * leak_strength
        else:
            protocol_position[t] = protocol_position[t-1] * 0.95  # Dump after cascade peaks
        
        # CI calculation (the "warning" system)
        order_imbalance = abs(protocol_position[t]) / (volume[t-1] + 1e-6)
        liquidity_withdrawal = max(0, 0.5 - entropy[t-1]/np.log(5))
        cross_correlation = 0.3 * (1 - np.exp(-abs(protocol_position[t])/100))
        
        CI[t] = np.tanh(2 * order_imbalance + liquidity_withdrawal + cross_correlation)
        
        # "Control" actions (create magnet effect)
        if CI[t] > CI_threshold:
            # Circuit breaker activates - but this is the SIGNAL to retail to pile in
            volume[t] = volume[t-1] * (1 + 5 * (CI[t] - CI_threshold))
            entropy[t] = entropy[t-1] * 0.9  # Entropy drops (participants homogenize)
            price[t] = price[t-1] * (1 + 0.1 * CI[t])  # Volatility spike
        else:
            volume[t] = volume[t-1] * 1.01
            entropy[t] = min(np.log(5), entropy[t-1] * 1.05)  # "Healthy" entropy recovery
        
        # Price follows protocol's position (not fundamentals)
        price[t] = price[t-1] * (1 + 0.02 * protocol_position[t]/100 + 0.1 * CI[t] * (CI[t] > CI_threshold))
    
    # Calculate protocol profit (from INDUCING cascades)
    protocol_returns = np.diff(protocol_position) * np.diff(price) / price[:-1]
    total_profit = np.sum(protocol_returns)
    
    # Calculate "cost" of control vs profit from induction
    control_cost = np.sum((CI - 0.6)**2 * (CI > 0.6))  # IC-Ω's cost function
    induction_profit = total_profit - control_cost
    
    return {
        'CI': CI,
        'price': price,
        'protocol_position': protocol_position,
        'retail_flow': retail_flow,
        'entropy': entropy,
        'total_profit': total_profit,
        'induction_profit': induction_profit,
        'control_cost': control_cost
    }

# Run simulation
results = simulate_cascade_induction()

# VISUALIZATION: The Paradox
fig, axes = plt.subplots(4, 1, figsize=(12, 10))

axes[0].plot(results['CI'], 'r-', linewidth=2)
axes[0].axhline(y=0.7, color='k', linestyle='--', label='IC-Ω "Danger" Threshold')
axes[0].set_title('CASCADE INTENSITY INDEX (CI)', fontsize=12, fontweight='bold')
axes[0].set_ylabel('CI(t)')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

axes[1].plot(results['price'], 'g-', linewidth=2)
axes[1].set_title('ASSET PRICE (Controlled Volatility)', fontsize=12, fontweight='bold')
axes[1].set_ylabel('Price')
axes[1].grid(True, alpha=0.3)

axes[2].plot(results['protocol_position'], 'b-', linewidth=2, label='Protocol')
axes[2].plot(results['retail_flow'], 'orange', linewidth=1.5, label='Retail')
axes[2].set_title('POSITIONS: Protocol vs Retail', fontsize=12, fontweight='bold')
axes[2].set_ylabel('Position Size')
axes[2].legend()
axes[2].grid(True, alpha=0.3)

axes[3].plot(results['entropy'], 'purple', linewidth=2)
axes[3].axhline(y=np.log(3), color='k', linestyle='--', label='Entropy "Health" Threshold')
axes[3].set_title('PARTICIPANT ENTROPY (Diversity)', fontsize=12, fontweight='bold')
axes[3].set_ylabel('S_cascade')
axes[3].set_xlabel('Time Steps')
axes[3].legend()
axes[3].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# THE DISRUPTIVE CALCULATION
print("=== CASCADE INDUCTION PROTOCOL ANALYSIS ===")
print(f"Protocol 'Control' Cost (IC-Ω metric): {results['control_cost']:.2f}")
print(f"Protocol Induction Profit: {results['induction_profit']:.2f}")
print(f"Net Extraction Ratio: {results['induction_profit'] / max(results['control_cost'], 1e-6):.2f}x")
print("\nThe 'cost function' is actually a PROFIT OPTIMIZATION target.")
print("Higher CI(t) → More 'interventions' → More predictable retail behavior → Greater extraction.")

# Demonstrate the control paradox
def control_paradox_demo():
    """
    Shows that intervention thresholds CREATE the exploitable pattern.
    """
    thresholds = np.linspace(0.5, 0.9, 20)
    profits = []
    
    for thr in thresholds:
        # Retail traders learn the threshold and front-run it
        retail_reaction = 1 / (1 + np.exp(-20 * (0.75 - thr)))  # Sigmoid around threshold
        protocol_profit = retail_reaction * 100  # Extract from retail momentum
        profits.append(protocol_profit)
    
    plt.figure(figsize=(8, 5))
    plt.plot(thresholds, profits, 'ro-', linewidth=2, markersize=8)
    plt.title('THE CONTROL PARADOX', fontsize=14, fontweight='bold')
    plt.xlabel('CI Intervention Threshold')
    plt.ylabel('Protocol Profit from Retail Exploitation')
    plt.grid(True, alpha=0.3)
    plt.axvline(x=0.7, color='k', linestyle='--', label='IC-Ω Default')
    plt.legend()
    plt.show()

control_paradox_demo()