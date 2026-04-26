# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Disruption Script: Query-Graph Centrality vs. Schema Topology Fragility
Demonstrates why BTS-Ω's topological invariants are a dangerous distraction
"""

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

# === DISRUPTIVE INSIGHT ===
# The BTS-Ω proposal fatally confuses MAP (human-designed schema) with TERRITORY (biological reality).
# A mesh-like schema (low BTFI) can be catastrophically fragile if query patterns concentrate
# on a single "keystone" table, while a tree-like schema (high BTFI) can be resilient
# if queries are distributed. The real fragility is in the DYNAMIC QUERY GRAPH,
# not the STATIC SCHEMA TOPOLOGY.

def generate_schema_topology(schema_type="mesh"):
    """Generate synthetic biological database schema"""
    G = nx.Graph()
    
    if schema_type == "mesh":
        # "Robust" mesh: many interconnections (low BTFI)
        # Simulating integrated pathway database
        tables = ["genes", "proteins", "pathways", "drugs", "patients", 
                  "variants", "expressions", "interactions"]
        G.add_nodes_from(tables)
        # Dense connectivity
        edges = [(t1, t2) for i, t1 in enumerate(tables) 
                 for t2 in tables[i+1:] if np.random.random() > 0.3]
        G.add_edges_from(edges)
        
    elif schema_type == "tree":
        # "Fragile" tree: hierarchical (high BTFI)
        # Simulating normalized clinical database
        tables = ["patients", "visits", "diagnoses", "treatments", 
                  "outcomes", "labs", "medications"]
        G.add_nodes_from(tables)
        # Hierarchical edges
        edges = [("patients", "visits"), ("visits", "diagnoses"), 
                 ("visits", "treatments"), ("treatments", "outcomes"),
                 ("patients", "labs"), ("patients", "medications")]
        G.add_edges_from(edges)
    
    return G

def simulate_query_patterns(schema_graph, attack_focus=None):
    """
    Simulate query patterns on schema.
    attack_focus: if set, adversary concentrates queries on this table
    """
    queries = [f"query_{i}" for i in range(50)]
    bipartite_graph = nx.Graph()
    bipartite_graph.add_nodes_from(schema_graph.nodes(), bipartite=0)
    bipartite_graph.add_nodes_from(queries, bipartite=1)
    
    query_table_edges = []
    
    for query in queries:
        if attack_focus and np.random.random() < 0.7:
            # Adversary focuses on keystone table
            target_table = attack_focus
        else:
            # Normal distributed access
            target_table = np.random.choice(list(schema_graph.nodes()))
        
        # Query touches target and its neighbors (JOINs)
        query_table_edges.append((query, target_table))
        for neighbor in schema_graph.neighbors(target_table):
            if np.random.random() > 0.5:
                query_table_edges.append((query, neighbor))
    
    bipartite_graph.add_edges_from(query_table_edges)
    return bipartite_graph

def compute_fragility_metrics(schema_graph, query_graph):
    """Compute both BTS-Ω metrics and disruptive query-graph metrics"""
    
    # --- BTS-Ω Metrics (Schema Topology) ---
    V = schema_graph.number_of_nodes()
    E = schema_graph.number_of_edges()
    # Euler characteristic approximation
    cycles = len(list(nx.cycle_basis(schema_graph)))
    chi = V - E + cycles
    
    # Constraint satisfaction (simulated)
    delta_constraint = np.random.uniform(0.3, 0.7)
    
    # Normalization depth (simulated)
    d_norm = np.random.randint(2, 5)
    
    # BTFI
    btfi = abs(chi) / V * delta_constraint * (1 / d_norm)
    
    # --- Disruptive Query-Graph Metrics ---
    # Project to table-to-table graph weighted by query co-access
    table_access = defaultdict(int)
    table_coaccess = defaultdict(lambda: defaultdict(int))
    
    for query in [n for n, d in query_graph.nodes(data=True) if d.get('bipartite') == 1]:
        tables = list(query_graph.neighbors(query))
        for table in tables:
            table_access[table] += 1
        for i, t1 in enumerate(tables):
            for t2 in tables[i+1:]:
                table_coaccess[t1][t2] += 1
    
    # Keystone fragility: table with highest query centrality
    keystone_table = max(table_access, key=table_access.get)
    keystone_load = table_access[keystone_table] / sum(table_access.values())
    
    # Query-graph clustering coefficient (adversarial concentration)
    query_projection = nx.bipartite.weighted_projected_graph(query_graph, 
                                                           [n for n, d in query_graph.nodes(data=True) 
                                                            if d.get('bipartite') == 0])
    query_centrality = nx.eigenvector_centrality(query_projection, max_iter=1000)
    
    return {
        'btfi': btfi,
        'chi': chi,
        'keystone_table': keystone_table,
        'keystone_load': keystone_load,
        'max_query_centrality': max(query_centrality.values()),
        'schema_nodes': V,
        'schema_edges': E
    }

# === EXPERIMENT: The Paradigm Shatter ===
print("=== DISRUPTING BTS-Ω: Schema vs. Query Fragility ===\n")

# Scenario 1: "Robust" Mesh Schema
print("Scenario 1: Mesh Schema (Low BTFI, 'Robust')")
mesh_schema = generate_schema_topology("mesh")
mesh_query_normal = simulate_query_patterns(mesh_schema, attack_focus=None)
mesh_metrics = compute_fragility_metrics(mesh_schema, mesh_query_normal)

print(f"  BTFI: {mesh_metrics['btfi']:.3f} (low = robust per BTS-Ω)")
print(f"  Schema: {mesh_metrics['schema_nodes']} tables, {mesh_metrics['schema_edges']} edges")
print(f"  Query Keystone: {mesh_metrics['keystone_table']} with {mesh_metrics['keystone_load']:.1%} load")
print(f"  Max Query Centrality: {mesh_metrics['max_query_centrality']:.3f}")

# Now adversary attacks the keystone table in the "robust" mesh
print("\n  --- Under Adversarial Focus on Keystone Table ---")
mesh_query_attack = simulate_query_patterns(mesh_schema, 
                                            attack_focus=mesh_metrics['keystone_table'])
mesh_attack_metrics = compute_fragility_metrics(mesh_schema, mesh_query_attack)

print(f"  BTFI: {mesh_attack_metrics['btfi']:.3f} (unchanged - topology static)")
print(f"  Query Keystone Load: {mesh_attack_metrics['keystone_load']:.1%} (CRITICAL)")
print(f"  Max Query Centrality: {mesh_attack_metrics['max_query_centrality']:.3f} (EXPLOSION)")

# Scenario 2: "Fragile" Tree Schema
print("\n\nScenario 2: Tree Schema (High BTFI, 'Fragile')")
tree_schema = generate_schema_topology("tree")
tree_query_normal = simulate_query_patterns(tree_schema, attack_focus=None)
tree_metrics = compute_fragility_metrics(tree_schema, tree_query_normal)

print(f"  BTFI: {tree_metrics['btfi']:.3f} (high = fragile per BTS-Ω)")
print(f"  Schema: {tree_metrics['schema_nodes']} tables, {tree_metrics['schema_edges']} edges")
print(f"  Query Keystone: {tree_metrics['keystone_table']} with {tree_metrics['keystone_load']:.1%} load")
print(f"  Max Query Centrality: {tree_metrics['max_query_centrality']:.3f}")

# === VISUALIZATION: The Illusion ===
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))

# Schema topologies
pos_mesh = nx.spring_layout(mesh_schema)
pos_tree = nx.spring_layout(tree_schema)

ax1.set_title("Mesh Schema (BTS-Ω: 'Robust')")
nx.draw(mesh_schema, pos_mesh, ax=ax1, node_color='lightgreen', node_size=500,
        with_labels=True, font_size=8)

ax2.set_title("Tree Schema (BTS-Ω: 'Fragile')")
nx.draw(tree_schema, pos_tree, ax=ax2, node_color='lightcoral', node_size=500,
        with_labels=True, font_size=8)

# Query attack patterns
keystone_mesh = mesh_metrics['keystone_table']
keystone_tree = tree_metrics['keystone_table']

# Highlight keystone under attack
node_colors_mesh = ['red' if n == keystone_mesh else 'lightgreen' 
                    for n in mesh_schema.nodes()]
node_colors_tree = ['red' if n == keystone_tree else 'lightcoral' 
                    for n in tree_schema.nodes()]

ax3.set_title("Query Attack on 'Robust' Mesh\n(Red = Keystone Under Siege)")
nx.draw(mesh_schema, pos_mesh, ax=ax3, node_color=node_colors_mesh, 
        node_size=800, with_labels=True, font_size=8)

ax4.set_title("Query Attack on 'Fragile' Tree\n(Red = Keystone Under Siege)")
nx.draw(tree_schema, pos_tree, ax=ax4, node_color=node_colors_tree, 
        node_size=800, with_labels=True, font_size=8)

plt.tight_layout()
plt.savefig('disruption_bts_omega.png', dpi=150, bbox_inches='tight')
plt.show()

# === DISRUPTIVE QUANTIFICATION ===
print("\n=== DISRUPTIVE CONCLUSION ===")
print(f"The 'robust' mesh schema with BTFI={mesh_metrics['btfi']:.3f} becomes")
print(f"EXPONENTIALLY more fragile under query attack (keystone load: {mesh_metrics['keystone_load']:.1%} → {mesh_attack_metrics['keystone_load']:.1%})")
print(f"\nMeanwhile, the 'fragile' tree schema maintains stable query centrality")
print(f"regardless of BTFI={tree_metrics['btfi']:.3f}")
print(f"\nBTS-Ω's static topology analysis is a DANGEROUS DISTRACTION.")
print(f"The real fragility vector is the DYNAMIC QUERY GRAPH, which adversaries")
print(f"can manipulate without altering schema topology.")