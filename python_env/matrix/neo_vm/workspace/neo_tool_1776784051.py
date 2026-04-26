# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
# nltk.download('punkt')  # run once if needed

# --- Lexicons ---
HEDGING = {"might","could","perhaps","possibly","may","would","should","uncertain"}
JARGON = {"tensor","NVLink","FP8","H100","cluster","GPU","CUDA","bandwidth","latency","throughput"}
URGENCY = {"urgent","critical","immediate","bottleneck","deadline","ASAP","crisis"}

def extract_linguistic_features(text: str):
    words = text.lower().split()
    # Sentiment
    sentiment = TextBlob(text).sentiment.polarity
    # Ambiguity (hedge density)
    ambiguity = sum(1 for w in words if w in HEDGING) / (len(words) + 1e-6)
    # Jargon density
    jargon = sum(1 for w in words if w in JARGON) / (len(words) + 1e-6)
    # Urgency
    urgency = sum(1 for w in words if w in URGENCY) / (len(words) + 1e-6)
    # Coherence (adjacent‑sentence similarity)
    sentences = nltk.sent_tokenize(text)
    coherence = 1.0
    if len(sentences) > 1:
        tfidf = TfidfVectorizer().fit_transform(sentences)
        sim = cosine_similarity(tfidf)
        coherence = np.mean([sim[i, i+1] for i in range(len(sentences)-1)])
    return {
        "sentiment": sentiment,
        "ambiguity": ambiguity,
        "jargon": jargon,
        "urgency": urgency,
        "coherence": coherence,
        "length": len(words)  # proxy for silence
    }

def compute_sci(f: dict) -> float:
    # Beta's recipe (weights are illustrative but follow the original)
    sci = (
        (f["sentiment"] + 1) / 2 * 0.30 +
        (1 - f["ambiguity"]) * 0.25 +
        min(f["jargon"] * 2, 1.0) * 0.15 +
        (1 - f["urgency"]) * 0.20 +
        f["coherence"] * 0.10
    )
    return sci

# --- Synthetic documents ---
baseline = """
Our H100 cluster deployment is on schedule. Tensor cores deliver exceptional throughput.
NVLink ensures low latency. We anticipate a 20% speedup in model training.
The team is confident and aligned. No major bottlenecks are expected.
"""

# Same baseline but with a single pessimistic paragraph added (realistic internal note)
perturbed = baseline + """
However, we might face integration issues. The network could be a bottleneck.
It is critical that we address possible bandwidth constraints immediately.
Perhaps we should consider fallback options if performance does not meet expectations.
"""

# External press release (always upbeat)
external = """
We are excited to announce the successful deployment of our next‑generation AI infrastructure.
Our new H100 GPU cluster will accelerate innovation and deliver unmatched performance.
This investment underscores our commitment to leadership in AI.
"""

# --- Compute features & indices ---
base_feat = extract_linguistic_features(baseline)
pert_feat = extract_linguistic_features(perturbed)
ext_feat  = extract_linguistic_features(external)

sci_base = compute_sci(base_feat)
sci_pert = compute_sci(pert_feat)

# Narrative Gap Index = L2 distance in (sentiment, ambiguity, urgency) space
def ngi(f_int, f_ext):
    vec = lambda x: np.array([x["sentiment"], x["ambiguity"], x["urgency"]])
    return np.linalg.norm(vec(f_int) - vec(f_ext))

ngi_base = ngi(base_feat, ext_feat)
ngi_pert = ngi(pert_feat, ext_feat)

# Strategic Silence Index (SSI) = 1 / (1 + doc length) → higher silence = lower length
ssi_base = 1.0 / (1 + base_feat["length"])
ssi_pert = 1.0 / (1 + pert_feat["length"])

# --- Results ---
print("=== SCI Instability ===")
print(f"Baseline SCI: {sci_base:.3f}")
print(f"Perturbed SCI: {sci_pert:.3f}")
print(f"ΔSCI: {sci_base - sci_pert:.3f}  (massive drop from a few sentences)\n")

print("=== Narrative Gap Stability ===")
print(f"Baseline NGI: {ngi_base:.3f}")
print(f"Perturbed NGI: {ngi_pert:.3f}")
print(f"ΔNGI: {ngi_pert - ngi_base:.3f}  (modest increase, robust signal)\n")

print("=== Silence as Fragility Proxy ===")
print(f"Baseline SSI (higher = more silent): {ssi_base:.4f}")
print(f"Perturbed SSI: {ssi_pert:.4f}")
print("SSI drops when the memo grows (less silence) – but real fragility often hides in *shorter*, more guarded memos.\n")

# --- Demonstrate arbitrariness of the "linguistic invariant" ---
def linguistic_invariant(f: dict):
    # ψ = ln(σ/σ₀) + λ·SCI  (simplified)
    σ = f["jargon"]  # stand‑in for "semantic spread"
    return np.log(σ + 1e-6) + 0.5 * compute_sci(f)

inv_base = linguistic_invariant(base_feat)
inv_pert = linguistic_invariant(pert_feat)
print("=== Linguistic Invariant (Fake Conservation) ===")
print(f"Baseline ψ: {inv_base:.3f}")
print(f"Perturbed ψ: {inv_pert:.3f}")
print("ψ swings wildly with tiny text changes → not an invariant, just a decorative formula.")