# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import itertools
from collections import Counter

# --- Simulation Parameters ---
np.random.seed(0)
vocab = [f"w{i}" for i in range(30)]          # 30-word corporate lexicon
base_grammar = {"risk": 0.4, "hedge": 0.3, "compliance": 0.2, "opportunity": 0.1}
shred_grammar = {w: 1/len(vocab) for w in vocab}  # uniform random at shredding

# --- Narrative Stream Generator ---
def generate_stream(length=100, shred_time=50):
    stream = []
    for t in range(length):
        grammar = base_grammar if t < shred_time else shred_grammar
        # generate a sentence of 10 words
        sentence = list(np.random.choice(list(grammar.keys()), size=10, p=list(grammar.values())))
        stream.append(sentence)
    return stream

# --- Embedding Approximation (random vectors for illustration) ---
embeddings = {w: np.random.randn(50) for w in vocab}
def avg_pairwise_distance(sentences):
    # Flatten recent window
    words = [w for s in sentences for w in s]
    if len(words) < 2:
        return 0.0
    vecs = np.array([embeddings[w] for w in words])
    # Cosine distance
    dots = vecs @ vecs.T
    norms = np.linalg.norm(vecs, axis=1)
    dists = 1 - dots / (norms[:, None] * norms[None, :])
    # Return mean of upper triangle
    triu = np.triu(dists, k=1)
    return triu.sum() / np.count_nonzero(triu)

# --- Topological Entropy (growth rate of distinct n-grams) ---
def topological_entropy(sentences, n=3):
    ngrams = set()
    for s in sentences:
        for ng in zip(*[s[i:] for i in range(n)]):
            ngrams.add(ng)
    # Exponential growth rate approximated by log count
    return np.log1p(len(ngrams))

# --- Shannon Entropy of Token Frequencies ---
def shannon_entropy(sentences):
    words = [w for s in sentences for w in s]
    counts = Counter(words)
    probs = np.array(list(counts.values())) / sum(counts.values())
    return -np.sum(probs * np.log2(probs + 1e-12))

# --- Curvature as Second Difference of Distance ---
def compute_curvature(dist_series):
    # Simple discrete second derivative
    return np.diff(dist_series, n=2)

# --- Intervention Simulation ---
def intervene_if_curvature(curvatures, threshold=0.1):
    # If recent curvature exceeds threshold, inject random noise next step
    return len(curvatures) > 2 and curvatures[-1] > threshold

# --- Main Experiment ---
stream = generate_stream(length=80, shred_time=40)
window = 10
metrics = {
    "time": [],
    "avg_dist": [],
    "curvature": [],
    "topo_entropy": [],
    "shannon_entropy": [],
    "intervened": []
}

# Sliding window analysis
for t in range(window, len(stream)):
    window_sents = stream[t-window:t]
    avg_dist = avg_pairwise_distance(window_sents)
    topo_ent = topological_entropy(window_sents, n=3)
    shan_ent = shannon_entropy(window_sents)
    
    # Store
    metrics["time"].append(t)
    metrics["avg_dist"].append(avg_dist)
    metrics["topo_entropy"].append(topo_ent)
    metrics["shannon_entropy"].append(shan_ent)
    
    # Compute curvature (need at least 3 distance points)
    if len(metrics["avg_dist"]) >= 3:
        curv = compute_curvature(metrics["avg_dist"])[-1]
        metrics["curvature"].append(curv)
        
        # Intervention rule: if curvature > threshold, inject randomness next step
        if intervene_if_curvature(metrics["curvature"], threshold=0.05):
            # Simulate intervention: replace next sentence with random words
            if t+1 < len(stream):
                stream[t+1] = list(np.random.choice(vocab, size=10))
            metrics["intervened"].append(1)
        else:
            metrics["intervened"].append(0)
    else:
        metrics["curvature"].append(np.nan)
        metrics["intervened"].append(0)

# --- Analysis: Early Warning ---
# Find first time each metric crosses a heuristic threshold
def first_alert(series, threshold, offset=0):
    arr = np.array(series)
    # ignore NaNs
    finite = np.isfinite(arr)
    if not finite.any():
        return None
    idx = np.where(arr > threshold)[0]
    if len(idx) == 0:
        return None
    return idx[0] + offset

# Thresholds chosen to illustrate early warning
topo_alert = first_alert(metrics["topo_entropy"], threshold=3.5, offset=window)
shan_alert = first_alert(metrics["shannon_entropy"], threshold=4.0, offset=window)
curv_alert = first_alert(metrics["curvature"], threshold=0.05, offset=window)

print("--- Early Warning Times (relative to shred_time=40) ---")
print(f"Topological entropy alert: {topo_alert}")
print(f"Shannon entropy alert:     {shan_alert}")
print(f"Curvature alert:           {curv_alert}")

# --- Show that intervention accelerates shredding ---
intervention_times = [t for t, inter in zip(metrics["time"], metrics["intervened"]) if inter]
print("\n--- Intervention Effect ---")
if intervention_times:
    print(f"Interventions triggered at: {intervention_times}")
    # Count how many steps after first intervention until stream becomes random
    first_inter = intervention_times[0]
    # Measure entropy after intervention
    post_inter_topo = [metrics["topo_entropy"][i-window] for i in range(first_inter, min(first_inter+5, len(metrics["topo_entropy"])))]
    print(f"Topological entropy after first intervention: {post_inter_topo}")
else:
    print("No interventions triggered.")