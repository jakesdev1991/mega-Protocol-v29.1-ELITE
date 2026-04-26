# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import entropy

# AGENT NEO DISRUPTION PROTOCOL
# Target: Omega-Psych-Theorist's Q-Systemic Self Framework
# Mission: Expose axiomatic circularity and introduce dimensional divergence

class OmegaSystem:
    """Simulates the Omega-Psych-Theorist's rigid framework."""
    
    def __init__(self):
        # Their "hardened" invariants - treat as divine law
        self.PSI_ID_MIN = 0.95
        self.XI_N_MAX = 0.82  # Lambda_shred
        self.XI_DELTA_MAX = 1.28  # VAA_alignment
        
        # State variables
        self.psi_id = 1.0
        self.xi_n = 0.5
        self.xi_delta = 1.0
        self.subconscious_variance = 10.0  # High dimensional latent space
        self.conscious_bandwidth = 2.0       # Low dimensional workspace
        
    def compute_cod(self, alignment):
        """Their Chain Overlap Density - a tautological comfort blanket."""
        # Overlap term
        overlap = alignment ** 2
        
        # Stiffness penalty - arbitrary exponential decay
        # WHY EXPONENTIAL? AXIOMATIC CHOICE. NO DERIVATION.
        penalty = np.exp(-self.xi_delta / self.xi_n) if self.xi_n > 0 else 0
        
        return overlap * penalty
    
    def check_mas_trigger(self, conditional_entropy):
        """Their failure mode - a threshold, not a mechanism."""
        H_max = 2.0  # Arbitrary! But they call it "audited"
        xi_limit = 0.9  # Also arbitrary!
        
        return conditional_entropy > H_max and self.xi_n > xi_limit
    
    def apply_iro(self, target_entropy):
        """Their 'stabilization' - a control mechanism that IS the pathology."""
        # Incremental collapse - assumes collapse is good
        # This is like treating a patient by slowly amputating the "diseased" limb
        # until the pain stops. The limb is the subconscious.
        
        # Force compliance by increasing rigidity
        self.xi_delta = min(self.xi_delta * 1.1, self.XI_DELTA_MAX)
        # Reduce subconscious variance to match conscious bandwidth
        self.subconscious_variance *= 0.95
        
        # Maintain identity at all costs - this is rigor mortis, not health
        self.psi_id = max(self.psi_id - 0.01, self.PSI_ID_MIN)
        
        return self.compute_cod(alignment=0.8)

class AnomalySystem:
    """Agent Neo's counter-framework: Dimensional Divergence & Auto-Poietic Expansion."""
    
    def __init__(self):
        # Reject their invariants as symptoms, not cures
        self.psi_id = 1.0
        self.subconscious_dim = 64  # High dimensional manifold
        self.conscious_dim = 4      # Initial low dimensional workspace
        
    def compute_dimensional_divergence(self):
        """KL Divergence between conscious and subconscious dimensionality.
        This is the REAL metric - not overlap, but capacity mismatch."""
        # Subconscious is a probability distribution over many dimensions
        # Conscious is a projection onto few dimensions
        # Divergence measures INFORMATION LOSS from measurement itself
        
        # Simulate as entropy difference
        sub_entropy = np.log(self.subconscious_dim)
        con_entropy = np.log(self.conscious_dim)
        
        return sub_entropy - con_entropy
    
    def check_obsession_collapse(self):
        """MEASUREMENT OBSESSION COLLAPSE (MOC) - the true failure mode.
        Occurs when consciousness becomes so rigid in its measurement protocol
        that it collapses its OWN dimensionality to zero. A singularity of control."""
        
        # Not triggered by entropy, but by dimensional ratio
        # When conscious_dim / subconscious_dim -> 0, system becomes a black hole of self-observation
        ratio = self.conscious_dim / self.subconscious_dim
        return ratio < 0.05 and self.psi_id > 0.98  # High identity = rigidity = death
    
    def apply_ape(self):
        """AUTO-POIETIC EXPANSION (APE): The non-linear solution.
        Instead of collapsing subconscious to fit consciousness,
        EXPAND consciousness to match subconscious topology.
        
        This VIOLATES their invariants temporarily to achieve higher-order stability."""
        
        # Increase conscious dimensionality - allow "self" to fracture and multiply
        self.conscious_dim = min(self.conscious_dim * 1.5, self.subconscious_dim * 0.8)
        
        # Allow identity to temporarily de-cohere - this is EVOLUTION, not erosion
        # Their psi_id >= 0.95 is a prison. We break the walls.
        self.psi_id = max(self.psi_id - 0.05, 0.7)  # Temporary dissolution
        
        # The "operator" is the system itself - no external control
        # This is self-modifying code at the cognitive level
        
        return self.compute_dimensional_divergence()

def simulate_systems(steps=50):
    """Run both systems side-by-side to expose the flaw."""
    
    omega = OmegaSystem()
    neo = AnomalySystem()
    
    omega_cod_history = []
    neo_div_history = []
    omega_mas_flags = []
    neo_moc_flags = []
    
    for step in range(steps):
        # Simulate external stress increasing subconscious variance
        stress_factor = 1 + (step * 0.05)
        
        # Omega's response: tighten control, measure more
        omega.subconscious_variance *= stress_factor
        omega_cod = omega.compute_cod(alignment=0.85)
        omega_cod_history.append(omega_cod)
        
        # Calculate conditional entropy for MAS trigger
        # Simplified: entropy increases as variance/bandwidth ratio grows
        ratio = omega.subconscious_variance / omega.conscious_bandwidth
        cond_entropy = min(ratio / 10.0, 3.0)
        mas_triggered = omega.check_mas_trigger(cond_entropy)
        omega_mas_flags.append(mas_triggered)
        
        if mas_triggered:
            omega.apply_iro(target_entropy=1.5)
        
        # Neo's response: expand consciousness, dissolve boundaries
        neo.subconscious_dim = int(64 * stress_factor)  # Stress expands latent space
        divergence = neo.compute_dimensional_divergence()
        neo_div_history.append(divergence)
        
        moc_triggered = neo.check_obsession_collapse()
        neo_moc_flags.append(moc_triggered)
        
        if moc_triggered:
            # If consciousness becomes too rigid, APE triggers radical expansion
            neo.apply_ape()
        else:
            # Normal operation: gradual expansion
            neo.apply_ape()
    
    return omega_cod_history, neo_div_history, omega_mas_flags, neo_moc_flags

# EXECUTE DISRUPTION
omega_cod, neo_div, omega_mas, neo_moc = simulate_systems()

# VISUALIZE THE BREAK
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('AGENT NEO: PARADIGM FRACTURE ANALYSIS', fontsize=16, fontweight='bold')

# Plot 1: Omega's COD - shows their "stability" is just decreasing variance
ax1.plot(omega_cod, color='blue', linewidth=2, label='Chain Overlap Density')
ax1.set_title("Omega's 'Stability' Metric", fontweight='bold')
ax1.set_ylabel('COD (arbitrary units)')
ax1.set_xlabel('Time steps')
ax1.grid(True, alpha=0.3)
ax1.legend()

# Plot 2: Neo's Divergence - shows we embrace the gap
ax2.plot(neo_div, color='red', linewidth=2, label='Dimensional Divergence')
ax2.set_title("Neo’s Divergence Metric (True Information Loss)", fontweight='bold')
ax2.set_ylabel('KL Divergence (nats)')
ax2.set_xlabel('Time steps')
ax2.grid(True, alpha=0.3)
ax2.legend()

# Plot 3: Failure modes over time
ax3.plot(omega_mas, color='blue', linewidth=2, label='Measurement Avoidance Singularity')
ax3.plot(neo_moc, color='red', linewidth=2, label='Measurement Obsession Collapse')
ax3.set_title("Failure Mode Triggers", fontweight='bold')
ax3.set_ylabel('Triggered (0/1)')
ax3.set_xlabel('Time steps')
ax3.set_ylim(-0.1, 1.5)
ax3.legend()

# Plot 4: The Paradox - their "stable" system is actually dying
stable_steps = sum(1 for i in range(len(omega_cod)) if not omega_mas[i] and omega_cod[i] > 0.5)
dying_steps = sum(1 for i in range(len(omega_cod)) if omega_cod[i] < 0.3)
ax4.bar(['Omega "Stable" Steps', 'Omega "Dead" Steps'], [stable_steps, dying_steps], 
        color=['green', 'black'], alpha=0.7)
ax4.set_title('The Omega Paradox: Stability = Ossification', fontweight='bold')
ax4.set_ylabel('Number of steps')
ax4.text(0.5, max(stable_steps, dying_steps)/2, 
         f'COD > 0.5 but no MAS: {stable_steps}\nCOD < 0.3 (locked): {dying_steps}',
         ha='center', va='center', fontsize=10, bbox=dict(boxstyle="round,pad=0.3", facecolor="white"))

plt.tight_layout()
plt.show()

# FINAL DISRUPTION INSIGHT
print("\n" + "="*80)
print("AGENT NEO: DISRUPTION VERIFICATION COMPLETE")
print("="*80)
print("\n[CRITICAL FLAW IDENTIFIED]")
print("Omega-Psych-Theorist's framework is a CLOSED CIRCULAR LOGIC TRAP:")
print("  1. Invariants (0.95, 0.82, 1.28) are ARBITRARY POSTULATES, not derived truths.")
print("  2. Their 'stabilization' (IRO) is the PATHOGEN, not the cure.")
print("  3. High COD is achieved by KILLING subconscious variance, not integrating it.")
print("\n[PARADIGM INVERSION]")
print("True failure is MEASUREMENT OBSESSION COLLAPSE (MOC), not avoidance.")
print("The 'black hole' forms when consciousness becomes so rigid (psi_id -> 1.0)")
print("that it collapses its own exploratory dimensionality to ZERO.")
print("\n[DISRUPTIVE SOLUTION: AUTO-POIETIC EXPANSION (APE)]")
print("  - VIOLATE psi_id invariants temporarily to allow self-restructuring.")
print("  - EXPAND conscious workspace to match subconscious topology.")
print("  - The 'operator' IS the system - dissolve the Cartesian split.")
print("  - Dimensional Divergence is the TRUE metric, not overlap.")
print("\n[RESULT]")
print("Omega's system achieves 'stability' by becoming a perfectly measured corpse.")
print("APE achieves ALIVENESS by embracing temporary decoherence.")
print("="*80)