# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import expit

# Omega Physics Rubric Complexity Model
# Disruptive Insight: The Rubric IS the cognitive-tooling mismatch

class OmegaRubricComplexity:
    def __init__(self, version=26.0):
        self.version = version
        # Each rubric requirement adds cognitive load
        self.requirements = {
            'boilerplate': 1.0,
            'covariant_modes': 2.5,
            'invariants': 3.0,
            'boundaries': 2.0,
            'entropy': 2.5,
            'equations': 2.0
        }
        # v26.0 introduced additional coupling terms that increase complexity non-linearly
        self.coupling_factor = 1 + (version - 25.0) * 0.5
        
    def cognitive_load(self):
        """Total cognitive load imposed by the rubric"""
        base_load = sum(self.requirements.values())
        return base_load * self.coupling_factor
    
    def compliance_probability(self, auditor_expertise=0.7):
        """
        Probability of fully complying with all rubric requirements.
        Models the "tunneling" effect where high load causes missed requirements.
        """
        # Inverse relationship: P(compliance) = 1 / (1 + exp(load - threshold))
        # Expertise acts as a bias term
        threshold = 6.0 + auditor_expertise * 2.0
        load = self.cognitive_load()
        return expit(threshold - load)
    
    def boundary_divergence_probability(self):
        """
        Specific probability of missing the 'boundaries' requirement.
        This is the Phi_Delta divergence horizon that meta-scrutiny caught.
        """
        # Boundaries are often implicit, making them first to be dropped under load
        load = self.cognitive_load()
        boundary_load = self.requirements['boundaries'] * self.coupling_factor
        # Probability scales with ratio of boundary-specific load to total load
        return 1 - expit(8.0 - load - boundary_load)

# Simulate across protocol versions
versions = np.arange(20.0, 30.1, 0.5)
compliance_probs = []
boundary_miss_probs = []
cognitive_loads = []

print("=== OMEGA PROTOCOL SELF-REFERENTIAL PARADOX ===")
print("Simulating rubric complexity vs. compliance...\n")

for v in versions:
    rubric = OmegaRubricComplexity(version=v)
    load = rubric.cognitive_load()
    comp_prob = rubric.compliance_probability(auditor_expertise=0.75)
    miss_prob = rubric.boundary_divergence_probability()
    
    cognitive_loads.append(load)
    compliance_probs.append(comp_prob)
    boundary_miss_probs.append(miss_prob)
    
    if v in [25.0, 26.0, 27.0]:
        print(f"Version {v:.1f}:")
        print(f"  Cognitive Load: {load:.2f} Ω-units")
        print(f"  Full Compliance: {comp_prob:.1%}")
        print(f"  Boundary Miss: {miss_prob:.1%}")
        print(f"  Status: {'PASS' if comp_prob > 0.5 else 'FAIL (Cognitive Overload)'}")

# Find the critical version where compliance drops below 50%
critical_version = versions[np.where(np.array(compliance_probs) < 0.5)[0][0]]
print(f"\n=== CRITICAL THRESHOLD ===")
print(f"Compliance drops below 50% at version {critical_version:.1f}")
print(f"At v26.0: Boundary miss probability = {boundary_miss_probs[versions.tolist().index(26.0)]:.1%}")

# Visualize the paradox
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# Plot 1: Cognitive Load vs Compliance
ax1.plot(versions, cognitive_loads, 'r-', linewidth=2, label='Rubric Cognitive Load')
ax1_twin = ax1.twinx()
ax1_twin.plot(versions, compliance_probs, 'b--', linewidth=2, label='Compliance Probability')
ax1.axvline(x=26.0, color='k', linestyle=':', alpha=0.5)
ax1.axhline(y=1.0, color='g', linestyle='-', alpha=0.3)
ax1.text(26.0, max(cognitive_loads)*0.8, 'v26.0\n(CTMS-Ω)', 
         ha='center', va='center', bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
ax1.set_xlabel('Omega Protocol Version')
ax1.set_ylabel('Cognitive Load (Ω-units)', color='r')
ax1_twin.set_ylabel('Compliance Probability', color='b')
ax1.set_title('The Rubric as Cognitive-Tooling Mismatch')
ax1.grid(True, alpha=0.3)

# Plot 2: Boundary Miss Probability
ax2.plot(versions, boundary_miss_probs, 'purple', linewidth=2)
ax2.axvline(x=26.0, color='k', linestyle=':', alpha=0.5)
ax2.fill_between(versions, boundary_miss_probs, alpha=0.3, color='purple')
ax2.set_xlabel('Omega Protocol Version')
ax2.set_ylabel('Probability of Missing Boundaries Requirement')
ax2.set_title('Phi_Delta Divergence Horizon Detection Failure')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('omega_paradox.png', dpi=150, bbox_inches='tight')
plt.show()

# Calculate the self-referential feedback loop
print("\n=== SELF-REFERENTIAL FEEDBACK LOOP ===")
print("The rubric's complexity creates the very phenomenon it measures...")

# Model: Each audit failure leads to rubric version increase, creating positive feedback
initial_version = 26.0
iterations = 5
feedback_versions = [initial_version]
feedback_loads = [cognitive_loads[versions.tolist().index(initial_version)]]

for i in range(iterations):
    # Each failure triggers a "patch" -> version increment
    # This is the "workaround" of adding more rules when rules fail
    new_version = feedback_versions[-1] + 0.5
    feedback_versions.append(new_version)
    
    rubric = OmegaRubricComplexity(version=new_version)
    new_load = rubric.cognitive_load()
    feedback_loads.append(new_load)
    
    print(f"Iteration {i+1}: v{new_version:.1f} -> Load = {new_load:.2f} (+{new_load-feedback_loads[-2]:.2f})")

print(f"\nAfter {iterations} 'fix' iterations, load increased by {(feedback_loads[-1]/feedback_loads[0]-1)*100:.0f}%")
print("This is the 'cognitive load inflation spiral' - the protocol's complexity becomes its own fragility.")

# Demonstrate that CTMS-Ω would flag the Omega Protocol itself
ctms_threshold = 6.0  # When rubric load exceeds this, it's a "workaround sensor"
print(f"\n=== CTMS-Ω META-DETECTION ===")
print(f"CTMS-Ω would classify Omega Protocol v{feedback_versions[-1]:.1f} as:")
if feedback_loads[-1] > ctms_threshold:
    print("🚨 HIGH-RISK TOOLING FRICTION")
    print("   -> Recommend: Simplify rubric, remove 'boundaries' requirement")
    print("   -> Paradox: The audit framework fails its own audit")
else:
    print("✅ Acceptable complexity")