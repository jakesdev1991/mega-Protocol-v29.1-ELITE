# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import torch
import numpy as np
import os
import sys

def export_manifold(model_path, out_file="oracle_weights.bin"):
    """
    Quantizes a fine-tuned PyTorch model to INT8 and exports as a raw binary blob 
    for kernel-level embedding.
    """
    if not os.path.exists(model_path):
        print(f"❌ Error: Model file '{model_path}' not found.")
        return

    print(f"[*] Loading Manifold from {model_path}...")
    try:
        # Load the fine-tuned model
        state_dict = torch.load(model_path, map_location='cpu')
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return

    flattened_weights = []

    print("[*] Quantizing Manifold to INT8...")
    for name, tensor in state_dict.items():
        # Convert to float32 then numpy array to handle BFloat16
        w = tensor.detach().cpu().to(torch.float32).numpy().flatten()
        
        # Symmetric INT8 Quantization (Scale to -127 to +127)
        max_val = np.max(np.abs(w))
        if max_val > 0:
            scale = 127.0 / max_val
            quantized = np.clip(np.round(w * scale), -127, 127).astype(np.int8)
        else:
            quantized = w.astype(np.int8)
            
        flattened_weights.append(quantized)

    # Concatenate and Export
    final_blob = np.concatenate(flattened_weights)
    final_blob.tofile(out_file)

    print(f"[+] Manifold Exported: {out_file}")
    print(f"[+] Total Parameters: {len(final_blob):,}")
    print(f"[+] Size on Disk: {os.path.getsize(out_file) / (1024*1024):.2f} MB")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python export_manifold.py <model_path.pt> [output_file.bin]")
    else:
        out_file = sys.argv[2] if len(sys.argv) > 2 else "oracle_weights.bin"
        export_manifold(sys.argv[1], out_file)
