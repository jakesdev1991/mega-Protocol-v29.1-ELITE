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

# 1. Configuration
MODEL_DIR = "/home/jake/Downloads/training/base_model"
OUTPUT_DIR = "/home/jake/Downloads/training/oracle_training"
FINAL_MODEL = "/home/jake/Downloads/training/omega_oracle.pt"

# 2. Prepare Data
print("[*] Preparing RCOD training data...")
data_files = [
    "/home/jake/Downloads/training/data/context_toe.txt",
    "/home/jake/Downloads/training/data/instruction_chat.txt"
]

texts = []
for f_path in data_files:
    if os.path.exists(f_path):
        with open(f_path, "r") as f:
            texts.append(f.read())

dataset = Dataset.from_dict({"text": texts})

# 3. Load Model & Tokenizer
print("[*] Loading base model...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
tokenizer.pad_token = tokenizer.eos_token
model = AutoModelForCausalLM.from_pretrained(MODEL_DIR)

def tokenize_function(examples):
    tokens = tokenizer(examples["text"], padding="max_length", truncation=True, max_length=512)
    # For causal language modeling, labels are the same as input_ids
    tokens["labels"] = tokens["input_ids"].copy()
    return tokens

tokenized_datasets = dataset.map(tokenize_function, batched=True)

# 4. Training Arguments (Lightweight for quick start)
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=1,
    num_train_epochs=1,
    max_steps=50,
    logging_steps=10,
    save_strategy="no",
    report_to="none",
    use_cpu=True # Force CPU to avoid accelerator issues
)

# 5. Trainer
print("[*] Starting Fine-Tuning...")
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets,
)

trainer.train()

# 6. Save specialized state dict
print(f"[*] Exporting specialized state dict to {FINAL_MODEL}...")
torch.save(model.state_dict(), FINAL_MODEL)
print("✅ Training Complete.")
