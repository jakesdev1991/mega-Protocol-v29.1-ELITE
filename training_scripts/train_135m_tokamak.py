# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import torch
import os
import json
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from datasets import Dataset

BASE_MODEL = "/home/jake/Downloads/training/base_model"
OUTPUT_DIR = "/home/jake/Downloads/training/135m_tokamak_physicist"
FINAL_MODEL = "/home/jake/Downloads/training/135m_tokamak_elite.pt"
DATA_FILE = "/home/jake/Downloads/training/data/normalized_tokamak_200k.jsonl"

def train_tokamak_lite():
    print("🚀 [Training] Fine-tuning 135M 'Physicist-Lite' on 200k shots...")
    
    texts = []
    with open(DATA_FILE, "r") as f:
        for line in f:
            texts.append(json.loads(line)["text"])
    
    dataset = Dataset.from_dict({"text": texts})

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(BASE_MODEL)

    def tokenize(ex):
        res = tokenizer(ex["text"], padding="max_length", truncation=True, max_length=128)
        res["labels"] = res["input_ids"].copy()
        return res

    tokenized_ds = dataset.map(tokenize, batched=True)

    args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=32, # 135M fits easily in VRAM
        num_train_epochs=3,
        learning_rate=8e-5,
        bf16=True,
        use_cpu=False,
        logging_steps=100,
        save_strategy="epoch",
        report_to="none"
    )

    trainer = Trainer(model=model, args=args, train_dataset=tokenized_ds)
    trainer.train()
    torch.save(model.state_dict(), FINAL_MODEL)
    print(f"✅ 135M Physicist-Lite weights saved to {FINAL_MODEL}")

if __name__ == "__main__":
    train_tokamak_lite()
