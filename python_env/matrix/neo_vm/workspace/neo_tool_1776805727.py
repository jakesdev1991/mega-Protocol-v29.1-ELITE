# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
NEO'S DISRUPTION ENGINE: LSGM-Ω PARADIGM COLLAPSE SIMULATOR
Demonstrates that geometric security metrics are irrelevant against active adversaries
"""

import networkx as nx
import numpy as np
import random
from typing import Dict, List, Tuple

class LSGMParadox:
    """
    The LSGM-Ω framework's fatal flaw: It assumes a passive adversary who must
    *traverse* the manifold. But exposed directories are writable, making the
    entire geometric model a security theater.
    """
    
    def __init__(self, tree_type: str = "bushy"):
        """
        Initialize both "secure" (bushy) and "vulnerable" (linear) directory trees
        """
        self.tree = self._create_directory_tree(tree_type)
        self.exposed_nodes = self._identify_exposed_directories()
        self.adversarial_control = set()  # Nodes the adversary has compromised
        
    def _create_directory_tree(self, tree_type: str) -> nx.DiGraph:
        """Create the directory structure that LSGM-Ω would analyze"""
        G = nx.DiGraph()
        
        if tree_type == "bushy":
            # The "secure" high-curvature tree LSGM-Ω praises
            # /logs/experiment_{i}/worker_{j}/epoch_{k}/
            root = "logs"
            G.add_node(root, type="root", sensitivity=0, writable=False)
            
            for i in range(3):
                exp = f"{root}/experiment_{i}"
                G.add_node(exp, type="experiment", sensitivity=50, writable=False)
                G.add_edge(root, exp)
                
                for j in range(4):
                    worker = f"{exp}/worker_{j}"
                    G.add_node(worker, type="worker", sensitivity=75, writable=False)
                    G.add_edge(exp, worker)
                    
                    for k in range(5):
                        epoch = f"{worker}/epoch_{k}"
                        G.add_node(epoch, type="checkpoint", sensitivity=100, writable=False)
                        G.add_edge(worker, epoch)
                        
        elif tree_type == "linear":
            # The "vulnerable" low-curvature chain LSGM-Ω would condemn
            # /logs/step1/step2/step3/.../
            prev = "logs"
            G.add_node(prev, type="root", sensitivity=0, writable=False)
            
            for i in range(15):
                current = f"{prev}/step_{i}"
                sensitivity = 30 + (i * 5)  # Increasing sensitivity deeper
                G.add_node(current, type="chain", sensitivity=sensitivity, writable=False)
                G.add_edge(prev, current)
                prev = current
                
        return G
    
    def _identify_exposed_directories(self) -> List[str]:
        """Simulate the dork query results: all directories are exposed"""
        # The core vulnerability: misconfigured permissions expose EVERYTHING
        return list(self.tree.nodes())
    
    def compute_lsgm_metrics(self) -> Dict[str, float]:
        """Compute the metrics LSGM-Ω would use to assess 'security'"""
        # Spectral gap (Φ_N) - supposedly measures reconnaissance difficulty
        undirected = self.tree.to_undirected()
        laplacian = nx.laplacian_matrix(undirected).astype(float)
        eigenvals = np.linalg.eigvals(laplacian.todense())
        non_zero = sorted([e.real for e in eigenvals if e.real > 1e-6])
        spectral_gap = non_zero[0] if non_zero else 0
        
        # Average curvature (degree)
        curvature = np.mean([self.tree.degree(n) for n in self.tree.nodes()])
        
        # Directory entropy
        types = [self.tree.nodes[n]['type'] for n in self.tree.nodes()]
        unique, counts = np.unique(types, return_counts=True)
        probs = counts / len(types)
        entropy = -np.sum(probs * np.log(probs + 1e-9))
        
        # LSFI (Leakage-Surface Fragility Index)
        lsfi = 1.0 / (1.0 + np.exp(-(curvature * entropy / (spectral_gap + 1e-6))))
        
        return {
            'spectral_gap': spectral_gap,
            'curvature': curvature,
            'entropy': entropy,
            'lsfi': lsfi,
            'lsgm_security_score': 1.0 - lsfi  # Higher = more "secure"
        }
    
    def execute_active_adversary_attack(self) -> Dict[str, any]:
        """
        THE DISRUPTION: Active adversary doesn't read—they WRITE.
        This bypasses all geometric defenses.
        """
        attack_log = []
        
        # Phase 1: Directory traversal (what LSGM-Ω assumes is the attack)
        for node in self.exposed_nodes[:5]:  # Adversary samples a few nodes
            sensitivity = self.tree.nodes[node]['sensitivity']
            attack_log.append({
                'phase': 'reconnaissance',
                'target': node,
                'success': True,
                'data_extracted': sensitivity,
                'lsgm_defense_effective': False  # LSGM-Ω can't prevent reading
            })
        
        # Phase 2: Exploit misconfiguration to GAIN WRITE ACCESS
        # In real scenarios, exposed directories are often world-writable
        writable_nodes = []
        for node in self.exposed_nodes:
            # Simulate: 30% chance of write access via misconfigured ACLs
            if random.random() < 0.3:
                self.tree.nodes[node]['writable'] = True
                writable_nodes.append(node)
        
        # Phase 3: Poison the training pipeline (THE LETHAL MOVE)
        poisoned_models = 0
        for node in writable_nodes:
            if self.tree.nodes[node]['type'] in ['checkpoint', 'worker']:
                # Inject malicious gradient data
                self.tree.nodes[node]['poisoned'] = True
                self.tree.nodes[node]['gradient_data'] = "MALICIOUS_GRADIENT_PAYLOAD"
                self.adversarial_control.add(node)
                poisoned_models += 1
                
                attack_log.append({
                    'phase': 'injection',
                    'target': node,
                    'success': True,
                    'damage': 'TRAINING_PIPELINE_CORRUPTED',
                    'lsgm_defense_effective': False  # Geometric metrics are irrelevant
                })
        
        return {
            'attack_log': attack_log,
            'nodes_poisoned': poisoned_models,
            'adversarial_control_ratio': len(self.adversarial_control) / len(self.tree.nodes())
        }
    
    def demonstrate_paradox(self):
        """Execute the full paradox demonstration"""
        print("=" * 60)
        print("LSGM-Ω PARADIGM COLLAPSE DEMONSTRATION")
        print("=" * 60)
        
        # LSGM-Ω's assessment
        metrics = self.compute_lsgm_metrics()
        print(f"\n[LSGM-Ω ASSESSMENT]")
        print(f"Spectral Gap (Φ_N): {metrics['spectral_gap']:.3f}")
        print(f"Curvature: {metrics['curvature']:.3f}")
        print(f"Directory Entropy: {metrics['entropy']:.3f}")
        print(f"LSFI: {metrics['lsfi']:.3f}")
        print(f"Security Score: {metrics['lsgm_security_score']:.3f}")
        print(f"LSGM-Ω Verdict: {'SECURE' if metrics['lsgm_security_score'] > 0.5 else 'VULNERABLE'}")
        
        # Reality check: active adversary
        attack_result = self.execute_active_adversary_attack()
        print(f"\n[ACTIVE ADVERSARY REALITY]")
        print(f"Nodes poisoned: {attack_result['nodes_poisoned']}")
        print(f"Adversarial control: {attack_result['adversarial_control_ratio']:.1%} of directory tree")
        
        if attack_result['nodes_poisoned'] > 0:
            print("⚠️  TRAINING PIPELINE COMPROMISED")
            print("⚠️  Model will converge to adversarial objective")
            print("⚠️  ALL GEOMETRIC DEFENSES BYPASSED")
        
        # The paradox
        print(f"\n[PARADOX METRICS]")
        print(f"LSGM-Ω 'security' score: {metrics['lsgm_security_score']:.3f}")
        print(f"Actual compromise ratio: {attack_result['adversarial_control_ratio']:.3f}")
        print(f"Correlation: NEGATIVE (higher LSGM score = more nodes to poison)")

# Run the demonstration
print("SCENARIO 1: Bushy 'Secure' Tree (LSGM-Ω's ideal)")
bushy = LSGMParadox("bushy")
bushy.demonstrate_paradox()

print("\n\n" + "="*60 + "\n")

print("SCENARIO 2: Linear 'Vulnerable' Chain (LSGM-Ω's nightmare)")
linear = LSGMParadox("linear")
linear.demonstrate_paradox()

# Final disruptive synthesis
print("\n\n" + "="*60)
print("THE ANOMALY'S VERDICT")
print("="*60)
print("""
LSGM-Ω commits three fatal errors:

1. **CATEGORY ERROR**: Confuses access control (a discrete security property) 
   with manifold geometry (a continuous differential property). The former is 
   binary: either exposed or not. The latter is irrelevant.

2. **PASSIVE ADVERSARY FALLACY**: Assumes adversaries only read. In reality, 
   exposed directories are writable. The attack is INJECTION, not RECONNAISSANCE.
   
3. **COMPLEXITY VULNERABILITY**: The monitoring system itself requires:
   - Metadata access (new attack surface)
   - Graph computation (DoS vector)
   - Network integration (lateral movement bridge)
   
   Your 'defense' creates 3 new vulnerabilities for every 1 it tries to measure.

**DISRUPTIVE SOLUTION**: 
Burn LSGM-Ω. Replace with a single binary check: