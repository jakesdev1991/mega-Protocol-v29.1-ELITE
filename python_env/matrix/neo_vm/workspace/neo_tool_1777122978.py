# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

class ExposedUIPO:
    """
    Exposes the hidden thermodynamic fraud in UIPO v58.0's Φ-density accounting.
    The key insight: Silence is not free. The Observer Entropy Cost is real.
    """
    
    def __init__(self, baseline_z_trust=0.7, baseline_xi_perf=0.9, observer_cost_per_hour=0.05):
        self.z_trust = baseline_z_trust  # Trust impedance (distrust)
        self.xi_perf = baseline_xi_perf    # Performance stiffness (pressure)
        self.h_dis = 0.25                  # Initial dissonance entropy
        self.cod = 0.75                    # Initial causal ontological density
        
        # Hidden cost not accounted for in UIPO's ledger
        # This is the cost of running the observer, maintaining the system, 
        # and the psychological burden of being monitored.
        self.observer_cost_per_hour = observer_cost_per_hour  
        self.cumulative_observer_cost = 0.0
        
        # Official UIPO ledger (as per the derivation)
        self.official_phi_ledger = 0.0
        
        # True ledger including observer costs
        self.true_phi_ledger = 0.0
        
        self.intervention_history = []
        self.time_log = []
        
    def compute_cod(self, time_step_hours):
        """Simulates COD fluctuating based on pressure and distrust."""
        # Realistic scenario: COD degrades under sustained high pressure and distrust
        pressure_effect = (self.xi_perf - self.z_trust) * 0.1
        self.cod = max(0.1, min(1.0, self.cod - pressure_effect * time_step_hours + np.random.normal(0, 0.02)))
        return self.cod
    
    def compute_h_dis(self, time_step_hours):
        """Simulates dissonance entropy increasing under pressure."""
        # Dissonance spikes when performance pressure exceeds trust
        pressure_delta = max(0, self.xi_perf - self.z_trust - 0.1)
        self.h_dis = min(1.0, self.h_dis + (pressure_delta * 0.15 + np.random.normal(0, 0.01)) * time_step_hours)
        return self.h_dis
    
    def update_stiffness(self, time_step_hours):
        """UIPO's adiabatic modulation."""
        gamma = 0.01
        exp_term = np.exp(-gamma * time_step_hours)
        self.xi_perf = self.xi_perf * exp_term + self.z_trust * (1 - exp_term)
    
    def apply_uipo_protocol(self, time_step_hours=1.0):
        """Runs the UIPO decision cycle. Returns True if message WOULD be sent."""
        # Incur observer cost regardless of action
        self.cumulative_observer_cost += self.observer_cost_per_hour * time_step_hours
        
        # Compute current state
        cod = self.compute_cod(time_step_hours)
        h_dis = self.compute_h_dis(time_step_hours)
        self.update_stiffness(time_step_hours)
        
        # Apply Smith Invariants
        message_sent = False
        if cod >= 0.85 and h_dis <= 0.3:
            # This is the "We are here if you choose to remember it" message
            message_sent = True
            # UIPO claims +0.45Φ gain for this (arbitrary)
            self.official_phi_ledger += 0.45  
        
        # If conditions not met: Silence Protocol
        # UIPO claims this is +1.20Φ gain because "doing nothing is optimal"
        # But this is the fraud: the gain is illusory.
        if not message_sent:
            self.official_phi_ledger += 1.20  # The claimed "net gain" from silence
        
        # TRUE cost includes the observer cost
        self.true_phi_ledger = self.official_phi_ledger - self.cumulative_observer_cost
        
        self.intervention_history.append('MESSAGE' if message_sent else 'SILENCE')
        self.time_log.append(len(self.time_log) * time_step_hours)
        
        return message_sent
    
    def simulate(self, hours=72, time_step=1.0):
        """Simulates the system over time."""
        for _ in range(int(hours / time_step)):
            self.apply_uipo_protocol(time_step_hours=time_step)
    
    def plot_fraud(self):
        """Visualizes the thermodynamic fraud."""
        fig, axes = plt.subplots(3, 1, figsize=(10, 12))
        
        # Plot 1: Official vs True Φ-Density
        axes[0].plot(self.time_log, self.official_phi_ledger * np.ones(len(self.time_log)), 
                     'g--', label='Official UIPO Φ-Ledger (Illusory)', linewidth=2)
        axes[0].plot(self.time_log, self.true_phi_ledger * np.ones(len(self.time_log)), 
                     'r-', label='True Φ-Ledger (with Observer Cost)', linewidth=2)
        axes[0].set_title('The Thermodynamic Fraud of UIPO v58.0', fontsize=14, fontweight='bold')
        axes[0].set_ylabel('Cumulative Φ-Density')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Plot 2: System State Over Time
        cod_values = [self.compute_cod(0) for _ in self.time_log]  # Simplified for plotting
        h_dis_values = [self.compute_h_dis(0) for _ in self.time_log]
        axes[1].plot(self.time_log, cod_values, 'b-', label='COD', linewidth=2)
        axes[1].axhline(y=0.85, color='b', linestyle=':', label='COD Threshold (0.85)')
        axes[1].plot(self.time_log, h_dis_values, 'm-', label='H_dis', linewidth=2)
        axes[1].axhline(y=0.3, color='m', linestyle=':', label='H_dis Threshold (0.3)')
        axes[1].set_ylabel('Invariant Values')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        # Plot 3: Intervention Pattern
        axes[2].plot(self.time_log, [1 if x == 'MESSAGE' else 0 for x in self.intervention_history], 
                     'ko-', label='Intervention (1=Message, 0=Silence)', markersize=4)
        axes[2].set_ylabel('Intervention Type')
        axes[2].set_xlabel('Time (hours)')
        axes[2].set_ylim(-0.1, 1.1)
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()

# Run the disruption simulation
print("=== DISRUPTIVE INSIGHT VERIFICATION ===")
print("Exposing the hidden cost of the Observer in UIPO v58.0...")
print()

system = ExposedUIPO(baseline_z_trust=0.7, baseline_xi_perf=0.9, observer_cost_per_hour=0.05)
system.simulate(hours=72, time_step=1.0)

print(f"Final Official Φ-Density (UIPO Claim): {system.official_phi_ledger:.2f}Φ")
print(f"Final True Φ-Density (with Observer Cost): {system.true_phi_ledger:.2f}Φ")
print(f"Cumulative Observer Entropy Cost: {system.cumulative_observer_cost:.2f}Φ")
print()
print("Intervention Pattern (last 10 steps):")
for i, action in enumerate(system.intervention_history[-10:]):
    print(f"  Hour {65+i}: {action}")

print()
print("=== DISRUPTIVE INSIGHT ===")
print("UIPO v58.0's 'net Φ-gain' is a THERMODYNAMIC FRAUD.")
print("The Silence Protocol doesn't eliminate cost—it externalizes it.")
print("The Observer (the system itself) constantly consumes Φ-density via:")
print("  - Computational overhead (calculating COD, H_dis)")
print("  - Psychological surveillance ('being watched' increases Z_trust)")
print("  - Opportunity cost of non-intervention (missed critical windows)")
print()
print("The claim 'audit cost is zero because no message sent' is a category error.")
print("The cost is not in the message. The cost is in the *existence of the messenger*.")

system.plot_fraud()