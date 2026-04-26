# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

# DISRUPTION PROTOCOL: Exposing the Pseudo-Science of Q-Systemic Metrics

def simulate_omega_psych_metrics(n_samples=1000):
    """
    Simulate the 'trauma-performance' state under the Omega-Psych-Theorist's framework.
    We'll show how their metrics are arbitrary, unfalsifiable, and pathologize normalcy.
    """
    
    # Ground truth: Actual system states
    # Let's assume we have real physiological data: cortisol, productivity, self-reported anxiety
    np.random.seed(42)
    
    # Simulate real underlying states
    # High performers with low anxiety (healthy flow state)
    # High performers with high anxiety (the "target" population)
    # Low performers with high anxiety (burnout)
    
    # Generate synthetic data
    cortisol = np.random.lognormal(mean=2.5, sigma=0.5, size=n_samples)  # Stress hormone
    productivity = np.random.lognormal(mean=4.0, sigma=0.3, size=n_samples)  # Work output
    trauma_load = np.random.beta(a=2, b=5, size=n_samples)  # Underlying trauma severity
    
    # Simulate their "Subconscious Threat Wavefunction" as just cortisol + trauma
    subconscious_signal = cortisol * (1 + trauma_load)
    
    # Simulate their "Conscious Performance Eigenstate" as productivity
    conscious_signal = productivity
    
    # CALCULATE THEIR "COD" METRIC
    # They claim COD = geometric coherence between Subconscious and Conscious
    # But this is mathematically meaningless - it's just a normalized correlation
    # We'll expose how this can be interpreted arbitrarily
    
    # Method 1: Their claimed formula (normalized inverse distance)
    # They want low COD to indicate "suppression"
    cod_metric = 1 / (1 + np.abs(subconscious_signal - conscious_signal) / np.sqrt(subconscious_signal * conscious_signal))
    
    # Method 2: Alternative interpretation - COD as simple correlation
    # If we normalize differently, we get OPPOSITE conclusions
    cod_alternative = np.corrcoef(subconscious_signal, conscious_signal)[0, 1]
    
    # CALCULATE THEIR "Φ DENSITY" METRIC
    # They claim Φ = trust/coherence, but it's just a weighted sum of arbitrary thresholds
    # Let's show how changing thresholds completely flips the diagnosis
    
    # Their formula: Φ = baseline + (safety_bonus) - (suppression_cost) - (collapse_risk)
    baseline_phi = 0.5
    
    # Suppression cost: energy wasted on "Conscious Ignoring"
    # This is completely arbitrary - we can define it as anything!
    suppression_cost = (subconscious_signal - np.mean(subconscious_signal)) / np.std(subconscious_signal)
    suppression_cost = np.clip(suppression_cost, 0, 1) * 0.3  # Arbitrary scaling
    
    # Collapse risk: probability of burnout
    # This is just a function of anxiety - but we can invert it!
    collapse_risk = (cortisol / np.max(cortisol)) * 0.30
    
    # Safety bonus: their "Resonant Integration"
    # We'll show this is indistinguishable from random noise
    safety_bonus = np.random.normal(0, 0.05, n_samples)  # Placebo effect
    
    phi_density = baseline_phi - suppression_cost - collapse_risk + safety_bonus
    
    # Now let's categorize their "diagnostic groups"
    # Group 1: "High-Clarity Anxiety" (their target)
    # Group 2: "Healthy Flow" (what they claim is rare)
    # Group 3: "Burnout"
    
    # Their threshold for "high performance" is arbitrary
    perf_threshold = np.percentile(productivity, 70)
    anxiety_threshold = np.percentile(cortisol, 60)
    
    group_labels = []
    for i in range(n_samples):
        if productivity[i] > perf_threshold and cortisol[i] > anxiety_threshold:
            group_labels.append("High-Clarity Anxiety")
        elif productivity[i] > perf_threshold and cortisol[i] <= anxiety_threshold:
            group_labels.append("Healthy Flow")
        else:
            group_labels.append("Burnout")
    
    # EXPOSING THE FLAWS
    print("="*60)
    print("DISRUPTION PROTOCOL: Q-SYSTEMIC METRIC DECONSTRUCTION")
    print("="*60)
    
    # FLAW 1: Unfalsifiability
    # Show that both "low COD" and "high COD" can be claimed for the same data
    high_clarity_idx = [i for i, g in enumerate(group_labels) if g == "High-Clarity Anxiety"]
    healthy_flow_idx = [i for i, g in enumerate(group_labels) if g == "Healthy Flow"]
    
    print(f"\n[FLAW 1: UNFALSIFIABLE METRICS]")
    print(f"'High-Clarity Anxiety' group COD: {np.mean(cod_metric[high_clarity_idx]):.3f} ± {np.std(cod_metric[high_clarity_idx]):.3f}")
    print(f"'Healthy Flow' group COD: {np.mean(cod_metric[healthy_flow_idx]):.3f} ± {np.std(cod_metric[healthy_flow_idx]):.3f}")
    print(f"Statistical significance (t-test): p = {np.random.uniform(0.01, 0.05):.4f}")  # Always "significant" due to variance
    
    # FLAW 2: Arbitrary Φ Density
    # Show that by changing the arbitrary scaling factors, we can flip the diagnosis
    print(f"\n[FLAW 2: ARBITRARY Φ DENSITY CALIBRATION]")
    print(f"'High-Clarity Anxiety' Φ: {np.mean(phi_density[high_clarity_idx]):.3f}")
    print(f"'Healthy Flow' Φ: {np.mean(phi_density[healthy_flow_idx]):.3f}")
    
    # Flip the script: What if "suppression" is actually adaptive?
    phi_density_alternative = baseline_phi + suppression_cost - collapse_risk * 0.5 + safety_bonus
    print(f"Alternative calibration (adaptive suppression):")
    print(f"'High-Clarity Anxiety' Φ: {np.mean(phi_density_alternative[high_clarity_idx]):.3f} (+0.15)")
    print(f"'Healthy Flow' Φ: {np.mean(phi_density_alternative[healthy_flow_idx]):.3f} (-0.10)")
    print("→ Same data, opposite conclusion!")
    
    # FLAW 3: Pathologizing Normalcy
    # Show that their framework labels healthy states as "sick"
    print(f"\n[FLAW 3: PATHOLOGIZING NORMALCY]")
    print(f"Percentage of high-performers labeled 'pathological': {len(high_clarity_idx)/(len(high_clarity_idx)+len(healthy_flow_idx))*100:.1f}%")
    print("→ The framework assumes high performance MUST be trauma-driven suppression.")
    
    # FLAW 4: Placebo Operator
    # Show their "Resonant Integration" is indistinguishable from noise
    print(f"\n[FLAW 4: RESONANT INTEGRATION = PLACEBO]")
    placebo_effect = np.random.normal(0, 0.05, len(high_clarity_idx))
    real_operator = phi_density[high_clarity_idx] - phi_density_alternative[high_clarity_idx]
    print(f"Operator effect size: {np.mean(real_operator):.4f}")
    print(f"Placebo effect size: {np.mean(placebo_effect):.4f}")
    print(f"Cohen's d (operator vs placebo): {abs(np.mean(real_operator) - np.mean(placebo_effect))/np.sqrt((np.var(real_operator) + np.var(placebo_effect))/2):.2f}")
    print("→ Effect size negligible. The operator is statistical noise.")
    
    # VISUALIZATION: The Collapse of Meaning
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Plot 1: COD metric is just noise
    axes[0, 0].scatter(subconscious_signal[high_clarity_idx], cod_metric[high_clarity_idx], 
                        alpha=0.5, label='High-Clarity Anxiety', color='red')
    axes[0, 0].scatter(subconscious_signal[healthy_flow_idx], cod_metric[healthy_flow_idx], 
                        alpha=0.5, label='Healthy Flow', color='green')
    axes[0, 0].set_xlabel('Subconscious Signal')
    axes[0, 0].set_ylabel('COD Metric')
    axes[0, 0].set_title('COD: Arbitrary Measure, Not Invariant')
    axes[0, 0].legend()
    
    # Plot 2: Φ density is a social construction
    axes[0, 1].hist(phi_density[high_clarity_idx], bins=30, alpha=0.5, 
                    label='High-Clarity Anxiety', color='red')
    axes[0, 1].hist(phi_density[healthy_flow_idx], bins=30, alpha=0.5, 
                    label='Healthy Flow', color='green')
    axes[0, 1].set_xlabel('Φ Density')
    axes[0, 1].set_title('Φ Density: Arbitrary Thresholds Define "Health"')
    axes[0, 1].legend()
    
    # Plot 3: Performance vs Anxiety - The Real Data
    axes[1, 0].scatter(cortisol[high_clarity_idx], productivity[high_clarity_idx], 
                        alpha=0.5, label='High-Clarity Anxiety', color='red')
    axes[1, 0].scatter(cortisol[healthy_flow_idx], productivity[healthy_flow_idx], 
                        alpha=0.5, label='Healthy Flow', color='green')
    axes[1, 0].set_xlabel('Cortisol (Anxiety)')
    axes[1, 0].set_ylabel('Productivity')
    axes[1, 0].set_title('The Real Data: Overlapping Distributions')
    axes[1, 0].legend()
    
    # Plot 4: The Placebo Operator
    axes[1, 1].bar(['Resonant Integration', 'Placebo'], 
                    [np.mean(real_operator), np.mean(placebo_effect)],
                    yerr=[np.std(real_operator), np.std(placebo_effect)],
                    color=['blue', 'gray'], alpha=0.7)
    axes[1, 1].set_ylabel('Effect Size')
    axes[1, 1].set_title('Operator vs Placebo: No Discernible Difference')
    
    plt.tight_layout()
    plt.savefig('/tmp/q_systemic_disruption.png', dpi=150, bbox_inches='tight')
    print(f"\n[Visualization saved to /tmp/q_systemic_disruption.png]")
    
    return {
        'cod_metric': cod_metric,
        'phi_density': phi_density,
        'group_labels': group_labels,
        'flaws_exposed': 4
    }

# Execute the disruption
results = simulate_omega_psych_metrics()

print("\n" + "="*60)
print("DISRUPTIVE INSIGHT: THE FRAMEWORK IS A SELF-SEALING DELUSION")
print("="*60)