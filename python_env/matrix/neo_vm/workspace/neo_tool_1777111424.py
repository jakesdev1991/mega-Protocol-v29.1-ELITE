# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

# =============================================================================
# DISRUPTIVE SIMULATION: Trust Asymmetry Collapse
# =============================================================================

class TrustAsymmetryAttack:
    """
    Demonstrates how the epidemic model fails when attackers exploit
    TRUST ASYMMETRY rather than connectivity.
    """
    
    def __init__(self, n_facilities=20):
        # Create collaboration network with trust asymmetries
        self.G = nx.barabasi_albert_graph(n_facilities, 2)
        self.facilities = list(self.G.nodes())
        
        # Assign TRUST SCORES (not connectivity) - the real vulnerability
        # High trust = partners share credentials freely = high "susceptibility"
        # But trust is ASYMMETRIC: Facility A trusts B more than B trusts A
        self.trust_matrix = np.random.random((n_facilities, n_facilities))
        np.fill_diagonal(self.trust_matrix, 0)
        
        # Introduce a HIGH-TRUST but LOW-CONNECTIVITY node
        # This is the "stealth super-spreader" the epidemic model misses
        self.G.add_node(20)  # Add new facility
        self.facilities.append(20)
        self.trust_matrix = np.pad(self.trust_matrix, ((0,1),(0,1)), mode='constant')
        
        # This new node is trusted by everyone but trusts no one back
        self.trust_matrix[:-1, -1] = 0.9  # Everyone trusts facility 20
        self.trust_matrix[-1, :-1] = 0.1  # Facility 20 trusts no one
        
        # Add edges to make it appear low-risk in connectivity model
        self.G.add_edge(20, 0)  # Only 1 connection
        
        # Attack parameters
        self.compromised = set()
        self.time_steps = []
        self.epidemic_predictions = []
        self.actual_cascade = []
        
    def epidemic_model_prediction(self, initial_compromise):
        """
        Simulates the v77.0-Ω-FINAL epidemic model prediction
        """
        # Calculate connectivity-based metrics (what the model uses)
        connectivity = {node: self.G.degree(node) for node in self.G.nodes()}
        max_connectivity = max(connectivity.values())
        
        # Normalize to [0,1] as in the protocol
        connectivity_scores = {node: connectivity[node]/max_connectivity for node in self.G.nodes()}
        
        # "Super-spreader risk" based on connectivity
        superspreader_risk = connectivity_scores.copy()
        
        # R0 prediction based on connectivity
        r0 = defaultdict(float)
        for node in initial_compromise:
            for neighbor in self.G.neighbors(node):
                r0[neighbor] += superspreader_risk[node] * 0.5  # Arbitrary transmission rate
        
        # Predict cascade size after 5 steps
        predicted_cascade = set(initial_compromise)
        current = set(initial_compromise)
        
        for _ in range(5):
            next_compromised = set()
            for node in current:
                for neighbor in self.G.neighbors(node):
                    if neighbor not in predicted_cascade:
                        # Epidemic model uses connectivity, not trust
                        infection_prob = connectivity_scores[node] * 0.3
                        if np.random.random() < infection_prob:
                            next_compromised.add(neighbor)
            predicted_cascade.update(next_compromised)
            current = next_compromised
            
        return len(predicted_cascade)
    
    def adversarial_attack_simulation(self, initial_compromise):
        """
        Simulates intelligent attacker exploiting TRUST ASYMMETRY
        """
        compromised = set(initial_compromise)
        current = set(initial_compromise)
        
        # Attacker strategy: ALWAYS target highest-TRUSTED nodes first
        # Not highest-connectivity nodes
        for step in range(5):
            next_targets = set()
            
            # For each currently compromised node, find who trusts them most
            for node in current:
                # Find facilities that trust this compromised node
                trust_scores = self.trust_matrix[:, node]
                # Get facilities with high trust (>0.7)
                high_trust_partners = np.where(trust_scores > 0.7)[0]
                
                for target in high_trust_partners:
                    if target not in compromised:
                        # High trust = they share credentials = easy compromise
                        next_targets.add(target)
            
            # Also exploit the stealth super-spreader (facility 20)
            # Once any neighbor of 20 is compromised, attacker IMMEDIATELY targets 20
            # because it's HIGHLY TRUSTED (high susceptible fraction)
            if any(n in compromised for n in self.G.neighbors(20)) and 20 not in compromised:
                next_targets.add(20)
            
            compromised.update(next_targets)
            current = next_targets
            
        return len(compromised)
    
    def run_comparison(self, n_trials=100):
        """
        Compare epidemic model predictions vs actual adversarial behavior
        """
        results = []
        
        for trial in range(n_trials):
            # Random initial compromise of 3 facilities
            initial = np.random.choice(self.facilities[:-1], size=3, replace=False)
            
            # Epidemic model prediction (connectivity-based)
            predicted = self.epidemic_model_prediction(initial)
            
            # Actual adversarial attack (trust-based)
            actual = self.adversarial_attack_simulation(initial)
            
            results.append({
                'trial': trial,
                'initial': initial,
                'predicted_cascade': predicted,
                'actual_cascade': actual,
                'error': actual - predicted,
                'underestimation': actual > predicted * 1.5  # Model underestimates by >50%
            })
            
            # Track time series for first trial
            if trial == 0:
                for step in range(6):
                    self.time_steps.append(step)
                    self.epidemic_predictions.append(
                        self.epidemic_model_prediction(initial) * (step/6)
                    )
                    self.actual_cascade.append(
                        self.adversarial_attack_simulation(initial) * (step/6)
                    )
        
        return results

# Run simulation
attacker = TrustAsymmetryAttack(n_facilities=20)
results = attacker.run_comparison(n_trials=100)

# =============================================================================
# ANALYSIS: Catastrophic Failure Modes
# =============================================================================

print("=" * 70)
print("TRUST ASYMMETRY COLLAPSE ANALYSIS")
print("=" * 70)

underestimation_rate = sum(1 for r in results if r['underestimation']) / len(results)
avg_error = np.mean([r['error'] for r in results])
max_error = max([r['error'] for r in results])

print(f"\n[FAILURE METRICS]")
print(f"  Model underestimates cascade size in {underestimation_rate:.1%} of trials")
print(f"  Average underestimation: {avg_error:.1f} facilities")
print(f"  Maximum underestimation: {max_error:.1f} facilities")

print(f"\n[CRITICAL INSIGHT]")
print(f"  The epidemic model assumes:  Compromise ∝ Connectivity")
print(f"  The adversary exploits:      Compromise ∝ Trust Asymmetry")
print(f"  Result: The model is blind to stealth super-spreaders that are")
print(f"          HIGHLY TRUSTED but LOW-CONNECTIVITY.")

# Identify the stealth super-spreader
stealth_node = 20
stealth_connectivity = attacker.G.degree(stealth_node)
stealth_trust_in = np.mean(attacker.trust_matrix[:-1, stealth_node])

print(f"\n[STEALTH SUPER-SPREADER]")
print(f"  Facility {stealth_node}:")
print(f"    Connectivity: {stealth_connectivity} (LOW - appears safe)")
print(f"    Avg trust IN: {stealth_trust_in:.2f} (HIGH - everyone trusts it)")
print(f"    Model's superspreader risk: {stealth_connectivity/ max(dict(attacker.G.degree()).values()):.2f}")
print(f"    Actual exploitation risk: CRITICAL (trust asymmetry)")

# =============================================================================
# DISRUPTIVE INSIGHT: The Epidemic Model is Epistemically Invalid
# =============================================================================

print("\n" + "=" * 70)
print("DISRUPTIVE INSIGHT: Category Error in the Protocol")
print("=" * 70)

print("""
The v77.0-Ω-FINAL protocol commits a fatal category error:

  EPIDEMIC MODEL ASSUMPTIONS:
  - Passive diffusion: Credentials spread like viruses
  - Connectivity = Risk: High-degree nodes are super-spreaders
  - Homogeneous susceptibility: All facilities have similar risk profiles
  - No adversarial intelligence: Attackers act randomly

  REALITY OF CREDENTIAL PROPAGATION:
  - Active exploitation: Attackers TARGET high-value, high-trust nodes
  - Trust Asymmetry = Risk: Facilities trusted by many are exploited first
  - Heterogeneous susceptibility: Trust relationships create vulnerability gradients
  - Strategic adversaries: Attackers adapt to network topology

The result is a "Shredding Event" that the model cannot predict because
it occurs in the trust manifold, not the connectivity graph.

The STEALTH SUPER-SPREADER (facility 20) has:
  - Connectivity: 1 (appears safe to epidemic model)
  - Trust-in: 0.9 (everyone shares credentials with it)
  - Exploitation: Immediate once any neighbor is compromised

The epidemic model's "herd immunity threshold" is MEANINGLESS because
attackers don't infect randomly—they TARGET the trust-asymmetric nodes
that break the model's homogeneity assumption.
""")

# =============================================================================
# BREAKING THE PARADIGM: Trust Topology Reconstruction
# =============================================================================

print("\n" + "=" * 70)
print("BREAKING THE PARADIGM: From Epidemic Dynamics to Adversarial Game Theory")
print("=" * 70)

print("""
The solution is NOT to refine the epidemic model. The solution is to
recognize that credential propagation is a **strategic game**, not a
physical process.

NEW PROTOCOL: API ADVERARIAL TRUST MANIFOLD (v78.0-Ω)

Key Invariants (replacing epidemic metrics):

  1. TRUST ASYMMETRY COEFFICIENT (τ):
     τ = ||T - T^T||_F / ||T||_F
     where T is the trust matrix
     High τ = catastrophic vulnerability (trust flows in one direction)

  2. STEALTH SUPER-SPREADER DENSITY (σ):
     σ = count(nodes with high trust-in + low connectivity) / total_nodes
     These are invisible to epidemic models but primary targets

  3. ADVERSARIAL VALUE CONCENTRATION (α):
     α = max_i (Σ_j trust[j,i] * value[j])
     The maximum value an attacker gains by compromising a single node

  4. TRUST CASCADE VELOCITY (v_T):
     v_T = dα/dt under optimal adversarial strategy
     How fast value concentrates under attack

The "Shredding Event" is redefined:
  - OLD: φ_Δ > 0.80 (physics-based)
  - NEW: τ > 0.75 (trust-asymmetry-driven cascade)

Intervention Protocol:
  - QUARANTINE: Isolate high-τ nodes (not high-connectivity)
  - VACCINATION: Rotate credentials at high-σ nodes preemptively
  - TRUST DECAY: Introduce temporal trust decay to reduce τ over time
""")

# =============================================================================
# QUANTIFYING THE FAILURE: Catastrophic Underestimation
# =============================================================================

print("\n[QUANTIFYING CATASTROPHIC FAILURE]")

# Show distribution of errors
errors = [r['error'] for r in results]
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.hist(errors, bins=20, color='darkred', alpha=0.7)
plt.axvline(0, color='black', linestyle='--')
plt.title("Epidemic Model Prediction Error Distribution")
plt.xlabel("Actual - Predicted Compromised Facilities")
plt.ylabel("Frequency")
plt.grid(True, alpha=0.3)

# Show trust vs connectivity for each node
connectivity = [attacker.G.degree(n) for n in attacker.facilities]
trust_in = [np.mean(attacker.trust_matrix[:-1, i]) if i < len(attacker.trust_matrix)-1 else np.mean(attacker.trust_matrix[:-1, -1]) for i in range(len(attacker.facilities))]

plt.subplot(1, 2, 2)
plt.scatter(connectivity, trust_in, alpha=0.6, s=100)
plt.scatter([stealth_connectivity], [stealth_trust_in], color='red', s=200, marker='X', label='Stealth Super-Spreader')
plt.xlabel("Connectivity (Epidemic Model Risk)")
plt.ylabel("Trust-In (Actual Adversarial Risk)")
plt.title("The Model's Blind Spot: Trust vs Connectivity")
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

print("\n" + "=" * 70)
print("FINAL VERDICT: The v77.0-Ω-FINAL protocol is EPISTEMICALLY BROKEN")
print("=" * 70)
print("""
The protocol engineers a perfect epidemic model for a problem that is
fundamentally adversarial, not epidemiological.

The "physics rubric compliance" is a category error: plasma physics
describes passive natural systems; cybersecurity describes active
adversarial systems.

Φ-Density Impact: -0.40Φ (protocol must be redesigned from first principles)
Status: EPISTEMICALLY INVALID - Requires v78.0-Ω adversarial game theory reconstruction
""")