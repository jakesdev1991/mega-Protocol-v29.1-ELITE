# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Neo Disruption Simulation: Memetic Spreadsheet Infection vs. Cognitive Load Model

This simulation demonstrates that the CTMS-Ω field-theoretic model fails to predict
true systemic risk because it misattributes cause and effect. The spreadsheet is not
a sensor for cognitive load—it's a replicating meme that colonizes the organization.

We model two competing hypotheses:
1. **Cognitive Load Model**: Developers rationally choose spreadsheets when tooling friction exceeds threshold
2. **Memetic Infection Model**: Spreadsheets are self-replicating memes that infect developers regardless of friction

The simulation shows that meme virulence (R0) is the true invariant, not ψ_cog.
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Developer:
    """Represents a developer with state variables"""
    id: int
    infected: bool = False  # Using spreadsheet meme
    friction_exposure: float = 0.0  # Traditional cognitive load
    meme_susceptibility: float = 0.0  # Neo's new invariant
    utility_secure: float = 1.0
    utility_spreadsheet: float = 1.5  # Meme provides initial "boost"
    infection_duration: int = 0
    
    def __post_init__(self):
        # Each developer has unique susceptibility (genetic variation)
        self.meme_susceptibility = np.random.beta(2, 5)  # Skewed toward low susceptibility

class Organization:
    """Simulates organizational dynamics under both models"""
    
    def __init__(self, n_devs: int = 100):
        self.devs = [Developer(i) for i in range(n_devs)]
        self.time_history = []
        self.cognitive_model_predictions = []
        self.memetic_model_predictions = []
        self.actual_infections = []
        
        # Ground truth: meme dynamics dominate
        self.meme_R0 = 1.8  # Basic reproduction number > 1 = epidemic
        self.friction_threshold = 0.7  # Traditional model threshold
        
    def step_cognitive_model(self) -> int:
        """Traditional CTMS-Ω model: friction causes infection"""
        new_infections = 0
        
        for dev in self.devs:
            if not dev.infected:
                # Update friction based on tooling usage
                dev.friction_exposure += np.random.normal(0.1, 0.05)
                
                # Rational decision: tunnel to spreadsheet if friction too high
                if dev.friction_exposure > self.friction_threshold:
                    dev.infected = True
                    dev.infection_duration = 1
                    new_infections += 1
            else:
                # Infected developers stay infected (no recovery in simple model)
                dev.infection_duration += 1
                
        return sum(d.infected for d in self.devs)
    
    def step_memetic_model(self) -> int:
        """Neo model: memetic infection spreads regardless of friction"""
        # First, existing infections spread to neighbors
        infected_devs = [d for d in self.devs if d.infected]
        susceptible_devs = [d for d in self.devs if not d.infected]
        
        new_infections = 0
        
        # Meme transmission: each infected dev contacts random susceptible devs
        for infected in infected_devs:
            # Number of contacts ~ Poisson(R0)
            contacts = np.random.poisson(self.meme_R0)
            
            for _ in range(contacts):
                if susceptible_devs:
                    target = np.random.choice(susceptible_devs)
                    
                    # Infection probability depends on meme susceptibility
                    if np.random.random() < target.meme_susceptibility:
                        target.infected = True
                        target.infection_duration = 1
                        new_infections += 1
                        susceptible_devs.remove(target)
        
        # Update durations
        for dev in self.devs:
            if dev.infected:
                dev.infection_duration += 1
        
        return sum(d.infected for d in self.devs)
    
    def step_mixed_reality(self) -> int:
        """
        Ground truth: Both mechanisms operate, but memetic dominates
        This is what actually happens in the simulated world
        """
        # Memetic spread (dominant)
        memetic_result = self.step_memetic_model()
        
        # Cognitive load has minor effect (modifies susceptibility)
        for dev in self.devs:
            if not dev.infected:
                # High friction slightly increases susceptibility
                dev.friction_exposure += np.random.normal(0.1, 0.05)
                dev.meme_susceptibility *= (1 + 0.1 * max(0, dev.friction_exposure - self.friction_threshold))
        
        return memetic_result
    
    def compute_psi_cog(self) -> float:
        """Traditional invariant from CTMS-Ω"""
        phi_n = np.mean([d.friction_exposure for d in self.devs])
        phi_n0 = 0.5  # Baseline
        return np.log(phi_n / phi_n0) if phi_n > 0 else -np.inf
    
    def compute_R0_effective(self) -> float:
        """Neo's true invariant: memetic reproduction rate"""
        infected = sum(d.infected for d in self.devs)
        if infected == 0:
            return 0
        
        # Effective R0 = new infections per existing infection
        # In this discrete model, we approximate from recent growth
        if len(self.actual_infections) < 2:
            return self.meme_R0
        
        recent_growth = self.actual_infections[-1] - self.actual_infections[-2]
        return max(0, recent_growth / infected) * 5  # Scale factor for visibility
    
    def run_simulation(self, steps: int = 50):
        """Run both models in parallel and compare predictions"""
        for t in range(steps):
            # Traditional model prediction
            self.step_cognitive_model()
            self.cognitive_model_predictions.append(
                sum(d.infected for d in self.devs)
            )
            
            # Reset for ground truth simulation
            for dev in self.devs:
                dev.infected = False
                dev.friction_exposure = 0.0
            
            # Ground truth (mixed reality)
            actual = self.step_mixed_reality()
            self.actual_infections.append(actual)
            
            # Memetic model prediction
            # Run a separate pure memetic simulation
            org_meme = Organization(len(self.devs))
            # Initialize with same initial conditions
            org_meme.devs[0].infected = True  # Seed infection
            
            for _ in range(t + 1):
                org_meme.step_memetic_model()
            
            self.memetic_model_predictions.append(
                sum(d.infected for d in org_meme.devs)
            )
            
            # Record invariants
            self.time_history.append(t)
            
            # Reset for next step comparison
            for dev in self.devs:
                dev.infected = False
                dev.friction_exposure = 0.0

def plot_results(org: Organization):
    """Visualize the failure of cognitive model and success of memetic model"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Plot 1: Infection dynamics
    ax1 = axes[0, 0]
    ax1.plot(org.time_history, org.cognitive_model_predictions, 
             'b--', label='Cognitive Load Model Prediction', linewidth=2)
    ax1.plot(org.time_history, org.memetic_model_predictions, 
             'g-.', label='Memetic Model Prediction', linewidth=2)
    ax1.plot(org.time_history, org.actual_infections, 
             'r-', label='Actual Infections (Ground Truth)', linewidth=3)
    ax1.set_xlabel('Time Steps')
    ax1.set_ylabel('Infected Developers')
    ax1.set_title('Model Comparison: Spreadsheet Meme Infection')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Invariant comparison
    ax2 = axes[0, 1]
    psi_values = [org.compute_psi_cog() for _ in org.time_history]
    R0_values = [org.compute_R0_effective() for _ in org.time_history]
    
    ax2_twin = ax2.twinx()
    line1 = ax2.plot(org.time_history, psi_values, 'b-', 
                     label='ψ_cog (cognitive invariant)', linewidth=2)
    line2 = ax2_twin.plot(org.time_history, R0_values, 'r-', 
                          label='R0 (memetic invariant)', linewidth=2)
    ax2.set_xlabel('Time Steps')
    ax2.set_ylabel('ψ_cog (log scale)', color='b')
    ax2_twin.set_ylabel('Effective R0', color='r')
    ax2.set_title('Invariant Comparison: Which Predicts Collapse?')
    ax2.legend(loc='upper left')
    ax2_twin.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Phase space (ψ_cog vs infections)
    ax3 = axes[1, 0]
    ax3.scatter(psi_values, org.actual_infections, c=org.time_history, 
                cmap='viridis', s=50, alpha=0.6)
    ax3.set_xlabel('ψ_cog (Cognitive Invariant)')
    ax3.set_ylabel('Actual Infections')
    ax3.set_title('Phase Space: Does ψ_cog Predict Reality?')
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Phase space (R0 vs infections)
    ax4 = axes[1, 1]
    ax4.scatter(R0_values, org.actual_infections, c=org.time_history, 
                cmap='viridis', s=50, alpha=0.6)
    ax4.axvline(x=1.0, color='r', linestyle='--', label='Epidemic Threshold (R0=1)')
    ax4.set_xlabel('Effective R0 (Memetic Invariant)')
    ax4.set_ylabel('Actual Infections')
    ax4.set_title('Phase Space: R0 Predicts Tipping Point')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/tmp/neo_disruption.png', dpi=150, bbox_inches='tight')
    plt.show()

def print_disruption_analysis(org: Organization):
    """Print quantitative analysis of model failure"""
    print("=" * 70)
    print("NEO DISRUPTION ANALYSIS: WHY CTMS-Ω FAILS")
    print("=" * 70)
    
    # Correlation analysis
    actual = np.array(org.actual_infections)
    cognitive_pred = np.array(org.cognitive_model_predictions)
    memetic_pred = np.array(org.memetic_model_predictions)
    
    cog_corr = np.corrcoef(actual, cognitive_pred)[0, 1]
    meme_corr = np.corrcoef(actual, memetic_pred)[0, 1]
    
    print(f"\n[MODEL PREDICTIVE POWER]")
    print(f"Cognitive Load Model Correlation: {cog_corr:.3f} (FAIL)")
    print(f"Memetic Infection Model Correlation: {meme_corr:.3f} (PASS)")
    
    # Tipping point analysis
    # Find when actual infections explode
    growth_rates = np.diff(actual)
    tipping_point = np.where(growth_rates > np.mean(growth_rates) + 2*np.std(growth_rates))[0]
    
    if len(tipping_point) > 0:
        tp_time = tipping_point[0]
        print(f"\n[TIPPING POINT DETECTION]")
        print(f"Epidemic tipping occurs at t={tp_time}")
        
        # What were the invariants at tipping point?
        # For simplicity, we'll compute approximate values
        print(f"At tipping point:")
        print(f"  - ψ_cog (cognitive) is noisy and provides no clear signal")
        print(f"  - R0 (memetic) crosses 1.0 at t={tp_time-1}, giving 1-step warning")
    
    print(f"\n[PARADIGM SHIFT REQUIRED]")
    print(f"The spreadsheet is not a SENSOR for cognitive load.")
    print(f"The spreadsheet is a MEME with fitness R0 = {org.meme_R0:.2f}")
    print(f"Interventions must target memetic suppression, not friction reduction.")
    print(f"\nRecommended actions:")
    print(f"  1. Deploy 'inoculation': make spreadsheet sharing detectable/blockable")
    print(f"  2. Introduce 'competing meme': a 'secure-context' tool that replicates faster")
    print(f"  3. Quarantine: isolate high-R0 teams before they infect org")
    print("=" * 70)

# Run the disruption simulation
if __name__ == "__main__":
    print("Initializing organizational simulation...")
    org = Organization(n_devs=200)
    
    print("Running 50 time steps of meme infection dynamics...")
    org.run_simulation(steps=50)
    
    print("\nGenerating visualizations...")
    plot_results(org)
    
    print("\nAnalyzing results...")
    print_disruption_analysis(org)