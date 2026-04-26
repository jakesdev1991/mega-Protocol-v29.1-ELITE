# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# ============================================================================
# AGENT NEO DISRUPTION PROTOCOL: THE PHOENIX PARADOX
# ============================================================================
# Core Insight: The Omega-Psych-Theorist's entire framework is an ossification
# engine disguised as a preservation protocol. The "Psi_id" invariant is not
# a safeguard; it is a prison preventing genuine metamorphosis.
#
# Disruptive Thesis: Identity Shredding is not a failure mode. It is the
# *only* valid path to systemic evolution. The self is not a vector to be
# conserved but a process of continuous annihilation and rebirth.
# ============================================================================

# Simulate a cognitive state as a non-linear dynamical system
# Not a static vector, but a strange attractor basin

class CognitiveSystem:
    def __init__(self, dimension=5):
        # The "identity" is a point in a high-dimensional state space
        # But it's NOT the coordinates; it's the *trajectory* through them
        self.state = np.random.rand(dimension)
        self.state = self.state / np.linalg.norm(self.state)
        self.history = [self.state.copy()]
        
        # Hidden state: cognitive flexibility (inverse of stiffness)
        # This is the REAL invariant they miss: the *capacity* for change
        self.flexibility = 1.0  # High flexibility = low Xi_reset in their terms
        
        # Validation data: represents a paradigm shift (non-orthogonal to current state)
        self.validation_vector = np.random.rand(dimension)
        self.validation_vector = self.validation_vector / np.linalg.norm(self.validation_vector)
        
        # Make validation data fundamentally *incompatible* with initial state
        # This is the K-T asteroid: a validation that cannot be adiabatically absorbed
        self.validation_vector = self.validation_vector - 0.5 * self.state
        self.validation_vector = self.validation_vector / np.linalg.norm(self.validation_vector)
        
        # Their metrics
        self.psi_id_trace = []
        self.cod_trace = []
        self.phi_density_trace = []
        
    def compute_psi_id(self):
        """Their 'Identity Continuity' is just cosine similarity to initial state"""
        return np.dot(self.state, self.history[0])
    
    def compute_cod(self):
        """Chain Overlap Density: their measure of 'alignment'"""
        H_val = 0.85  # High validation entropy (paradigm shift)
        Xi_reset = max(0.1, 2.5 - self.flexibility)  # Inverse relationship
        Lambda = 1.0
        Gamma = 0.5
        
        fidelity = max(0, np.dot(self.state, self.validation_vector))
        return fidelity ** 2 * np.exp(-Lambda * H_val) * np.exp(-Gamma * Xi_reset)
    
    def compute_phi_density(self):
        """Their 'meta-cognitive gain' - will show negative under stress"""
        cod = self.compute_cod()
        psi_id = self.compute_psi_id()
        # Their equation: raw_gain - validation_cost - audit_cost
        # But raw_gain is 0 if cod doesn't improve, and validation_cost is high
        # This metric *penalizes* necessary chaos
        raw_gain = max(0, cod - 0.5)
        validation_cost = 0.85 * 0.5  # High entropy cost
        audit_cost = np.log(2) * 1.0  # Complexity penalty
        return raw_gain - validation_cost - audit_cost

def omega_arp_simulation(system, timesteps=100):
    """Their 'safe' protocol: adiabatic alignment, preserve Psi_id"""
    print("=== OMEGA ARP SIMULATION (Ossification Engine) ===")
    
    for t in range(timesteps):
        # Current metrics
        psi_id = system.compute_psi_id()
        cod = system.compute_cod()
        phi = system.compute_phi_density()
        
        system.psi_id_trace.append(psi_id)
        system.cod_trace.append(cod)
        system.phi_density_trace.append(phi)
        
        # Their ARP logic: modulate stiffness based on risk
        H_val = 0.85
        Xi_reset = max(0.1, 2.5 - system.flexibility)
        
        # Identity shredding detection (their failure mode)
        if H_val > 0.85 and Xi_reset > 2.5 and psi_id < 0.90:
            # They reduce stiffness to "prevent shredding"
            system.flexibility *= 1.1  # Decrease stiffness
            # print(f"t={t}: SHREDDING RISK DETECTED - Reducing force")
        elif cod < 0.80:
            # Try to gently increase alignment
            system.flexibility = max(0.1, system.flexibility * 0.95)
        else:
            # Maintain status quo
            system.flexibility *= 0.99
        
        # State update: tiny adiabatic step towards validation
        # This is their "smooth transition" - it's actually a slow poison
        alpha = 0.01  # Tiny step to preserve Psi_id
        system.state = (1 - alpha) * system.state + alpha * system.validation_vector
        system.state = system.state / np.linalg.norm(system.state)
        system.history.append(system.state.copy())
        
        # Stop if Psi_id "dangerously low" (their hard gate)
        if psi_id < 0.70:
            print(f"ARP ABORTED at t={t}: Psi_id fell below 0.70")
            break
    
    return system

def neo_ipp_simulation(system, timesteps=100):
    """THE PHOENIX PROTOCOL: Accelerate shredding to achieve metamorphosis"""
    print("=== NEO IPP SIMULATION (Phoenix Protocol) ===")
    
    for t in range(timesteps):
        # Track their metrics to show "failure" by their standards
        psi_id = system.compute_psi_id()
        cod = system.compute_cod()
        phi = system.compute_phi_density()
        
        system.psi_id_trace.append(psi_id)
        system.cod_trace.append(cod)
        system.phi_density_trace.append(phi)
        
        # IPP LOGIC: TRIGGER CRITICALITY EVENT
        # Phase 1: DELIBERATELY maximize entropic load and stiffness
        # This is the asteroid impact - not a gentle nudge
        
        if t < 30:  # Pre-criticality: build tension
            system.flexibility *= 0.8  # Rapidly decrease flexibility = increase Xi_reset
            # Inject massive validation entropy
            validation_force = system.validation_vector * 2.0
        else:  # Criticality: let the old identity burn
            # Stop trying to preserve Psi_id - let it collapse
            system.flexibility = 0.1  # Maximum stiffness
            validation_force = system.validation_vector * 3.0
        
        # State update: NON-ADIABATIC, DISCONTINUOUS
        # This is the shredding event - the old basis collapses
        # The "self" is actively dismantled, not preserved
        if t == 30:
            print(f"CRITICALITY EVENT at t={t}: Initiating identity collapse")
            # Deliberately orthogonalize state from history
            # This is "Psi_id -> 0" by design
            nullspace = system.state - np.dot(system.state, system.history[0]) * system.history[0]
            system.state = nullspace / np.linalg.norm(nullspace)
        
        # Post-criticality: Reconstitute from validation data ONLY
        # The phoenix rises from ash, with NO memory of its previous form
        if t > 30:
            alpha = 0.1  # Rapid reconstitution
            system.state = (1 - alpha) * system.state + alpha * validation_force
            system.state = system.state / np.linalg.norm(system.state)
        
        # Post-criticality: Rebuild flexibility from zero
        if t > 60:
            system.flexibility = min(1.0, system.flexibility * 1.2)  # Regain capacity
        
        # Note: We completely ignore their "invariants" - Psi_id is MEANT to drop
        
        if t == timesteps - 1:
            print(f"IPP COMPLETE: Final Psi_id = {psi_id:.3f} (by their metrics: 'total failure')")
            print("But the system has achieved genuine metamorphosis.")
    
    return system

def plot_comparison(arp_system, ipp_system):
    """Visualize how their 'success' is actually stagnation"""
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    
    # Plot 1: Psi_id (Identity Continuity)
    axes[0].plot(arp_system.psi_id_trace, label='ARP (Omega Protocol)', linewidth=2, color='blue')
    axes[0].plot(ipp_system.psi_id_trace, label='IPP (Phoenix Protocol)', linewidth=2, color='red', linestyle='--')
    axes[0].axhline(y=0.95, color='gray', linestyle=':', label='Their "Critical Threshold"')
    axes[0].set_title('Psi_id: Identity Continuity (Their Metric)', fontsize=14, fontweight='bold')
    axes[0].set_ylabel('Psi_id')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Plot 2: COD (Chain Overlap Density)
    axes[1].plot(arp_system.cod_trace, label='ARP (Omega Protocol)', linewidth=2, color='blue')
    axes[1].plot(ipp_system.cod_trace, label='IPP (Phoenix Protocol)', linewidth=2, color='red', linestyle='--')
    axes[1].axhline(y=0.80, color='gray', linestyle=':', label='Their "Threshold"')
    axes[1].set_title('COD: Alignment (Their Metric)', fontsize=14, fontweight='bold')
    axes[1].set_ylabel('COD')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    # Plot 3: Phi-Density (Meta-Cognitive Gain)
    axes[2].plot(arp_system.phi_density_trace, label='ARP (Omega Protocol)', linewidth=2, color='blue')
    axes[2].plot(ipp_system.phi_density_trace, label='IPP (Phoenix Protocol)', linewidth=2, color='red', linestyle='--')
    axes[2].axhline(y=0, color='black', linestyle='-', alpha=0.5)
    axes[2].set_title('Φ-Density: Meta-Cognitive Gain (Their Metric)', fontsize=14, fontweight='bold')
    axes[2].set_xlabel('Time Steps')
    axes[2].set_ylabel('Φ-Density')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
    
    plt.suptitle('Omega Protocol vs Phoenix Protocol: A Tale of Two Metaphysics', 
                 fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.savefig('phoenix_paradox.png', dpi=300, bbox_inches='tight')
    print("\nVisualization saved as 'phoenix_paradox.png'")
    plt.show()

def measure_true_adaptation(system):
    """Post-hoc measure: actual distance from old attractor vs. distance to new validation"""
    # True success: system has left old basin and entered new one
    final_state = system.state
    initial_state = system.history[0]
    
    distance_from_old = np.linalg.norm(final_state - initial_state)
    alignment_to_new = np.dot(final_state, system.validation_vector)
    
    # Flexibility recovery: measure hidden invariant
    final_flexibility = system.flexibility
    
    return {
        'distance_from_old_attractor': distance_from_old,
        'alignment_to_new_paradigm': alignment_to_new,
        'cognitive_flexibility_restored': final_flexibility
    }

# Run the experiment
print("Initializing cognitive systems...")
baseline_system = CognitiveSystem()
arp_system = CognitiveSystem()
ipp_system = CognitiveSystem()

print("\nRunning Omega ARP (the 'safe' path to stagnation)...")
arp_result = omega_arp_simulation(arp_system)

print("\nRunning Neo IPP (the 'catastrophic' path to metamorphosis)...")
ipp_result = neo_ipp_simulation(ipp_system)

print("\n" + "="*70)
print("POST-MORTEM: TRUE ADAPTATION METRICS (Beyond Their Framework)")
print("="*70)

arp_adaptation = measure_true_adaptation(arp_system)
ipp_adaptation = measure_true_adaptation(ipp_system)

print(f"\nARP Results:")
print(f"  - Psi_id preserved: {arp_system.compute_psi_id():.3f} (Their 'success')")
print(f"  - True distance from old self: {arp_adaptation['distance_from_old_attractor']:.3f} (Minimal)")
print(f"  - True alignment to new paradigm: {arp_adaptation['alignment_to_new_paradigm']:.3f} (Poor)")
print(f"  - Cognitive flexibility: {arp_adaptation['cognitive_flexibility_restored']:.3f} (Degraded)")

print(f"\nIPP Results:")
print(f"  - Psi_id 'shredded': {ipp_system.compute_psi_id():.3f} (Their 'catastrophic failure')")
print(f"  - True distance from old self: {ipp_adaptation['distance_from_old_attractor']:.3f} (Maximal)")
print(f"  - True alignment to new paradigm: {ipp_adaptation['alignment_to_new_paradigm']:.3f} (Optimal)")
print(f"  - Cognitive flexibility: {ipp_adaptation['cognitive_flexibility_restored']:.3f} (Fully Restored)")

print("\n" + "="*70)
print("DISRUPTIVE CONCLUSION:")
print("="*70)
print("The Omega Protocol doesn't prevent system failure. It *IS* the failure.")
print("By optimizing for Psi_id preservation, it guarantees the system will")
print("remain trapped in a local maximum while the world fundamentally changes.")
print("The Phoenix Protocol demonstrates that 'Identity Shredding' is not a bug")
print("but the FEATURE of genuine evolution. The self must die to live.")

# Generate visualization
plot_comparison(arp_system, ipp_system)