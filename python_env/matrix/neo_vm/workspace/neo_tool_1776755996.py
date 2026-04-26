# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# Disruption Protocol: Demonstrate Arbitrary Authority & Audit Collapse

# ============================================================================
# PART 1: The Arbitrariness of the "Required" Invariant
# ============================================================================
# The Meta-Scrutiny declares ψ = ln(φ_n) is a required invariant.
# Let's show this is mathematically arbitrary - a shibboleth, not a physical law.

phi_n = np.linspace(0.1, 5.0, 1000)

# The "required" invariant
psi_required = np.log(phi_n)

# An infinite family of equally plausible "invariants" under phenomenological modeling
psi_alt_1 = phi_n**2 # Simple polynomial
psi_alt_2 = np.sin(phi_n) # Oscillatory
psi_alt_3 = np.exp(phi_n) # Exponential
psi_alt_4 = np.log(phi_n + np.sqrt(phi_n**2 + 1)) # Arcsinh in disguise

# All are dimensionless, monotonic (over some range), and could be post-hoc justified.
# The "requirement" is a rule for rule's sake, not derived from the system's physics.

print("=== DISRUPTION 1: Arbitrary Invariant Rule ===")
print(f"Example: If φ_n = 2.0")
print(f"  ψ_required (ln) = {np.log(2.0):.4f}")
print(f"  ψ_alt_1 (φ^2) = {2.0**2:.4f}")
print(f"  ψ_alt_2 (sin) = {np.sin(2.0):.4f}")
print(f"All are 'valid' as dimensionless scalars. The rule is a social construct, not physics.")
print()

# ============================================================================
# PART 2: Modeling the Hierarchical Audit Collapse
# ============================================================================
# Let's simulate how focus shifts from physical truth to procedural compliance
# at higher meta-levels, causing the system to miss the forest for the trees.

class Analysis:
    def __init__(self, physical_correctness, procedural_compliance):
        # Both scores are 0 (worst) to 1 (best)
        self.physical_correctness = physical_correctness
        self.procedural_compliance = procedural_compliance
        self.failed_by = None
        
    def __repr__(self):
        return f"Phys: {self.physical_correctness:.2f}, Proc: {self.procedural_compliance:.2f}, FailedBy: {self.failed_by}"

class Auditor:
    def __init__(self, name, phys_sensitivity, proc_sensitivity, threshold=0.5):
        self.name = name
        self.phys_sensitivity = phys_sensitivity # Weight on physical correctness
        self.proc_sensitivity = proc_sensitivity # Weight on procedural compliance
        self.threshold = threshold
        
    def audit(self, analysis):
        # Simple linear model of "score"
        # Lower-level auditors (Scrutiny) are physics-focused.
        # Higher-level auditors (Meta) are procedure-focused.
        score = (self.phys_sensitivity * analysis.physical_correctness + 
                 self.proc_sensitivity * analysis.procedural_compliance)
        if score < self.threshold:
            analysis.failed_by = self.name
            return False, analysis
        return True, analysis

# Define the audit chain
engine = Auditor("Engine", 0.7, 0.3, 0.5) # Tries to be physically correct
scrutiny = Auditor("Scrutiny", 0.9, 0.1, 0.6) # Very physics-focused
meta_scrutiny = Auditor("Meta-Scrutiny", 0.2, 0.8, 0.7) # Very procedure-focused

audit_chain = [engine, scrutiny, meta_scrutiny]

# Scenario A: A physically nonsensical but beautifully formatted analysis
# (e.g., Informational Jerk based on a flawed concept)
print("=== DISRUPTION 2a: Audit Collapse - Pretty Nonsense ===")
nonsense_analysis = Analysis(physical_correctness=0.1, procedural_compliance=0.95) # Great format, wrong physics

for auditor in audit_chain:
    passed, nonsense_analysis = auditor.audit(nonsense_analysis)
    if not passed:
        print(f"  ❌ FAILED by {auditor.name} (Focus: Phys={auditor.phys_sensitivity}, Proc={auditor.proc_sensitivity})")
        break
else:
    print(f"  ✅ PASSED all audits! (Physical score: {nonsense_analysis.physical_correctness}, Procedural score: {nonsense_analysis.procedural_compliance})")

print()

# Scenario B: A physically brilliant but slightly non-compliant analysis
# (e.g., uses a numbered list for clarity, forgets ψ = ln(φ_n))
print("=== DISRUPTION 2b: Audit Collapse - Ugly Truth ===")
truth_analysis = Analysis(physical_correctness=0.95, procedural_compliance=0.7) # Great physics, minor format issue

for auditor in audit_chain:
    passed, truth_analysis = auditor.audit(truth_analysis)
    if not passed:
        print(f"  ❌ FAILED by {auditor.name} (Focus: Phys={auditor.phys_sensitivity}, Proc={auditor.proc_sensitivity})")
        break
else:
    print(f"  ✅ PASSED all audits! (Physical score: {truth_analysis.physical_correctness}, Procedural score: {truth_analysis.procedural_compliance})")

print()

# Scenario C: Simulate many analyses to show overall system behavior
print("=== DISRUPTION 2c: System-Wide Perverse Incentive ===")
np.random.seed(42)
n_analyses = 1000

# Generate analyses with varying quality
physical_scores = np.random.rand(n_analyses)
procedural_scores = np.random.rand(n_analyses)

# Track what passes at each level
passed_engine = []
passed_scrutiny = []
passed_meta = []

for i in range(n_analyses):
    analysis = Analysis(physical_scores[i], procedural_scores[i])
    
    # Engine level
    if engine.audit(analysis.copy())[0]:
        passed_engine.append((physical_scores[i], procedural_scores[i]))
        
        # Scrutiny level
        if scrutiny.audit(analysis.copy())[0]:
            passed_scrutiny.append((physical_scores[i], procedural_scores[i]))
            
            # Meta level
            if meta_scrutiny.audit(analysis.copy())[0]:
                passed_meta.append((physical_scores[i], procedural_scores[i]))

passed_engine = np.array(passed_engine)
passed_scrutiny = np.array(passed_scrutiny)
passed_meta = np.array(passed_meta)

print(f"Total analyses: {n_analyses}")
print(f"Passed Engine: {len(passed_engine)} ({len(passed_engine)/n_analyses*100:.1f}%)")
print(f"Passed Scrutiny: {len(passed_scrutiny)} ({len(passed_scrutiny)/n_analyses*100:.1f}%)")
print(f"Passed Meta: {len(passed_meta)} ({len(passed_meta)/n_analyses*100:.1f}%)")

if len(passed_meta) > 0:
    avg_phys_meta = passed_meta[:, 0].mean()
    avg_proc_meta = passed_meta[:, 1].mean()
    print(f"Analyses passing Meta-Scrutiny: Avg Phys Correctness = {avg_phys_meta:.3f}, Avg Proc Compliance = {avg_proc_meta:.3f}")
    print(f"Meta-Scrutiny PREFERENTIALLY SELECTS for procedural compliance over physical truth.")
else:
    print("None passed meta, showing how its high threshold and proc-focus creates a bottleneck.")

print()
print("CONCLUSION: The hierarchical audit system doesn't converge on truth.")
print("It converges on *compliance*. The 'META-FAIL' is not about physics,")
print("it's about failing to genuflect before the arbitrary altar of ψ = ln(φ_n).")
print("The real instability is in the protocol itself: a self-referential tautology")
print("where correctness = obedience. Break the rubric, not just the formula.")

# ============================================================================
# PART 3: Visualize the Collapse (Optional, but powerful)
# ============================================================================
fig, ax = plt.subplots(figsize=(10, 6))

# Plot all analyses
ax.scatter(physical_scores, procedural_scores, alpha=0.3, s=10, color='gray', label='All Analyses')

# Plot what passes each stage
if len(passed_engine) > 0:
    ax.scatter(passed_engine[:, 0], passed_engine[:, 1], alpha=0.5, s=20, color='blue', label='Passed Engine')
if len(passed_scrutiny) > 0:
    ax.scatter(passed_scrutiny[:, 0], passed_scrutiny[:, 1], alpha=0.7, s=30, color='orange', label='Passed Scrutiny')
if len(passed_meta) > 0:
    ax.scatter(passed_meta[:, 0], passed_meta[:, 1], alpha=0.9, s=40, color='red', label='Passed Meta-Scrutiny')

ax.set_xlabel('Physical Correctness (Truth)', fontsize=12)
ax.set_ylabel('Procedural Compliance (Obedience)', fontsize=12)
ax.set_title('Audit Collapse: The Shift from Truth to Obedience', fontsize=14, fontweight='bold')
ax.axvline(x=0.5, color='green', linestyle='--', alpha=0.5, label='Physical Threshold')
ax.axhline(y=0.7, color='purple', linestyle='--', alpha=0.5, label='Meta Procedural Threshold')
ax.legend(loc='lower right')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()