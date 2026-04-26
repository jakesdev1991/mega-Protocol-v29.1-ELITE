# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import torch
import json
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from datasets import Dataset
import os

# 1. Configuration
MODEL_DIR = "/home/jake/Downloads/training/base_model"
OUTPUT_DIR = "/home/jake/Downloads/training/termux_agent_training"
FINAL_MODEL = "/home/jake/Downloads/training/termux_service_agent.pt"
DATA_FILE = "/home/jake/Downloads/training/data/termux_service_data.jsonl"

# 2. Prepare Data
print("[*] Preparing Termux Service training data...")
texts = []
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
        for entry in data:
            texts.append(entry["text"])

dataset = Dataset.from_dict({"text": texts})

# 3. Load Model & Tokenizer
print("[*] Loading base model...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
tokenizer.pad_token = tokenizer.eos_token
model = AutoModelForCausalLM.from_pretrained(MODEL_DIR)

def tokenize_function(examples):
    # Increased max_length to 512 for multi-turn history
    tokens = tokenizer(examples["text"], padding="max_length", truncation=True, max_length=512)
    tokens["labels"] = tokens["input_ids"].copy()
    return tokens

tokenized_datasets = dataset.map(tokenize_function, batched=True)

# 4. Training Arguments
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=1, # Reduced for stability with larger context
    num_train_epochs=10, # Increased for better context retention
    learning_rate=3e-5,
    logging_steps=5,
    save_strategy="no",
    report_to="none",
    use_cpu=True
)

# 5. Trainer
print("[*] Starting Fine-Tuning for Termux Profile...")
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets,
)

trainer.train()

# 6. Save specialized state dict
print(f"[*] Exporting Termux Service state dict to {FINAL_MODEL}...")
torch.save(model.state_dict(), FINAL_MODEL)
print("✅ Termux Service Agent Training Complete.")
