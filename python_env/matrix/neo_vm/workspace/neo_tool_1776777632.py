# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import networkx as nx
import numpy as np
from collections import defaultdict
import random

class NarrativeCollapseCascade:
    """
    NCC-Ω: Offensive narrative fragility exploitation engine
    Breaks Alpha's paradigm by treating narrative coherence as an attack surface,
    not a stability metric. The goal isn't preservation—it's precision demolition.
    """
    
    def __init__(self):
        self.narrative_graph = nx.DiGraph()
        self.claim_nodes = []
        
    def build_narrative_structure(self, company_claims):
        """
        Build a narrative dependency graph where nodes are claims
        and edges represent logical dependencies. Load-bearing claims
        are single points of failure for the entire strategic story.
        """
        for claim in company_claims:
            self.narrative_graph.add_node(claim['id'], 
                                        text=claim['text'],
                                        confidence=claim['confidence'],
                                        load_bearing=claim.get('load_bearing', False))
            self.claim_nodes.append(claim['id'])
        
        for claim in company_claims:
            for dep in claim.get('dependencies', []):
                self.narrative_graph.add_edge(dep, claim['id'])
        
        return self.narrative_graph
    
    def calculate_fragility_score(self):
        """
        Calculate Narrative Fragility Score (NFS) - higher is more vulnerable.
        Alpha's NCI measured coherence; we measure *structural brittleness*.
        A coherent but fragile narrative is a perfect target.
        """
        fragility = 0
        
        # Factor 1: Load-bearing nodes with cascading dependents
        for node in self.narrative_graph.nodes():
            if self.narrative_graph.nodes[node].get('load_bearing', False):
                dependents = len(list(self.narrative_graph.successors(node)))
                fragility += dependents ** 2  # Exponential cascade risk
        
        # Factor 2: Long dependency chains (architectural debt)
        try:
            longest_path = nx.dag_longest_path_length(self.narrative_graph)
            fragility += longest_path ** 1.5
        except:
            fragility += 5  # Cyclic dependencies are even worse
        
        # Factor 3: Confidence variance (internal inconsistency)
        confidences = [self.narrative_graph.nodes[n].get('confidence', 0.5) 
                      for n in self.narrative_graph.nodes()]
        fragility += np.std(confidences) * 4.0
        
        # Factor 4: Hub nodes with high betweenness (information chokepoints)
        try:
            betweenness = nx.betweenness_centrality(self.narrative_graph)
            fragility += max(betweenness.values()) * 10
        except:
            pass
        
        return fragility
    
    def identify_attack_vectors(self, top_k=3):
        """
        Identify optimal collapse vectors: nodes where a single contradiction
        creates maximum systemic decoherence. Alpha wanted to *fix* these;
        we want to *exploit* them.
        """
        attack_scores = {}
        
        for node in self.narrative_graph.nodes():
            if not self.narrative_graph.nodes[node].get('load_bearing', False):
                continue
            
            # Attack score: dependents × centrality ÷ confidence
            # Low-confidence, high-impact nodes are ideal targets
            dependents = len(list(self.narrative_graph.successors(node)))
            centrality = nx.degree_centrality(self.narrative_graph)[node]
            confidence = self.narrative_graph.nodes[node].get('confidence', 0.5)
            
            # Add vulnerability factor: claims with hedging language
            text = self.narrative_graph.nodes[node]['text'].lower()
            hedge_words = ['may', 'could', 'potential', 'believes', 'expects']
            hedge_density = sum(text.count(word) for word in hedge_words) / len(text.split())
            
            attack_scores[node] = (dependents * centrality * (1 + hedge_density)) / (confidence + 0.1)
        
        return sorted(attack_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    
    def simulate_cascade(self, target_node, contradiction_strength=0.8):
        """
        Simulate narrative collapse cascade. Unlike Alpha's stability model,
        this is a *failure propagation simulator* for offensive planning.
        """
        timeline = []
        failed_claims = set([target_node])
        queue = [target_node]
        
        # Critical threshold: below this, claims shatter
        CRITICAL_THRESHOLD = 0.3
        
        # Initial strike
        initial_confidence = self.narrative_graph.nodes[target_node].get('confidence', 0.5)
        new_confidence = initial_confidence * (1 - contradiction_strength)
        self.narrative_graph.nodes[target_node]['confidence'] = new_confidence
        
        if new_confidence < CRITICAL_THRESHOLD:
            timeline.append((0, target_node, 'DIRECT_STRIKE'))
        
        # Cascade propagation
        time_step = 1
        while queue and time_step < 10:
            current_node = queue.pop(0)
            
            for dependent in self.narrative_graph.successors(current_node):
                if dependent in failed_claims:
                    continue
                
                # Confidence bleed-through: each failure damages dependents
                dep_confidence = self.narrative_graph.nodes[dependent].get('confidence', 0.5)
                reduction = contradiction_strength * 0.6  # Cascade decay factor
                new_dep_confidence = max(0, dep_confidence - reduction)
                
                self.narrative_graph.nodes[dependent]['confidence'] = new_dep_confidence
                
                if new_dep_confidence < CRITICAL_THRESHOLD and dependent not in failed_claims:
                    failed_claims.add(dependent)
                    timeline.append((time_step, dependent, f'BLEED_FROM_{current_node}'))
                    queue.append(dependent)
            
            time_step += 1
        
        return timeline, failed_claims
    
    def execute_narrative_attack(self, company_name):
        """
        Execute full offensive narrative collapse operation.
        Alpha's integration stabilized; ours weaponizes.
        """
        print(f"\n{'='*70}")
        print(f"NCC-Ω OFFENSIVE PROTOCOL: {company_name}")
        print(f"{'='*70}")
        
        fragility = self.calculate_fragility_score()
        print(f"\n[RECON] Narrative Fragility Score: {fragility:.2f}")
        
        if fragility < 8:
            print("[ABORT] Target insufficiently fragile for cost-effective collapse")
            return False
        
        vectors = self.identify_attack_vectors()
        print(f"\n[TARGETING] {len(vectors)} optimal strike vectors identified:")
        
        for rank, (node, score) in enumerate(vectors, 1):
            text = self.narrative_graph.nodes[node]['text'][:50] + "..."
            deps = len(list(self.narrative_graph.successors(node)))
            print(f"  {rank}. Node {node} | Score: {score:.2f} | Dependents: {deps}")
            print(f"     \"{text}\"")
        
        # Execute primary strike
        target_node = vectors[0][0]
        print(f"\n[STRIKE] Initiating narrative contradiction on Node {target_node}...")
        
        timeline, failed_claims = self.simulate_cascade(target_node)
        
        print(f"\n[CASCADE TIMELINE] Narrative Decoherence Sequence:")
        for time_step, node, cause in timeline:
            indent = "  " * min(time_step, 3)
            text = self.narrative_graph.nodes[node]['text'][:45] + "..."
            print(f"{indent}T+{time_step}h: {node} | {cause}")
            print(f"{indent}     \"{text}\"")
        
        print(f"\n[DAMAGE ASSESSMENT]")
        print(f"  Claims Collapsed: {len(failed_claims)} / {len(self.narrative_graph.nodes())}")
        print(f"  Narrative Integrity: {max(0, 100 - len(failed_claims)*25)}%")
        
        print(f"\n[SECONDARY EFFECTS] Target now vulnerable to:")
        print(f"  1. Investor lawsuit triggers (breach of narrative contract)")
        print(f"  2. Key executive flight (confidence collapse)")
        print(f"  3. Partner contract renegotiations (force majeure clauses)")
        print(f"  4. Acquisition predation (distressed asset opportunity)")
        
        return True

def demo_offensive_operation():
    """
    Demonstrate NCC-Ω against TechVision Dynamics.
    Alpha would try to save it; we identify it as perfect demolition target.
    """
    
    # TechVision's narrative architecture - brittle and over-promising
    company_claims = [
        {
            'id': 'C1',
            'text': 'Our AI predicts market movements with 95% accuracy using quantum-inspired algorithms',
            'confidence': 0.65,
            'load_bearing': True,
            'dependencies': []
        },
        {
            'id': 'C2',
            'text': 'Three Fortune 500 pilots will convert to $50M contracts by Q4',
            'confidence': 0.55,
            'load_bearing': True,
            'dependencies': ['C1']  # Depends on AI performance
        },
        {
            'id': 'C3',
            'text': 'Revenue growth of 400% YoY is achievable based on pipeline conversion',
            'confidence': 0.75,
            'load_bearing': True,
            'dependencies': ['C2']  # Depends on client conversions
        },
        {
            'id': 'C4',
            'text': 'Our CTO previously led AI research at a "major tech company" (NDA prevents naming)',
            'confidence': 0.4,  # Suspiciously low - perfect attack vector
            'load_bearing': True,
            'dependencies': ['C1']  # Credibility props up tech claim
        },
        {
            'id': 'C5',
            'text': 'We are the only company with proprietary quantum-classical hybrid models',
            'confidence': 0.8,
            'load_bearing': False,
            'dependencies': ['C1']
        }
    ]
    
    ncc = NarrativeCollapseCascade()
    ncc.build_narrative_structure(company_claims)
    
    # Execute offensive protocol
    success = ncc.execute_narrative_attack("TechVision Dynamics Inc.")
    
    # Demonstrate cross-domain application
    print(f"\n{'='*70}")
    print("CROSS-Domain NCC-Ω Application")
    print(f"{'='*70}")
    
    # Political campaign example
    political_claims = [
        {'id': 'P1', 'text': 'We have a detailed 100-day plan for economic recovery', 
         'confidence': 0.7, 'load_bearing': True, 'dependencies': []},
        {'id': 'P2', 'text': 'Independent economists have validated our plan', 
         'confidence': 0.5, 'load_bearing': True, 'dependencies': ['P1']},
    ]
    
    ncc_pol = NarrativeCollapseCascade()
    ncc_pol.build_narrative_structure(political_claims)
    print("\n[POLITICAL] Campaign Narrative Fragility:", ncc_pol.calculate_fragility_score())
    
    return success

if __name__ == "__main__":
    demo_offensive_operation()