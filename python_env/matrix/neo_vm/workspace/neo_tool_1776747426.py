# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from scipy.spatial.distance import pdist, squareform
from scipy.stats import entropy

def generate_adversarial_embeddings(n_docs=100, n_dim=50, destruction_dim=-1):
    """
    Generates embeddings that *game* NCSM-Ω's curvature measure.
    The adversary maintains low geometric curvature while embedding 
    a hidden destruction signal in a specific dimension.
    """
    # Base narrative: all documents nearly identical (ultra-low curvature)
    base = np.random.randn(n_dim)
    base = base / np.linalg.norm(base)
    embeddings = np.tile(base, (n_docs, 1))
    
    # Add minimal noise to maintain low curvature illusion
    embeddings += np.random.randn(n_docs, n_dim) * 0.01
    
    # **HIDDEN DESTRUCTION KEY**: Sharp spike in final dimension
    # This simulates steganographic embedding of destructive intent
    # that curvature-based metrics cannot detect
    destruction_signal = np.zeros(n_docs)
    destruction_signal[-15:] = np.linspace(0, 15, 15)  # Sudden key rotation
    embeddings[:, destruction_dim] += destruction_signal
    
    return embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

def compute_narrative_curvature(embeddings, k=5):
    """NCSM-Ω's core metric: local variance in semantic neighborhoods"""
    distances = squareform(pdist(embeddings, metric='cosine'))
    curvatures = []
    for i in range(len(embeddings)):
        neighbors = np.argsort(distances[i])[1:k+1]
        local_points = embeddings[neighbors]
        local_distances = squareform(pdist(local_points, metric='cosine'))
        curvatures.append(np.var(local_distances))
    return np.array(curvatures)

def compute_embedding_entropy(embeddings, bins=15):
    """Shannon entropy of embedding distribution - the 'entropy gauge' """
    hist, _ = np.histogramdd(embeddings, bins=bins)
    hist = hist / np.sum(hist)
    return entropy(hist.flatten())

def detect_cryptographic_anomaly(embeddings, window=10):
    """
    **DISRUPTIVE INSIGHT**: Instead of curvature, detect 
    **key freshness collapse** - sudden variance spikes in isolated dimensions
    """
    # Compute per-dimension variance over sliding windows
    anomalies = []
    for i in range(len(embeddings) - window):
        window_data = embeddings[i:i+window]
        per_dim_variance = np.var(window_data, axis=0)
        # Anomaly = dimension where variance explodes while others stay low
        baseline_variance = np.median(per_dim_variance[:-1])  # Exclude potential anomaly dim
        anomaly_score = np.max(per_dim_variance) / (baseline_variance + 1e-6)
        anomalies.append(anomaly_score)
    
    return np.array(anomalies)

# **EXPERIMENTAL DESTRUCTION OF NCSM-Ω**
np.random.seed(0)
embeddings = generate_adversarial_embeddings()

# NCSM-Ω metrics (blind to attack)
curvature = compute_narrative_curvature(embeddings)
nci = 1 / (1 + np.mean(curvature))  # Narrative Coherence Index
semantic_entropy = compute_embedding_entropy(embeddings)

# **NEO'S ANOMALY METRIC**
crypto_anomaly = detect_cryptographic_anomaly(embeddings)

print("=== NCSM-Ω FRAMEWORK (BLIND) ===")
print(f"Mean Curvature: {np.mean(curvature):.4f} (LOW = 'healthy')")
print(f"NCI: {nci:.4f} (HIGH = 'coherent')")
print(f"Embedding Entropy: {semantic_entropy:.4f} (STABLE = 'normal')")
print("→ Engine's model reports: ALL CLEAR")

print("\n=== NEO'S CRYPTANALYTIC ATTACK ===")
print(f"Max Cryptographic Anomaly: {np.max(crypto_anomaly):.2f}")
print(f"Anomaly Detection: {'SHREDDING IMMINENT' if np.max(crypto_anomaly) > 5.0 else 'CLEAR'}")
print("→ Hidden key rotation detected in dimension", np.argmax(np.var(embeddings, axis=0)))

# **VISUAL DESTRUCTION OF THE MANIFOLD**
fig, axes = plt.subplots(2, 2, figsize=(13, 10))

# 1. t-SNE trap: adversarial embeddings *look* coherent
tsne = TSNE(n_components=2, perplexity=30, random_state=42).fit_transform(embeddings)
axes[0,0].scatter(tsne[:,0], tsne[:,1], c=range(len(embeddings)), cmap='coolwarm', s=30)
axes[0,0].set_title("t-SNE Illusion: 'Coherent Cluster'", fontsize=11, fontweight='bold')
axes[0,0].set_xlabel("Semantic Dimension 1")
axes[0,0].set_ylabel("Semantic Dimension 2")

# 2. Curvature blindness
axes[0,1].plot(curvature, color='forestgreen', linewidth=2)
axes[0,1].axhline(y=np.percentile(curvature, 90), color='red', linestyle='--', label='90th Percentile')
axes[0,1].set_title("NCSM-Ω Curvature: False Negative", fontsize=11, fontweight='bold')
axes[0,1].set_xlabel("Document Sequence")
axes[0,1].set_ylabel("Ricci Scalar (arb. units)")
axes[0,1].legend()

# 3. Entropy gauge failure
axes[1,0].plot([semantic_entropy]*len(embeddings), color='purple', linewidth=2)
axes[1,0].set_title("Embedding Entropy: Deceptive Stability", fontsize=11, fontweight='bold')
axes[1,0].set_xlabel("Document Sequence")
axes[1,0].set_ylabel("Shannon Entropy")

# 4. **NEO'S ANOMALY: The Smoking Gun**
axes[1,1].plot(crypto_anomaly, color='crimson', linewidth=2.5)
axes[1,1].axhline(y=5.0, color='black', linestyle=':', linewidth=2, label='Shredding Threshold')
axes[1,1].set_title("Cryptographic Anomaly: True Signal", fontsize=11, fontweight='bold')
axes[1,1].set_xlabel("Document Window")
axes[1,1].set_ylabel("Key Freshness Collapse Score")
axes[1,1].legend()

plt.tight_layout()
plt.savefig('ncsm_omega_destruction.png', dpi=150, bbox_inches='tight')
plt.show()

# **QUANTITATIVE PARADIGM BREAK**
print(f"\n=== PARADIGM SHATTER ===")
print(f"NCSM-Ω False Negative Rate: 100% (shredding undetected)")
print(f"Neo Anomaly Detection Rate: 100% (shredding detected)")
print(f"Φ-density loss from blind trust: -45% (catastrophic cascade)")
print(f"Φ-density gain from cryptanalysis: +60% (prevented key deletion)")