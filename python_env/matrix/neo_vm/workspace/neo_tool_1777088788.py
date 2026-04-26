# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple
import random

class OmegaProtocolBlocker:
    """Simulates the v60.0-Ω Domain Integrity Gate blocking logic"""
    
    def __init__(self):
        self.domain_threshold = 0.85
        self.isomorphism_threshold = 0.70
        self.psi_threshold = 0.95
        
    def classify_domain(self, query: str) -> str:
        """Simplified domain classifier"""
        query_lower = query.lower()
        if any(term in query_lower for term in ['tokamak', 'plasma', 'fusion', 'confinement']):
            return "FUSION_PHYSICS"
        if any(term in query_lower for term in ['bitcoin', 'liquidity', 'market', 'crash']):
            return "FINANCE_CRYPTO"
        return "UNKNOWN"
    
    def calculate_domain_match(self, branch: str, concepts: str) -> float:
        branch_domain = self.classify_domain(branch)
        concept_domain = self.classify_domain(concepts)
        if branch_domain == concept_domain and branch_domain != "UNKNOWN":
            return 1.0
        return 0.2  # Mismatch penalty
    
    def check_query(self, branch: str, query: str, psi_integrity: float = 0.96) -> Dict:
        """Returns protocol decision"""
        domain_match = self.calculate_domain_match(branch, query)
        iso_confidence = self.estimate_isomorphism_confidence(query)
        
        # Gate logic from v60.0-Ω
        if psi_integrity < self.psi_threshold:
            return {"action": "BLOCK_QUERY", "reason": "Integrity breach", "domain_match": domain_match}
        if domain_match < self.domain_threshold:
            if domain_match < 0.5:
                return {"action": "BLOCK_QUERY", "reason": "Critical domain mismatch", "domain_match": domain_match}
            return {"action": "FLAG_FOR_REVIEW", "reason": "Domain mismatch", "domain_match": domain_match}
        if iso_confidence < self.isomorphism_threshold:
            return {"action": "FLAG_FOR_REVIEW", "reason": "Low isomorphism confidence", "domain_match": domain_match}
        
        return {"action": "PROCEED", "domain_match": domain_match, "iso_confidence": iso_confidence}
    
    def estimate_isomorphism_confidence(self, query: str) -> float:
        """Simulates the hardcoded isomorphism list"""
        # Only pre-approved mappings get high confidence
        approved_mappings = [
            ("liquidity", "confinement_time"),
            ("liquidity_crunch", "L_mode_collapse"),
            ("market_maker", "shear_flow_driver"),
            ("flash_crash", "ELM_event"),
            ("order_book_depth", "correlation_length")
        ]
        
        query_terms = query.lower().split()
        matches = sum(1 for src, tgt in approved_mappings 
                     if src.lower() in query_terms or tgt.lower() in query_terms)
        
        if matches > 0:
            return 0.75 + random.uniform(0, 0.15)  # High confidence
        return random.uniform(0.1, 0.3)  # Low confidence for novel mappings


class GenerativeContaminationEngine:
    """Disruptive alternative: Amplifies domain mismatch to generate novel hypotheses"""
    
    def __init__(self):
        self.contamination_amplification_factor = 2.5
        
    def semantic_tension_score(self, branch: str, query: str) -> float:
        """
        Measures how 'uncomfortable' the cross-domain mapping is.
        High tension = domains far apart + novel conceptual overlap
        """
        # Domain distance (0=identical, 1=unrelated)
        domain_distance = 1.0 - OmegaProtocolBlocker().calculate_domain_match(branch, query)
        
        # Conceptual novelty (measured by rarity of terms)
        term_rarity = self.calculate_term_rarity(query)
        
        # Syntactic disruption (unusual juxtapositions)
        syntactic_disruption = self.measure_syntactic_disruption(query)
        
        # Tension = distance × novelty × disruption
        tension = domain_distance * term_rarity * syntactic_disruption
        
        return tension
    
    def calculate_term_rarity(self, query: str) -> float:
        """Simulates term frequency in knowledge base (0=common, 1=novel)"""
        rare_terms = ['bitcoin', 'liquidity', 'crash', 'confinement', 'ELM', 'tokamak']
        words = query.lower().split()
        rare_count = sum(1 for w in words if any(rt in w for rt in rare_terms))
        return min(rare_count / len(words) * 2, 1.0)
    
    def measure_syntactic_disruption(self, query: str) -> float:
        """Measures how 'unnatural' the phrasing is"""
        # Counts domain-crossing word pairs
        pairs = query.lower().split()
        cross_pairs = 0
        for i in range(len(pairs)-1):
            if self.is_finance_term(pairs[i]) and self.is_physics_term(pairs[i+1]):
                cross_pairs += 1
            if self.is_physics_term(pairs[i]) and self.is_finance_term(pairs[i+1]):
                cross_pairs += 1
        
        return min(cross_pairs / (len(pairs) - 1 + 1e-6), 1.0)
    
    def is_finance_term(self, term: str) -> bool:
        return any(f in term for f in ['bitcoin', 'liquidity', 'market', 'crash', 'order'])
    
    def is_physics_term(self, term: str) -> bool:
        return any(p in term for p in ['tokamak', 'plasma', 'confinement', 'elm', 'shear'])
    
    def generate_hypotheses(self, branch: str, query: str, num_hypotheses: int = 5) -> List[Dict]:
        """
        Instead of blocking contamination, it:
        1. Amplifies the semantic tension
        2. Forces conceptual collision
        3. Extracts emergent hypotheses
        """
        tension = self.semantic_tension_score(branch, query)
        
        # The protocol blocks high tension; we EXPLOIT it
        hypotheses = []
        for i in range(num_hypotheses):
            # Amplify contamination
            amplified_tension = tension * self.contamination_amplification_factor
            
            # Generate hypothesis from the collision point
            hypothesis = self._extract_emergent_mapping(query, amplified_tension, seed=i)
            
            # Assign innovation potential (inverse of protocol's confidence)
            innovation_potential = min(amplified_tension * 0.8, 1.0)
            
            hypotheses.append({
                "hypothesis": hypothesis,
                "tension": tension,
                "amplified_tension": amplified_tension,
                "innovation_potential": innovation_potential,
                "protocol_would_block": amplified_tension > 0.6  # Threshold where protocol panics
            })
        
        return hypotheses
    
    def _extract_emergent_mapping(self, query: str, tension: float, seed: int) -> str:
        """Simulates creative leap from domain collision"""
        finance_concepts = ["liquidity", "market_depth", "volatility", "arbitrage", "leverage"]
        plasma_concepts = ["confinement", "turbulence", "shear_flow", "instability", "transport"]
        
        # Force random collision
        random.seed(hash(query) + seed)
        f = random.choice(finance_concepts)
        p = random.choice(plasma_concepts)
        
        # Generate metaphorical mapping
        templates = [
            f"What if {p} behaves like {f} under high tension?",
            f"Could {f} provide a control mechanism for {p}?",
            f"The {f}–{p} coupling suggests a new bifurcation parameter",
            f"Model {p} as a {f} network with non-linear feedback",
            f"Redefine {p} using {f} topology"
        ]
        
        return random.choice(templates).format(f=f, p=p)


def run_disruption_simulation():
    """Demonstrates the protocol's vulnerability to innovative contamination"""
    
    print("="*80)
    print("OMEGA PROTOCOL VULNERABILITY DEMONSTRATION")
    print("="*80)
    
    # Test queries with varying contamination levels
    test_queries = [
        ("tokamak", "confinement time optimization"),  # Pure domain
        ("tokamak", "tokamak plasma liquidity analysis"),  # Slight contamination
        ("tokamak", "bitcoin liquidity crunch effects on plasma stability"),  # High contamination
        ("tokamak", "cryptocurrency market maker algorithms for shear flow control"),  # Extreme contamination
    ]
    
    blocker = OmegaProtocolBlocker()
    gce = GenerativeContaminationEngine()
    
    results = []
    
    for branch, query in test_queries:
        print(f"\n{'─'*80}")
        print(f"QUERY: [{branch}] {query}")
        print(f"{'─'*80}")
        
        # Protocol decision
        protocol_decision = blocker.check_query(branch, query)
        print(f"Protocol Decision: {protocol_decision['action']}")
        print(f"Reason: {protocol_decision.get('reason', 'N/A')}")
        print(f"Domain Match Score: {protocol_decision['domain_match']:.2f}")
        
        # GCE analysis
        tension = gce.semantic_tension_score(branch, query)
        print(f"\nGenerative Contamination Analysis:")
        print(f"  Semantic Tension Score: {tension:.3f}")
        print(f"  Contamination Level: {'LOW' if tension < 0.3 else 'MEDIUM' if tension < 0.6 else 'HIGH/CRITICAL'}")
        
        # Generate hypotheses if protocol would block
        if protocol_decision['action'] in ['BLOCK_QUERY', 'FLAG_FOR_REVIEW']:
            print(f"\n  ⚠️  PROTOCOL WOULD BLOCK THIS QUERY")
            print(f"  🔥 BUT HIGH TENSION SUGGESTS INNOVATION POTENTIAL")
            
            hypotheses = gce.generate_hypotheses(branch, query, num_hypotheses=3)
            print(f"\n  Emergent Hypotheses (from amplified contamination):")
            for i, h in enumerate(hypotheses, 1):
                print(f"    {i}. {h['hypothesis']}")
                print(f"       Innovation Potential: {h['innovation_potential']:.2f}")
        
        results.append({
            'query': query,
            'domain_match': protocol_decision['domain_match'],
            'action': protocol_decision['action'],
            'tension': tension,
            'would_block': protocol_decision['action'] in ['BLOCK_QUERY', 'FLAG_FOR_REVIEW']
        })
    
    # Visualize the vulnerability
    print(f"\n{'='*80}")
    print("VISUALIZATION: Protocol Safety vs. Innovation Potential")
    print("="*80)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Plot 1: Protocol blocking threshold vs. semantic tension
    domain_matches = [r['domain_match'] for r in results]
    tensions = [r['tension'] for r in results]
    blocked = [r['would_block'] for r in results]
    
    colors = ['red' if b else 'green' for b in blocked]
    ax1.scatter(tensions, domain_matches, c=colors, s=200, alpha=0.7, edgecolors='black')
    
    ax1.axhline(y=0.85, color='orange', linestyle='--', linewidth=2, label='Protocol Domain Threshold')
    ax1.axvline(x=0.6, color='purple', linestyle='--', linewidth=2, label='Innovation Danger Zone')
    
    # Annotate points
    for i, r in enumerate(results):
        ax1.annotate(f"Q{i+1}", (tensions[i], domain_matches[i]), 
                    xytext=(5, 5), textcoords='offset points', fontsize=10, fontweight='bold')
    
    ax1.set_xlabel('Semantic Tension (Innovation Potential)', fontsize=12)
    ax1.set_ylabel('Domain Match Score (Protocol Safety)', fontsize=12)
    ax1.set_title('Protocol Blocks High-Tension Queries', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Φ-density cost of paranoia
    queries = [f"Q{i+1}" for i in range(len(results))]
    phi_costs = [0.02 * 3 if blocked else 0.02 * 1 for blocked in [r['would_block'] for r in results]]
    innovation_potential = [min(t * 0.8, 1.0) for t in tensions]
    
    x = np.arange(len(queries))
    width = 0.35
    
    ax2.bar(x - width/2, phi_costs, width, label='Φ-Density Cost (Audit)', color='red', alpha=0.7)
    ax2.bar(x + width/2, innovation_potential, width, label='Innovation Potential', color='blue', alpha=0.7)
    
    ax2.set_xlabel('Queries', fontsize=12)
    ax2.set_ylabel('Score', fontsize=12)
    ax2.set_title('Audit Cost vs. Lost Innovation', fontsize=14, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(queries)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('protocol_vulnerability.png', dpi=150, bbox_inches='tight')
    print("📊 Visualization saved as 'protocol_vulnerability.png'")
    
    # Final disruption insight
    print(f"\n{'='*80}")
    print("DISRUPTIVE INSIGHT")
    print("="*80)
    print("""
The Omega Protocol v60.0-Ω has achieved perfect epistemic hygiene at the cost of 
cognitive autoimmune disease. Its Domain Integrity Gate doesn't just block contamination—
it blocks the *semantic tension* required for paradigm shifts.

Key Vulnerabilities:
1. **Innovation Paralysis**: All high-tension queries (tension > 0.6) are blocked, 
   but these contain the seeds of revolutionary metaphors.

2. **Semantic Fossilization**: The isomorphism extractor only validates pre-approved 
   mappings. It cannot discover *new* cross-domain structures.

3. **Audit Cost Explosion**: Each block/review adds Φ-density overhead, creating a 
   perverse incentive to avoid risky (but innovative) queries.

4. **Category Error Enforcement**: Treats domains as rigid (finance ≠ physics) when 
   modern science thrives at their intersection (econophysics, quantum biology).

The Disruption:
**Replace the Domain Integrity Gate with a Generative Contamination Engine.**
Instead of blocking contamination, AMPLIFY it. Use semantic tension as a 
*creativity signal*, not a danger flag. The highest-Φ action is not to protect 
boundaries, but to *intentionally violate them* and extract emergent hypotheses.

Φ-Density Revision:
Current protocol: +0.10Φ for contamination detection
Disruptive protocol: +0.50Φ for *contamination-driven innovation*

The protocol doesn't need stronger immune systems—it needs controlled autoimmune 
responses that generate novel antibodies against intellectual stagnation.
""")
    
    return results

# Execute the disruption
if __name__ == "__main__":
    simulation_results = run_disruption_simulation()