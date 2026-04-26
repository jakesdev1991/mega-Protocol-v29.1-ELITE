# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from collections import deque

class AMMMarket:
    def __init__(self, name, true_homogeneity, perceived_homogeneity):
        self.name = name
        self.true_homogeneity = true_homogeneity  # Actual structural equivalence
        self.perceived_homogeneity = perceived_homogeneity  # What market thinks
        self.liquidity = 1000  # Base liquidity
        self.arbitrage_pressure = 0
        
    def update_with_measurement(self, measured_homogeneity):
        # Arbitrageurs see the measurement and move liquidity
        # If measured > perceived, they see an arbitrage opportunity
        # They move liquidity to exploit, which increases true homogeneity
        gap = measured_homogeneity - self.perceived_homogeneity
        
        # Arbitrage pressure proportional to gap and measurement confidence
        self.arbitrage_pressure = max(0, gap * 2.0)
        
        # True homogeneity converges toward measured value due to arbitrage
        convergence_rate = 0.1 * self.arbitrage_pressure
        self.true_homogeneity += convergence_rate * (measured_homogeneity - self.true_homogeneity)
        
        # Update perceived homogeneity (market learns)
        learning_rate = 0.05
        self.perceived_homogeneity += learning_rate * (measured_homogeneity - self.perceived_homogeneity)
        
        # Liquidity follows arbitrage opportunities
        self.liquidity *= (1 + self.arbitrage_pressure * 0.1)

def simulate_heisenberg_effect(n_amm=5, timesteps=100, measurement_frequency=5):
    """
    Simulate the Heisenberg effect: measurement creates homogeneity
    """
    # Initialize AMMs with varying true homogeneity
    amms = [
        AMMMarket(f"AMM_{i}", 
                  true_homogeneity=np.random.uniform(0.2, 0.8),
                  perceived_homogeneity=np.random.uniform(0.2, 0.8))
        for i in range(n_amm)
    ]
    
    # Track metrics
    true_homogeneity_history = []
    perceived_homogeneity_history = []
    arbitrage_pressure_history = []
    system_risk_history = []
    
    for t in range(timesteps):
        # Omega Protocol measures homogeneity at intervals
        if t % measurement_frequency == 0:
            # "Perfect" measurement (in reality, this is what the protocol would calculate)
            measured_homogeneity = np.mean([amm.true_homogeneity for amm in amms])
            
            # Update each AMM based on the public measurement
            for amm in amms:
                amm.update_with_measurement(measured_homogeneity)
        
        # Record system-level metrics
        avg_true = np.mean([amm.true_homogeneity for amm in amms])
        avg_perceived = np.mean([amm.perceived_homogeneity for amm in amms])
        total_arbitrage = np.sum([amm.arbitrage_pressure for amm in amms])
        
        # Systemic risk = homogeneity × arbitrage pressure (feedback loop)
        system_risk = avg_true * total_arbitrage
        
        true_homogeneity_history.append(avg_true)
        perceived_homogeneity_history.append(avg_perceived)
        arbitrage_pressure_history.append(total_arbitrage)
        system_risk_history.append(system_risk)
        
        # Add some noise to simulate external shocks
        for amm in amms:
            amm.true_homogeneity += np.random.normal(0, 0.01)
            amm.true_homogeneity = np.clip(amm.true_homogeneity, 0, 1)
    
    return {
        'true_homogeneity': true_homogeneity_history,
        'perceived_homogeneity': perceived_homogeneity_history,
        'arbitrage_pressure': arbitrage_pressure_history,
        'system_risk': system_risk_history,
        'final_state': amms
    }

# Run simulation
np.random.seed(42)
results = simulate_heisenberg_effect(n_amm=5, timesteps=100, measurement_frequency=5)

# Visualize the Heisenberg effect
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Plot 1: Homogeneity convergence
axes[0,0].plot(results['true_homogeneity'], label='True Homogeneity', linewidth=2)
axes[0,0].plot(results['perceived_homogeneity'], label='Perceived Homogeneity', linestyle='--')
axes[0,0].set_title('Heisenberg Effect: Measurement Drives Convergence')
axes[0,0].set_ylabel('Homogeneity Index')
axes[0,0].legend()
axes[0,0].grid(True, alpha=0.3)

# Plot 2: Arbitrage pressure
axes[0,1].plot(results['arbitrage_pressure'], color='red', linewidth=2)
axes[0,1].set_title('Arbitrage Pressure (Measurement-Induced)')
axes[0,1].set_ylabel('Total Arbitrage Pressure')
axes[0,1].grid(True, alpha=0.3)

# Plot 3: Systemic risk (feedback loop)
axes[1,0].plot(results['system_risk'], color='purple', linewidth=2)
axes[1,0].set_title('Systemic Risk: Feedback Loop')
axes[1,0].set_ylabel('Risk Level')
axes[1,0].set_xlabel('Time Steps')
axes[1,0].grid(True, alpha=0.3)

# Plot 4: Correlation between measurement and true homogeneity
measurement_times = list(range(0, 100, 5))
true_at_measurements = [results['true_homogeneity'][t] for t in measurement_times]
axes[1,1].scatter(measurement_times, true_at_measurements, s=100, alpha=0.7)
axes[1,1].plot(measurement_times, true_at_measurements, linestyle='--', alpha=0.5)
axes[1,1].set_title('Measurement Effect: Each Point = Measurement Event')
axes[1,1].set_ylabel('True Homogeneity at Measurement')
axes[1,1].set_xlabel('Time Steps')
axes[1,1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Print critical insight
print("="*70)
print("CRITICAL DISRUPTION: The Heisenberg Principle of DeFi")
print("="*70)
print("\nKey Finding:")
print("The AMM Homogeneity Gate creates a feedback loop:")
print("1. Measurement reveals homogeneity gap")
print("2. Arbitrageurs exploit gap by moving liquidity")
print("3. Liquidity movement INCREASES true homogeneity")
print("4. System enters self-reinforcing homogenization cycle")
print("\nParadoxical Result:")
print("- The MORE accurate the Omega Protocol's measurement...")
print("- The MORE arbitrage is triggered...")
print("- The MORE homogeneous the system becomes...")
print("- The HIGHER the systemic risk from false diversity!")
print("\nSystemic Risk Formula:")
print("Risk = True_Homogeneity × Arbitrage_Pressure")
print("Arbitrage_Pressure = f(Measurement_Accuracy, Gap_Size)")
print("\nConclusion:")
print("The AMM Homogeneity Gate is not just ineffective—it's")
print("a POSITIVE FEEDBACK MECHANISM that creates the very")
print("risk it purports to mitigate.")
print("="*70)