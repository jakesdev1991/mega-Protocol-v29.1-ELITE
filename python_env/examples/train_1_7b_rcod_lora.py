# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import argparse
import torch
import os
import json
import pytorch_lightning as pl
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoConfig, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

from rcod.monitor import RCODMonitor
from rcod.hooks import layer_stat

class EvolutionDataset(Dataset):
    def __init__(self, log_path, tokenizer, max_length=512):
        self.examples = []
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        # We want to train on the successful reasonings
                        text = f"Task: {data.get('task')}\nSolution: {data.get('constructive_final') or data.get('thought_process')}"
                        self.examples.append(text)
                    except:
                        pass
        
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        tokenized = self.tokenizer(
            self.examples[idx],
            truncation=True,
            max_length=self.max_length,
            padding="max_length",
            return_tensors="pt"
        )
        return {
            "input_ids": tokenized["input_ids"].squeeze(),
            "labels": tokenized["input_ids"].squeeze()
        }

class RCOD17BLightningModule(pl.LightningModule):
    def __init__(self, model_id, base_lr=2e-4):
        super().__init__()
        self.save_hyperparameters()
        
        # 4-bit Quantization for memory efficiency on 1.7B
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16
        )

        print(f"🚀 Loading 1.7B Model: {model_id}")
        base_model = AutoModelForCausalLM.from_pretrained(
            model_id,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True
        )
        
        base_model = prepare_model_for_kbit_training(base_model)
        
        lora_config = LoraConfig(
            r=16,
            lora_alpha=32,
            target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
            lora_dropout=0.05,
            bias="none",
            task_type="CAUSAL_LM"
        )
        
        self.model = get_peft_model(base_model, lora_config)
        self.monitor = RCODMonitor()
        self.base_lr = base_lr

    def forward(self, **batch):
        return self.model(**batch)

    def training_step(self, batch, batch_idx):
        outputs = self.model(input_ids=batch["input_ids"], labels=batch["labels"], output_hidden_states=True)
        loss = outputs.loss

        # RCOD Monitoring (using last hidden state)
        # Note: Depending on the model, we might need to find the correct layer
        h = outputs.hidden_states[-1]
        v = layer_stat(h)
        phi_n, phi_delta = self.monitor.step(v)

        self.log("train_loss", loss, prog_bar=True)
        self.log("phi_delta", phi_delta, prog_bar=True)
        
        return loss

    def configure_optimizers(self):
        return torch.optim.AdamW(self.parameters(), lr=self.base_lr)

def main():
    parser = argparse.ArgumentParser(description="Train SmolLM2-1.7B with Omega Evolution Data")
    parser.add_argument("--evolution_log", type=str, default="python_env/agent_zero/knowledge/evolution_log.jsonl")
    parser.add_argument("--batch_size", type=int, default=1)
    parser.add_argument("--max_steps", type=int, default=100)
    args = parser.parse_args()

    model_id = "HuggingFaceTB/SmolLM2-1.7B"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    tokenizer.pad_token = tokenizer.eos_token

    dataset = EvolutionDataset(args.evolution_log, tokenizer)
    if len(dataset) == 0:
        print("⚠️ No data found in evolution log. Model cannot train on empty manifold.")
        return

    dataloader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True, num_workers=1)
    
    module = RCOD17BLightningModule(model_id)
    
    trainer = pl.Trainer(
        max_steps=args.max_steps,
        accelerator="auto",
        devices=1,
        precision="16-mixed", # PEFT usually handles this
        log_every_n_steps=1
    )

    print("🔥 Starting 1.7B Fine-Tuning on 300M Model's Learned Successes...")
    trainer.fit(module, train_dataloaders=dataloader)

if __name__ == "__main__":
    main()
