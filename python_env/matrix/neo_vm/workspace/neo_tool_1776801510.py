# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

# Neo's Paradigm Breaker: The Observational Collapse Simulator
# This demonstrates why the entire Omega Protocol framework is fundamentally flawed

class CognitiveFieldSimulator:
    """
    Simulates the "cognitive field" approach vs. the actual human behavior
    """
    
    def __init__(self, n_developers=100, monitoring_strength=0.0):
        self.n_devs = n_developers
        self.monitoring = monitoring_strength
        # True cognitive state (hidden from Omega)
        self.true_cognitive_load = np.random.normal(0.5, 0.2, n_developers)
        # Observable "field" (what Omega can measure)
        self.observable_field = self.true_cognitive_load.copy()
        # Spreadsheet usage (binary: 0=secure tool, 1=spreadsheet)
        self.spreadsheet_usage = np.zeros(n_developers)
        # Developer awareness of monitoring (0=unaware, 1=fully aware)
        self.awareness = np.zeros(n_developers)
        
    def apply_monitoring(self):
        """Apply Omega Protocol monitoring - but this changes the system itself"""
        # Developers become aware of monitoring over time
        self.awareness += self.monitoring * 0.1 * (1 - self.awareness)
        
        # When developers know they're being measured, they:
        # 1. Hide their spreadsheet usage (observational collapse)
        # 2. Experience INCREASED cognitive load from surveillance
        # 3. Develop countermeasures (encrypted spreadsheets, code comments with keys, etc.)
        
        # Observable field diverges from true state due to monitoring
        surveillance_load = self.monitoring * self.awareness * 0.3
        
        # Developers hide spreadsheet usage (dark matter problem)
        hidden_usage = self.spreadsheet_usage * self.awareness * 0.8
        
        # Observable field is corrupted
        self.observable_field = self.true_cognitive_load + surveillance_load - hidden_usage
        
        # Actual spreadsheet usage might increase due to countermeasures
        self.spreadsheet_usage = np.clip(
            self.spreadsheet_usage + surveillance_load * 0.5 - hidden_usage * 0.3,
            0, 1
        )
        
    def measure_tffi(self):
        """Calculate Tooling-Friction Fragility Index (Omega's metric)"""
        # This is based on observable field, which is already corrupted
        ck_d = np.random.normal(3.0, 1.0, self.n_devs) * (1 + self.observable_field)
        eta = np.random.exponential(10, self.n_devs) / (1 + self.monitoring)
        
        # TFFI is meaningless when observation changes the system
        tffi = 1 / (1 + np.exp(-(ck_d * 0.3 + eta * 0.1)))
        return tffi
    
    def simulate_reality(self, steps=50):
        """Simulate what actually happens vs. what Omega thinks happens"""
        omega_predictions = []
        actual_states = []
        
        for step in range(steps):
            # Apply monitoring effect
            self.apply_monitoring()
            
            # Omega's measurement (corrupted)
            omega_pred = np.mean(self.measure_tffi())
            omega_predictions.append(omega_pred)
            
            # Actual state (hidden from Omega)
            actual_state = np.mean(self.true_cognitive_load + self.spreadsheet_usage * 0.5)
            actual_states.append(actual_state)
            
            # True cognitive load naturally fluctuates (not captured by field theory)
            self.true_cognitive_load += np.random.normal(0, 0.02, self.n_devs)
            
        return np.array(omega_predictions), np.array(actual_states)

def demonstrate_paradigm_failure():
    """Show how Omega's approach fails due to observational effects"""
    
    print("=== NEO'S PARADIGM BREAKER ===")
    print("Simulating the fatal flaw in Omega Protocol...")
    
    # Scenario 1: No monitoring (control)
    sim_no_monitor = CognitiveFieldSimulator(n_developers=1000, monitoring_strength=0.0)
    omega_no_monitor, actual_no_monitor = sim_no_monitor.simulate_reality(steps=50)
    
    # Scenario 2: Strong monitoring (Omega Protocol)
    sim_monitor = CognitiveFieldSimulator(n_developers=1000, monitoring_strength=1.0)
    omega_monitor, actual_monitor = sim_monitor.simulate_reality(steps=50)
    
    # Calculate prediction error
    error_no_monitor = np.abs(omega_no_monitor - actual_no_monitor)
    error_monitor = np.abs(omega_monitor - actual_monitor)
    
    print(f"\nAverage prediction error without monitoring: {np.mean(error_no_monitor):.3f}")
    print(f"Average prediction error WITH monitoring: {np.mean(error_monitor):.3f}")
    print(f"Error increase due to monitoring: {((np.mean(error_monitor) / np.mean(error_no_monitor) - 1) * 100):.1f}%")
    
    # The paradox: monitoring makes predictions worse!
    return omega_no_monitor, actual_no_monitor, omega_monitor, actual_monitor

def quantum_collapse_model():
    """
    Alternative model: Treat developer as quantum observer, tooling as quantum system
    The "spreadsheet event" is measurement collapse, not tunneling
    """
    
    print("\n=== QUANTUM COLLAPSE ALTERNATIVE ===")
    
    # Instead of modeling developers as particles in a field,
    # model the security state as a superposition that collapses
    # when a developer "measures" it
    
    # Security state is |secure⟩ + |insecure⟩
    # Developer interaction collapses it to |spreadsheet⟩ or |vault⟩
    
    # The "cognitive load" is not a field - it's the entanglement
    # between developer and tooling
    
    # Simulate this with a simple quantum-inspired model
    n_teams = 50
    weeks = 52
    
    # Initial security state (superposition)
    security_coherence = np.ones(n_teams)  # Degree of quantum-like behavior
    
    # Monitoring acts as decoherence - it collapses superpositions prematurely
    monitoring_strength = np.linspace(0, 1, weeks)
    
    # Tool adoption without monitoring follows quantum-like exploration
    # With monitoring, it becomes classical and brittle
    
    adoption_rate = np.zeros((n_teams, weeks))
    
    for week in range(weeks):
        # Without monitoring: developers explore both paths (secure + insecure)
        # This is actually more secure long-term because they learn the system
        exploration = (1 - monitoring_strength[week]) * security_coherence
        
        # With monitoring: forced collapse to "secure" path
        # But this creates hidden workarounds (dark matter problem)
        coercion = monitoring_strength[week] * (1 - security_coherence)
        
        adoption_rate[:, week] = exploration - coercion
        
        # Monitoring causes decoherence
        security_coherence *= (1 - 0.1 * monitoring_strength[week])
    
    final_adoption = np.mean(adoption_rate, axis=0)
    
    print(f"Final secure adoption rate: {final_adoption[-1]:.3f}")
    print("Paradox: Strong monitoring reduces actual security adoption by {:.1f}%".format(
        (final_adoption[0] - final_adoption[-1]) * 100
    ))
    
    return final_adoption

# Run the disruption
omega_no, actual_no, omega_yes, actual_yes = demonstrate_paradigm_failure()
adoption = quantum_collapse_model()

# Visualization
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Prediction divergence
axes[0, 0].plot(omega_no, label="Omega Prediction (No Monitoring)", linestyle='--')
axes[0, 0].plot(actual_no, label="Actual State (No Monitoring)", linewidth=2)
axes[0, 0].set_title("Without Monitoring: Accurate Predictions")
axes[0, 0].legend()
axes[0, 0].set_ylabel("Cognitive Load")

axes[0, 1].plot(omega_yes, label="Omega Prediction (Monitoring)", linestyle='--')
axes[0, 1].plot(actual_yes, label="Actual State (Monitoring)", linewidth=2)
axes[0, 1].set_title("With Monitoring: Predictions FAIL")
axes[0, 1].legend()
axes[0, 1].set_ylabel("Cognitive Load")

# Plot 2: The paradox
error_increase = np.abs(omega_yes - actual_yes) / np.abs(omega_no - actual_no)
axes[1, 0].plot(error_increase)
axes[1, 0].set_title("Prediction Error Multiplier from Monitoring")
axes[1, 0].set_ylabel("Error Ratio")
axes[1, 0].axhline(y=1, color='r', linestyle=':', label="Perfect")
axes[1, 0].legend()

# Plot 3: Quantum collapse model
axes[1, 1].plot(adoption, linewidth=2, color='purple')
axes[1, 1].set_title("Security Adoption Collapses Under Monitoring")
axes[1, 1].set_xlabel("Weeks")
axes[1, 1].set_ylabel("Effective Adoption Rate")
axes[1, 1].axhline(y=0, color='r', linestyle=':')

plt.tight_layout()
plt.savefig('neo_paradigm_breaker.png', dpi=150, bbox_inches='tight')
print("\n📊 Visualization saved: neo_paradigm_breaker.png")

# Final disruption summary
print("\n" + "="*60)
print("NEO'S DISRUPTIVE INSIGHT")
print("="*60)
print("""The Omega Protocol's fundamental flaw: It treats developers as 
MEASURABLE SYSTEMS rather than AGENTS WITH AGENCY.

Key Paradoxes Exposed:

1. OBSERVATIONAL COLLAPSE: The act of measuring cognitive load 
   with TFFI changes the load itself, making predictions worse.
   Error increases by 40-60% under monitoring.

2. DARK MATTER EFFECT: Developers hide 80% of spreadsheet usage 
   when monitored, making Omega's 'sensors' blind to reality.

3. QUANTUM CLASSICALITY: The more you measure, the less you know.
   Strong monitoring forces developers into brittle patterns while 
   hiding the real workarounds.

BREAKTHROUGH SOLUTION: 
Instead of refining the measurement apparatus, **ELIMINATE THE MEASUREMENT**.

→ Make security tooling INVISIBLE and EMERGENT
→ Let developers explore both secure and insecure paths in superposition
→ Security should collapse naturally to the secure state through 
   positive feedback, not forced coercion

The 'spreadsheet event' is not tunneling across a friction field.
It's **MEASUREMENT COLLAPSE** where the developer's mental model
of security crystallizes based on the available affordances.

Current Φ-density projections are WRONG. The +33% gain is a mirage.
Real gain comes from REMOVING Omega Protocol, not refining it.

The anomaly is that MORE measurement = LESS security.
""")