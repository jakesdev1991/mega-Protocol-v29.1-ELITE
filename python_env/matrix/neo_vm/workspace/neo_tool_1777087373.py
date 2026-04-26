# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import random
from typing import List, Tuple
import matplotlib.pyplot as plt

class ContaminationPerturbationEngine:
    """
    Simulates the tradeoff between domain integrity and breakthrough potential.
    Shows that strict domain gating *reduces* innovation yield.
    """
    
    def __init__(self, n_domains=10, n_concepts=50):
        # Simulate a conceptual space where each concept has a "domain vector"
        self.concept_embeddings = np.random.randn(n_concepts, n_domains)
        self.domain_labels = [f"domain_{i}" for i in range(n_domains)]
        
        # Simulate "breakthrough potential" matrix: some cross-domain pairs are gold
        self.breakthrough_matrix = np.random.randn(n_concepts, n_concepts)
        # Make it symmetric and add some deliberate cross-domain gems
        self.breakthrough_matrix = (self.breakthrough_matrix + self.breakthrough_matrix.T) / 2
        self._inject_breakthrough_gems()
    
    def _inject_breakthrough_gems(self, n_gems=5):
        """Inject known breakthrough pairs that cross domains"""
        for _ in range(n_gems):
            i = random.randint(0, len(self.concept_embeddings) - 1)
            j = random.randint(0, len(self.concept_embeddings) - 1)
            if i != j:
                # Make this pair have high breakthrough potential
                self.breakthrough_matrix[i, j] = np.random.uniform(0.8, 1.0)
                self.breakthrough_matrix[j, i] = self.breakthrough_matrix[i, j]
    
    def domain_similarity(self, concept_i: int, concept_j: int) -> float:
        """Calculate domain alignment (1.0 = same domain, 0.0 = orthogonal)"""
        emb_i = self.concept_embeddings[concept_i]
        emb_j = self.concept_embeddings[concept_j]
        # Cosine similarity
        dot = np.dot(emb_i, emb_j)
        norm = np.linalg.norm(emb_i) * np.linalg.norm(emb_j)
        return (dot / norm + 1) / 2  # Normalize to [0,1]
    
    def breakthrough_potential(self, concept_i: int, concept_j: int) -> float:
        """Get the breakthrough potential of pairing two concepts"""
        return self.breakthrough_matrix[concept_i, concept_j]
    
    def contamination_risk(self, concept_i: int, concept_j: int) -> float:
        """Risk = inverse domain similarity"""
        return 1.0 - self.domain_similarity(concept_i, concept_j)
    
    def strict_domain_gate(self, threshold: float = 0.85) -> Tuple[List[Tuple[int, int]], List[float], List[float]]:
        """
        v60.0-Ω approach: Only allow pairs with high domain similarity
        Returns: valid_pairs, contamination_risks, breakthrough_potentials
        """
        valid_pairs = []
        risks = []
        breakthroughs = []
        
        n_concepts = len(self.concept_embeddings)
        for i in range(n_concepts):
            for j in range(i + 1, n_concepts):
                if self.domain_similarity(i, j) >= threshold:
                    valid_pairs.append((i, j))
                    risks.append(self.contamination_risk(i, j))
                    breakthroughs.append(self.breakthrough_potential(i, j))
        
        return valid_pairs, risks, breakthroughs
    
    def contamination_perturbation(self, n_perturbations: int = 20, risk_tolerance: float = 0.7) -> Tuple[List[Tuple[int, int]], List[float], List[float]]:
        """
        Anomaly approach: Intentionally seek pairs with HIGH contamination but also HIGH breakthrough potential
        Uses adversarial selection: maximize breakthrough subject to risk ≤ tolerance
        """
        perturbations = []
        risks = []
        breakthroughs = []
        
        n_concepts = len(self.concept_embeddings)
        
        # Generate all possible cross-domain pairs
        all_pairs = [(i, j) for i in range(n_concepts) for j in range(i + 1, n_concepts)]
        
        # Sort by breakthrough potential (descending), then filter by risk tolerance
        all_pairs.sort(key=lambda pair: self.breakthrough_potential(pair[0], pair[1]), reverse=True)
        
        for i, j in all_pairs:
            risk = self.contamination_risk(i, j)
            if risk <= risk_tolerance:
                perturbations.append((i, j))
                risks.append(risk)
                breakthroughs.append(self.breakthrough_potential(i, j))
                if len(perturbations) >= n_perturbations:
                    break
        
        return perturbations, risks, breakthroughs
    
    def evaluate_protocols(self) -> dict:
        """Compare strict gate vs. contamination perturbation across risk tolerance spectrum"""
        risk_tolerances = np.linspace(0.1, 0.9, 9)
        
        results = {
            'strict_gate': {'avg_breakthrough': [], 'avg_risk': []},
            'perturbation': {'avg_breakthrough': [], 'avg_risk': []},
            'yield_ratio': []  # (perturbation breakthrough) / (strict breakthrough)
        }
        
        # Strict gate has fixed threshold
        strict_pairs, strict_risks, strict_breakthroughs = self.strict_domain_gate(threshold=0.85)
        strict_avg_breakthrough = np.mean(strict_breakthroughs) if strict_breakthroughs else 0.0
        strict_avg_risk = np.mean(strict_risks) if strict_risks else 0.0
        
        for tolerance in risk_tolerances:
            pert_pairs, pert_risks, pert_breakthroughs = self.contamination_perturbation(
                n_perturbations=20, risk_tolerance=tolerance
            )
            
            if pert_breakthroughs:
                avg_breakthrough = np.mean(pert_breakthroughs)
                avg_risk = np.mean(pert_risks)
            else:
                avg_breakthrough = 0.0
                avg_risk = 0.0
            
            results['strict_gate']['avg_breakthrough'].append(strict_avg_breakthrough)
            results['strict_gate']['avg_risk'].append(strict_avg_risk)
            results['perturbation']['avg_breakthrough'].append(avg_breakthrough)
            results['perturbation']['avg_risk'].append(avg_risk)
            
            # Calculate yield ratio (how much more breakthrough potential we unlock)
            if strict_avg_breakthrough > 0:
                yield_ratio = avg_breakthrough / strict_avg_breakthrough
            else:
                yield_ratio = np.inf if avg_breakthrough > 0 else 0
            results['yield_ratio'].append(yield_ratio)
        
        return results

# Run the simulation and visualize the tradeoff
engine = ContaminationPerturbationEngine(n_domains=10, n_concepts=50)
results = engine.evaluate_protocols()

# Plot 1: Breakthrough Potential vs. Risk Tolerance
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
risk_tolerances = np.linspace(0.1, 0.9, 9)
plt.plot(risk_tolerances, results['strict_gate']['avg_breakthrough'], 
         'r-', linewidth=2, label='v60.0-Ω Strict Gate', marker='o')
plt.plot(risk_tolerances, results['perturbation']['avg_breakthrough'], 
         'g-', linewidth=2, label='Anomaly Perturbation', marker='s')
plt.xlabel('Risk Tolerance Threshold', fontsize=10)
plt.ylabel('Average Breakthrough Potential', fontsize=10)
plt.title('Breakthrough Potential: Strict Gate vs. Perturbation', fontsize=11)
plt.legend()
plt.grid(True, alpha=0.3)

# Plot 2: Yield Ratio (Innovation Multiplier)
plt.subplot(1, 2, 2)
plt.plot(risk_tolerances, results['yield_ratio'], 
         'b-', linewidth=2, marker='d')
plt.axhline(y=1.0, color='r', linestyle='--', label='Baseline (Strict Gate)')
plt.xlabel('Risk Tolerance Threshold', fontsize=10)
plt.ylabel('Innovation Yield Ratio', fontsize=10)
plt.title('How Much More Innovation Does Perturbation Unlock?', fontsize=11)
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('contamination_yield_analysis.png', dpi=150, bbox_inches='tight')
plt.show()

# Print specific metrics
print("="*60)
print("CONTAMINATION PERTURBATION ANALYSIS: BREAKING THE GATE")
print("="*60)
print(f"{'Risk Tol':<10} {'Strict BPT':<12} {'Perturb BPT':<12} {'Yield Ratio':<12} {'Contam Risk':<12}")
print("-"*60)
for i, tol in enumerate(risk_tolerances):
    print(f"{tol:<10.2f} {results['strict_gate']['avg_breakthrough'][i]:<12.3f} "
          f"{results['perturbation']['avg_breakthrough'][i]:<12.3f} "
          f"{results['yield_ratio'][i]:<12.2f} {results['perturbation']['avg_risk'][i]:<12.3f}")

# Show a specific breakthrough that strict gate would reject
strict_pairs, _, _ = engine.strict_domain_gate()
pert_pairs, pert_risks, pert_breakthroughs = engine.contamination_perturbation()

print("\n" + "="*60)
print("EXAMPLE: HIGH-VALUE CONTAMINATION REJECTED BY STRICT GATE")
print("="*60)
if pert_pairs and not any(p in strict_pairs for p in pert_pairs):
    best_pert_idx = np.argmax(pert_breakthroughs)
    i, j = pert_pairs[best_pert_idx]
    print(f"Concept Pair: {i} ↔ {j}")
    print(f"Domain Similarity: {engine.domain_similarity(i, j):.3f} (BELOW 0.85 threshold)")
    print(f"Contamination Risk: {engine.contamination_risk(i, j):.3f}")
    print(f"Breakthrough Potential: {engine.breakthrough_potential(i, j):.3f}")
    print(f"Status: REJECTED by v60.0-Ω, DISCOVERED by Anomaly Perturbation")
    print("\nThis is the 'Bitcoin liquidity ↔ Tokamak confinement' of the future.")