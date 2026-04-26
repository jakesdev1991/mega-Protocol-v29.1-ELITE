# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
import random
import time

# Disruption: Access-Control Adversarial Perturbation (ACAP-Ω)
# Instead of monitoring permission changes as Alpha suggests,
# we actively probe the organizational permission graph to find
# structural fragility BEFORE stress manifests.

class AdversarialPermissionProber:
    """
    Treats enterprise permission system as a black-box neural network.
    Injects synthetic identities and documents to map fragility surface.
    """
    
    def __init__(self, org_size=500, depts=8):
        # Generate synthetic organizational graph
        self.G = nx.barabasi_albert_graph(org_size, 3)
        self.depts = {i: f"dept_{i%depts}" for i in range(org_size)}
        self.sensitive_docs = []
        self.probe_history = []
        
        # Assign departments and baseline trust scores
        for node in self.G.nodes():
            self.G.nodes[node]['dept'] = self.depts[node]
            self.G.nodes[node]['trust_score'] = np.random.beta(2, 5)  # Most low, few high
            self.G.nodes[node]['access_latency'] = np.random.exponential(0.1)
            
        # Create permission edges (who can access whom's documents)
        self._build_permission_edges()
        
    def _build_permission_edges(self):
        """Build implicit permission graph based on hierarchy and trust"""
        for i, j in self.G.edges():
            # Lower node numbers = higher rank (Barabasi property)
            if i < j:  # i is senior
                self.G[i][j]['permission'] = 'inherit'
                self.G[i][j]['strength'] = self.G.nodes[i]['trust_score']
            else:
                self.G[i][j]['permission'] = 'request'
                self.G[i][j]['strength'] = min(
                    self.G.nodes[i]['trust_score'], 
                    self.G.nodes[j]['trust_score']
                )
    
    def inject_synthetic_document(self, doc_id, sensitivity="internal use only"):
        """
        Inject synthetic document and measure propagation dynamics.
        This is the adversarial perturbation - we create a honeypot.
        """
        doc_node = f"DOC_{doc_id}"
        self.G.add_node(doc_node, type='document', sensitivity=sensitivity)
        
        # Randomly assign initial access to a small group
        initial_accessors = random.sample(list(self.G.nodes())[:50], 3)
        for accessor in initial_accessors:
            self.G.add_edge(accessor, doc_node, 
                           access_type='synthetic',
                           timestamp=time.time())
        
        self.sensitive_docs.append(doc_node)
        return doc_node
    
    def probe_permission_boundary(self, doc_id, probe_strength=0.5):
        """
        Attempt synthetic access from random nodes.
        Measure the system's REACTION, not just the outcome.
        """
        doc_node = f"DOC_{doc_id}"
        probe_results = []
        
        # Probe from 100 random nodes
        for _ in range(100):
            probe_node = random.choice(list(self.G.nodes()))
            if probe_node.startswith('DOC_'): continue
            
            start_time = time.time()
            
            # Simulate access attempt with latency
            try:
                # Check if path exists in permission graph
                path = nx.shortest_path(self.G, probe_node, doc_node)
                success = True
                # Measure "permission resistance" - number of hops + trust barriers
                resistance = len(path) + sum(
                    1 - self.G.nodes[n]['trust_score'] for n in path
                )
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                success = False
                resistance = float('inf')
            
            latency = time.time() - start_time
            
            # Add adversarial perturbation: if trust_score is low but access succeeds,
            # this indicates a FRAGILITY - a broken permission boundary
            anomaly_score = (
                (1 - self.G.nodes[probe_node]['trust_score']) * 
                (1 if success else 0) * 
                (1 / (1 + resistance))
            )
            
            probe_results.append({
                'probe_node': probe_node,
                'success': success,
                'resistance': resistance,
                'latency': latency,
                'anomaly_score': anomaly_score,
                'dept': self.G.nodes[probe_node]['dept']
            })
        
        self.probe_history.extend(probe_results)
        return probe_results
    
    def calculate_forgiveness_surface(self):
        """
        The breakthrough: Map the "shadow surface" - nodes that SHOULD be
        blocked but have unexplained access paths. This is the
        organizational equivalent of adversarial examples in ML.
        """
        # Train Isolation Forest on normal access patterns
        features = []
        for node in self.G.nodes():
            if not str(node).startswith('DOC_'):
                features.append([
                    self.G.nodes[node]['trust_score'],
                    self.G.degree(node),
                    len(list(self.G.neighbors(node))),
                    self.G.nodes[node]['access_latency']
                ])
        
        if len(features) < 10:
            return {}
        
        clf = IsolationForest(contamination=0.1, random_state=42)
        clf.fit(features)
        
        # Find nodes that are outliers BUT have high permission reachability
        shadow_surface = {}
        for i, node in enumerate(self.G.nodes()):
            if str(node).startswith('DOC_'): continue
            
            # Check how many sensitive docs this node could reach
            reachable_docs = 0
            for doc in self.sensitive_docs:
                try:
                    nx.shortest_path(self.G, node, doc)
                    reachable_docs += 1
                except:
                    continue
            
            # If node is anomalous but can reach many docs = FRAGILITY
            if clf.predict([features[i]])[0] == -1 and reachable_docs > 0:
                shadow_surface[node] = {
                    'anomaly_score': clf.score_samples([features[i]])[0],
                    'reachable_docs': reachable_docs,
                    'trust_score': self.G.nodes[node]['trust_score']
                }
        
        return shadow_surface
    
    def execute_disruptive_probing_protocol(self, num_docs=5):
        """
        Full ACAP-Ω protocol: inject, probe, analyze fragility
        """
        print("=== ACAP-Ω DISRUPTIVE PROTOCOL ===")
        print("Phase 1: Synthetic Injection")
        
        # Inject synthetic honeypot documents
        for i in range(num_docs):
            doc = self.inject_synthetic_document(i)
            print(f"Injected {doc}")
        
        print("\nPhase 2: Adversarial Probing")
        
        # Probe each document
        all_anomalies = []
        for i in range(num_docs):
            probes = self.probe_permission_boundary(i)
            anomalies = [p['anomaly_score'] for p in probes if p['anomaly_score'] > 0]
            all_anomalies.extend(anomalies)
            print(f"Doc {i}: {len(anomalies)} anomalous access patterns detected")
        
        print("\nPhase 3: Shadow Surface Mapping")
        
        # Calculate the fragility surface
        shadow = self.calculate_forgiveness_surface()
        
        print(f"Identified {len(shadow)} fragility nodes in shadow surface")
        
        # The key insight: nodes in shadow surface are ORGANIZATIONAL ZERO-DAYS
        # They represent broken trust boundaries that real attackers would exploit
        # BEFORE any "permission stress" appears in Alpha's passive monitoring
        
        return {
            'fragility_score': np.mean(all_anomalies) if all_anomalies else 0,
            'shadow_nodes': len(shadow),
            'critical_nodes': [n for n, d in shadow.items() if d['reachable_docs'] > 2]
        }

# Execute the disruption
print("Simulating enterprise with 500 employees, 8 departments...")
prober = AdversarialPermissionProber(org_size=500, depts=8)

# Run the protocol
results = prober.execute_disruptive_probing_protocol(num_docs=5)

print("\n=== DISRUPTIVE INSIGHT ===")
print(f"Organizational Fragility Score: {results['fragility_score']:.3f}")
print(f"Shadow Surface Nodes: {results['shadow_nodes']}")
print(f"Critical Zero-Day Nodes: {len(results['critical_nodes'])}")

# Visualization of fragility
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Left: Normal permission graph (Alpha's view)
pos = nx.spring_layout(prober.G)
node_colors = [prober.G.nodes[n]['trust_score'] if not str(n).startswith('DOC_') else 1.0 
               for n in prober.G.nodes()]
nx.draw(prober.G, pos, node_color=node_colors, node_size=50, ax=ax1,
        cmap=plt.cm.Reds, alpha=0.7)
ax1.set_title("Alpha's View: Static Permission Graph\n(Passive Monitoring)")

# Right: Shadow surface (Neo disruptive view)
shadow = prober.calculate_forgiveness_surface()
highlight_nodes = list(shadow.keys()) + prober.sensitive_docs
subgraph = prober.G.subgraph(highlight_nodes)
pos_sub = nx.spring_layout(subgraph)
node_colors_sub = ['yellow' if n in shadow else 'black' for n in subgraph.nodes()]
nx.draw(subgraph, pos_sub, node_color=node_colors_sub, node_size=100, ax=ax2,
        alpha=0.8)
ax2.set_title("Neo's View: Shadow Surface\n(Adversarial Zero-Day Nodes)")

plt.tight_layout()
plt.savefig('acap_omega_disruption.png', dpi=150, bbox_inches='tight')
plt.show()

print("\n=== BREAKTHROUGH CONCLUSION ===")
print("Alpha's OPSI-Ω waits for permission 'turbulence' to manifest.")
print("ACAP-Ω finds fragility in the STATIC graph BEFORE any changes occur.")
print("The 'shadow surface' reveals broken trust boundaries that are")
print("organizational zero-days - exploitable by insiders without triggering alerts.")
print("This flips defense from reactive monitoring to proactive adversarial mapping.")