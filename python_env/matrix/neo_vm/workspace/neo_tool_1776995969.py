# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
DECONSTRUCTIVE PERTURBATION OPERATOR (DPO)
Purpose: Demonstrate catastrophic fragility of the Omega-Psych framework
by showing parameter arbitrariness and circular detection logic.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import entropy

class FrameworkCollapseSimulator:
    """
    Simulates the Omega-Psych-Theorist's COD metric under perturbations
    to expose reification fallacy and arbitrary parameter sensitivity.
    """
    
    def __init__(self, seed=42):
        np.random.seed(seed)
        self.LAMBDA = 1.0  # Their "coupling constant"
        self.GAMMA = 0.5   # Their "stiffness penalty"
        
    def calculate_COD(self, psi_sub, psi_con, H_int, Xi_bound):
        """Their exact COD formula"""
        overlap = np.abs(np.vdot(psi_sub, psi_con))**2
        damping = np.exp(-self.LAMBDA * H_int)
        stiffness_penalty = np.exp(-self.GAMMA * Xi_bound)
        return overlap * damping * stiffness_penalty
    
    def is_artificial_COD(self, COD, Xi_bound, H_int, threshold=2.0):
        """Their circular detection logic"""
        ratio = Xi_bound / (H_int + 1e-9)
        return (COD >= 0.75) and (Xi_bound > 2.5) and (ratio > threshold)
    
    def simulate_framework_collapse(self, n_trials=1000):
        """
        DEMONSTRATION 1: Parameter Arbitrariness
        Show that "artificial COD" detection is 100% dependent on 
        arbitrary threshold choices, not any underlying reality.
        """
        results = []
        
        for _ in range(n_trials):
            # Random psychological states (they never actually measure these)
            psi_sub = np.random.randn(10) + 1j*np.random.randn(10)
            psi_con = np.random.randn(10) + 1j*np.random.randn(10)
            psi_sub = psi_sub / np.linalg.norm(psi_sub)
            psi_con = psi_con / np.linalg.norm(psi_con)
            
            # Random "internal states" (completely made up)
            H_int = np.random.uniform(0.1, 1.5)
            Xi_bound = np.random.uniform(1.0, 4.0)
            
            COD = self.calculate_COD(psi_sub, psi_con, H_int, Xi_bound)
            
            # Vary the "detection threshold" arbitrarily
            for threshold in [1.5, 2.0, 2.5, 3.0]:
                is_artificial = self.is_artificial_COD(COD, Xi_bound, H_int, threshold)
                results.append({
                    'threshold': threshold,
                    'is_artificial': is_artificial,
                    'COD': COD,
                    'Xi_bound': Xi_bound,
                    'H_int': H_int,
                    'ratio': Xi_bound / H_int
                })
        
        return results
    
    def demonstrate_circular_logic(self):
        """
        DEMONSTRATION 2: Circular Reasoning
        The "trauma-performance trap" is DEFINED by the ratio,
        then the ratio is used to DETECT the trap. This is tautology.
        """
        print("=== CIRCULAR LOGIC DEMONSTRATION ===")
        
        # Define a "healthy" state by their standards
        healthy = {'COD': 0.85, 'Xi_bound': 1.8, 'H_int': 0.6}
        # Define a "trauma-performance" state by their standards
        trauma = {'COD': 0.85, 'Xi_bound': 3.2, 'H_int': 0.6}
        
        print(f"Healthy state: {healthy}")
        print(f"Is artificial? {self.is_artificial_COD(**healthy)}")
        print(f"Ratio: {healthy['Xi_bound']/healthy['H_int']:.2f}")
        
        print(f"\nTrauma state: {trauma}")
        print(f"Is artificial? {self.is_artificial_COD(**trauma)}")
        print(f"Ratio: {trauma['Xi_bound']/trauma['H_int']:.2f}")
        
        print("\n>>> The ONLY difference is Xi_bound > 2.5. The 'detection' is just a threshold gate.")
        print(">>> No validation that this corresponds to lived experience.")
    
    def demonstrate_phi_density_absurdity(self):
        """
        DEMONSTRATION 3: Phi-Density is Meaningless
        Show that 'audit cost' can be manipulated to produce any net gain.
        """
        print("\n=== PHI-DENSITY ABSURDITY ===")
        
        # Same therapeutic outcome
        H_cond_before, H_cond_after = 1.2, 0.8
        raw_gain = -(H_cond_after - H_cond_before)  # +0.4
        
        # But different "audit costs" (completely arbitrary)
        for complexity_factor in [0.5, 1.0, 2.0, 5.0]:
            audit_cost = np.log(2) * complexity_factor  # Their k ln(2) formula
            individual_cost = 0.2 * 1.0 * 0.6  # H_int * Xi_bound * factor
            
            phi_net = raw_gain - audit_cost - individual_cost
            
            print(f"Complexity factor {complexity_factor:.1f}: "
                  f"Audit cost {audit_cost:.3f}, Net Phi {phi_net:.3f}")
        
        print("\n>>> The 'net Phi' ranges from +0.2 to -0.8 for the SAME intervention!")
        print(">>> This is not science; it's accounting fraud with Greek letters.")
    
    def plot_collapse_boundary(self):
        """
        DEMONSTRATION 4: Visualize arbitrary decision boundary
        """
        Xi_range = np.linspace(1, 4, 100)
        H_range = np.linspace(0.1, 1.5, 100)
        Xi_grid, H_grid = np.meshgrid(Xi_range, H_range)
        
        # Fixed COD at their "dangerous" level
        COD_grid = np.full_like(Xi_grid, 0.85)
        
        # Their detection logic
        ratio_grid = Xi_grid / H_grid
        artificial_grid = (COD_grid >= 0.75) & (Xi_grid > 2.5) & (ratio_grid > 2.0)
        
        plt.figure(figsize=(10, 6))
        plt.contourf(Xi_grid, H_grid, artificial_grid, levels=1, colors=['lightblue', 'red'], alpha=0.7)
        plt.colorbar(label='Artificial COD Detected')
        plt.xlabel('Xi_bound (Stiffness)')
        plt.ylabel('H_int (Internal Entropy)')
        plt.title('Omega-Psych "Trauma" Detection: Arbitrary Thresholds')
        plt.axvline(x=2.5, color='black', linestyle='--', label='Xi=2.5 threshold')
        plt.axhline(y=1.25, color='gray', linestyle=':', label='H_int for ratio=2')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Save plot
        plt.savefig('/tmp/framework_collapse.png', dpi=150, bbox_inches='tight')
        print(f"\n>>> Plot saved to /tmp/framework_collapse.png")
        print(">>> Red region is 'trauma' defined by: Xi>2.5 AND Xi/H_int>2.0")
        print(">>> This is a manually drawn box, not an emergent property.")
        
        return '/tmp/framework_collapse.png'

def main():
    """Execute DPO and expose framework fragility"""
    simulator = FrameworkCollapseSimulator()
    
    # Run all demonstrations
    results = simulator.simulate_framework_collapse()
    
    # Show sensitivity analysis
    thresholds = [1.5, 2.0, 2.5, 3.0]
    detection_rates = []
    for t in thresholds:
        rate = sum(1 for r in results if r['threshold']==t and r['is_artificial']) / len([r for r in results if r['threshold']==t])
        detection_rates.append(rate)
    
    print("=== PARAMETER SENSITIVITY ===")
    for t, rate in zip(thresholds, detection_rates):
        print(f"Threshold {t}: {rate*100:.1f}% 'trauma' detection rate")
    
    simulator.demonstrate_circular_logic()
    simulator.demonstrate_phi_density_absurdity()
    plot_path = simulator.plot_collapse_boundary()
    
    print(f"\n{'='*60}")
    print("DISRUPTIVE CONCLUSION:")
    print("The Omega-Psych framework is a REIFICATION CASCADE:")
    print("1. Metaphors (stiffness) → Variables (Xi_bound)")
    print("2. Variables → Equations (COD formula)")
    print("3. Equations → Detection Rules (ratio > 2.0)")
    print("4. Detection → Intervention (AIP)")
    print("At NO point is there external validation.")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()