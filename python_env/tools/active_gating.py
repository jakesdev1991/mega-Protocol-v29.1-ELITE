# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import torch
import argparse
import os
from transformers import LlamaForCausalLM, LlamaConfig, AutoTokenizer
from datasets import load_dataset, load_from_disk, Dataset, concatenate_datasets
from tqdm import tqdm
import numpy as np

# Check for DirectML
try:
    import torch_directml
    DML_DEVICE = torch_directml.device()
    HAS_DIRECTML = True
except:
    HAS_DIRECTML = False
    DML_DEVICE = torch.device("cpu")

def load_from_lightning(ckpt_path):
    config = LlamaConfig(
        vocab_size=32000,
        hidden_size=1024,
        intermediate_size=4096,
        num_hidden_layers=12,
        num_attention_heads=16,
        max_position_embeddings=2048
    )
    model = LlamaForCausalLM(config)
    checkpoint = torch.load(ckpt_path, map_location="cpu")
    state_dict = checkpoint["state_dict"]
    new_state_dict = {k[6:] if k.startswith("model.") else k: v for k, v in state_dict.items()}
    model.load_state_dict(new_state_dict)
    return model

def active_gating(ckpt_path, dataset_name, output_path, max_docs=10000, shard_size=1000, threshold=2.0):
    model = load_from_lightning(ckpt_path)
    model.to(DML_DEVICE if HAS_DIRECTML else torch.device("cpu"))
    model.eval()
    
    tokenizer = AutoTokenizer.from_pretrained("hf-internal-testing/llama-tokenizer")
    tokenizer.pad_token = tokenizer.eos_token
    
    ds = load_dataset(dataset_name, split="train", streaming=True)
    
    all_kept = []
    current_shard = []
    
    print(f"Starting Active Gating using model from {ckpt_path}...")
    
    count = 0
    for row in tqdm(ds, total=max_docs):
        if count >= max_docs:
            break
        
        text = row["text"]
        inputs = tokenizer(text, truncation=True, max_length=512, return_tensors="pt").to(model.device)
        
        with torch.no_grad():
            outputs = model(**inputs, labels=inputs["input_ids"])
            loss = outputs.loss.item()
        
        # Keep if loss is high (novel/surprising) OR sample randomly (keep structural glue)
        if loss > threshold or np.random.random() < 0.1:
            all_kept.append({"text": text, "loss": loss})
        
        count += 1
        
        if len(all_kept) >= shard_size:
            # Periodically save shards if needed, but for 500k we might just collect in RAM
            # or save to disk iteratively.
            pass

    final_ds = Dataset.from_list(all_kept)
    final_ds.save_to_disk(output_path)
    print(f"Active Gating complete. Kept {len(final_ds)} samples. Saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ckpt", type=str, required=True)
    parser.add_argument("--dataset", type=str, default="cerebras/SlimPajama-627B")
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--max_docs", type=int, default=10000)
    parser.add_argument("--threshold", type=float, default=2.5)
    args = parser.parse_args()
    
    active_gating(args.ckpt, args.dataset, args.output, args.max_docs, threshold=args.threshold)
