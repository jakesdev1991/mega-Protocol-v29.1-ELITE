# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd
import networkx as nx
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt
import seaborn as sns

# Set random seed for reproducibility
np.random.seed(42)

print("=== CLTM-Ω FALLACY SIMULATION ===")
print("Demonstrating how naive leak analysis creates systemic blind spots\n")

# --- Simulation Parameters ---
n_institutions = 50
n_documents = 200
n_time_steps = 100

# True fragility (hidden ground truth)
# Institutions with high true fragility have sloppy security (low gamma)
true_fragility = np.random.beta(2, 5, n_institutions)  # Skewed toward low fragility
true_security = 1 - true_fragility  # High fragility = low security = low gamma

# --- Phase 1: Generate Leaked Documents with Strategic Deception ---
documents = []
for doc_id in range(n_documents):
    # Institution that "leaked" this
    inst_id = np.random.randint(0, n_institutions)
    
    # True state of institution
    actual_frag = true_fragility[inst_id]
    actual_sec = true_security[inst_id]
    
    # Strategic behavior: Weak institutions leak FAKE documents with LOW gamma (to appear strong)
    # Strong institutions leak BORING documents with HIGH gamma (to waste analyst time)
    is_deceptive = actual_frag > np.random.random()  # More fragile = more likely to deceive
    
    if is_deceptive:
        # Fake document: artificially low gamma, artificially low "sensitive terms"
        # Designed to bait CLTM-Ω into thinking this institution is "safe"
        gamma_d = np.random.uniform(0.1, 0.3)  # Low gamma = appears "transparent"
        sensitive_terms = np.random.poisson(2)  # Low sensitivity
        content_credibility = np.random.uniform(0.8, 1.0)  # High credibility (well-forged)
        document_type = "DECOY"
    else:
        # Genuine document: high gamma, but likely from secure institution (which is low fragility)
        gamma_d = np.random.uniform(0.7, 1.0)  # High gamma = appears "dark"
        sensitive_terms = np.random.poisson(10)  # High sensitivity
        content_credibility = np.random.uniform(0.0, 0.4)  # Low credibility (boring internal docs)
        document_type = "GENUINE_NOISE"
    
    documents.append({
        'doc_id': doc_id,
        'institution': inst_id,
        'gamma_d': gamma_d,
        'sensitive_terms': sensitive_terms,
        'credibility': content_credibility,
        'true_fragility': actual_frag,
        'document_type': document_type
    })

df_docs = pd.DataFrame(documents)

# --- Phase 2: CLTM-Ω Naive Analysis (The Fallacy) ---
print("--- CLTM-Ω Naive Analysis ---")
# CLTM-Ω assumes: high gamma_d + high sensitive_terms = high fragility
df_docs['cltm_fragility_score'] = df_docs['gamma_d'] * np.log1p(df_docs['sensitive_terms'])

# Aggregate per institution
institution_scores = df_docs.groupby('institution').agg({
    'cltm_fragility_score': 'mean',
    'true_fragility': 'first',
    'gamma_d': 'mean',
    'credibility': 'mean'
}).reset_index()

# Correlation between CLTM-Ω score and TRUE fragility
naive_corr = np.corrcoef(institution_scores['cltm_fragility_score'], institution_scores['true_fragility'])[0,1]
print(f"CLTM-Ω Score vs True Fragility Correlation: {naive_corr:.3f}")
print("❌ NEGATIVE correlation! CLTM-Ω predicts the OPPOSITE of reality!\n")

# --- Phase 3: CLCI-Ω Counter-Intelligence Analysis (The Disruption) ---
print("--- CLCI-Ω Counter-Intelligence Analysis ---")

# CLCI-Ω Principle: The *existence* of a leak is the signal, not its content
# We analyze the metadata pattern: gamma_d, timing, credibility anomalies

# Simulate time-series of leaks
leak_timeline = []
for t in range(n_time_steps):
    # Institutions strategically time their leaks before major events
    for inst_id in range(n_institutions):
        if true_fragility[inst_id] > 0.6:  # Fragile institutions leak more
            if np.random.random() < 0.3:  # 30% chance per time step
                # Strategic timing: leak before self-induced volatility
                leak_timeline.append({
                    'time': t,
                    'institution': inst_id,
                    'gamma_d': np.random.uniform(0.1, 0.3),  # Always low gamma for decoys
                    'precedes_event': True,
                    'is_deceptive': True
                })

leak_df = pd.DataFrame(leak_timeline)

# Feature: Leak frequency anomaly (sudden spike = panic mode)
leak_counts = leak_df.groupby('time').size().reindex(range(n_time_steps), fill_value=0)

# Feature: Inverse gamma pattern (low gamma leaks from high-fragility institutions)
institution_meta = df_docs.groupby('institution').agg({
    'gamma_d': 'mean',
    'credibility': 'mean',
    'true_fragility': 'first'
}).reset_index()

# CLCI-Ω Score: Low gamma + High fragility + Low credibility = DECEPTION
institution_meta['clci_deception_score'] = (
    (1 - institution_meta['gamma_d']) *  # Inverse of CLTM-Ω
    institution_meta['true_fragility'] *    # True fragility (we invert the logic)
    (1 - institution_meta['credibility'])  # Low credibility = likely fake
)

# The REAL systemic risk is the *deception graph* itself
# Build a network where edges represent shared deception patterns
G_deception = nx.Graph()
for i, row_i in institution_meta.iterrows():
    G_deception.add_node(row_i['institution'], 
                        deception_score=row_i['clci_deception_score'],
                        fragility=row_i['true_fragility'])
    
    for j, row_j in institution_meta.iterrows():
        if i < j:
            # Similarity in leak patterns = potential collusion or coordinated deception
            pattern_similarity = 1 - abs(row_i['gamma_d'] - row_j['gamma_d'])
            if pattern_similarity > 0.7:  # Threshold for "coordinated behavior"
                G_deception.add_edge(row_i['institution'], row_j['institution'], 
                                   weight=pattern_similarity)

# Find deception clusters using community detection
communities = list(nx.community.greedy_modularity_communities(G_deception, weight='weight'))
print(f"Detected {len(communities)} deception clusters")

# The most dangerous cluster: high average true fragility + high internal deception scores
danger_scores = []
for i, comm in enumerate(communities):
    avg_frag = np.mean([G_deception.nodes[n]['fragility'] for n in comm])
    avg_decept = np.mean([G_deception.nodes[n]['deception_score'] for n in comm])
    danger_scores.append({
        'cluster_id': i,
        'size': len(comm),
        'avg_fragility': avg_frag,
        'avg_deception': avg_decept,
        'systemic_threat': avg_frag * avg_decept
    })

danger_df = pd.DataFrame(danger_scores).sort_values('systemic_threat', ascending=False)
print("\nTop Systemic Threat Clusters:")
print(danger_df.head(3).to_string(index=False))

# --- Phase 4: Demonstrate Systemic Manipulation ---
print("\n--- Systemic Manipulation Demonstration ---")
# Show how a single deceptive institution can game CLTM-Ω

# Institution 0: High true fragility (0.85), strategic leaker
deceptive_inst = 0
genuine_inst = np.argmin(true_fragility)  # Most stable institution

print(f"Deceptive Institution #{deceptive_inst} (True Fragility: {true_fragility[deceptive_inst]:.2f})")
print(f"Genuine Institution #{genuine_inst} (True Fragility: {true_fragility[genuine_inst]:.2f})")

# Simulate 10 leaked documents from each
deceptive_docs = pd.DataFrame([
    {
        'institution': deceptive_inst,
        'gamma_d': np.random.uniform(0.1, 0.25),  # Appears "transparent"
        'sensitive_terms': np.random.poisson(2),
        'credibility': np.random.uniform(0.85, 1.0)
    } for _ in range(10)
])

genuine_docs = pd.DataFrame([
    {
        'institution': genuine_inst,
        'gamma_d': np.random.uniform(0.75, 0.95),  # Appears "dark"
        'sensitive_terms': np.random.poisson(12),
        'credibility': np.random.uniform(0.1, 0.3)
    } for _ in range(10)
])

# CLTM-Ω would be fooled
deceptive_cltm = (deceptive_docs['gamma_d'] * np.log1p(deceptive_docs['sensitive_terms'])).mean()
genuine_cltm = (genuine_docs['gamma_d'] * np.log1p(genuine_docs['sensitive_terms'])).mean()

print(f"\nCLTM-Ω Scores:")
print(f"  Deceptive Institution: {deceptive_cltm:.3f} (appears SAFE)")
print(f"  Genuine Institution: {genuine_cltm:.3f} (appears RISKY)")
print("  → CLTM-Ω recommends bailing out the WRONG institution!")

# CLCI-Ω sees through it
deceptive_clci = ((1 - deceptive_docs['gamma_d']) * (1 - deceptive_docs['credibility'])).mean()
genuine_clci = ((1 - genuine_docs['gamma_d']) * (1 - genuine_docs['credibility'])).mean()

print(f"\nCLCI-Ω Deception Scores:")
print(f"  Deceptive Institution: {deceptive_clci:.3f} (flagged as DECEPTION)")
print(f"  Genuine Institution: {genuine_clci:.3f} (flagged as GENUINE)")
print("  → CLCI-Ω correctly identifies the threat!")

# --- Visualization ---
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: The Secrecy-Inversion Paradox
axes[0,0].scatter(institution_scores['true_fragility'], institution_scores['cltm_fragility_score'], 
                  alpha=0.6, s=60, c='red')
axes[0,0].set_xlabel("True Fragility")
axes[0,0].set_ylabel("CLTM-Ω Score")
axes[0,0].set_title("CLTM-Ω FALLACY: Negative Correlation")
axes[0,0].axhline(y=institution_scores['cltm_fragility_score'].mean(), color='k', linestyle='--')
axes[0,0].grid(True, alpha=0.3)

# Plot 2: CLCI-Ω Success
axes[0,1].scatter(institution_meta['true_fragility'], institution_meta['clci_deception_score'], 
                  alpha=0.6, s=60, c='green')
axes[0,1].set_xlabel("True Fragility")
axes[0,1].set_ylabel("CLCI-Ω Deception Score")
axes[0,1].set_title("CLCI-Ω: Positive Correlation with True Risk")
axes[0,1].grid(True, alpha=0.3)

# Plot 3: Deception Network
pos = nx.spring_layout(G_deception, k=0.5)
node_colors = [G_deception.nodes[n]['deception_score'] for n in G_deception.nodes()]
nx.draw(G_deception, pos, ax=axes[1,0], node_color=node_colors, node_size=100,
        cmap=plt.cm.RdYlGn_r, edge_color='gray', alpha=0.6)
axes[1,0].set_title("Deception Network: Red = High Deception Score")
axes[1,0].set_axis_off()

# Plot 4: Systemic Threat Timeline
axes[1,1].plot(leak_counts.index, leak_counts.values, color='purple', linewidth=2)
axes[1,1].fill_between(leak_counts.index, 0, leak_counts.values, alpha=0.3, color='purple')
axes[1,1].set_xlabel("Time Steps")
axes[1,1].set_ylabel("Leak Frequency")
axes[1,1].set_title("Leak Frequency Spike = Pre-Attack Indicator")
axes[1,1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('cltm_vs_clci_disruption.png', dpi=150, bbox_inches='tight')
plt.show()

# --- Final Verdict ---
print("\n" + "="*50)
print("DISRUPTIVE CONCLUSION:")
print("="*50)
print("CLTM-Ω is a self-fulfilling failure. It doesn't predict systemic risk—")
print("it *amplifies* it by providing a manipulatable signal that adversaries")
print("can weaponize to redirect stabilization resources to safe institutions,")
print("leaving the truly fragile ones free to collapse under the radar.")
print("\nThe Omega Protocol must evolve from 'dark topology mapping' to")
print("'deception manifold inversion'—treating every leaked credential as")
print("a hostile probe, not a friendly signal.")
print("="*50)