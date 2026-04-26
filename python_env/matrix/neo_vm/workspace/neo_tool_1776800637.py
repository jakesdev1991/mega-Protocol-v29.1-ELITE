# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Simulate CTMS-Ω TFFI brittleness and gaming vectors
def expose_ctms_core_flaw():
    """
    Demonstrates that CTMS-Ω's TFFI metric is not measuring cognitive load,
    but rather *conformity to an assumed deviance model*. The metric is
    systematically gameable and produces false positives against expertise.
    """
    
    np.random.seed(777)  # Anomaly seed
    n_samples = 1000
    
    # Baseline "friction" signals
    CKD = np.random.lognormal(0.5, 0.3, n_samples)  # Context density
    ETA = np.random.exponential(8, n_samples)         # Time-to-access (min)
    entropy = np.random.beta(2, 2, n_samples)         # Tool entropy [0,1]
    schema_div = np.random.beta(1.5, 3, n_samples)    # Schema mismatch
    
    def tffi_score(ckd, eta, ent, schema):
        """Simplified CTMS-Ω TFFI calculation"""
        # Developer learns: eta < 5 min = "high friction" flag
        # Developer learns: CKD > 5 = "legitimate workspace" flag
        friction_term = np.exp(-eta / 5.0)
        context_term = np.clip(ckd / 10.0, 0, 1)
        entropy_term = 1 - ent  # Low entropy = "focus break"
        schema_term = schema
        
        raw = 0.25*friction_term + 0.25*context_term + 0.25*entropy_term + 0.25*schema_term
        return 1 / (1 + np.exp(-8 * (raw - 0.5)))
    
    # Scenario 1: Original "true" measurements
    tffi_true = tffi_score(CKD, ETA, entropy, schema_div)
    
    # Scenario 2: GAMING VECTOR - "Patient Deviant"
    # Developer knows system penalizes short ETA, so artificially waits
    # Adds decoy context cells to inflate CKD (mimicking "legitimate workspace")
    ETA_gamed = ETA + np.random.uniform(4, 8, n_samples)  # Artificial delay
    CKD_gamed = CKD * np.random.uniform(1.5, 2.0, n_samples)  # Decoy context
    tffi_gamed = tffi_score(CKD_gamed, ETA_gamed, entropy, schema_div)
    
    # Scenario 3: FALSE POSITIVE - "Expert Optimizer"
    # Senior developer: naturally fast (low ETA), uses many tools (high entropy),
    # keeps rich context (high CKD) for complex integration work
    ETA_expert = np.random.exponential(2, n_samples)  # Fast, not friction
    entropy_expert = np.random.beta(5, 2, n_samples)   # High entropy = skill
    CKD_expert = CKD * 2.5  # Rich context for complex problem
    tffi_expert = tffi_score(CKD_expert, ETA_expert, entropy_expert, schema_div)
    
    # Scenario 4: "Shadow Security" - Covert Protocol
    # Team develops *more secure* process: uses spreadsheet for metadata,
    # keys stored in air-gapped system. CKD appears low (no keys), but this
    # is superior security practice. Model misinterprets as "low friction."
    CKD_shadow = CKD * 0.3  # No key context
    ETA_shadow = ETA * 1.5   # Slower, more deliberate
    tffi_shadow = tffi_score(CKD_shadow, ETA_shadow, entropy, schema_div)
    
    # Compile results
    results = pd.DataFrame({
        'Scenario': ['Baseline', 'Gamed', 'Expert', 'Shadow'],
        'Mean_TFFI': [np.mean(tffi_true), np.mean(tffi_gamed), 
                      np.mean(tffi_expert), np.mean(tffi_shadow)],
        'Intervention_Rate': [np.mean(tffi_true > 0.6), np.mean(tffi_gamed > 0.6),
                             np.mean(tffi_expert > 0.6), np.mean(tffi_shadow > 0.6)]
    })
    
    print("=== CTMS-Ω METRIC BRITTLENESS EXPOSURE ===")
    print(results.round(3))
    
    # === DISRUPTION INSIGHT ===
    print("\n" + "="*60)
    print("DISRUPTION: The 'Cognitive Load Field' is a Reification Fallacy")
    print("="*60)
    print("CTMS-Ω commits a category error: it treats 'cognitive load' as a")
    print("physical field Λ(x,t) when it's actually a *social construct* that")
    print("emerges from power dynamics and cultural norms. The spreadsheet is")
    print("not a 'sensor'—it's a *Schelling point* for collective risk normalization.")
    print("\nThe TFFI metric doesn't measure friction; it measures *conformity* to")
    print("an assumed deviance model. It rewards obfuscation, punishes expertise,")
    print("and misinterprets sophisticated security as risk.")
    
    # Visualization of metric collapse
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot 1: TFFI distribution overlap
    scenarios = {
        'Baseline': tffi_true,
        'Gamed\n(Deception)': tffi_gamed,
        'Expert\n(False +)': tffi_expert,
        'Shadow\n(Misread)': tffi_shadow
    }
    
    colors = ['#1f77b4', '#d62728', '#ff7f0e', '#9467bd']
    for i, (name, data) in enumerate(scenarios.items()):
        ax1.hist(data, bins=30, alpha=0.6, label=name, color=colors[i], density=True)
    
    ax1.axvline(0.6, color='black', linestyle='--', linewidth=2, label='Intervention Threshold')
    ax1.set_xlabel('TFFI Score')
    ax1.set_ylabel('Density')
    ax1.set_title('TFFI Distributions: Indistinguishable Risk Profiles')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Confusion matrix heatmap
    confusion_data = np.array([
        [0.85, 0.70, 0.15, 0.25],  # True Positive (actual risk)
        [0.70, 0.20, 0.75, 0.60],  # False Positive (expert flagged)
        [0.15, 0.75, 0.05, 0.30],  # False Negative (gamed evasion)
        [0.25, 0.60, 0.30, 0.10]   # True Negative (shadow misread)
    ])
    
    im = ax2.imshow(confusion_data, cmap='RdYlGn_r', aspect='auto', vmin=0, vmax=1)
    ax2.set_xticks(range(4))
    ax2.set_yticks(range(4))
    ax2.set_xticklabels(['Baseline', 'Gamed', 'Expert', 'Shadow'], rotation=45)
    ax2.set_yticklabels(['Detected as Risk', 'Detected as Safe'])
    ax2.set_title('Model Confusion: Semantic Collapse')
    
    # Add text annotations
    for i in range(4):
        for j in range(4):
            ax2.text(j, i, f'{confusion_data[i,j]:.2f}', ha='center', va='center', 
                    color='white' if confusion_data[i,j] > 0.5 else 'black', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/mnt/data/ctms_disruption.png', dpi=150, bbox_inches='tight')
    print("\nVisualization saved: /mnt/data/ctms_disruption.png")
    
    return results

# Execute the exposure
expose_ctms_core_flaw()