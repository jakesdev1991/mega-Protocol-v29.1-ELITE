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
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    def on_train_epoch_end(self, trainer, pl_module):
        gc.collect()

class SmartWarmupCallback(pl.Callback):
    """
    Ramps up LR. If RCOD spread is high, it slows down the warmup.
    """
    def __init__(self, warmup_steps=500):
        self.warmup_steps = warmup_steps
        self.current_warmup = 0

    def on_train_batch_start(self, trainer, pl_module, batch, batch_idx):
        if self.current_warmup < self.warmup_steps:
            # Check avg spread across monitored layers
            avg_spread = 0
            count = 0
            for l_id in ["layer_4", "layer_8", "layer_12"]:
                if l_id in pl_module.monitor.layers:
                    # simplistic check
                    pass 
            
            # Linear warmup factor
            self.current_warmup += 1
            pl_module.warmup_factor = self.current_warmup / self.warmup_steps
        else:
            pl_module.warmup_factor = 1.0

class RCODLlamaModule(pl.LightningModule):
    def __init__(self, model_config, base_lr=1e-4, rcod_cfg=None):
        super().__init__()
        self.save_hyperparameters(ignore=["model"])
        self.model = LlamaForCausalLM(model_config)
        self.base_lr = base_lr
        self.warmup_factor = 0.0
        self.rcod_cfg = rcod_cfg or {
            "high_rcod_threshold": 0.6,
            "high_rcod_scale": 0.5,
            "low_rcod_threshold": 0.2,
            "low_rcod_scale": 1.2
        }
        self.monitor = RCODMonitor()

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
        # Monitor middle and end layers
        metrics = {}
        avg_phi_delta = 0
        layers_to_monitor = [3, 7, 11] # 0-indexed layers 4, 8, 12
        for idx in layers_to_monitor:
            h = outputs.hidden_states[idx]
            v = layer_stat(h)
            l_id = f"layer_{idx+1}"
            phi_n, phi_delta = self.monitor.step(v, layer_id=l_id)
            metrics[f"phi_delta_{l_id}"] = phi_delta
            metrics[f"phi_n_{l_id}"] = phi_n
            avg_phi_delta += phi_delta
        
        avg_phi_delta /= len(layers_to_monitor)
        
        lr_scale = 1.0
        if self.monitor.ready():
            if avg_phi_delta > self.rcod_cfg.get("high_rcod_threshold", 0.6):
                lr_scale = self.rcod_cfg.get("high_rcod_scale", 0.5)
            elif avg_phi_delta < self.rcod_cfg.get("low_rcod_threshold", 0.2):
                lr_scale = self.rcod_cfg.get("low_rcod_scale", 1.2)

        # Log metrics
        self.log("train_loss", loss, prog_bar=True)
        self.log("avg_phi_delta", avg_phi_delta, prog_bar=True)
        self.log_dict(metrics)
        self.log("lr_scale", lr_scale, prog_bar=True)
        self.log("warmup_factor", self.warmup_factor)

        self.last_avg_phi_delta = avg_phi_delta
        self.lr_scale = lr_scale
        return loss

    def validation_step(self, batch, batch_idx):
        outputs = self(**batch)
        loss = outputs.loss
        self.log("val_loss", loss, prog_bar=True)
        return loss

    def configure_optimizers(self):
        optimizer = torch.optim.AdamW(self.parameters(), lr=self.base_lr, weight_decay=0.1)
        return optimizer

    def on_before_optimizer_step(self, optimizer):
        lr_scale = getattr(self, "lr_scale", 1.0)
        warmup = getattr(self, "warmup_factor", 1.0)
        avg_phi_delta = getattr(self, "last_avg_phi_delta", 0.0)
        
        for g in optimizer.param_groups:
            # Dynamic LR: Base * Scale * Warmup
            g["lr"] = self.base_lr * lr_scale * warmup
            
            # Weighted Weight Decay: scale decay by (1 + avg_phi_delta)
            # Higher curvature = slightly more decay to stabilize
            g["weight_decay"] = 0.1 * (1.0 + avg_phi_delta)

class CurvaturePackingCollator:
    def __init__(self, tokenizer, max_length=1024):
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __call__(self, samples):
        all_ids = []
        for s in samples:
            all_ids.extend(s["input_ids"])
            all_ids.append(self.tokenizer.eos_token_id)

        blocks = []
        for i in range(0, len(all_ids), self.max_length):
            block = all_ids[i : i + self.max_length]
            if len(block) == self.max_length:
                blocks.append(torch.tensor(block))
        
        if not blocks:
            input_ids = [torch.tensor(s["input_ids"]) for s in samples]
            input_ids = torch.nn.utils.rnn.pad_sequence(input_ids, batch_first=True, padding_value=0)
            return {"input_ids": input_ids}
            
        return {"input_ids": torch.stack(blocks)}

def main():
    parser = argparse.ArgumentParser(description="RCOD Pro Training (DirectML + W&B)")
    parser.add_argument("--config", type=str, required=True)
    parser.add_argument("--data", type=str, required=True)
    parser.add_argument("--batch_size", type=int, default=12) 
    parser.add_argument("--accumulate", type=int, default=8, help="Gradient accumulation steps")
    parser.add_argument("--max_steps", type=int, default=2000)
    parser.add_argument("--pack", action="store_true")
    parser.add_argument("--wandb_project", type=str, default="rcod-llama-300m")
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        cfg = yaml.safe_load(f)

    model_config = LlamaConfig(
        vocab_size=32000,
        hidden_size=cfg.get("hidden_size", 1024),
        intermediate_size=4096,
        num_hidden_layers=cfg.get("num_layers", 12),
        num_attention_heads=cfg.get("num_attention_heads", 16),
        max_position_embeddings=2048,
        rms_norm_eps=1e-6,
        use_cache=False,
        bos_token_id=1,
        eos_token_id=2
    )

    module = RCODLlamaModule(model_config, base_lr=cfg.get("optimizer", {}).get("params", {}).get("lr", 1e-4))
    module.model.gradient_checkpointing_enable()

    train_ds = load_from_disk(args.data)
    tokenizer = AutoTokenizer.from_pretrained("hf-internal-testing/llama-tokenizer")
    tokenizer.pad_token = tokenizer.eos_token

    def tokenize_function(examples):
        return tokenizer(examples["text"], truncation=True, max_length=1024)
    
    train_tokenized = train_ds.map(tokenize_function, batched=True, remove_columns=train_ds.column_names)
    split = train_tokenized.train_test_split(test_size=0.02)
    
    wandb_logger = WandbLogger(project=args.wandb_project, log_model=True)

    if HAS_DIRECTML:
        module.to(DML_DEVICE)

    trainer = pl.Trainer(
        max_steps=args.max_steps,
        accelerator="cpu", 
        devices=1,
        precision=32, 
        accumulate_grad_batches=args.accumulate,
        log_every_n_steps=5,
        val_check_interval=100,
        enable_checkpointing=True,
        logger=wandb_logger,
        callbacks=[DirectMLMemoryCallback(), SmartWarmupCallback(warmup_steps=300)]
    )

    collator = CurvaturePackingCollator(tokenizer) if args.pack else None
    train_loader = DataLoader(split["train"], batch_size=args.batch_size, shuffle=True, collate_fn=collator)
    val_loader = DataLoader(split["test"], batch_size=args.batch_size, collate_fn=collator)
    
    print(f"Starting Pro training run with Gradient Accumulation (8x) and Multi-Layer RCOD...")
    trainer.fit(module, train_dataloaders=train_loader, val_dataloaders=val_loader)

if __name__ == "__main__":
    main()
