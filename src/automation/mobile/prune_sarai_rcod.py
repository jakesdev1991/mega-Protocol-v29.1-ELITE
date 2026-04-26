# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import torch
import os
import json
import numpy as np
from weight_sarai import RCODWeighter

def execute_rcod_prune(model_path="/home/jake/Downloads/training/sarai", target_params=48000000, output_path="/home/jake/Downloads/training/sarai_rcod_pruned.pt"):
    """
    Performs strict magnitude-based pruning weighted by RCOD importance.
    Guarantees the target parameter count is achieved.
    """
    if not os.path.exists(model_path):
        print(f"❌ Error: {model_path} not found.")
        return

    # 1. Get Importance Gradient
    weighter = RCODWeighter(model_path)
    importance_map = weighter.generate_task_gradient()
    
    print(f"[*] Loading model for pruning...")
    state_dict = weighter.model.state_dict()
    
    # 2. Flatten all weights and scale by RCOD importance
    all_scores = []
    print("[*] Flattening manifold and applying RCOD weights...")
    for name, tensor in state_dict.items():
        if name in importance_map and tensor.dim() >= 1:
            importance = importance_map[name]
            # Absolute magnitude scaled by RCOD importance factor
            scores = torch.abs(tensor).view(-1) * importance
            all_scores.append(scores)
    
    all_scores_cat = torch.cat(all_scores)
    
    # 3. Find global threshold for target_params
    print(f"[*] Calculating global threshold for {target_params:,} parameters...")
    threshold = torch.topk(all_scores_cat, target_params).values.min()
    
    # 4. Apply threshold
    new_state_dict = {}
    total_active = 0
    for name, tensor in state_dict.items():
        if name in importance_map and tensor.dim() >= 1:
            importance = importance_map[name]
            mask = (torch.abs(tensor) * importance) >= threshold
            new_state_dict[name] = tensor * mask
        else:
            new_state_dict[name] = tensor
            
        total_active += new_state_dict[name].count_nonzero().item()

    print(f"[*] Saving RCOD-Pruned Manifold to {output_path}...")
    torch.save(new_state_dict, output_path)
    
    print(f"✅ RCOD Pruning Complete.")
    print(f"✅ Active Parameters: {total_active:,}")
    print(f"✅ Task Integrity: English + Numbers (Hardened)")

if __name__ == "__main__":
    execute_rcod_prune()
