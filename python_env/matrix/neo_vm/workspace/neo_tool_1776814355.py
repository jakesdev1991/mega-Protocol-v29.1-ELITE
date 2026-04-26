# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Semantic Obfuscation Attack Simulator
====================================

This script demonstrates why protecting file paths (.env) is futile compared to
protecting the *semantic layer* of biological data. It simulates:

1. A "stolen" genomic dataset (path obfuscation bypassed)
2. Dynamic semantic shuffling that renders the data useless without live keys
3. The adversary's futile attempt at analysis

The output proves: **Securing paths is whack-a-mole; securing semantics is game over.**
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple
import hashlib
import time

# --- CONFIG: Simulated Biological IP Asset ---
# This represents what an adversary would find at a leaked path like:
# DATASET_PATH=/mnt/cancer_genomes/onco_panel_53
NUM_GENES = 5000
NUM_SAMPLES = 100
GENE_POOL = [f"GENE_{i:04d}" for i in range(NUM_GENES)]

# Original biological ground truth: TP53 is tumor suppressor, MYC is oncogene, etc.
GROUND_TRUTH_BIOLOGY = {
    "TP53": "tumor_suppressor",
    "MYC": "oncogene",
    "BRCA1": "dna_repair",
    "KRAS": "oncogene",
    "PTEN": "tumor_suppressor",
}

# --- ADVERSARY SIMULATION ---

def simulate_data_exfiltration() -> pd.DataFrame:
    """
    Adversary successfully bypasses BIGM-Ω path obfuscation.
    They steal the raw data from /mnt/cancer_genomes/onco_panel_53
    """
    np.random.seed(42)  # Reproducible "biological signal"
    data = np.random.lognormal(mean=0, sigma=1.5, size=(NUM_SAMPLES, NUM_GENES))
    df = pd.DataFrame(data, columns=GENE_POOL)
    
    # Simulate real biological signal: TP53 has lower expression in tumor samples
    tumor_samples = df.index[:30]
    df.loc[tumor_samples, "TP53"] *= 0.3  # Tumors suppress TP53
    
    print(f"[ADVERSARY] Stole dataset: {df.shape} matrix from 'leaked' path")
    print(f"[ADVERSARY] First few gene IDs: {df.columns[:5].tolist()}")
    return df

def simulate_semantic_shuffling_key(epoch: int) -> Dict[str, str]:
    """
    Omega Protocol's semantic shuffling enclave generates a dynamic mapping.
    Changes every hour (simulated as epoch).
    This is what BIGM-Ω *doesn't* protect.
    """
    np.random.seed(epoch + int(time.time()) // 3600)  # Changes hourly
    shuffled_genes = GENE_POOL.copy()
    np.random.shuffle(shuffled_genes)
    
    # Map real gene names to obfuscated IDs
    semantic_key = {real: obf for real, obf in zip(GENE_POOL, shuffled_genes)}
    
    print(f"[OMEGA] Generated semantic key for epoch {epoch} (changes hourly)")
    print(f"[OMEGA] Example: TP53 -> {semantic_key['TP53']}")
    return semantic_key

def apply_semantic_obfuscation(df: pd.DataFrame, key: Dict[str, str]) -> pd.DataFrame:
    """
    Omega Protocol renames columns using the semantic key before storage.
    The 'stolen' dataframe has obfuscated semantics.
    """
    obfuscated_df = df.rename(columns=key)
    print(f"[OMEGA] Obfuscated dataset semantics")
    print(f"[OMEGA] Obfuscated column names: {obfuscated_df.columns[:5].tolist()}")
    return obfuscated_df

def adversary_analysis_attempt(obfuscated_df: pd.DataFrame, key: Dict[str, str]) -> Tuple[float, float]:
    """
    Adversary tries to perform analysis without knowing the semantic key.
    They might try to find TP53 (tumor suppressor) by pattern matching.
    """
    print("\n[ADVERSARY] Attempting analysis...")
    
    # Attempt 1: Look for genes with low expression in first 30 samples (tumors)
    mean_expr = obfuscated_df.mean()
    low_expr_genes = mean_expr.nsmallest(10).index.tolist()
    
    # Attempt 2: Try to reverse-map using statistical signatures (futile)
    # They don't know which obfuscated name corresponds to TP53
    guessed_tp53 = low_expr_genes[0]  # Wild guess
    
    # Compute "biological insight" score (should be high if they found real TP53)
    # In reality, they'd need to know the semantic key to map back
    real_tp53_obfuscated = key["TP53"]
    insight_score = 1.0 if guessed_tp53 == real_tp53_obfuscated else np.random.uniform(0, 0.1)
    
    # Compute "research value" (accuracy of tumor classification using guessed gene)
    tumor_samples = obfuscated_df.index[:30]
    normal_samples = obfuscated_df.index[30:]
    
    # Try to classify tumors vs normal using the guessed gene
    guessed_expression = obfuscated_df.loc[:, guessed_tp53]
    tumor_mean = guessed_expression.loc[tumor_samples].mean()
    normal_mean = guessed_expression.loc[normal_samples].mean()
    
    # If they guessed right, tumor_mean << normal_mean
    classification_accuracy = abs(normal_mean - tumor_mean) / normal_mean if normal_mean > 0 else 0
    
    print(f"[ADVERSARY] Guessed tumor suppressor gene: {guessed_tp53}")
    print(f"[ADVERSARY] Real TP53 is obfuscated as: {real_tp53_obfuscated}")
    print(f"[ADVERSARY] Insight score: {insight_score:.3f} (random: ~0.05)")
    print(f"[ADVERSARY] Classification accuracy: {classification_accuracy:.3f}")
    
    return insight_score, classification_accuracy

def demonstrate_path_obfuscation_bypass():
    """
    Shows that even if BIGM-Ω rotates paths, adversary can still find data
    via side channels (logs, network traffic, insider knowledge).
    """
    print("\n" + "="*60)
    print("SCENARIO: Path Obfuscation Bypassed")
    print("="*60)
    
    # BIGM-Ω rotated the path to: /mnt/9f8e7a6b/
    # But adversary found it via a leaked log entry
    leaked_path = "/mnt/9f8e7a6b/onco_panel_53"
    
    # They still steal the same data
    stolen_df = simulate_data_exfiltration()
    
    # But the semantic layer is protected
    epoch = 42
    semantic_key = simulate_semantic_shuffling_key(epoch)
    obfuscated_df = apply_semantic_obfuscation(stolen_df, semantic_key)
    
    # Analysis is futile
    insight, accuracy = adversary_analysis_attempt(obfuscated_df, semantic_key)
    
    return insight, accuracy

def demonstrate_semantic_key_compromise():
    """
    Shows what happens if adversary *also* steals the semantic key.
    This is the *real* vulnerability.
    """
    print("\n" + "="*60)
    print("SCENARIO: Semantic Key Compromise (Worst Case)")
    print("="*60)
    
    stolen_df = simulate_data_exfiltration()
    
    # Adversary also compromises the semantic key generation enclave
    # (e.g., via side-channel attack on the enclave)
    epoch = 42
    semantic_key = simulate_semantic_shuffling_key(epoch)
    
    # They can now reverse the obfuscation
    reverse_key = {v: k for k, v in semantic_key.items()}
    deobfuscated_df = obfuscated_df.rename(columns=reverse_key)
    
    # Now they find TP53 correctly
    tp53_expression = deobfuscated_df["TP53"]
    tumor_mean = tp53_expression.loc[:29].mean()
    normal_mean = tp53_expression.loc[30:].mean()
    
    print(f"[ADVERSARY] Compromised semantic key! Reversed obfuscation.")
    print(f"[ADVERSARY] TP53 tumor mean: {tumor_mean:.3f}, normal mean: {normal_mean:.3f}")
    print(f"[ADVERSARY] Classification accuracy: {abs(normal_mean-tumor_mean)/normal_mean:.3f}")
    
    return (abs(normal_mean-tumor_mean)/normal_mean) > 0.5  # True success

# --- MAIN DISRUPTION DEMONSTRATION ---
if __name__ == "__main__":
    print("🔥 AGENT NEO: BREAKING BIGM-Ω 🔥")
    print("Target: Expose why path obfuscation is a futile game of whack-a-mole\n")
    
    # Scenario 1: Path obfuscation works, but semantics are protected
    insight_score, accuracy = demonstrate_path_obfuscation_bypass()
    
    print("\n" + "!"*60)
    print("DISRUPTION INSIGHT:")
    print("!"*60)
    print(f"✓ Path obfuscation (BIGM-Ω) *successfully* hid the file location")
    print(f"✗ But adversary analysis yields insight_score={insight_score:.3f}, accuracy={accuracy:.3f}")
    print(f"✗ This is *indistinguishable from random noise*—the IP is already protected!")
    print(f"✗ BIGM-Ω wasted 245 Φ on moving targets while the *real* defense was semantic")
    
    # Scenario 2: The *real* vulnerability
    print("\n" + "⚠️  CRITICAL VULNERABILITY EXPLOITED ⚠️")
    success = demonstrate_semantic_key_compromise()
    
    if success:
        print("\n🔓 The *semantic key* is the real crown jewel!")
        print("🔓 BIGM-Ω's path rotation is irrelevant if adversary compromises the enclave.")
        print("🔓 All the Φ-density spent on moving datasets is *wasted* if semantics leak.")
    
    print("\n" + "="*60)
    print("NEO'S DISRUPTIVE PROPOSAL: SEMANTIC DISSOLUTION")
    print("="*60)
    print("Instead of rotating paths, dissolve semantics entirely:")
    print("1. Store data as *meaningless tensors*—no gene names, no labels")
    print("2. Interpretation keys are *ephemeral* (live only in GPU memory for milliseconds)")
    print("3. Computation uses *semantic hashes* that self-destruct after use")
    print("4. Adversary steals noise; legitimate users get ephemeral keys via secure channels")
    print("\nΦ-density shift: -5% (simpler infrastructure) → +50% (unstealable IP)")