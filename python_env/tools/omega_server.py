# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch
from transformers import LlamaForCausalLM, LlamaConfig, AutoTokenizer
import uvicorn
import os

# Check for DirectML
try:
    import torch_directml
    DML_DEVICE = torch_directml.device()
    HAS_DIRECTML = True
except:
    HAS_DIRECTML = False
    DML_DEVICE = torch.device("cpu")

app = FastAPI(title="Omega Protocol Intelligence Server")

class Query(BaseModel):
    prompt: str
    max_tokens: int = 100
    temperature: float = 0.7

# Global model/tokenizer variables
model = None
tokenizer = None

def load_model(ckpt_path):
    global model, tokenizer
    config = LlamaConfig(
        vocab_size=32000,
        hidden_size=1024,
        intermediate_size=4096,
        num_hidden_layers=12,
        num_attention_heads=16,
        max_position_embeddings=2048
    )
    model = LlamaForCausalLM(config)
    print(f"Loading weights from {ckpt_path}...")
    checkpoint = torch.load(ckpt_path, map_location="cpu")
    state_dict = checkpoint["state_dict"]
    new_state_dict = {k[6:] if k.startswith("model.") else k: v for k, v in state_dict.items()}
    model.load_state_dict(new_state_dict)
    
    model.to(DML_DEVICE if HAS_DIRECTML else torch.device("cpu"))
    model.eval()
    
    tokenizer = AutoTokenizer.from_pretrained("hf-internal-testing/llama-tokenizer")
    tokenizer.pad_token = tokenizer.eos_token
    print("Model ready for inference.")

@app.post("/ask")
async def ask_omega(query: Query):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded. Please provide a checkpoint path.")
    
    inputs = tokenizer(query.prompt, return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=query.max_tokens,
            temperature=query.temperature,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return {"prompt": query.prompt, "response": response}

@app.get("/status")
async def status():
    return {
        "status": "online",
        "device": str(DML_DEVICE),
        "model_loaded": model is not None
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--ckpt", type=str, help="Path to model checkpoint")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    
    if args.ckpt:
        load_model(args.ckpt)
    else:
        print("Starting server without model. Use /status to check.")
        
    uvicorn.run(app, host="0.0.0.0", port=args.port)
