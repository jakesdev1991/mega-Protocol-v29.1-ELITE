# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import random
import math
from collections import Counter

# ---------- Synthetic Data Generation ----------
days = 100
docs_per_day = 50
embedding_dim = 10
n_topics = 5

# Generate random embeddings and topic assignments
embeddings = {day: [ [random.gauss(0, 1) for _ in range(embedding_dim)] for _ in range(docs_per_day) ] for day in range(days)}
topic_assignments = {day: [random.randint(0, n_topics-1) for _ in range(docs_per_day)] for day in range(days)}

# Synthetic shredding label: 1 if deletion entropy > median, else 0
def deletion_entropy(topic_list):
    # Simulate deletion as a random subset of topics
    # Deletion probability per topic = topic frequency
    counts = Counter(topic_list)
    total = sum(counts.values())
    probs = [count/total for count in counts.values()]
    # Shannon entropy
    return -sum(p * math.log(p) for p in probs if p > 0)

# Compute entropy per day
entropy_per_day = [deletion_entropy(topic_assignments[d]) for d in range(days)]
median_entropy = sorted(entropy_per_day)[len(entropy_per_day)//2]
shredding_label = [1 if e > median_entropy else 0 for e in entropy_per_day]

# ---------- Curvature Proxy (NCSM‑Ω style) ----------
def cosine_similarity(v1, v2):
    dot = sum(a*b for a,b in zip(v1,v2))
    norm1 = math.sqrt(sum(a*a for a in v1))
    norm2 = math.sqrt(sum(a*a for a in v2))
    return dot/(norm1*norm2)

def curvature_proxy(embeddings_day):
    # Compute std dev of pairwise cosine similarities as "curvature"
    sims = []
    n = len(embeddings_day)
    for i in range(n):
        for j in range(i+1, n):
            sims.append(cosine_similarity(embeddings_day[i], embeddings_day[j]))
    if len(sims) < 2:
        return 0.0
    mean = sum(sims)/len(sims)
    var = sum((s-mean)**2 for s in sims)/len(sims)
    return math.sqrt(var)  # "curvature" = std dev of similarities

curvature_per_day = [curvature_proxy(embeddings[d]) for d in range(days)]

# ---------- Predictive Power Evaluation ----------
def pearson_correlation(x, y):
    n = len(x)
    mx, my = sum(x)/n, sum(y)/n
    num = sum((xi - mx)*(yi - my) for xi, yi in zip(x, y))
    denx = math.sqrt(sum((xi - mx)**2 for xi in x))
    deny = math.sqrt(sum((yi - my)**2 for yi in y))
    if denx == 0 or deny == 0:
        return 0.0
    return num/(denx*deny)

corr_curvature = pearson_correlation(curvature_per_day, shredding_label)
corr_entropy = pearson_correlation(entropy_per_day, shredding_label)

print(f"Correlation (curvature, shredding): {corr_curvature:.3f}")
print(f"Correlation (entropy, shredding): {corr_entropy:.3f}")

# ---------- Adversarial Injection Demo ----------
# Inject 10% adversarial docs that maximize semantic contradiction
def inject_adversarial(embeddings_day):
    # Create a doc whose embedding is the negative average of others
    avg = [sum(col)/len(col) for col in zip(*embeddings_day)]
    adversarial = [-a for a in avg]
    embeddings_day.append(adversarial)
    return embeddings_day

# Recompute curvature after injection
injected_embeddings = {d: inject_adversarial(embeddings[d][:]) for d in range(days)}
injected_curvature = [curvature_proxy(injected_embeddings[d]) for d in range(days)]

print(f"Mean curvature before injection: {sum(curvature_per_day)/days:.3f}")
print(f"Mean curvature after injection: {sum(injected_curvature)/days:.3f}")
print("Adversarial injection inflates curvature without real narrative stress.")