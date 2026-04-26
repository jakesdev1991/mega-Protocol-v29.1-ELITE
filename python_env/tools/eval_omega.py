# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import torch
import json
import argparse
from transformers import LlamaForCausalLM, LlamaConfig, AutoTokenizer
from sentence_transformers import SentenceTransformer, util
from tqdm import tqdm

# Check for DirectML
try:
    import torch_directml
    DML_DEVICE = torch_directml.device()
    HAS_DIRECTML = True
except:
    HAS_DIRECTML = False
    DML_DEVICE = torch.device("cpu")

def load_model(ckpt_path):
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

def evaluate(model, tokenizer, dataset_path):
    print(f"Loading evaluation dataset from {dataset_path}...")
    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = [json.loads(line) for line in f]
    
    # We'll use a standard embedding model for similarity scoring
    eval_embedder = SentenceTransformer("all-MiniLM-L6-v2")
    
    model.to(DML_DEVICE if HAS_DIRECTML else torch.device("cpu"))
    model.eval()
    
    total_score = 0
    results = []
    
    print("Evaluating model accuracy on Omega Protocol axioms...")
    for item in tqdm(data):
        instruction = item["instruction"]
        expected = item["response"]
        
        inputs = tokenizer(instruction, return_tensors="pt").to(model.device)
        with torch.no_grad():
            output_ids = model.generate(
                **inputs, 
                max_new_tokens=100,
                pad_token_id=tokenizer.eos_token_id
            )
        
        prediction = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        # Remove the instruction from the output
        prediction = prediction.replace(instruction, "").strip()
        
        # Calculate semantic similarity
        emb1 = eval_embedder.encode(prediction, convert_to_tensor=True)
        emb2 = eval_embedder.encode(expected, convert_to_tensor=True)
        score = float(util.cos_sim(emb1, emb2))
        
        total_score += score
        results.append({
            "instruction": instruction,
            "prediction": prediction,
            "expected": expected,
            "score": score
        })

    avg_score = total_score / len(data)
    print(f"\nEvaluation Complete. Average Semantic Accuracy: {avg_score:.4f}")
    
    with open("omega_eval_results.json", "w") as f:
        json.dump({"avg_score": avg_score, "details": results}, f, indent=2)
    print("Detailed results saved to omega_eval_results.json")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ckpt", type=str, required=True, help="Path to model checkpoint")
    parser.add_argument("--data", type=str, required=True, help="Path to JSONL dataset")
    args = parser.parse_args()
    
    tokenizer = AutoTokenizer.from_pretrained("hf-internal-testing/llama-tokenizer")
    tokenizer.pad_token = tokenizer.eos_token
    
    model = load_model(args.ckpt)
    evaluate(model, tokenizer, args.data)
