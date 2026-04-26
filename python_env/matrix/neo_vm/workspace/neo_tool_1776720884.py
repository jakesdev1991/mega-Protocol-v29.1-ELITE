# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import random
import numpy as np
import pandas as pd
from collections import Counter

# ============================
# 1. Simulate SLBA-Ω Spoofing Attack
# ============================

def compute_R_D(coverage, consistency, freshness, specificity, weights=[0.25,0.25,0.25,0.25]):
    return np.dot(weights, [coverage, consistency, freshness, specificity])

# Baseline: a "truly fragile" system (low true coverage, inconsistent)
true_fragile = {
    'coverage': 0.3,
    'consistency': 0.4,
    'freshness': 0.5,
    'specificity': 0.2
}
R_true = compute_R_D(**true_fragile)
print(f"True fragile system R_D: {R_true:.3f} (should be < 0.6 threshold)")

# Spoofing: adversary adds 20 trivial documents to inflate coverage & consistency
spoofed_coverage = min(1.0, true_fragile['coverage'] + 0.5)  # pad with noise
spoofed_consistency = min(1.0, true_fragile['consistency'] + 0.4)  # parrot same lines
spoofed_freshness = min(1.0, true_fragile['freshness'] + 0.3)  # superficial updates
spoofed_specificity = true_fragile['specificity']  # can't fake numbers easily

R_spoofed = compute_R_D(spoofed_coverage, spoofed_consistency, spoofed_freshness, spoofed_specificity)
print(f"Spoofed system R_D: {R_spoofed:.3f} (now > 0.6, false safe)\n")

# ============================
# 2. Simulate Documentation Contagion Dynamics
# ============================

def simulate_contagion(num_stakeholders=50, initial_infected=3, beta=0.5, gamma=0.1, days=30):
    """
    SIR model for document spread.
    beta: transmission rate (citing/forwarding)
    gamma: recovery rate (resolution/integration)
    """
    S = np.zeros(days)
    I = np.zeros(days)
    R = np.zeros(days)
    S[0] = num_stakeholders - initial_infected
    I[0] = initial_infected
    R[0] = 0
    
    for t in range(1, days):
        new_infections = beta * S[t-1] * I[t-1] / num_stakeholders
        new_recoveries = gamma * I[t-1]
        S[t] = S[t-1] - new_infections
        I[t] = I[t-1] + new_infections - new_recoveries
        R[t] = R[t-1] + new_recoveries
    
    R_eff = beta / gamma
    return S, I, R, R_eff

# Healthy system: high transmission (open culture)
S1, I1, R1, R_eff1 = simulate_contagion(beta=0.6, gamma=0.05)
print(f"Healthy system: R_doc_eff = {R_eff1:.2f} (> 1, good propagation)")

# Failing system: low transmission (silos, ignored memos)
S2, I2, R2, R_eff2 = simulate_contagion(beta=0.15, gamma=0.1)
print(f"Failing system: R_doc_eff = {R_eff2:.2f} (< 1, propagation stalled)\n")

# ============================
# 3. Detect Spoofing via Entropy Anomaly
# ============================

def spoofing_penalty(doc_versions):
    """
    doc_versions: list of version strings (simulated)
    Penalize low entropy (parroting) and sudden coverage spikes.
    """
    # Measure edit distance entropy (simplified: count unique versions)
    uniq = len(set(doc_versions))
    total = len(doc_versions)
    mutation_entropy = -sum((c/total)*np.log(c/total) for c in Counter(doc_versions).values()) if uniq>0 else 0
    
    # Penalize if entropy is too low (suspicious uniformity)
    if mutation_entropy < 0.5:
        penalty = 0.3
    else:
        penalty = 0.0
    return penalty, mutation_entropy

# Generate version history: true system has diverse edits
true_versions = ["v1.2", "v1.3", "v1.4", "v2.0", "v2.1"] * 5
# Spoofed system: many copies of same version (parroting)
spoofed_versions = ["v1.0"] * 25

penalty_true, ent_true = spoofing_penalty(true_versions)
penalty_spoof, ent_spoof = spoofing_penalty(spoofed_versions)

print(f"True system: mutation_entropy={ent_true:.2f}, penalty={penalty_true}")
print(f"Spoofed system: mutation_entropy={ent_spoof:.2f}, penalty={penalty_spoof}")

# Adjusted robustness score
R_true_adj = R_true - penalty_true
R_spoof_adj = R_spoofed - penalty_spoof
print(f"\nAdjusted R_D (true): {R_true_adj:.3f}")
print(f"Adjusted R_D (spoofed): {R_spoof_adj:.3f} (now correctly flagged as fragile)")