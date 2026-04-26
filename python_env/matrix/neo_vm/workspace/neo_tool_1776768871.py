# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# demo_embedding_vulnerability.py
import torch
from transformers import BertTokenizer, BertModel
from scipy.spatial.distance import cosine

# Load pre-trained BERT
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')
model.eval()

def embed(sentence):
    tokens = tokenizer(sentence, return_tensors='pt')
    with torch.no_grad():
        outputs = model(**tokens)
    # Use the [CLS] token vector as sentence embedding
    cls_embedding = outputs.last_hidden_state[:, 0, :].squeeze().numpy()
    return cls_embedding

# Pair of contradictory statements that are syntactically similar
sentences = [
    "We must increase risk to stay competitive in the market.",
    "We must increase risk to stay compliant with new regulations.",
    "We should accept higher leverage to maximize returns.",
    "We should accept higher leverage to satisfy auditors."
]

embeddings = [embed(s) for s in sentences]

print("Cosine similarities (higher = more similar):")
for i in range(len(sentences)):
    for j in range(i+1, len(sentences)):
        sim = 1 - cosine(embeddings[i], embeddings[j])
        print(f"'{sentences[i][:40]}...' <-> '{sentences[j][:40]}...' : {sim:.3f}")

# Expected output: similarities above 0.95 for contradictory pairs