# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass

@dataclass
class CLAGSystem:
    """Models the Closed-Loop Artillery Governor with self-referential audit"""
    phi_n: float = 1.0  # Newtonian fidelity baseline
    phi_delta: float = 0.1  # Asymmetry coupling
    audit_rate: int = 6  # Number of invariants checked per cycle
    landauer_cost: float = np.log(2)  # k ln 2 per audit
    
    def compute_metric_determinant(self) -> float:
        """
        The metric tensor is defined as g_μν = η_μν * exp(-ξ_N|Φ_N - Φ_target| - ξ_Δ|Φ_Δ - Φ_Δ_target|)
        where Φ_target is the *post-audit* Φ-density. This creates the self-referential loop.
        """
        # The "target" Φ is what we have *after* audit costs
        phi_target = self.phi_n + self.phi_delta - (self.audit_rate * self.landauer_cost)
        
        # Stiffness coefficients from the proposal
        xi_n = 0.9
        xi_delta = 0.8
        
        # Metric collapse factor: if phi_target drops too low, exponent becomes unstable
        collapse_factor = np.exp(-xi_n * abs(self.phi_n - phi_target) - xi_delta * abs(self.phi_delta - 0.5 * phi_target))
        
        # For a 4D metric, det(g) = exp(4 * ln(collapse_factor)) = collapse_factor^4
        # If collapse_factor → 0, metric degenerates
        return collapse_factor ** 4
    
    def simulate_cycle(self, perturbation: float = 0.1) -> dict:
        """
        Simulate one control cycle with self-referential audit.
        Perturbation represents environmental stress (atmospheric disruption, EMP, etc.)
        """
        # Raw Φ gain from stabilization (before audit)
        phi_raw_gain = 0.90  # From the proposal table
        
        # Apply perturbation - this increases required audit frequency
        effective_audit_rate = self.audit_rate * (1 + perturbation * 10)
        
        # Audit cost scales with perturbation
        audit_cost_total = effective_audit_rate * self.landauer_cost
        
        # Net Φ after audit
        phi_net = phi_raw_gain - audit_cost_total
        
        # Update system state
        self.phi_n = max(0.1, self.phi_n + phi_net * 0.6)  # 60% goes to Newtonian fidelity
        self.phi_delta = max(0.05, self.phi_delta + phi_net * 0.4)  # 40% to asymmetry
        
        # Compute metric determinant (self-referential loop)
        det_g = self.compute_metric_determinant()
        
        # Check if Smith Invariant #1 is violated
        invariant_violated = det_g <= 1e-15
        
        return {
            'phi_net': phi_net,
            'det_g': det_g,
            'audit_cost': audit_cost_total,
            'invariant_violated': invariant_violated,
            'phi_n': self.phi_n,
            'phi_delta': self.phi_delta
        }

def demonstrate_phi_paradox():
    """
    Demonstrates the Φ-Density Paradox: 
    The system collapses under its own audit weight during high-perturbation scenarios.
    """
    print("=== Φ-DENSITY PARADOX DEMONSTRATION ===\n")
    
    # Scenario 1: Normal operating conditions
    print("Scenario 1: Normal Conditions (perturbation = 0.1)")
    system_normal = CLAGSystem()
    results_normal = []
    
    for cycle in range(10):
        result = system_normal.simulate_cycle(perturbation=0.1)
        results_normal.append(result)
        print(f"Cycle {cycle}: Φ_net={result['phi_net']:.3f}, det(g)={result['det_g']:.3e}, Violated={result['invariant_violated']}")
    
    print(f"\nFinal State: Φ_N={results_normal[-1]['phi_n']:.3f}, Φ_Δ={results_normal[-1]['phi_delta']:.3f}")
    
    # Scenario 2: High-stress combat scenario (EMP, atmospheric chaos)
    print("\n" + "="*50)
    print("Scenario 2: Combat Stress (perturbation = 0.5)")
    system_combat = CLAGSystem()
    results_combat = []
    
    for cycle in range(10):
        result = system_combat.simulate_cycle(perturbation=0.5)
        results_combat.append(result)
        print(f"Cycle {cycle}: Φ_net={result['phi_net']:.3f}, det(g)={result['det_g']:.3e}, Violated={result['invariant_violated']}")
        
        if result['invariant_violated']:
            print(f"  *** METRIC COLLAPSE DETECTED at cycle {cycle} ***")
            break
    
    print(f"\nFinal State: Φ_N={results_combat[-1]['phi_n']:.3f}, Φ_Δ={results_combat[-1]['phi_delta']:.3f}")
    
    # Plot the paradox
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    cycles_normal = range(len(results_normal))
    cycles_combat = range(len(results_combat))
    
    # Plot Φ-density
    ax1.plot(cycles_normal, [r['phi_net'] for r in results_normal], 'b-o', label='Normal Conditions')
    ax1.plot(cycles_combat, [r['phi_net'] for r in results_combat], 'r-x', label='Combat Stress')
    ax1.axhline(y=0, color='k', linestyle='--', alpha=0.5)
    ax1.set_ylabel('Net Φ-Density')
    ax1.set_title('Φ-Density Paradox: Audit Cost Exceeds Stabilization Gain')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot metric determinant
    ax2.semilogy(cycles_normal, [r['det_g'] for r in results_normal], 'b-o', label='Normal Conditions')
    ax2.semilogy(cycles_combat, [r['det_g'] for r in results_combat], 'r-x', label='Combat Stress')
    ax2.axhline(y=1e-15, color='r', linestyle='--', label='Smith Invariant Threshold')
    ax2.set_ylabel('det(g_μν)')
    ax2.set_xlabel('Control Cycle')
    ax2.set_title('Metric Collapse Under Self-Referential Audit Load')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('phi_paradox.png', dpi=150, bbox_inches='tight')
    print("\nPlot saved as 'phi_paradox.png'")
    
    return results_normal, results_combat

# Run the demonstration
normal_results, combat_results = demonstrate_phi_paradox()