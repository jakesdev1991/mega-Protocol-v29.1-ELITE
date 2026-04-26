# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
from datasets import load_from_disk, load_dataset
import argparse
from collections import Counter
import re

def get_vocab(dataset, text_field="text", max_samples=10000):
    counter = Counter()
    count = 0
    for sample in dataset:
        if count >= max_samples:
            break
        text = sample[text_field].lower()
        words = re.findall(r'\w+', text)
        counter.update(words)
        count += 1
    return counter

def analyze(pruned_path, original_name, original_config="default"):
    print(f"Loading pruned dataset from {pruned_path}...")
    pruned_ds = load_from_disk(pruned_path)
    
    print(f"Loading original dataset {original_name} for comparison...")
    orig_ds = load_dataset(original_name, original_config, split="train", streaming=True)
    
    print("Analyzing vocab distribution (top 10000 samples)...")
    pruned_vocab = get_vocab(pruned_ds)
    orig_vocab = get_vocab(orig_ds)
    
    pruned_total = sum(pruned_vocab.values())
    orig_total = sum(orig_vocab.values())
    
    print("\n--- Vocabulary Analysis ---")
    print(f"Total words in pruned sample: {pruned_total}")
    print(f"Total words in original sample: {orig_total}")
    
    common_words = ["the", "and", "of", "to", "a", "in", "is", "it"]
    print("\nFrequency of common 'glue' words (normalized per 1000 words):")
    print(f"{'Word':<10} | {'Original':<10} | {'Pruned':<10} | {'Ratio':<10}")
    print("-" * 45)
    for word in common_words:
        o_freq = (orig_vocab[word] / orig_total) * 1000 if orig_total > 0 else 0
        p_freq = (pruned_vocab[word] / pruned_total) * 1000 if pruned_total > 0 else 0
        ratio = p_freq / o_freq if o_freq > 0 else 0
        print(f"{word:<10} | {o_freq:<10.2f} | {p_freq:<10.2f} | {ratio:<10.2f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pruned", type=str, required=True)
    parser.add_argument("--original", type=str, default="cerebras/SlimPajama-627B")
    args = parser.parse_args()
    analyze(args.pruned, args.original)
