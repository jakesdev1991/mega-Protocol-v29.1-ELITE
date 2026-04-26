# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from datasets import Dataset
import os

# Configuration for 135M "Mini" Sarai
BASE_MODEL = "/home/jake/Downloads/training/base_model"
OUTPUT_DIR = "/home/jake/Downloads/training/sarai_135m_training"
FINAL_MODEL = "/home/jake/Downloads/training/sarai_135m_elite.pt"

# 1. Compile Training Knowledge
print("[*] Harvesting Omega Protocol Knowledge for Mini-Sarai...")
training_data = []

# Include Whitepaper Concepts
whitepaper_path = "/home/jake/Downloads/training/python_env/docs/OMEGA_PROTOCOL_WHITEPAPER.md"
if os.path.exists(whitepaper_path):
    with open(whitepaper_path, "r") as f:
        training_data.append({"text": f"Instruction: Explain Omega Protocol. Response: {f.read()}"})

# Include Distributed Automation Logic
training_data.append({"text": "Instruction: How to distribute Sarai knowledge? Response: Utilize Relational Sharding. Export pruned state-dicts to sub-nodes via Shizuku/Termux bridges. Maintain Phi-consistency across the mesh."})

# Load existing agentic data
data_file = "/home/jake/Downloads/training/data/termux_service_data.jsonl"
if os.path.exists(data_file):
    import json
    with open(data_file, "r") as f:
        # data is a list of objects with a "text" key
        raw_data = json.load(f)
        for entry in raw_data:
            training_data.append({"text": entry["text"]})

dataset = Dataset.from_dict({"text": [d["text"] for d in training_data]})

# 2. Setup Model
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
tokenizer.pad_token = tokenizer.eos_token
model = AutoModelForCausalLM.from_pretrained(BASE_MODEL)

def tokenize_func(examples):
    result = tokenizer(examples["text"], padding="max_length", truncation=True, max_length=512)
    result["labels"] = result["input_ids"].copy()
    return result

tokenized_ds = dataset.map(tokenize_func, batched=True)

# 3. Training Loop (Elite Parameters)
args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=2,
    num_train_epochs=5,
    learning_rate=5e-5,
    weight_decay=0.01,
    logging_steps=10,
    save_strategy="no",
    use_cpu=True, # Safety for 4GB constraints if GPU is tiny
    report_to="none"
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=tokenized_ds
)

print("🚀 INITIATING MINI-SARAI 135M TRAINING LOOP...")
trainer.train()

# 4. Save Final State
torch.save(model.state_dict(), FINAL_MODEL)
print(f"✅ Mini-Sarai 135M Exported to {FINAL_MODEL}")
