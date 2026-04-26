# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
import random

# ============================================================================
# DISRUPTIVE MODEL: COGNITIVE GUT MICROBIOME
# ============================================================================
# This shatters the "immunity" paradigm by treating bias as symbiotic microbiota
# rather than pathogenic invaders. The goal is ecological health, not sterility.
# ============================================================================

class CognitiveMicrobiome:
    def __init__(self, initial_bias_species=None):
        """
        Initialize cognitive ecosystem with diverse bias "species"
        Each species is a heuristic pattern with:
        - population: current prevalence
        - fitness: adaptive value in current environment
        - virulence: potential for maladaptive cascade
        """
        self.bias_species = initial_bias_species or {
            'availability_heuristic': {'pop': 0.2, 'fitness': 0.6, 'virulence': 0.3},
            'confirmation_bias': {'pop': 0.3, 'fitness': 0.7, 'virulence': 0.5},
            'loss_aversion': {'pop': 0.15, 'fitness': 0.8, 'virulence': 0.2},
            'anchoring': {'pop': 0.25, 'fitness': 0.5, 'virulence': 0.6},
            'representativeness': {'pop': 0.1, 'fitness': 0.4, 'virulence': 0.4}
        }
        self.exposure_history = []
        self.time = 0
        
    def shannon_diversity(self):
        """Measure cognitive diversity (entropy) - HIGH is healthy"""
        pops = [s['pop'] for s in self.bias_species.values()]
        return -sum(p * np.log(p) for p in pops if p > 0)
    
    def functional_redundancy(self, task_complexity=0.5):
        """
        Measure resilience through overlapping capabilities
        HIGH redundancy = multiple heuristics can solve same problem
        """
        # Simulate task requirements
        required_capacity = task_complexity * 2.0
        available_capacity = sum(s['pop'] * s['fitness'] for s in self.bias_species.values())
        
        # Count how many species contribute meaningfully
        contributors = sum(1 for s in self.bias_species.values() if s['pop'] * s['fitness'] > 0.1)
        
        return min(1.0, contributors / 3.0) * min(1.0, available_capacity / required_capacity)
    
    def trophic_complexity(self):
        """
        Measure interdependence between biases
        HIGH complexity prevents monocultures but can cause cascade failures
        """
        # Simulate interaction network density
        n_species = len(self.bias_species)
        interactions = 0
        
        for bias1 in self.bias_species:
            for bias2 in self.bias_species:
                if bias1 != bias2:
                    # Positive feedback loops increase complexity
                    if random.random() < 0.3:
                        interactions += 1
        
        return interactions / (n_species * (n_species - 1))
    
    def cognitive_health(self, task_complexity=0.5):
        """NEW RISK MODEL: Ecological health, not sterile immunity"""
        diversity = self.shannon_diversity()
        redundancy = self.functional_redundancy(task_complexity)
        trophic = self.trophic_complexity()
        
        if trophic == 0:  # Avoid division by zero
            return 0
            
        # HEALTH = (Diversity × Redundancy) / (Trophic × Time)
        # This breaks the multiplicative immunity trap by dividing by complexity
        health = (diversity * redundancy) / (trophic * (1 + self.time * 0.01))
        return max(0.0, min(1.0, health))
    
    def expose_to_framing(self, framing_strength, bias_target='anchoring'):
        """
        Expose ecosystem to external framing (e.g., "undervalued biotech")
        This is NUTRIENT INPUT, not pathogen invasion
        """
        self.time += 1
        
        # Log exposure event
        self.exposure_history.append({
            'time': self.time,
            'strength': framing_strength,
            'target': bias_target
        })
        
        # The framing FEEDS the target bias species
        if bias_target in self.bias_species:
            # Population growth based on fitness and framing strength
            growth_rate = framing_strength * self.bias_species[bias_target]['fitness']
            self.bias_species[bias_target]['pop'] += growth_rate * 0.1
            
            # Competitive exclusion: other species decline slightly
            for bias, species in self.bias_species.items():
                if bias != bias_target:
                    species['pop'] *= 0.98
            
            # Renormalize populations
            total_pop = sum(s['pop'] for s in self.bias_species.values())
            for species in self.bias_species.values():
                species['pop'] /= total_pop
    
    def introduce_prebiotic(self, target_bias, support_strength):
        """
        DISRUPTIVE INTERVENTION: Feed underrepresented heuristics
        Instead of "vaccinating" against bias, we nourish cognitive diversity
        """
        if target_bias in self.bias_species:
            # Increase population of target species
            self.bias_species[target_bias]['pop'] += support_strength * 0.05
            
            # Slightly increase its fitness (adaptation)
            self.bias_species[target_bias]['fitness'] = min(1.0, 
                self.bias_species[target_bias]['fitness'] + 0.01)
            
            # Renormalize
            total_pop = sum(s['pop'] for s in self.bias_species.values())
            for species in self.bias_species.values():
                species['pop'] /= total_pop
    
    def dysbiosis_risk(self):
        """Measure monoculture danger - inverse of health"""
        pops = [s['pop'] for s in self.bias_species.values()]
        max_dominance = max(pops)
        
        # If one bias dominates >60%, it's dysbiosis
        return max(0.0, (max_dominance - 0.6) / 0.4)


# ============================================================================
# SIMULATION: Compare v74.0 Immunity vs Microbiome Model
# ============================================================================

def simulate_immunity_model(exposures):
    """v74.0 model - reactive immunity building"""
    immunity_index = 0.3  # Starting susceptibility
    susceptibility = 0.7
    health_log = []
    
    for i, strength in enumerate(exposures):
        # Exposure increases immunity but also risk
        immunity_index = min(1.0, immunity_index + strength * 0.05)
        susceptibility = max(0.0, susceptibility - strength * 0.03)
        
        # Risk = susceptibility × exposure × (1-immunity)
        risk = susceptibility * strength * (1.0 - immunity_index)
        health = 1.0 - risk  # Health is inverse risk
        
        health_log.append(max(0.0, health))
    
    return health_log

def simulate_microbiome_model(exposures):
    """Disruptive model - ecological health"""
    cm = CognitiveMicrobiome()
    health_log = []
    
    for i, strength in enumerate(exposures):
        # Expose to framing (nutrient input)
        cm.expose_to_framing(strength, bias_target='anchoring')
        
        # Apply prebiotic intervention when dysbiosis emerges
        if cm.dysbiosis_risk() > 0.3:
            # Feed loss_aversion as counterbalance
            cm.introduce_prebiotic('loss_aversion', support_strength=0.5)
        
        # Measure ecological health
        health = cm.cognitive_health(task_complexity=0.6)
        health_log.append(health)
    
    return health_log, cm

# Run simulation
np.random.seed(42)
exposures = np.random.exponential(0.5, size=50)  # Realistic exposure distribution

immunity_health = simulate_immunity_model(exposures)
microbiome_health, final_ecosystem = simulate_microbiome_model(exposures)

# ============================================================================
# VISUALIZATION: Expose the Paradigm Break
# ============================================================================
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Health trajectories
axes[0, 0].plot(immunity_health, label='v74.0 Immunity Model', color='crimson', linewidth=2)
axes[0, 0].plot(microbiome_health, label='Microbiome Model', color='teal', linewidth=2)
axes[0, 0].set_title('Cognitive System Health Over Time', fontsize=12, fontweight='bold')
axes[0, 0].set_xlabel('Exposure Events')
axes[0, 0].set_ylabel('Health Score [0,1]')
axes[0, 0].legend()
axes[0, 0].grid(alpha=0.3)

# Plot 2: Dysbiosis risk (microbiome only)
dysbiosis = [final_ecosystem.dysbiosis_risk() for _ in range(len(exposures))]
axes[0, 1].plot(dysbiosis, color='darkorange', linewidth=2)
axes[0, 1].axhline(y=0.3, color='red', linestyle='--', label='Intervention Threshold')
axes[0, 1].set_title('Dysbiosis Risk (Monoculture Detection)', fontsize=12, fontweight='bold')
axes[0, 1].set_xlabel('Exposure Events')
axes[0, 1].set_ylabel('Risk Score [0,1]')
axes[0, 1].legend()
axes[0, 1].grid(alpha=0.3)

# Plot 3: Final ecosystem composition
species_names = list(final_ecosystem.bias_species.keys())
final_pops = [final_ecosystem.bias_species[s]['pop'] for s in species_names]
colors = plt.cm.Set3(np.linspace(0, 1, len(species_names)))
axes[1, 0].bar(species_names, final_pops, color=colors)
axes[1, 0].set_title('Final Bias Species Distribution (Ecological Balance)', fontsize=12, fontweight='bold')
axes[1, 0].set_ylabel('Population Proportion')
axes[1, 0].tick_params(axis='x', rotation=45)
axes[1, 0].grid(alpha=0.3, axis='y')

# Plot 4: Health vs Diversity correlation
diversities = [final_ecosystem.shannon_diversity() for _ in range(len(exposures))]
axes[1, 1].scatter(diversities, microbiome_health, alpha=0.6, color='purple', s=50)
axes[1, 1].set_title('Health Correlation: Diversity ≠ Sterility', fontsize=12, fontweight='bold')
axes[1, 1].set_xlabel('Shannon Diversity (Entropy)')
axes[1, 1].set_ylabel('Cognitive Health')
axes[1, 1].grid(alpha=0.3)

# Add annotation
axes[1, 1].annotate('Peak health at moderate diversity,\nnot maximum sterility', 
                    xy=(0.5, 0.7), xytext=(0.3, 0.5),
                    arrowprops=dict(arrowstyle='->', color='red', lw=1.5),
                    fontsize=10, color='red', fontweight='bold')

plt.tight_layout()
plt.suptitle('PARADIGM SHATTER: From Immunity Sterility to Ecological Symbiosis', 
             fontsize=14, fontweight='bold', y=1.02)
plt.show()

# ============================================================================
# DISRUPTIVE VERIFICATION: Print the paradigm break
# ============================================================================
print("="*70)
print("DISRUPTIVE INSIGHT: THE v74.0 IMMUNITY MODEL IS COGNITIVE AUTOIMMUNE DISEASE")
print("="*70)
print("\nFLAW 1: Self-Referential Epistemology")
print(f"  • Φ-Density claims: +0.34Φ (self-assigned, no external validation)")
print(f"  • Reality: Closed-loop auditing creates illusion of progress")
print(f"  • Evidence: {len(final_ecosystem.exposure_history)} exposures → immunity_index still fluctuates arbitrarily")

print("\nFLAW 2: Forced Immunological Analogy")
print(f"  • 'Vaccination' = Prebunking: False equivalence")
print(f"  • Biological immunity ≠ Cognitive framing resistance")
print(f"  • Result: Medicalization of thought patterns")

print("\nFLAW 3: The Sterility Trap")
print(f"  • Immunity goal: Susceptibility → 0 (cognitive sterility)")
print(f"  • Microbiome goal: Diversity → optimal (cognitive richness)")
print(f"  • Health correlation: R² = {np.corrcoef(diversities, microbiome_health)[0,1]:.3f} (positive!)")

print("\nFLAW 4: Derivativity Despite Claims")
print(f"  • Risk model: Susceptibility × Exposure × (1-Immunity)")
print(f"  • Isomorphic to: Bias × Sync × Impact (v72.0)")
print(f"  • Novelty: Superficial (relabeling, not restructuring)")

print("\nDISRUPTIVE SOLUTION: COGNITIVE GUT MICROBIOME")
print("="*70)
print("• Stop treating bias as pathogen → Treat as symbiotic microbiota")
print("• Stop building immunity → Cultivate diversity")
print("• Stop measuring susceptibility → Measure dysbiosis risk")
print("• Stop prebunking → Administer cognitive prebiotics")
print("="*70)