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
from transformers import LlamaForCausalLM, LlamaConfig, AutoTokenizer
from peft import LoraConfig, get_peft_model
from datasets import load_from_disk
import os
import yaml
import gc
from pytorch_lightning.loggers import WandbLogger

# Check for DirectML
try:
    import torch_directml
    HAS_DIRECTML = True
    DML_DEVICE = torch_directml.device()
    print(f"DirectML Backend: {torch_directml.device_name(0)}")
except ImportError:
    HAS_DIRECTML = False
    DML_DEVICE = torch.device("cpu")
    print("DirectML not found, falling back to CPU.")

from rcod.monitor import RCODMonitor
from rcod.hooks import layer_stat

class DirectMLMemoryCallback(pl.Callback):
    def on_validation_start(self, trainer, pl_module):
        gc.collect()
        if torch.cuda.is_available(): torch.cuda.empty_cache()

class RCODLoraModule(pl.LightningModule):
    def __init__(self, model_config, lora_config, base_lr=2e-4, rcod_cfg=None):
        super().__init__()
        self.save_hyperparameters(ignore=["model"])
        base_model = LlamaForCausalLM(model_config)
        self.model = get_peft_model(base_model, lora_config)
        self.model.print_trainable_parameters()
        
        self.base_lr = base_lr
        self.rcod_cfg = rcod_cfg or {
            "high_rcod_threshold": 0.6,
            "high_rcod_scale": 0.5,
            "low_rcod_threshold": 0.2,
            "low_rcod_scale": 1.5,
            "shock_threshold": 0.85, # NEW: Shock detection (Paradigm Shift)
            "shock_lr_scale": 0.1     # Drop LR 10x for shocks
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

        # Multi-Layer Phi Monitoring
        avg_phi_delta = 0
        layers_to_monitor = [len(outputs.hidden_states)//2, len(outputs.hidden_states)-1] 
        for idx in layers_to_monitor:
            h = outputs.hidden_states[idx]
            v = layer_stat(h)
            phi_n, phi_delta = self.monitor.step(v, layer_id=f"layer_{idx}")
            avg_phi_delta += phi_delta
        avg_phi_delta /= len(layers_to_monitor)

        lr_scale = 1.0
        is_shock = False
        
        if self.monitor.ready():
            # ELITE SHOCK DETECTION
            if avg_phi_delta > self.rcod_cfg.get("shock_threshold", 0.85):
                # Paradigm Shift detected: The model is struggling with very novel logic
                lr_scale = self.rcod_cfg.get("shock_lr_scale", 0.1)
                is_shock = True
            elif avg_phi_delta > self.rcod_cfg.get("high_rcod_threshold", 0.6):
                lr_scale = self.rcod_cfg.get("high_rcod_scale", 0.5)
            elif avg_phi_delta < self.rcod_cfg.get("low_rcod_threshold", 0.2):
                lr_scale = self.rcod_cfg.get("low_rcod_scale", 1.5)

        self.log("train_loss", loss, prog_bar=True)
        self.log("avg_phi_delta", avg_phi_delta, prog_bar=True)
        self.log("lr_scale", lr_scale)
        if is_shock:
            self.log("SHOCK_DETECTED", 1.0)
        
        self.current_lr_scale = lr_scale
        return loss

    def configure_optimizers(self):
        return torch.optim.AdamW(self.parameters(), lr=self.base_lr)

    def on_before_optimizer_step(self, optimizer):
        lr_scale = getattr(self, "current_lr_scale", 1.0)
        for g in optimizer.param_groups:
            g["lr"] = self.base_lr * lr_scale

def main():
    parser = argparse.ArgumentParser(description="RCOD Elite: 1.3B Llama + LoRA + Shock Detection")
    parser.add_argument("--data", type=str, required=True)
    parser.add_argument("--batch_size", type=int, default=4)
    parser.add_argument("--max_steps", type=int, default=1000)
    parser.add_argument("--wandb", type=str, default="rcod-1.3b-elite")
    args = parser.parse_args()

    model_config = LlamaConfig(
        vocab_size=32000,
        hidden_size=2048,
        intermediate_size=5632,
        num_hidden_layers=24,
        num_attention_heads=16,
        max_position_embeddings=2048,
        use_cache=False
    )

    lora_config = LoraConfig(
        r=8,
        lora_alpha=32,
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )

    print("Loading RCODLoraModule...")
    module = RCODLoraModule(model_config, lora_config)
    module.model.gradient_checkpointing_enable()

    if HAS_DIRECTML:
        print(f"Moving module to {DML_DEVICE}...")
        module.to(DML_DEVICE)

    print(f"Loading dataset from {args.data}...")
    train_ds = load_from_disk(args.data)
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained("hf-internal-testing/llama-tokenizer")
    tokenizer.pad_token = tokenizer.eos_token
    
    print("Tokenizing dataset...")
    def tokenize_fn(x): return tokenizer(x["text"], truncation=True, max_length=1024)
    train_tokenized = train_ds.map(tokenize_fn, batched=True, remove_columns=train_ds.column_names)
    train_tokenized.set_format("torch")

    print("Initializing WandB Logger...")
    wandb_logger = WandbLogger(project=args.wandb)

    # Memory-efficient checkpointing: Save only LoRA weights, not full 1.3B model
    checkpoint_callback = pl.callbacks.ModelCheckpoint(
        dirpath="checkpoints",
        filename="rcod-1.3b-{step}",
        save_weights_only=True,
        every_n_train_steps=500
    )

    trainer = pl.Trainer(
        max_steps=args.max_steps,
        accelerator="cpu", 
        devices=1,
        precision=32,
        accumulate_grad_batches=4,
        logger=wandb_logger,
        callbacks=[DirectMLMemoryCallback(), checkpoint_callback],
        enable_checkpointing=True
    )

    loader = DataLoader(train_tokenized, batch_size=args.batch_size, shuffle=True)
    
    print("Launching Elite 1.3B LoRA Training with Shock Detection...")
    trainer.fit(module, train_dataloaders=loader)

if __name__ == "__main__":
    main()
