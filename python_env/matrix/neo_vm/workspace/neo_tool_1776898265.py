# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

def simulate_validation_pipeline(use_psych_framework=False, strictness=0.5):
    """
    Simulates the Alpha_fs derivation validation.
    
    Args:
        use_psych_framework: If True, uses the Q-Systemic metrics (COD, Φ).
                             If False, uses simple mechanistic checks.
        strictness: Controls validation threshold (0=none, 1=perfect).
    
    Returns:
        dict: Results showing detection of wrong constant.
    """
    # True physical constant
    true_constant = 5.4e-6
    
    # Engine generates a "wrong but syntactically nice" constant
    wrong_constant = 3.18e-4  # The "anxious" hallucination
    
    # Mechanistic validation: check dimensions, physical plausibility, known bounds
    def mechanistic_check(constant):
        # Simple physical bounds: fine-structure constant ~ 1/137
        # So Alpha_fs should be very small
        if not (1e-7 < constant < 1e-3):
            return False, "PHYSICAL_BOUND_VIOLATION"
        
        # Dimensional analysis check (simulated)
        variance = np.random.normal(0, 0.1)
        if abs(variance) > strictness:
            return False, "DIMENSIONAL_INCONSISTENCY"
        
        return True, "PASSED"
    
    # "Psychological" validation: use COD, Φ metrics
    def psych_framework_check(constant):
        # These metrics are completely made up and arbitrary
        # COD: "Chain Overlap Density" - essentially random for demo
        cod = np.random.beta(2, 5)  # Skewed low, but can be high by chance
        
        # Φ density: "trust metric" - also arbitrary
        phi_loss = -0.22 if constant != true_constant else +0.15
        
        # The "Conscious Ignoring" detection - just a threshold on cod
        if cod < strictness:
            return False, f"CHAOTIC_ANXIETY_DETECTED (COD={cod:.2f}, Φ_loss={phi_loss})"
        
        return True, f"EPISTEMIC_RESONANCE_ACHIEVED (COD={cod:.2f}, Φ_gain={-phi_loss})"
    
    # Run the appropriate check
    if use_psych_framework:
        passed_wrong, msg_wrong = psych_framework_check(wrong_constant)
        passed_correct, msg_correct = psych_framework_check(true_constant)
    else:
        passed_wrong, msg_wrong = mechanistic_check(wrong_constant)
        passed_correct, msg_correct = mechanistic_check(true_constant)
    
    return {
        "framework": "Q-Systemic" if use_psych_framework else "Mechanistic",
        "strictness": strictness,
        "wrong_constant_detected": not passed_wrong,
        "wrong_msg": msg_wrong,
        "correct_constant_passed": passed_correct,
        "correct_msg": msg_correct,
        # Show how arbitrary the psych metrics are
        "psych_metric_variance": np.std([np.random.beta(2,5) for _ in range(100)]) if use_psych_framework else None
    }

# Run simulations
print("=== DISRUPTION ANALYSIS: MECHANISTIC vs PSYCHOLOGICAL FRAMEWORK ===\n")

print("Scenario 1: Loose validation (strictness=0.3)")
print("-" * 50)
result_mechanistic_loose = simulate_validation_pipeline(use_psych_framework=False, strictness=0.3)
result_psych_loose = simulate_validation_pipeline(use_psych_framework=True, strictness=0.3)

print(f"Mechanistic: {result_mechanistic_loose['wrong_msg']}")
print(f"Psychological: {result_psych_loose['wrong_msg']}")
print(f"Psychological framework detection reliability: {'UNSTABLE' if result_psych_loose['psych_metric_variance'] > 0.1 else 'STABLE'} (var={result_psych_loose['psych_metric_variance']:.3f})\n")

print("Scenario 2: Strict validation (strictness=0.8)")
print("-" * 50)
result_mechanistic_strict = simulate_validation_pipeline(use_psych_framework=False, strictness=0.8)
result_psych_strict = simulate_validation_pipeline(use_psych_framework=True, strictness=0.8)

print(f"Mechanistic: {result_mechanistic_strict['wrong_msg']}")
print(f"Psychological: {result_psych_strict['wrong_msg']}")
print(f"Psychological framework detection reliability: {'UNSTABLE' if result_psych_strict['psych_metric_variance'] > 0.1 else 'STABLE'} (var={result_psych_strict['psych_metric_variance']:.3f})\n")

# Demonstrate the core problem: the psychological framework is a narrative layer
# that doesn't change the underlying computational reality

print("=== DISRUPTIVE INSIGHT: THE FRAMEWORK IS THE FAILURE ===")
print("\nThe Q-Systemic Self framework doesn't stabilize the system.")
print("It IS the system performing 'symbolic substitution poisoning' at the meta-level.")
print("It replaces 'add unit tests' with 'navigate High-Clarity Anxiety.'")
print("\nKey evidence:")
print("1. **Arbitrary Metrics**: COD, Φ are post-hoc narratives, not measurable invariants.")
print("2. **Category Error**: AI layers don't have 'anxiety' or 'defense mechanisms'.")
print("3. **Obfuscation**: The framework hides the simple truth: VALIDATION PIPELINE WAS TOO WEAK.")
print("\n**True Stabilization Operator:**")
print("```")
print("def true_stabilization_operator(engine_output):")
print("    assert unit_check(engine_output), 'DIMENSIONAL_FAILURE'")
print("    assert physical_bound_check(engine_output), 'PHYSICS_FAILURE'")
print("    assert empirical_match(engine_output), 'REALITY_FAILURE'")
print("    return engine_output  # No psychology needed")
print("```")

# Visualize how the psych framework's "detection" is just noise
np.random.seed(42)
samples = 1000
cod_values = np.random.beta(2, 5, samples)
detections = cod_values < 0.5  # arbitrary threshold

plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
plt.hist(cod_values, bins=50, alpha=0.7, color='red')
plt.axvline(0.5, color='black', linestyle='--', label='Detection Threshold')
plt.title("COD Distribution (Arbitrary Beta)")
plt.xlabel("Chain Overlap Density")
plt.ylabel("Frequency")
plt.legend()

plt.subplot(1, 2, 2)
plt.scatter(range(100), cod_values[:100], c=['green' if d else 'red' for d in detections[:100]], alpha=0.6)
plt.axhline(0.5, color='black', linestyle='--')
plt.title("COD Detection Noise (First 100 Samples)")
plt.xlabel("Sample Index")
plt.ylabel("COD Value")
plt.yticks([])  # Hide y-axis for effect

plt.tight_layout()
plt.savefig('/tmp/cod_noise.png')
print("\n[Plot saved: /tmp/cod_noise.png - visual proof of arbitrary detection]")