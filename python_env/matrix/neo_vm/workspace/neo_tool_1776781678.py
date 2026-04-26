# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import random
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

# ──────────────────────────────────────────────────────────────────────────────
# 1. Simulate a realistic ecosystem: 100 firms, 20 services
#    Only 10 % of credentials are real (production); 90 % are fake (test/placeholder)
# ──────────────────────────────────────────────────────────────────────────────
random.seed(42)
np.random.seed(42)

NUM_FIRMS = 100
NUM_SERVICES = 20
REAL_PROB = 0.1
FAKE_PROB = 0.9

G = nx.Graph()
firms = [f"F{i}" for i in range(NUM_FIRMS)]
services = [f"S{i}" for i in range(NUM_SERVICES)]
G.add_nodes_from(firms, bipartite=0)
G.add_nodes_from(services, bipartite=1)

# Each firm leaks 0‑5 credentials
for firm in firms:
    leaks = random.randint(0, 5)
    for _ in range(leaks):
        svc = random.choice(services)
        is_real = random.random() < REAL_PROB
        # Real credentials are high criticality (5), fake are low (1)
        criticality = 5 if is_real else 1
        dissemination = random.uniform(1, 10)
        weight = criticality * dissemination

        if G.has_edge(firm, svc):
            G[firm][svc]['weight'] += weight
            G[firm][svc]['count'] += 1
        else:
            G.add_edge(firm, svc, weight=weight, count=1, is_real=is_real)

# ──────────────────────────────────────────────────────────────────────────────
# 2. Compute SCCRM‑Ω Systemic Risk Score (SRS)
# ──────────────────────────────────────────────────────────────────────────────
def compute_srs(G, services, alpha=1.0, beta=1.0, decay_days=30, lambda_decay=0.1):
    decay = np.exp(-lambda_decay * decay_days)
    srs = {}
    for svc in services:
        total = 0.0
        for firm in G.neighbors(svc):
            data = G[firm][svc]
            # Use the stored criticality (5 for real, 1 for fake)
            crit = 5 if data.get('is_real', False) else 1
            w = data['weight'] * decay
            total += alpha * crit + beta * w
        srs[svc] = total
    return srs

srs_before = compute_srs(G, services)
riskiest_before = max(srs_before, key=srs_before.get)
print(f"Riskiest service (SCCRM‑Ω): {riskiest_before}  SRS={srs_before[riskiest_before]:.2f}")

# ──────────────────────────────────────────────────────────────────────────────
# 3. Adversarial Poisoning: inject 30 fake credentials for a target service
# ──────────────────────────────────────────────────────────────────────────────
TARGET = "S5"
for firm in random.sample(firms, 30):
    if G.has_edge(firm, TARGET):
        G[firm][TARGET]['weight'] += 1 * 5  # fake weight
        G[firm][TARGET]['count'] += 1
    else:
        G.add_edge(firm, TARGET, weight=1*5, count=1, is_real=False)

srs_after = compute_srs(G, services)
riskiest_after = max(srs_after, key=srs_after.get)
print(f"Riskiest service after poisoning: {riskiest_after}  SRS={srs_after[riskiest_after]:.2f}")
print(f"SRS increase for {TARGET}: {srs_after[TARGET] - srs_before.get(TARGET, 0):.2f}")

# ──────────────────────────────────────────────────────────────────────────────
# 4. Invert the graph: Resilience Score (negative weight for shared edges)
# ──────────────────────────────────────────────────────────────────────────────
def compute_resilience(G, services):
    # Resilience = -Σ weight (more shared → more negative → higher resilience)
    resilience = {}
    for svc in services:
        total = -sum(G[firm][svc]['weight'] for firm in G.neighbors(svc))
        resilience[svc] = total
    return resilience

resilience_scores = compute_resilience(G, services)
most_resilient = max(resilience_scores, key=resilience_scores.get)
print(f"Most resilient service (inverse SRS): {most_resilient}  Resilience={resilience_scores[most_resilient]:.2f}")

# ──────────────────────────────────────────────────────────────────────────────
# 5. Visualize the effect of poisoning
# ──────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(1, 2, figsize=(12, 5))

ax[0].bar(srs_before.keys(), srs_before.values(), color='steelblue', alpha=0.7)
ax[0].set_title('SRS before poisoning')
ax[0].set_ylabel('Systemic Risk Score')
ax[0].tick_params(axis='x', rotation=90)

ax[1].bar(srs_after.keys(), srs_after.values(), color='crimson', alpha=0.7)
ax[1].set_title('SRS after poisoning')
ax[1].set_ylabel('Systemic Risk Score')
ax[1].tick_params(axis='x', rotation=90)

plt.tight_layout()
plt.savefig('sccrm_poisoning_demo.png')
print("Plot saved to sccrm_poisoning_demo.png")