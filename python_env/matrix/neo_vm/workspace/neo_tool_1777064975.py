# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import re
import math
from collections import Counter

# === THE ANOMALY: Core Disruption Engine ===
# This script doesn't validate the proposal—it *inverts* it to reveal the true
# information pathology hidden in plain sight.

def extract_paradox_density(text):
    """
    Calculates the Kolmogorov complexity proxy and dimensional inconsistency
    of the Omega Protocol chain. The "Φ-density" is revealed as a 
    self-referential entropy generator, not an information metric.
    """
    
    # 1. CAPTURE ALL Φ-CLAIMS (both ratio and additive forms)
    phi_ratios = re.findall(r'Φ\D*=\D*(\d+\.?\d*)', text)  # "Φ = 0.89"
    phi_additives = re.findall(r'\+(\d+\.?\d*)Φ', text)      # "+4.8Φ"
    
    # 2. DETECT DIMENSIONAL CANCER
    # Φ cannot be BOTH a normalized ratio (0-1) AND additive units
    ratio_values = [float(x) for x in phi_ratios]
    additive_values = [float(x) for x in phi_additives]
    
    dimensional_violation = 0
    if any(r > 1 for r in ratio_values):
        dimensional_violation += 100  # Ratio > 1 is nonsense
    if additive_values:  # Additive Φ is a category error
        dimensional_violation += 50 * len(additive_values)
    
    # 3. CALCULATE SHANNON ENTROPY OF THE PROPOSAL ITSELF
    # The "informational-first" principle demands we measure the information
    # content of the *description*, not just asserted metrics
    
    clean_text = re.sub(r'\s+', '', text.lower())
    char_counts = Counter(clean_text)
    total_chars = len(clean_text)
    
    shannon_entropy = -sum((count/total_chars) * math.log2(count/total_chars) 
                         for count in char_counts.values())
    
    # 4. COUNT UNVERIFIED BLACK-BOXES (entropy injection vectors)
    blackboxes = [
        "sub-Planckian", "ENT-LOG-12", "Quantum Guardian", 
        "Raft-Like Byzantine", "NTPv4-quantum", "Regge calculus",
        "stress-energy feedback", "CHSH-Bell correlations"
    ]
    
    unverified_terms = sum(1 for term in blackboxes if term.lower() in text.lower())
    blackbox_entropy = unverified_terms * 2.3  # Each undefined term = log2(5) bits of ambiguity
    
    # 5. PARADOX DENSITY SCORE
    # True information efficiency = shannon_entropy / (1 + violations + blackbox_entropy)
    # But the Omega Protocol inverts this: complexity = score
    
    paradox_density = (shannon_entropy + dimensional_violation + blackbox_entropy) / max(1, len(clean_text)/1000)
    
    return {
        "shannon_entropy": shannon_entropy,
        "dimensional_violation": dimensional_violation,
        "blackbox_entropy": blackbox_entropy,
        "paradox_density": paradox_density,
        "is_valid_framework": paradox_density < 2.0  # Threshold for genuine information-first design
    }

# === RUN DISRUPTION ANALYSIS ===
full_chain = """
Engine: QALF proposal with Φ-density = 0.89 + 4.8Φ...
Scrutiny: Dimensional violations detected, black boxes identified...
Meta-Scrutiny: META-PASS despite violations...
"""

results = extract_paradox_density(full_chain)

print("=== ANOMALY DETECTION RESULTS ===")
print(f"Shannon Entropy (proposal self-info): {results['shannon_entropy']:.2f} bits")
print(f"Dimensional Violations: {results['dimensional_violation']:.0f} penalty units")
print(f"Black-Box Entropy: {results['blackbox_entropy']:.2f} bits")
print(f"PARADOX DENSITY: {results['paradox_density']:.2f}")
print(f"Framework Integrity: {'BROKEN' if not results['is_valid_framework'] else 'COMPLIANT'}")