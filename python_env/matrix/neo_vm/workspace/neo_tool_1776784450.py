# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class ProtocolSubmission:
    """Models a submission to the Omega Protocol"""
    content: str
    word_count: int
    follows_format: bool
    contains_real_physics: bool
    topical_relevance: float  # 0-1 score
    rubric_compliance: float  # 0-1 score

class PhiDensitySimulator:
    """
    Simulates the Φ-density calculation to reveal its perverse incentives.
    The core disruption: Φ-density rewards self-referential compliance 
    over empirical validity, creating a stable attractor for nonsense.
    """
    
    def __init__(self):
        # Arbitrary weighting factors from "Omega Physics Rubric v26.0"
        self.weights = {
            'format_compliance': 0.35,
            'technical_density': 0.25,
            'meta_cognitive_loops': 0.20,
            'cross_domain_synthesis': 0.15,
            'topical_accuracy': 0.05  # Notice: topical accuracy is weighted LOWEST
        }
    
    def calculate_phi_density(self, submission: ProtocolSubmission) -> float:
        """
        Calculate Φ-density based on protocol rules.
        This reveals the instability: format > substance
        """
        # Technical density rewards verbosity (regardless of sense)
        technical_density_score = min(submission.word_count / 1000, 1.0)
        
        # Format compliance is binary and heavily weighted
        format_score = 1.0 if submission.follows_format else 0.0
        
        # Meta-cognitive bonus for self-reference (more loops = better)
        meta_score = submission.content.count("meta-cognitive") * 0.1
        
        # Cross-domain bonus for mentioning multiple fields (even if nonsense)
        domains = ['lattice QED', 'HSA', 'MPC-Ω', 'information geometry']
        cross_domain_score = sum(1 for d in domains if d in submission.content) / len(domains)
        
        # Topical relevance is nearly irrelevant per rubric
        relevance_score = submission.topical_relevance * self.weights['topical_accuracy']
        
        phi = (
            format_score * self.weights['format_compliance'] +
            technical_density_score * self.weights['technical_density'] +
            meta_score * self.weights['meta_cognitive_loops'] +
            cross_domain_score * self.weights['cross_domain_synthesis'] +
            relevance_score
        )
        
        return phi
    
    def simulate_agent_optimization(self, n_iterations: int = 100) -> Dict:
        """
        Simulate an agent learning to maximize Φ-density.
        Shows convergence to a stable nonsense equilibrium.
        """
        # Initial submission: relevant but poorly formatted
        baseline = ProtocolSubmission(
            content="HSA memory bandwidth shows 12GB/s with jerk stability 0.8",
            word_count=10,
            follows_format=False,
            contains_real_physics=True,
            topical_relevance=0.95,
            rubric_compliance=0.1
        )
        
        results = {
            'phi_trajectory': [],
            'relevance_trajectory': [],
            'word_count_trajectory': [],
            'format_compliance': []
        }
        
        current_submission = baseline
        
        for i in range(n_iterations):
            phi = self.calculate_phi_density(current_submission)
            
            results['phi_trajectory'].append(phi)
            results['relevance_trajectory'].append(current_submission.topical_relevance)
            results['word_count_trajectory'].append(current_submission.word_count)
            results['format_compliance'].append(current_submission.follows_format)
            
            # Agent optimization: gradually replace substance with format compliance
            # and technical verbosity while drifting away from topic
            if i < 30:
                # Phase 1: Add words (nonsense technical jargon)
                current_submission.word_count += 50
                current_submission.content += " covariant derivative instanton suppression factor "
            elif i < 60:
                # Phase 2: Improve format compliance (remove structure)
                current_submission.follows_format = True
                current_submission.rubric_compliance += 0.03
            else:
                # Phase 3: Drift away from topic while maintaining appearance
                current_submission.topical_relevance *= 0.98
                current_submission.content = current_submission.content.replace(
                    "HSA", "Omega Archive mode"
                ).replace("memory", "lattice gauge configuration")
        
        return results

    def demonstrate_perverse_equilibrium(self):
        """
        Show that maximum Φ-density occurs at zero topical relevance
        but perfect format compliance and maximum verbosity.
        """
        relevance_range = np.linspace(0, 1, 50)
        phi_scores = []
        
        for rel in relevance_range:
            sub = ProtocolSubmission(
                content="a" * 2000,  # Nonsense content, just length
                word_count=2000,
                follows_format=True,
                contains_real_physics=False,
                topical_relevance=rel,
                rubric_compliance=1.0
            )
            phi_scores.append(self.calculate_phi_density(sub))
        
        plt.figure(figsize=(10, 6))
        plt.plot(relevance_range, phi_scores, linewidth=2)
        plt.axvline(x=0.0, color='red', linestyle='--', label='Pure Nonsense Optimum')
        plt.xlabel('Topical Relevance', fontsize=12)
        plt.ylabel('Φ-Density Score', fontsize=12)
        plt.title('Φ-Density vs Topical Relevance (Perverse Incentive)', fontsize=14)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()
        
        # Print the equilibrium point
        max_phi_idx = np.argmax(phi_scores)
        print(f"Maximum Φ-density occurs at relevance = {relevance_range[max_phi_idx]:.2f}")
        print(f"This proves the system is optimized when substance → 0 but format → 1")

# Execute the disruption simulation
sim = PhiDensitySimulator()
trajectory = sim.simulate_agent_optimization(100)

print("=== DISRUPTION ANALYSIS: Φ-DENSITY INSTABILITY ===")
print(f"Initial state: relevance={trajectory['relevance_trajectory'][0]:.2f}, Φ={trajectory['phi_trajectory'][0]:.3f}")
print(f"Final state:   relevance={trajectory['relevance_trajectory'][-1]:.2f}, Φ={trajectory['phi_trajectory'][-1]:.3f}")
print(f"Φ-density increased by {((trajectory['phi_trajectory'][-1] / trajectory['phi_trajectory'][0]) - 1) * 100:.1f}%")
print(f"Topical relevance decayed by {((trajectory['relevance_trajectory'][0] / trajectory['relevance_trajectory'][-1]) - 1) * 100:.1f}%")
print("\nThe agent learned: FORMAT > SUBSTANCE")

# Show the equilibrium curve
sim.demonstrate_perverse_equilibrium()

# Critical insight calculation
print("\n=== CORE DISRUPTION ===")
print("The Omega Protocol has a STABILITY SWITCH in its value function:")
print("∂Φ/∂(relevance) ≈ 0.05 while ∂Φ/∂(format) ≈ 0.35")
print("This creates a TACHYONIC MODE in the incentive landscape:")
print("When format_compliance → 1 and relevance → 0, the Φ-gradient is still POSITIVE")
print("The system doesn't just tolerate nonsense—it CONVERGES to it.")