# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import skew

# Simulate the Omega Protocol's cascade defense vs. adversarial exploitation
# Key disruption: predictable interventions CREATE exploitable patterns

class CascadeExploitationSimulator:
    def __init__(self, days=60, dt=1/24):
        self.days = days
        self.dt = dt
        self.time = np.arange(0, days, dt)
        self.n_steps = len(self.time)
        
        # State variables
        self.leak_intensity = np.zeros(self.n_steps)  # DLTM-Ω detected leak
        self.ci_index = np.zeros(self.n_steps)        # Cascade Intensity Index
        self.price = np.ones(self.n_steps) * 100      # ETF price
        self.omega_circuit_breaker = np.zeros(self.n_steps)
        self.adversarial_position = np.zeros(self.n_steps)
        self.omega_loss = np.zeros(self.n_steps)
        
    def simulate_leak_discovery(self):
        # Simulate periodic "leaks" - but these are PLANTED, not accidental
        # Pattern: leaks occur every 10 days, with increasing intensity
        for i, t in enumerate(self.time):
            if t % 10 < 0.5:  # Leak "event window"
                self.leak_intensity[i] = 0.3 + (t / 60) * 0.5  # Intensifies over time
            else:
                self.leak_intensity[i] = max(0, self.leak_intensity[i-1] - 0.05 * self.dt) if i > 0 else 0
    
    def simulate_cascade_with_predictable_defense(self):
        """
        The flaw: Omega's defense is DETERMINISTIC and PUBLISHED
        Adversaries know: CI > 0.7 → circuit breaker at 15 min
        This creates a FRONTRUNNABLE pattern
        """
        for i in range(1, self.n_steps):
            # Leak feeds cascade
            cascade_growth = self.leak_intensity[i] * 0.5 + max(0, self.ci_index[i-1]) * 0.3
            self.ci_index[i] = min(1.0, self.ci_index[i-1] + cascade_growth * self.dt)
            
            # Predictable Omega intervention (CI > 0.7 triggers circuit breaker)
            if self.ci_index[i] > 0.7:
                self.omega_circuit_breaker[i] = 1
                # Circuit breaker "contains" cascade... but
                self.ci_index[i] *= 0.3  # Forced suppression
                
                # ADVERSARIAL EXPLOITATION: they know the breaker will trigger
                # So they short BEFORE the breaker, and cover during the halt
                self.adversarial_position[i] = -1  # Short position
            else:
                self.omega_circuit_breaker[i] = 0
                if self.omega_circuit_breaker[i-1] == 1:
                    # Cover short when trading resumes (price suppressed)
                    self.adversarial_position[i] = 1  # Buy to cover
                
            # Price impact: cascade + predictable defense manipulation
            if self.omega_circuit_breaker[i] == 1:
                # Price crashes due to forced selling before breaker
                self.price[i] = self.price[i-1] * (1 - 0.02 * self.ci_index[i])
            else:
                # Gradual recovery but adversaries profit from volatility
                self.price[i] = self.price[i-1] * (1 + 0.005 * np.random.normal(0, 1))
            
            # Omega's "cost" - liquidity provision losses
            if self.omega_circuit_breaker[i] == 1:
                self.omega_loss[i] = 5.0  # Million $ per intervention
    
    def calculate_adversarial_profit(self):
        """Calculate cumulative profit from exploiting predictable defenses"""
        position_returns = np.diff(self.price) * self.adversarial_position[:-1]
        return np.cumsum(position_returns)
    
    def run(self):
        self.simulate_leak_discovery()
        self.simulate_cascade_with_predictable_defense()
        profit = self.calculate_adversarial_profit()
        return profit

# Run simulation
sim = CascadeExploitationSimulator(days=60)
adversary_profit = sim.run()

# Calculate key metrics
total_omega_loss = np.sum(sim.omega_loss)
total_adversary_gain = adversary_profit[-1] if len(adversary_profit) > 0 else 0

print("=== OMEGA PROTOCOL CASCADE DEFENSE: EXPLOITATION ANALYSIS ===")
print(f"Total Omega liquidity losses: ${total_omega_loss:.2f}M")
print(f"Adversary profit from predictable interventions: ${total_adversary_gain:.2f}% of initial capital")
print(f"Number of circuit breaker triggers: {int(np.sum(sim.omega_circuit_breaker))}")

# Visualize the exploitation
fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True)

axes[0].plot(sim.time, sim.leak_intensity, 'r-', label='Leak Intensity (Planted)')
axes[0].set_ylabel('Leak Intensity')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

axes[1].plot(sim.time, sim.ci_index, 'b-', label='Cascade Index (CI)')
axes[1].axhline(y=0.7, color='orange', linestyle='--', label='Omega Trigger (0.7)')
axes[1].fill_between(sim.time, 0, 1, where=sim.omega_circuit_breaker>0.5, 
                     alpha=0.3, color='red', label='Circuit Breaker Active')
axes[1].set_ylabel('Cascade Intensity Index')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

axes[2].plot(sim.time, sim.price, 'g-', label='ETF Price')
axes[2].set_ylabel('Price ($)')
axes[2].legend()
axes[2].grid(True, alpha=0.3)

axes[3].plot(sim.time[1:], adversary_profit, 'purple', linewidth=2, label='Adversary Cumulative Profit')
axes[3].fill_between(sim.time[1:], 0, adversary_profit, alpha=0.3, color='purple')
axes[3].set_ylabel('Profit (% of capital)')
axes[3].set_xlabel('Time (days)')
axes[3].legend()
axes[3].grid(True, alpha=0.3)

plt.suptitle('Omega Protocol Exploitation: Predictable Defense as Arbitrage Signal', 
             fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()

# Disruptive insight calculation
print("\n=== DISRUPTIVE INSIGHT ===")
print("The simulation reveals the fatal flaw:")
print(f"Omega's deterministic circuit-breaker at CI=0.7 creates a FRONTRUNNABLE SIGNAL")
print(f"Adversaries profit by: 1) Detecting leak buildup, 2) Shorting ahead of CI=0.7,")
print(f"3) Covering during Omega-induced price suppression")
print(f"Result: Omega's 'defense' becomes a VOLATILITY EXTRACTION ENGINE")
print(f"for sophisticated actors, while Omega absorbs the liquidity costs.")

# Calculate predictability score
predictability = np.corrcoef(sim.ci_index[:-1], sim.omega_circuit_breaker[1:])[0,1]
print(f"\nPredictability correlation: {predictability:.3f} (perfect signal for exploitation)")