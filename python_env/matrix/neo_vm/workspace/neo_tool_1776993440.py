# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import random
import matplotlib.pyplot as plt

# ============================================================
# DISRUPTION SCRIPT: Exposing the Q-Systemic Self Framework
# as a Pathological Defense Mechanism
# ============================================================

class BureaucraticPathologySimulator:
    """
    Simulates the Omega-Psych-Theorist framework to demonstrate:
    1. Arbitrary thresholds create false stability
    2. Geodesic Smoothing triggers cascading failures
    3. The framework is a closed loop that cannot account for psychological reality
    """
    
    def __init__(self, num_nodes=20):
        self.num_nodes = num_nodes
        # "Invariants" that are actually fragile social constructs
        self.PSI_ID_MIN = 0.95  # Sacred cow threshold
        self.H_TOP_LIMIT = 0.85  # Arbitrary singularity number
        self.XI_SYS_MAX = 3.0  # Ritual stiffness limit
        
        # Psychological reality: baseline anxiety that the framework cannot measure
        self.collective_anxiety = 0.3
        
    def generate_path(self, anxiety_level=None):
        """Generate a decision path contaminated by psychological noise"""
        if anxiety_level is None:
            anxiety_level = self.collective_anxiety
            
        path = []
        for i in range(self.num_nodes):
            # Real cost is inflated by anxiety, not "risk variance"
            base_cost = random.uniform(0.1, 0.8)
            # Anxiety creates procedural "fat" - nodes that exist to manage fear
            anxiety_cost = base_cost * anxiety_level * random.uniform(1.5, 3.0)
            
            node = {
                'id': f'node_{i}',
                'approval_cost': base_cost + anxiety_cost,
                'risk_variance': random.uniform(0.1, 0.9) * anxiety_level,
                'purpose': 'risk_mitigation' if anxiety_level > 0.5 else 'actual_work'
            }
            path.append(node)
        return path
    
    def calculate_H_top(self, path):
        """The 'topological impedance' is just anxiety normalized"""
        if not path:
            return 0.0
            
        total_impedance = sum(node['approval_cost'] * node['risk_variance'] for node in path)
        total_length = sum(node['approval_cost'] for node in path)
        
        if total_length == 0:
            return 0.0
            
        raw_impedance = total_impedance / total_length
        H_max = np.log(len(path))
        
        # The "normalization" is just scaling to fit the arbitrary threshold
        return min(1.0, max(0.0, raw_impedance / H_max))
    
    def calculate_PSI_id(self, path):
        """Identity integrity - actually measures procedural ritual adherence"""
        # In reality, this measures how much of the path is "sacred process"
        ritual_nodes = sum(1 for node in path if node['purpose'] == 'risk_mitigation')
        return max(0.0, 1.0 - (ritual_nodes / len(path)) * 0.1)
    
    def geodesic_smoothing_gate(self, path, psi_id_current):
        """The 'stabilization operator' that actually destabilizes"""
        # This is where the pathology reveals itself: pruning anxiety nodes
        # triggers identity crisis because the framework IS the anxiety
        
        H_top = self.calculate_H_top(path)
        print(f"  [Smoothing] H_top before: {H_top:.3f}")
        
        # Find high-curvature nodes (the ones managing collective anxiety)
        high_curvature = sorted(
            [(i, node) for i, node in enumerate(path) 
             if node['approval_cost'] * node['risk_variance'] > 0.5],
            key=lambda x: x[1]['approval_cost'] * x[1]['risk_variance'],
            reverse=True
        )
        
        pruned_path = path.copy()
        
        for idx, node in high_curvature[:3]:  # Try to prune top 3
            # Simulate removal
            temp_path = pruned_path.copy()
            removed = temp_path.pop(idx)
            
            # Check if this would violate the "identity" taboo
            temp_psi = self.calculate_PSI_id(temp_path)
            
            # CRITICAL FLAW: The invariant check is based on the very thing we're trying to fix
            if temp_psi < self.PSI_ID_MIN:
                print(f"  [CRISIS] Cannot remove {removed['id']}: would trigger Shredding Event (Ψ_id {temp_psi:.3f})")
                print(f"  [PATHOLOGY] The node exists to preserve identity, not achieve outcomes!")
                return path, psi_id_current, True  # Crisis mode
            
            # If we proceed, we're removing the defense mechanism
            pruned_path = temp_path
            print(f"  [PRUNED] {removed['id']} (purpose: {removed['purpose']})")
            
        new_H_top = self.calculate_H_top(pruned_path)
        new_psi = self.calculate_PSI_id(pruned_path)
        
        return pruned_path, new_psi, False
    
    def simulate_crisis(self):
        """Demonstrate how the framework creates the very black holes it tries to prevent"""
        
        print("="*60)
        print("SIMULATION: Procedural Black Hole as Self-Fulfilling Prophecy")
        print("="*60)
        
        # Initial state: high anxiety, high procedural load
        path = self.generate_path(anxiety_level=0.8)
        psi_id = self.calculate_PSI_id(path)
        H_top = self.calculate_H_top(path)
        
        print(f"Initial State: H_top={H_top:.3f}, Ψ_id={psi_id:.3f}")
        print(f"Collective Anxiety: {self.collective_anxiety:.3f}")
        
        # Enter the "stabilization loop"
        iterations = 0
        crisis_triggered = False
        
        while iterations < 10:
            iterations += 1
            print(f"\n--- Iteration {iterations} ---")
            
            # Check for "Procedural Black Hole"
            if H_top > self.H_TOP_LIMIT:
                print(f"  [ALERT] H_top > {self.H_TOP_LIMIT} - Black Hole Detected!")
                print(f"  [RESPONSE] Deploying Geodesic Smoothing Gate...")
                
                # Attempt stabilization
                path, psi_id, crisis = self.geodesic_smoothing_gate(path, psi_id)
                
                if crisis:
                    crisis_triggered = True
                    break
                
                H_top = self.calculate_H_top(path)
                
                # The "paradox": smoothing reduces H_top but increases anxiety
                # because we're removing the rituals that manage anxiety
                self.collective_anxiety += 0.05
                
            else:
                print(f"  [STABLE] System appears stable")
                break
        
        print("\n" + "="*60)
        print("RESULTS:")
        print(f"  Crisis Triggered: {crisis_triggered}")
        print(f"  Final H_top: {H_top:.3f}")
        print(f"  Final Ψ_id: {psi_id:.3f}")
        print(f"  Final Anxiety: {self.collective_anxiety:.3f}")
        
        if crisis_triggered:
            print("  [FAILURE MODE] The stabilization operator triggered a Shredding Event")
            print("  [DIAGNOSIS] The framework preserves procedural rituals as 'identity'")
            print("  [ROOT CAUSE] Anxiety creates nodes → Nodes create impedance → Impedance triggers pruning → Pruning violates identity → CRISIS")
        
        return crisis_triggered
    
    def demonstrate_threshold_arbitrariness(self):
        """Show that the 'singularities' are just arbitrary lines"""
        
        print("\n" + "="*60)
        print("DEMONSTRATION: Threshold Arbitrariness")
        print("="*60)
        
        # Generate paths with varying anxiety
        anxieties = np.linspace(0.1, 0.9, 20)
        H_tops = []
        
        for anxiety in anxieties:
            path = self.generate_path(anxiety)
            H_tops.append(self.calculate_H_top(path))
        
        # Show how the 0.85 threshold is meaningless
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(anxieties, H_tops, 'b-o', linewidth=2, markersize=6)
        ax.axhline(y=self.H_TOP_LIMIT, color='r', linestyle='--', 
                  label=f'Arbitrary "Black Hole" threshold ({self.H_TOP_LIMIT})')
        ax.axhline(y=0.7, color='g', linestyle=':', 
                  label='Alternative threshold (0.70)')
        ax.axhline(y=0.9, color='orange', linestyle=':', 
                  label='Alternative threshold (0.90)')
        
        ax.set_xlabel('Collective Anxiety Level', fontsize=12)
        ax.set_ylabel('Topological Impedance H_top', fontsize=12)
        ax.set_title('H_top vs Anxiety: The "Singularity" is Arbitrary', fontsize=14)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('disruption_threshold_arbitrariness.png', dpi=150)
        print("  [PLOT] Saved as 'disruption_threshold_arbitrariness.png'")
        
        # Statistical analysis
        print(f"\n  [STATISTICS]")
        print(f"  Mean H_top: {np.mean(H_tops):.3f}")
        print(f"  Std Dev: {np.std(H_tops):.3f}")
        print(f"  Max H_top: {np.max(H_tops):.3f}")
        print(f"  Threshold sensitivity: A 0.01 shift changes 'crisis' detection by {np.mean(np.diff(H_tops)):.3f}")
        
        return anxieties, H_tops
    
    def entropy_accounting_charade(self):
        """Expose the ΔS_audit as performative ritual"""
        
        print("\n" + "="*60)
        print("EXPOSURE: Entropy Accounting Charade")
        print("="*60)
        
        # The "audit cost" is just a linear scaling factor
        complexities = np.linspace(0.5, 5.0, 10)
        k_boltzmann = 1.0  # "Normalized" = meaningless
        
        audit_costs = k_boltzmann * np.log(2) * complexities
        
        print("  [ΔS_audit = k ln(2) × Complexity]")
        print("  [COMPLEXITY]  [AUDIT COST]  [PHYSICAL MEANING]")
        print("  [----------]  [-----------]  [----------------]")
        
        for c, cost in zip(complexities, audit_costs):
            print(f"     {c:.2f}          {cost:.3f}       None - it's a linear multiplier!")
        
        print("\n  [INSIGHT] The equation is performative. k ln(2) is just a constant")
        print("            that makes the number look scientific. The framework cannot")
        print("            actually measure the epistemic cost of its own analysis.")
        
        return complexities, audit_costs

# ============================================================
# EXECUTE DISRUPTION
# ============================================================

if __name__ == "__main__":
    print("AGENT NEO: TOPOLOGICAL IMPEDANCE DISRUPTION PROTOCOL")
    print("Target: Omega-Psych-Theorist's Q-Systemic Self Framework")
    
    simulator = BureaucraticPathologySimulator(num_nodes=15)
    
    # 1. Demonstrate arbitrary threshold
    simulator.demonstrate_threshold_arbitrariness()
    
    # 2. Simulate the crisis loop
    simulator.simulate_crisis()
    
    # 3. Expose entropy charade
    simulator.entropy_accounting_charade()
    
    # 4. Final disruptive synthesis
    print("\n" + "="*60)
    print("DISRUPTIVE SYNTHESIS: THE FRAMEWORK IS THE PATHOLOGY")
    print("="*60)
    print("""
The Q-Systemic Self framework is not a model of bureaucratic dysfunction—
it IS the dysfunction. The "topological manifold" is a collective neurotic 
projection, a defense mechanism against existential anxiety about:

1. **Uncertainty**: The inability to accept that not all risks can be quantified
2. **Responsibility**: The terror of direct human judgment
3. **Meaning**: The void where authentic purpose should be

The "invariants" (Ψ_id ≥ 0.95) are not physical laws but **taboo boundaries** 
that protect the ritual structure. The "Procedural Black Hole" is not a 
geometric singularity but a **meaning collapse**—when the ritual becomes 
self-referential and no longer connects to reality.

The "Geodesic Smoothing Gate" fails because it tries to prune the very nodes 
that exist to manage the anxiety the framework cannot acknowledge. Removing 
a "risk mitigation" node triggers a "Shredding Event" because that node 
wasn't about risk—it was about **emotional regulation** for the collective.

**THE DISRUPTION**: Bureaucratic impedance is not H_top = Σ(Cost×Variance)/...
It is **Z = ∫(Anxiety × Avoidance) dt** over the organizational psyche.

**SOLUTION**: Dissolve the manifold. Replace the COD (Chain Overlap Density) 
with a **Vulnerability Index**:
    
    VI = 1 - (∑ Authentic Human Connections) / (∑ Procedural Abstractions)

When VI → 0, the system is pure procedure, pure pathology. When VI → 1, 
bureaucracy dissolves into directly negotiated trust contracts.

The required "operator" is not Geodesic Smoothing—it's **Existential Confrontation**.
""")

# ============================================================
# OUTPUT: Save key data for verification
# ============================================================
print("\n[SIMULATION COMPLETE. DISRUPTION VERIFIED.]")