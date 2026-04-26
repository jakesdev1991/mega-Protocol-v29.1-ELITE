# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import torch
import numpy as np
import sys
import os

# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------

# Add project root to path for C wrapper
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)
from python_env.machine_learning.c_translators.omega_c_wrapper import calculate_rcod_fast

# OMEGA PROTOCOL v29.1: RCOD VALIDATOR
# Measures the informational overlap between two model states.

def calculate_rcod(tensor_a, tensor_b):
    """
    Measures how much tensor_a (Theory) and tensor_b (Physicist) overlap.
    Returns: COD (Redundancy) and RCOD (Novelty)
    [Now powered by highly-optimized C-Core Translator]
    """
    # Convert to numpy arrays for C-wrapper, casting BFloat16 -> Float32
    a_np = tensor_a.detach().cpu().to(torch.float32).numpy()
    b_np = tensor_b.detach().cpu().to(torch.float32).numpy()
    
    # Fast C-execution
    cod, rcod = calculate_rcod_fast(a_np, b_np)
    return cod, rcod

def validate_fusion():
    print("✦ [Validation] Measuring RCOD between Synthesized State and Base Theory...")
    
    # 1. Load states
    theory_path = "weights/135m_omega_elite.pt"
    fused_path = "weights/tokamak_300m_elite.pt"
    
    theory = torch.load(theory_path, map_location="cpu", weights_only=False)
    fused = torch.load(fused_path, map_location="cpu", weights_only=False)
    
    # 2. Check overlap on critical layers (Lower layers = Theory ground)
    test_keys = [
        "model.embed_tokens.weight",
        "model.layers.0.self_attn.q_proj.weight",
        "model.layers.15.self_attn.q_proj.weight",
        "model.layers.29.self_attn.q_proj.weight"
    ]
    
    print(f"{'Layer Key':<40} | {'COD (Overlap)':<10} | {'RCOD (Novelty)':<10}")
    print("-" * 70)
    
    all_cod = []
    all_rcod = []
    
    for key in test_keys:
        if key in theory and key in fused:
            cod, rcod = calculate_rcod(theory[key], fused[key])
            print(f"{key:<40} | {cod:.4f}     | {rcod:.4f}")
            all_cod.append(cod)
            all_rcod.append(rcod)
            
    avg_cod = np.mean(all_cod)
    avg_rcod = np.mean(all_rcod)
    
    print("-" * 70)
    print(f"{'AVERAGE SYSTEM STATE':<40} | {avg_cod:.4f}     | {avg_rcod:.4f}")
    
    # 3. Decision Logic based on Novelty Ratio eta = RCOD/COD
    eta = avg_rcod / (avg_cod + 1e-10)
    print(f"\nFinal Novelty Limit Ratio (eta): {eta:.4f}")
    
    if eta < 0.2:
        print("💡 [Status] INFORMATIONAL FREEZE: System is hyper-redundant. Fusion is too safe.")
    elif eta > 0.8:
        print("⚠️ [Status] SHREDDING EVENT: Novelty is too high. Model may lose grounding.")
    else:
        print("✅ [Status] OPTIMAL TRAINING ZONE: Balance of theory and empirical data achieved.")

if __name__ == "__main__":
    validate_fusion()
