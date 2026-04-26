# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import argparse
import torch
import pytorch_lightning as pl
from torch.utils.data import DataLoader
from transformers import MistralForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import Dataset
import gc
import json

from utils.logger import logger
import sys
import os

# Root path for configs
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from configs.config import config
from rcod.monitor import RCODMonitor
from rcod.hooks import layer_stat

# --- DYNAMIC HARDWARE DETECTION ---
def get_best_accelerator():
    if torch.cuda.is_available():
        return "gpu", "cuda", torch.float16
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps", "mps", torch.float16
    try:
        import torch_directml
        return "cpu", torch_directml.device(), torch.float32 # PyTorch Lightning accelerator string for DML isn't natively supported, usually custom or "cpu" wrapping DML tensors
    except ImportError:
        pass
    
    return "cpu", torch.device("cpu"), torch.float32

class DynamicMemoryCallback(pl.Callback):
    def on_validation_start(self, trainer, pl_module):
        gc.collect()
        if torch.cuda.is_available(): 
            torch.cuda.empty_cache()

class MistralRCODLoraModule(pl.LightningModule):
    def __init__(self, model_id: str, lora_config: LoraConfig, device_map_strategy: str, dtype: torch.dtype, base_lr: float = 1e-4):
        super().__init__()
        self.save_hyperparameters(ignore=["model"])
        
        try:
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=dtype
            )
            logger.info("Attempting 4-bit loading for Mistral...")
            self.model = MistralForCausalLM.from_pretrained(
                model_id, 
                quantization_config=bnb_config,
                device_map=device_map_strategy
            )
            self.model = prepare_model_for_kbit_training(self.model)
        except Exception as e:
            logger.warning(f"4-bit loading failed: {e}. Falling back to standard precision.")
            self.model = MistralForCausalLM.from_pretrained(model_id, torch_dtype=dtype, device_map=device_map_strategy)

        self.model = get_peft_model(self.model, lora_config)
        self.model.print_trainable_parameters()
        
        self.base_lr = base_lr
        self.rcod_cfg = {
            "high_rcod_threshold": 0.6,
            "high_rcod_scale": 0.5,
            "low_rcod_threshold": 0.2,
            "low_rcod_scale": 1.5
        }
        self.monitor = RCODMonitor()
        self.current_lr_scale = 1.0

    def forward(self, **batch):
        return self.model(
            input_ids=batch["input_ids"], 
            labels=batch["input_ids"], 
            output_hidden_states=True
        )

    def training_step(self, batch, batch_idx):
        outputs = self(**batch)
        loss = outputs.loss

        # Mistral 7B has 32 layers
        layers_to_monitor = [7, 15, 23, 31]
        avg_phi_delta = 0.0
        
        for idx in layers_to_monitor:
            if idx < len(outputs.hidden_states):
                h = outputs.hidden_states[idx]
                v = layer_stat(h)
                phi_n, phi_delta = self.monitor.step(v, layer_id=f"layer_{idx+1}")
                avg_phi_delta += phi_delta
                
        avg_phi_delta /= len(layers_to_monitor)
        
        lr_scale = 1.0
        if self.monitor.ready():
            if avg_phi_delta > self.rcod_cfg["high_rcod_threshold"]:
                lr_scale = self.rcod_cfg["high_rcod_scale"]
            elif avg_phi_delta < self.rcod_cfg["low_rcod_threshold"]:
                lr_scale = self.rcod_cfg["low_rcod_scale"]

        self.log("train_loss", loss, prog_bar=True)
        self.log("avg_phi_delta", avg_phi_delta, prog_bar=True)
        self.log("lr_scale", lr_scale)
        
        self.current_lr_scale = lr_scale
        return loss

    def configure_optimizers(self):
        return torch.optim.AdamW(self.parameters(), lr=self.base_lr)

    def on_before_optimizer_step(self, optimizer):
        for g in optimizer.param_groups:
            g["lr"] = self.base_lr * getattr(self, "current_lr_scale", 1.0)


def main():
    parser = argparse.ArgumentParser(description="Omega-Mistral: Fine-tuning Mistral 7B with RCOD")
    parser.add_argument("--data", type=str, default="omega.jsonl", help="Path to JSONL dataset")
    parser.add_argument("--model", type=str, default="mistralai/Mistral-7B-v0.1")
    parser.add_argument("--batch_size", type=int, default=1)
    parser.add_argument("--max_steps", type=int, default=500)
    args = parser.parse_args()

    pl_accelerator, map_strategy, dtype = get_best_accelerator()
    logger.info(f"Using compute logic: Accelerator={pl_accelerator}, Mapping={map_strategy}")

    lora_config = LoraConfig(
        r=16,
        lora_alpha=64,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )

    module = MistralRCODLoraModule(args.model, lora_config, map_strategy, dtype)
    module.model.gradient_checkpointing_enable()

    try:
        with open(args.data, 'r', encoding='utf-8') as f:
            rows = [json.loads(line) for line in f]
    except FileNotFoundError:
        logger.error(f"Dataset not found at {args.data}. Ensure you have provided a valid path.")
        return
        
    dataset = Dataset.from_list(rows)
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    tokenizer.pad_token = tokenizer.eos_token

    def format_prompt(x):
        text = f"Instruction: {x['instruction']}\nContext: {x['context']}\nResponse: {x['response']}"
        return tokenizer(text, truncation=True, max_length=1024)

    tokenized_ds = dataset.map(format_prompt, remove_columns=dataset.column_names)
    loader = DataLoader(tokenized_ds, batch_size=args.batch_size, shuffle=True)
    
    # pl.Trainer maps
    trainer = pl.Trainer(
        max_steps=args.max_steps,
        accelerator=pl_accelerator, 
        devices="auto",
        precision="16-mixed" if dtype == torch.float16 else "32",
        accumulate_grad_batches=16,
        callbacks=[DynamicMemoryCallback()]
    )

    logger.info(f"Launching Mistral 7B Fine-Tuning on {args.data}...")
    trainer.fit(module, train_dataloaders=loader)

if __name__ == "__main__":
    main()
