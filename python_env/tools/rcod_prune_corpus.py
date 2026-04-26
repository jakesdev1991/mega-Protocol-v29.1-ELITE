# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
import numpy as np
from tqdm import tqdm
from typing import List
import argparse
import torch

from rcod.gating import rcod_filter_indices

# You can swap this for any embedding model you like
from sentence_transformers import SentenceTransformer
from datasets import load_dataset, Dataset, concatenate_datasets

def chunk_text(text: str, max_tokens: int = 256) -> List[str]:
    # naive whitespace chunking; replace with tokenizer-based if you want
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_tokens):
        chunks.append(" ".join(words[i:i+max_tokens]))
    return chunks

def compute_overlaps(embeddings: np.ndarray, context_window: int = 16) -> np.ndarray:
    """
    For each chunk, compute cosine similarity vs mean of previous context_window chunks.
    Using a larger window (16) for more stability on large datasets.
    """
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-9
    emb_norm = embeddings / norms

    overlaps = []
    for i in range(len(embeddings)):
        start = max(0, i - context_window)
        if i == start:
            overlaps.append(0.0)
            continue
        ctx = emb_norm[start:i]
        ctx_mean = ctx.mean(axis=0, keepdims=True)
        ctx_mean /= (np.linalg.norm(ctx_mean) + 1e-9)
        sim = float((emb_norm[i:i+1] @ ctx_mean.T)[0, 0])
        overlaps.append(sim)
    return np.array(overlaps, dtype=np.float32)

def rcod_prune_hf_dataset(
    dataset_name: str,
    config_name: str = None,
    text_field: str = "text",
    split: str = "train",
    max_docs: int = 100000,
    shard_size: int = 5000,
    max_tokens_per_chunk: int = 256,
    mu_threshold: float = 0.25,
    keep_flow_fraction: float = 0.1,
    output_path: str = "data/rcod_pruned_corpus",
):
    print(f"Loading dataset {dataset_name} (config: {config_name})...")
    ds = load_dataset(dataset_name, name=config_name, split=split, streaming=True)
    
    # We use a streaming dataset to avoid loading the whole thing into RAM
    # but we will pull shards into RAM for embedding processing.

    model = SentenceTransformer("all-MiniLM-L6-v2")
    if torch.cuda.is_available():
        model = model.to("cuda")
    elif hasattr(torch, "directml") and torch.directml.is_available():
        # DML doesn't support all ops for SentenceTransformers yet, 
        # so we stay on CPU if CUDA isn't there, or let ST handle it.
        pass

    all_pruned_shards = []
    current_shard_docs = []
    doc_count = 0
    total_original_chunks = 0
    total_kept_chunks = 0

    print(f"Starting Sharded RCOD Pruning (Target: {max_docs} docs)...")
    
    for row in tqdm(ds, desc="Processing Stream", total=max_docs):
        if doc_count >= max_docs:
            break
            
        current_shard_docs.append(row[text_field])
        doc_count += 1
        
        if len(current_shard_docs) >= shard_size:
            pruned_shard, orig_c, kept_c = process_shard(
                current_shard_docs, model, max_tokens_per_chunk, 
                mu_threshold, keep_flow_fraction
            )
            all_pruned_shards.append(pruned_shard)
            total_original_chunks += orig_c
            total_kept_chunks += kept_c
            current_shard_docs = []
            
            # Print stats after each shard
            compression = (1.0 - (total_kept_chunks / (total_original_chunks + 1e-9))) * 100
            print(f"\n[Shard Stats] Total Kept: {total_kept_chunks} | Original: {total_original_chunks} | Compression: {compression:.2f}%")

    # Handle remaining docs
    if current_shard_docs:
        pruned_shard, orig_c, kept_c = process_shard(
            current_shard_docs, model, max_tokens_per_chunk, 
            mu_threshold, keep_flow_fraction
        )
        all_pruned_shards.append(pruned_shard)
        total_original_chunks += orig_c
        total_kept_chunks += kept_c

    final_ds = concatenate_datasets(all_pruned_shards)
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    final_ds.save_to_disk(output_path)
    
    print(f"\n--- Final RCOD Pruning Report ---")
    print(f"Output Path: {output_path}")
    print(f"Original Chunks: {total_original_chunks}")
    print(f"Kept Chunks: {total_kept_chunks}")
    print(f"Final Compression Ratio: {(1.0 - (total_kept_chunks/total_original_chunks))*100:.2f}%")

def process_shard(docs, model, max_tokens_per_chunk, mu_threshold, keep_flow_fraction):
    shard_chunks = []
    for text in docs:
        shard_chunks.extend(chunk_text(text, max_tokens=max_tokens_per_chunk))
    
    if not shard_chunks:
        return Dataset.from_dict({"text": []}), 0, 0
        
    embeddings = model.encode(shard_chunks, batch_size=128, show_progress_bar=False, convert_to_numpy=True)
    overlaps = compute_overlaps(embeddings)
    
    keep_idx = rcod_filter_indices(
        overlaps=overlaps,
        mu_threshold=mu_threshold,
        keep_flow_fraction=keep_flow_fraction,
    )
    
    pruned_chunks = [shard_chunks[i] for i in keep_idx]
    shard_ds = Dataset.from_dict({"text": pruned_chunks})
    
    return shard_ds, len(shard_chunks), len(pruned_chunks)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Big Prune: RCOD Data Gating at Scale")
    parser.add_argument("--dataset", type=str, default="cerebras/SlimPajama-627B", help="HF Dataset name")
    parser.add_argument("--config", type=str, default="default", help="HF Dataset config")
    parser.add_argument("--max_docs", type=int, default=50000, help="Total documents to process")
    parser.add_argument("--shard_size", type=int, default=5000, help="Docs per processing shard")
    parser.add_argument("--output", type=str, default="data/rcod_slimpajama_pruned", help="Output path")
    parser.add_argument("--mu_threshold", type=float, default=0.25, help="RCOD Mu threshold (novelty)")
    
    args = parser.parse_args()
    
    rcod_prune_hf_dataset(
        dataset_name=args.dataset,
        config_name=args.config,
        max_docs=args.max_docs,
        shard_size=args.shard_size,
        output_path=args.output,
        mu_threshold=args.mu_threshold
    )
