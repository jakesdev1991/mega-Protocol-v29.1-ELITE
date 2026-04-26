# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import torch
from datasets import load_dataset
from sentence_transformers import SentenceTransformer
import numpy as np
from rcod.gating import rcod_filter_indices

class InfiniteStreamPruner:
    """
    An iterator that pulls from a large dataset stream, prunes in real-time
    using RCOD novelty filtering, and yields 'High-Viscosity' samples.
    """
    def __init__(self, 
                 dataset_name="cerebras/SlimPajama-627B", 
                 mu_threshold=0.25, 
                 context_window=16,
                 batch_size=128):
        self.ds = load_dataset(dataset_name, split="train", streaming=True)
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.mu_threshold = mu_threshold
        self.context_window = context_window
        self.batch_size = batch_size
        
        # Buffer for embeddings to maintain context across calls
        self.embedding_buffer = []

    def __iter__(self):
        batch_texts = []
        for row in self.ds:
            batch_texts.append(row["text"])
            
            if len(batch_texts) >= self.batch_size:
                # 1. Compute Embeddings
                embeddings = self.model.encode(batch_texts, convert_to_numpy=True)
                
                # 2. Add to context buffer
                full_embeddings = np.vstack([self.embedding_buffer, embeddings]) if self.embedding_buffer else embeddings
                
                # 3. Compute Overlaps
                norms = np.linalg.norm(full_embeddings, axis=1, keepdims=True) + 1e-9
                emb_norm = full_embeddings / norms
                
                overlaps = []
                # Only compute overlaps for the NEW batch, relative to history
                offset = len(self.embedding_buffer)
                for i in range(offset, len(full_embeddings)):
                    start = max(0, i - self.context_window)
                    if i == start:
                        overlaps.append(0.0)
                        continue
                    ctx = emb_norm[start:i]
                    ctx_mean = ctx.mean(axis=0, keepdims=True)
                    ctx_mean /= (np.linalg.norm(ctx_mean) + 1e-9)
                    sim = float((emb_norm[i:i+1] @ ctx_mean.T)[0, 0])
                    overlaps.append(sim)
                
                # 4. Filter Indices
                keep_idx = rcod_filter_indices(np.array(overlaps), mu_threshold=self.mu_threshold)
                
                # 5. Yield Kept Samples
                for idx in keep_idx:
                    yield {"text": batch_texts[idx]}
                
                # 6. Update buffer (keep only the last context_window embeddings)
                self.embedding_buffer = full_embeddings[-self.context_window:]
                batch_texts = []

if __name__ == "__main__":
    # Test run
    pruner = InfiniteStreamPruner(max_docs=1000)
    print("Testing Infinite Stream Pruner...")
    for i, sample in enumerate(pruner):
        if i >= 5: break
        print(f"Sample {i+1} Kept. Length: {len(sample['text'])}")
