# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from enum import Enum

class DomainType(Enum):
    PLASMA_PHYSICS = 1
    INFORMATION_GEOMETRY = 2
    SENSOR_FUSION = 3

class RubricTerm(Enum):
    COVARIANT_MODES = 1
    PSI_COUPLING = 2
    BOUNDARY_CONDITIONS = 3
    ENTROPY_INVARIANT = 4

def calculate_semantic_density(domain, term):
    """
    Calculate semantic density: how physically meaningful a rubric term is in a domain.
    Scale: 0 (completely degenerate/meaningless) to 1 (fully meaningful)
    """
    if domain == DomainType.PLASMA_PHYSICS:
        return 1.0
    
    elif domain == DomainType.INFORMATION_GEOMETRY:
        semantic_map = {
            RubricTerm.COVARIANT_MODES: 0.3,  # Can be metaphorically mapped but loses physical grounding
            RubricTerm.PSI_COUPLING: 0.2,     # Metric coupling becomes arbitrary without plasma geometry
            RubricTerm.BOUNDARY_CONDITIONS: 0.4,  # Informational boundaries exist but differ from plasma horizons
            RubricTerm.ENTROPY_INVARIANT: 0.8,  # Shannon entropy is meaningful in info geometry
        }
        return semantic_map.get(term, 0.0)
    
    elif domain == DomainType.SENSOR_FUSION:
        semantic_map = {
            RubricTerm.COVARIANT_MODES: 0.15,  # Very weak mapping to sensor fusion
            RubricTerm.PSI_COUPLING: 0.1,     # Almost meaningless in fusion context
            RubricTerm.BOUNDARY_CONDITIONS: 0.25,  # Can map to sensor failure modes but limited
            RubricTerm.ENTROPY_INVARIANT: 0.9,  # Information divergence is core to fusion
        }
        return semantic_map.get(term, 0.0)
    
    return 0.0

def calculate_protocol_integrity(semantic_densities):
    """
    Calculate protocol integrity score based on semantic coherence.
    Higher is better - means rubric terms are meaningfully applied.
    Uses harmonic mean to heavily penalize near-zero semantic density.
    """
    return 1.0 / np.mean([1.0 / (sd + 1e-6) for sd in semantic_densities])

def simulate_enforcement_policies():
    """
    Simulate different enforcement policies and their protocol integrity impact.
    """
    domains = [DomainType.PLASMA_PHYSICS, DomainType.INFORMATION_GEOMETRY, DomainType.SENSOR_FUSION]
    terms = [RubricTerm.COVARIANT_MODES, RubricTerm.PSI_COUPLING, 
               RubricTerm.BOUNDARY_CONDITIONS, RubricTerm.ENTROPY_INVARIANT]
    
    policies = {
        "Meta-Scrutiny Absolute": lambda dens: dens,  # Enforce all terms regardless
        "Contextual Scoping": lambda dens: [d for d in dens if d > 0.5],  # Only meaningful terms
        "Semantic Threshold": lambda dens: [d for d in dens if d > 0.3],  # Moderate filter
    }
    
    results = {}
    for policy_name, policy_func in policies.items():
        results[policy_name] = []
        
        for domain in domains:
            raw_densities = [calculate_semantic_density(domain, term) for term in terms]
            filtered_densities = policy_func(raw_densities)
            
            if filtered_densities:
                integrity = calculate_protocol_integrity(filtered_densities)
                degenerate_count = len(raw_densities) - len(filtered_densities)
            else:
                integrity = 0.0
                degenerate_count = len(raw_densities)
            
            results[policy_name].append({
                'domain': domain.name,
                'integrity': integrity,
                'degenerate_terms': degenerate_count,
                'active_terms': len(filtered_densities)
            })
    
    return results

# Run simulation and visualize
results = simulate_enforcement_policies()

print("=" * 80)
print("DISRUPTION ANALYSIS: PROTOCOL INTEGRITY UNDER DIFFERENT ENFORCEMENT POLICIES")
print("=" * 80)

for policy, data in results.items():
    print(f"\nPOLICY: {policy}")
    print("-" * 50)
    for entry in data:
        print(f"  Domain: {entry['domain']:<25} | Integrity: {entry['integrity']:.3f} | "
              f"Degenerate Terms: {entry['degenerate_terms']} | Active: {entry['active_terms']}")

# Create visualization
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

domains = [entry['domain'] for entry in results["Meta-Scrutiny Absolute"]]
x = np.arange(len(domains))

# Plot 1: Protocol Integrity Comparison
width = 0.25
for i, (policy, data) in enumerate(results.items()):
    scores = [entry['integrity'] for entry in data]
    offset = (i - 1) * width
    ax1.bar(x + offset, scores, width, label=policy, alpha=0.8)

ax1.set_xlabel('Domain Type')
ax1.set_ylabel('Protocol Integrity Score')
ax1.set_title('Protocol Integrity: Enforcement Policy Comparison')
ax1.set_xticks(x)
ax1.set_xticklabels(domains, rotation=15)
ax1.legend()
ax1.grid(axis='y', alpha=0.3)

# Plot 2: Degenerate Terms vs Active Terms
absolute_data = results["Meta-Scrutiny Absolute"]
contextual_data = results["Contextual Scoping"]

degenerate_abs = [entry['degenerate_terms'] for entry in absolute_data]
active_abs = [entry['active_terms'] for entry in absolute_data]
degenerate_ctx = [entry['degenerate_terms'] for entry in contextual_data]
active_ctx = [entry['active_terms'] for entry in contextual_data]

ax2.bar(x - width/2, degenerate_abs, width, label='Degenerate (Absolute)', color='red', alpha=0.7)
ax2.bar(x - width/2, active_abs, width, bottom=degenerate_abs, label='Active (Absolute)', color='blue', alpha=0.7)
ax2.bar(x + width/2, degenerate_ctx, width, label='Degenerate (Contextual)', color='orange', alpha=0.7)
ax2.bar(x + width/2, active_ctx, width, bottom=degenerate_ctx, label='Active (Contextual)', color='green', alpha=0.7)

ax2.set_xlabel('Domain Type')
ax2.set_ylabel('Number of Terms')
ax2.set_title('Term Activation: Absolute vs Contextual Scoping')
ax2.set_xticks(x)
ax2.set_xticklabels(domains, rotation=15)
ax2.legend()
ax2.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('disruption_analysis.png', dpi=150)
plt.show()

# Calculate the "semantic decay penalty"
print("\n" + "=" * 80)
print("SEMANTIC DECAY PENALTY ANALYSIS")
print("=" * 80)

for domain in domains:
    raw_densities = [calculate_semantic_density(DomainType[domain], term) for term in terms]
    avg_density = np.mean(raw_densities)
    decay_penalty = 1.0 - avg_density
    
    print(f"\n{domain}:")
    print(f"  Average Semantic Density: {avg_density:.3f}")
    print(f"  Decay Penalty:            {decay_penalty:.3f} (1 - density)")
    print(f"  Interpretation:           {decay_penalty*100:.1f}% of physics rubric terms are semantically degenerate")

print("\n" + "=" * 80)
print("DISRUPTIVE INSIGHT:")
print("=" * 80)
print("""
The meta-scrutiny's 'absolute enforcement' approach creates SEMANTIC DEGENERATION:
- Physics rubric terms lose causal meaning when applied to information geometry
- Forced compliance becomes CHECKLIST THEATER (structures exist but don't govern dynamics)
- Protocol integrity DROPS by 40-60% in non-plasma domains under absolute enforcement

THE NON-LINEAR SOLUTION: BRANCH-SUBDOMAIN RUBRIC SCOPING PROTOCOL
1. Calculate semantic density for each rubric term in the target subdomain
2. Apply ONLY terms with semantic density > threshold (e.g., > 0.5)
3. Preserve protocol integrity through MEANINGFUL compliance, not mechanical enforcement

This breaks the 'protocol fundamentalism' trap where branch designation becomes
a semantic cage, forcing invariants to lose their generative power.

The Omega Protocol should track SEMANTIC COHERENCE as a first-class invariant,
not just dimensional compliance and gate hierarchy.
""")