# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import torch
import os
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from datasets import Dataset

BASE_MODEL = "/home/jake/Downloads/training/base_model"
OUTPUT_DIR = "/home/jake/Downloads/training/135m_omega_protocol"
FINAL_MODEL = "/home/jake/Downloads/training/135m_omega_elite.pt"

def train_omega_theory():
    print("🚀 [Training] Fine-tuning 135M on Omega Protocol Theory...")
    
    # 1. Load Knowledge
    knowledge_path = "/home/jake/Downloads/training/python_env/docs/OMEGA_PROTOCOL_WHITEPAPER.md"
    with open(knowledge_path, "r") as f:
        content = f.read()
    
    # Chunking for 135M context
    dataset = Dataset.from_dict({"text": [content[i:i+512] for i in range(0, len(content), 256)]})

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(BASE_MODEL)

    def tokenize(ex):
        res = tokenizer(ex["text"], padding="max_length", truncation=True, max_length=256)
        res["labels"] = res["input_ids"].copy()
        return res

    tokenized_ds = dataset.map(tokenize, batched=True)

    args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=16,
        num_train_epochs=10,
        learning_rate=1e-4,
        bf16=True,
        use_cpu=False,
        logging_steps=5,
        save_strategy="no",
        report_to="none"
    )

    trainer = Trainer(model=model, args=args, train_dataset=tokenized_ds)
    trainer.train()
    torch.save(model.state_dict(), FINAL_MODEL)
    print(f"✅ 135M Omega Elite weights saved to {FINAL_MODEL}")

if __name__ == "__main__":
    train_omega_theory()
