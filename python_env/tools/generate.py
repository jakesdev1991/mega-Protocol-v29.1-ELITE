# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import torch
import argparse
from transformers import LlamaForCausalLM, LlamaConfig, AutoTokenizer
import pytorch_lightning as pl
import os

# Check for DirectML
try:
    import torch_directml
    DML_DEVICE = torch_directml.device()
    HAS_DIRECTML = True
except:
    HAS_DIRECTML = False
    DML_DEVICE = torch.device("cpu")

def load_from_lightning(ckpt_path):
    # This requires knowing the config used during training
    # For our 300M model:
    config = LlamaConfig(
        vocab_size=32000,
        hidden_size=1024,
        intermediate_size=4096,
        num_hidden_layers=12,
        num_attention_heads=16,
        max_position_embeddings=2048
    )
    model = LlamaForCausalLM(config)
    
    print(f"Loading checkpoint from {ckpt_path}...")
    checkpoint = torch.load(ckpt_path, map_location="cpu")
    state_dict = checkpoint["state_dict"]
    
    # Remove 'model.' prefix from lightning state dict
    new_state_dict = {}
    for k, v in state_dict.items():
        if k.startswith("model."):
            new_state_dict[k[6:]] = v
        else:
            new_state_dict[k] = v
            
    model.load_state_dict(new_state_dict)
    return model

def generate(model, tokenizer, prompt, max_length=50):
    device = DML_DEVICE if HAS_DIRECTML else torch.device("cpu")
    model.to(device)
    
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    
    print(f"\nPrompt: {prompt}")
    print("Generating...")
    
    with torch.no_grad():
        output = model.generate(
            **inputs, 
            max_new_tokens=max_length,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.2,
            pad_token_id=tokenizer.eos_token_id
        )
    
    decoded = tokenizer.decode(output[0], skip_special_tokens=True)
    print(f"\nOutput:\n{decoded}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ckpt", type=str, required=True, help="Path to .ckpt file")
    parser.add_argument("--prompt", type=str, default="The future of artificial intelligence is")
    parser.add_argument("--max_tokens", type=int, default=100)
    args = parser.parse_args()

    tokenizer = AutoTokenizer.from_pretrained("hf-internal-testing/llama-tokenizer")
    tokenizer.pad_token = tokenizer.eos_token
    
    model = load_from_lightning(args.ckpt)
    model.eval()
    
    generate(model, tokenizer, args.prompt, args.max_tokens)
