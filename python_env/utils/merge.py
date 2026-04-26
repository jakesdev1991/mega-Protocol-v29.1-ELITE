# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch

# Pointing explicitly to the FOLDER containing model.safetensors
base_model_path = "/home/jake/Downloads/training/Sarai_Deployment/sarai"  
adapter_path = "./sarai_qlora_adapter"
save_path = "./sarai_merged"

print(f"[*] Loading base model from: {base_model_path} ...")
try:
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_path,
        torch_dtype=torch.float16,
        device_map="cpu"
    )
    tokenizer = AutoTokenizer.from_pretrained(base_model_path)
except Exception as e:
    print(f"[-] FATAL: Failed to load base model. Is config.json in that folder?\nError: {e}")
    exit(1)

print("[*] Fusing Omega Protocol LoRA adapter...")
model = PeftModel.from_pretrained(base_model, adapter_path)
model = model.merge_and_unload()

print("[*] Saving unified model to ./sarai_merged ...")
model.save_pretrained(save_path)
tokenizer.save_pretrained(save_path)
print("[+] Fusion Complete.")
