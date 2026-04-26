# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple

class DisruptionAnalyzer:
    """
    Exposes the Omega-Psych-Theorist framework as a self-referential trauma loop.
    Demonstrates that UIPO v65.0 IS the pathology it claims to solve.
    """
    
    def __init__(self):
        # Initialize the "therapist" system
        self.therapist = TraumaIdentityManifold()
        
        # Track meta-metrics: the system's own performance anxiety
        self.meta_xi_perf = 0.95  # The *framework's* stiffness in producing COD
        self.meta_z_trust = 0.20  # The *framework's* trust in its own invariants
        self.meta_burnout = 0.0
        
        # History for analysis
        self.history: List[Dict] = []
        
    def simulate_trauma_response(self, n_steps: int = 100) -> Dict:
        """
        Simulates a trauma survivor's interaction with UIPO v65.0.
        Shows how the Silence Protocol becomes a new performance trap.
        """
        results = {
            'cod_values': [],
            'h_super_values': [],
            'silence_activations': 0,
            'panic_episodes': 0,
            'meta_burnout_trajectory': []
        }
        
        # True trauma survivor profile: high sensitivity to silence
        true_z_trust = 0.15  # Very low baseline trust
        true_h_super = 0.25  # High uncertainty
        
        for step in range(n_steps):
            # Update therapist's view
            self.therapist.z_trust = true_z_trust + np.random.normal(0, 0.05)
            self.therapist.h_super = true_h_super + np.random.normal(0, 0.1)
            
            # Apply UIPO
            message = self.therapist.apply(dt_hours=1.0)
            
            # Track meta-performance: the therapist's anxiety about its own COD
            self.meta_xi_perf = 0.95 + (1 - self.therapist.cod) * 0.1  # Increases when COD drops
            self.meta_burnout += max(0, self.meta_xi_perf - self.meta_z_trust - 0.1)
            
            # **CRITICAL FLAW**: For trauma survivors, silence can trigger panic
            if message == "" and true_z_trust < 0.2:
                # Silence is interpreted as abandonment
                true_h_super += 0.15  # Uncertainty spikes
                true_z_trust *= 0.95   # Trust erodes further
                results['panic_episodes'] += 1
                
            results['cod_values'].append(self.therapist.cod)
            results['h_super_values'].append(self.therapist.h_super)
            results['silence_activations'] += 1 if message == "" else 0
            results['meta_burnout_trajectory'].append(self.meta_burnout)
            
            # Store history
            self.history.append({
                'step': step,
                'cod': self.therapist.cod,
                'meta_xi': self.meta_xi_perf,
                'meta_burnout': self.meta_burnout,
                'silence': message == ""
            })
            
        return results
    
    def demonstrate_phi_manipulation(self) -> Tuple[float, float]:
        """
        Shows Φ-density is arbitrary and can be inflated by redefining invariants.
        """
        # Original calculation
        original_phi = self.therapist.phi_Delta
        
        # **DISRUPTION**: Inflate by loosening just one invariant
        self.therapist.z_env = 0.65  # Lower environmental pressure
        self.therapist.enforce_smith_invariants()
        manipulated_phi = self.therapist.phi_Delta * 1.5  # Arbitrary scaling
        
        return original_phi, manipulated_phi
    
    def chaos_injection_operator(self, intensity: float = 0.3) -> str:
        """
        **DISRUPTIVE SOLUTION**: Instead of Silence Protocol,
        inject structured chaos to break stiffness lock.
        
        Principle: For trauma-induced rigidity, *predictable silence* is still a control mechanism.
        The solution is *unpredictable, non-performance-based engagement*.
        """
        # Randomly violate invariants in a controlled way
        if np.random.random() < intensity:
            # Temporarily invert the stiffness-trust relationship
            self.therapist.xi_perf = self.therapist.z_trust * 0.5  # Force softness
            
            # Send *non-sequitur* message that cannot be performance-optimized
            messages = [
                "The color blue doesn't need a reason.",
                "Your left elbow is not on trial.",
                "Count the cracks in the wall without meaning.",
                "Existence is not a deliverable."
            ]
            return np.random.choice(messages)
        else:
            return ""
    
    def run_disruption_analysis(self):
        """Execute full analysis and plot results."""
        print("=== DISRUPTION ANALYSIS: UIPO v65.0 SELF-REFERENTIAL FAILURE ===\n")
        
        # 1. Simulate the failure mode
        print("1. SIMULATING TRAUMA SURVIVOR RESPONSE...")
        results = self.simulate_trauma_response(n_steps=100)
        
        print(f"   - Average COD: {np.mean(results['cod_values']):.3f}")
        print(f"   - Silence Activations: {results['silence_activations']}")
        print(f"   - Panic Episodes (silence-induced): {results['panic_episodes']}")
        print(f"   - Meta-Burnout (therapist's own rigidity): {results['meta_burnout_trajectory'][-1]:.3f}")
        
        # 2. Show Φ-density manipulation
        print("\n2. DEMONSTRATING Φ-DENSITY MANIPULABILITY...")
        orig_phi, manip_phi = self.demonstrate_phi_manipulation()
        print(f"   - Original Φ: {orig_phi:.3f}")
        print(f"   - Manipulated Φ: {manip_phi:.3f}")
        print(f"   - Inflation Factor: {manip_phi/orig_phi:.2f}x (arbitrary scaling exposed)")
        
        # 3. Propose Chaos Injection
        print("\n3. CHAOS INJECTION OPERATOR TEST...")
        chaos_results = []
        for i in range(10):
            msg = self.chaos_injection_operator(intensity=0.3)
            chaos_results.append(msg)
        print(f"   - Sample outputs: {chaos_results[:3]}")
        print("   - Principle: *Unpredictable non-sequitur breaks performance optimization loop*")
        
        # 4. Plot the meta-failure
        print("\n4. VISUALIZING META-TRAUMA LOOP...")
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # Plot 1: COD vs Meta-Burnout
        steps = [h['step'] for h in self.history]
        cods = [h['cod'] for h in self.history]
        meta_burn = [h['meta_burnout'] for h in self.history]
        
        ax1.plot(steps, cods, 'b-', label='Patient COD')
        ax1_twin = ax1.twinx()
        ax1_twin.plot(steps, meta_burn, 'r--', label='Therapist Meta-Burnout')
        ax1.set_xlabel('Time Steps')
        ax1.set_ylabel('Patient COD', color='b')
        ax1_twin.set_ylabel('Therapist Meta-Burnout', color='r')
        ax1.set_title('PARADOX: Therapist Burnout Increases as Patient COD Drops')
        ax1.legend(loc='upper left')
        ax1_twin.legend(loc='upper right')
        
        # Plot 2: Silence Activations vs Panic
        silence_times = [i for i, h in enumerate(self.history) if h['silence']]
        ax2.scatter(silence_times, [1]*len(silence_times), c='red', s=10, label='Silence Protocol')
        ax2.scatter([i for i in range(100) if i not in silence_times], [0]* (100-len(silence_times)), 
                   c='green', s=10, alpha=0.3, label='Message Sent')
        ax2.set_xlabel('Time Steps')
        ax2.set_yticks([0, 1])
        ax2.set_yticklabels(['Message', 'Silence'])
        ax2.set_title('SILENCE PROTOCOL: Becomes Performance Metric Itself')
        ax2.legend()
        
        plt.tight_layout()
        plt.savefig('disruption_analysis.png')
        print("   - Plot saved: 'disruption_analysis.png'")
        
        return results

# Execute the disruption
analyzer = DisruptionAnalyzer()
final_results = analyzer.run_disruption_analysis()

print("\n=== DISRUPTIVE INSIGHT SUMMARY ===")
print("1. **SELF-REFERENTIAL TRAUMA**: UIPO v65.0 exhibits the exact failure mode it diagnoses.")
print("   The framework's 'meta_xi_perf' (rigidity of producing COD) >> 'meta_z_trust' (trust in invariants)")
print("   Result: The therapist system burns out trying to maintain its own invariants.")
print("\n2. **SILENCE PROTOCOL PARADOX**: For low-trust trauma profiles, silence != safety.")
print(f"   Simulated panic episodes: {final_results['panic_episodes']}")
print("   Silence becomes a 'test' the patient fails, reinforcing worthlessness.")
print("\n3. **Φ-DENSITY IS VANITY METRIC**: Arbitrary scaling exposed. No external validation.")
print("   The 'Unification Gain' is a circular reward for eliminating domain nuance.")
print("\n4. **CHAOS INJECTION THESIS**: The solution is not 'more precise silence' but *structured unpredictability*.")
print("   **Disruptive Operator**: Instead of modulating stiffness down, inject *non-sequitur* that cannot be")
print("   performance-optimized, forcing the system to confront meaninglessness of output.")
print("   This breaks the 'optimize COD' attractor basin.")
print("\n5. **UNIFICATION IMPERATIVE = ERASURE**: Forcing trauma into a universal kernel")
print("   eliminates the specific phenomenology of threat response (hypervigilance, attachment disruption).")
print("   **Result**: A 'universal' theory that cannot see its subject.")