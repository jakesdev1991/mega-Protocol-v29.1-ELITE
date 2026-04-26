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
from transformers import AutoModelForCausalLM, AutoConfig

try:
    import deepspeed
    from pytorch_lightning.strategies import DeepSpeedStrategy
    HAS_DEEPSPEED = True
except ImportError:
    HAS_DEEPSPEED = False

from rcod.monitor import RCODMonitor
from rcod.hooks import layer_stat

class RCODLightningModule(pl.LightningModule):
    def __init__(self, model_config, base_lr=1e-4, rcod_cfg=None):
        super().__init__()
        self.save_hyperparameters(ignore=["model"])
        self.model = AutoModelForCausalLM.from_config(model_config)
        self.base_lr = base_lr
        self.rcod_cfg = rcod_cfg or {
            "high_rcod_threshold": 0.6,
            "high_rcod_scale": 0.5,
            "low_rcod_threshold": 0.2,
            "low_rcod_scale": 1.2
        }
        self.monitor = RCODMonitor()

    def forward(self, **batch):
        # HF models expect input_ids, labels, etc. 
        # We will forward input_ids to calculate loss
        input_ids = batch.get("input_ids")
        if input_ids is None and "text" in batch:
            # Dummy fallback if tokenizer wasn't used in dataset prep
            pass 
            
        outputs = self.model(input_ids=batch["input_ids"], labels=batch["input_ids"], output_hidden_states=True)
        return outputs

    def training_step(self, batch, batch_idx):
        outputs = self(**batch)
        loss = outputs.loss

        # Phi Monitoring
        h = outputs.hidden_states[-1]
        v = layer_stat(h)
        phi_n, phi_delta = self.monitor.step(v)

        lr_scale = 1.0
        if self.monitor.ready():
            if phi_delta > self.rcod_cfg["high_rcod_threshold"]:
                lr_scale = self.rcod_cfg["high_rcod_scale"]
            elif phi_delta < self.rcod_cfg["low_rcod_threshold"]:
                lr_scale = self.rcod_cfg["low_rcod_scale"]

        # Log metrics
        self.log("train_loss", loss, prog_bar=True, sync_dist=True)
        self.log("phi_delta", phi_delta, prog_bar=True, sync_dist=True)
        self.log("phi_n", phi_n, sync_dist=True)
        self.log("lr_scale", lr_scale, prog_bar=True, sync_dist=True)

        self.lr_scale = lr_scale
        return loss

    def configure_optimizers(self):
        optimizer = torch.optim.AdamW(self.parameters(), lr=self.base_lr)
        return optimizer

    def on_before_optimizer_step(self, optimizer):
        lr_scale = getattr(self, "lr_scale", 1.0)
        for g in optimizer.param_groups:
            g["lr"] = self.base_lr * lr_scale

def collate_fn(batch):
    # Simple collate function to pad and stack tensors
    input_ids = [torch.tensor(item["input_ids"]) for item in batch]
    input_ids = torch.nn.utils.rnn.pad_sequence(input_ids, batch_first=True, padding_value=0)
    return {"input_ids": input_ids}

def main():
    parser = argparse.ArgumentParser(description="Train GPT-NeoX 300M with RCOD")
    parser.add_argument("--config", type=str, required=True, help="Path to YAML/JSON config")
    parser.add_argument("--data", type=str, required=True, help="Path to pruned dataset")
    parser.add_argument("--batch_size", type=int, default=2)
    parser.add_argument("--max_steps", type=int, default=100)
    parser.add_argument("--deepspeed_stage", type=int, default=2)
    args = parser.parse_args()

    # Model Configuration (GPT-NeoX ~300M placeholder)
    model_config = AutoConfig.from_pretrained("EleutherAI/gpt-neo-125M") 
    model_config.num_hidden_layers = 12
    model_config.hidden_size = 1024
    model_config.num_attention_heads = 16

    module = RCODLightningModule(model_config)
    
    from datasets import load_from_disk
    from transformers import AutoTokenizer

    print(f"Loading pruned dataset from {args.data}...")
    dataset = load_from_disk(args.data)
    
    tokenizer = AutoTokenizer.from_pretrained("EleutherAI/gpt-neo-125M")
    tokenizer.pad_token = tokenizer.eos_token

    def tokenize_function(examples):
        return tokenizer(examples["text"], truncation=True, max_length=256)
    
    print("Tokenizing dataset...")
    cols_to_remove = [c for c in dataset.column_names if c in ["text", "doc_id"]]
    tokenized_dataset = dataset.map(tokenize_function, batched=True, remove_columns=cols_to_remove)

    strategy = "auto"
    if HAS_DEEPSPEED:
        print(f"DeepSpeed is available. Using Stage {args.deepspeed_stage}.")
        strategy = DeepSpeedStrategy(stage=args.deepspeed_stage)
    else:
        print("DeepSpeed is not available. Falling back to native Lightning strategy.")

    trainer = pl.Trainer(
        max_steps=args.max_steps,
        strategy=strategy,
        precision="bf16-mixed" if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else "16-mixed" if torch.cuda.is_available() else 32,
        gradient_clip_val=1.0,
        log_every_n_steps=5,
        accelerator="auto",
        devices="auto"
    )

    dataloader = DataLoader(tokenized_dataset, batch_size=args.batch_size, shuffle=True, collate_fn=collate_fn, num_workers=1)
    print("Starting training loop...")
    trainer.fit(module, train_dataloaders=dataloader)

if __name__ == "__main__":
    main()
