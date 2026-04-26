# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import torch
import os
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer, TrainerCallback
from datasets import Dataset
import time

class GPUComputeThrottler(TrainerCallback):
    """
    Caps total GPU utilization by introducing a rest period after each step.
    To target 80% max usage, we use a 4:1 work:rest ratio.
    """
    def __init__(self, target_utilization=0.8):
        self.target = target_utilization
        self.last_step_time = time.time()

    def on_step_begin(self, args, state, control, **kwargs):
        self.step_start = time.time()

    def on_step_end(self, args, state, control, **kwargs):
        step_duration = time.time() - self.step_start
        
        # Calculation:
        # utilization = work / (work + rest)
        # 0.8 = duration / (duration + rest)
        # 0.8*duration + 0.8*rest = duration
        # 0.8*rest = 0.2*duration
        # rest = 0.25 * duration
        
        rest_time = ((1.0 - self.target) / self.target) * step_duration
        
        # Max rest cap to prevent freezing (10s)
        rest_time = min(rest_time, 10.0)
        
        if rest_time > 0.01:
            # print(f" 🛌 [Throttle] Resting for {rest_time:.2f}s to maintain 80% GPU cap...")
            time.sleep(rest_time)

class VRAMSafetyCallback(TrainerCallback):
    """Pauses training if VRAM usage exceeds a specific threshold."""
    def __init__(self, threshold_pct=0.8):
        self.threshold = threshold_pct

    def on_step_end(self, args, state, control, **kwargs):
        if torch.cuda.is_available():
            # Get VRAM usage
            allocated = torch.cuda.memory_allocated() / torch.cuda.get_device_properties(0).total_memory
            if allocated > self.threshold:
                print(f"\n⚠️ [Safety Guard] VRAM at {allocated*100:.1f}%. Pausing for cooling/cleanup...")
                torch.cuda.empty_cache()
                time.sleep(5) # Throttle to reduce load

# 1. Configuration
BASE_MODEL_DIR = "/home/jake/Downloads/training/base_model" 
SYNTHESIZED_WEIGHTS = "/home/jake/Downloads/training/tokamak_300m_elite_synthesized.pt"
OUTPUT_DIR = "/home/jake/Downloads/training/tokamak_300m_training"
FINAL_MODEL = "/home/jake/Downloads/training/tokamak_300m_elite.pt"
DATA_FILE = "/home/jake/Downloads/training/data/normalized_tokamak_200k.jsonl"

def train_tokamak_300m():
    """
    Fine-tunes the 300M 'Predictive Frontal Lobe' with strict 80% VRAM cap.
    """
    print("🚀 [Training] Starting SAFE Mode Training (80% GPU Cap)...")
    
    # Load dataset
    print(f"[*] Loading data from {DATA_FILE}...")
    texts = []
    import json
    with open(DATA_FILE, "r") as f:
        for line in f:
            texts.append(json.loads(line)["text"])
    
    dataset = Dataset.from_dict({"text": texts})

    # Load Model structure
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_DIR)
    tokenizer.pad_token = tokenizer.eos_token
    
    model = AutoModelForCausalLM.from_pretrained(BASE_MODEL_DIR)
    
    # Inject synthesized weights
    print(f"[*] Injecting Synthesized weights...")
    state_dict = torch.load(SYNTHESIZED_WEIGHTS, map_location="cpu", weights_only=False)
    model.load_state_dict(state_dict, strict=False)
    
    # Enable Gradient Checkpointing to save VRAM
    model.gradient_checkpointing_enable()
    model.to("cuda")

    def tokenize_function(examples):
        tokens = tokenizer(examples["text"], padding="max_length", truncation=True, max_length=128)
        tokens["labels"] = tokens["input_ids"].copy()
        return tokens

    tokenized_datasets = dataset.map(tokenize_function, batched=True)

    # 4. Training Arguments - Aggressively tuned for 80% cap
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=4, # Reduced from 8 to save VRAM
        gradient_accumulation_steps=4, # Increased to keep effective batch size stable
        num_train_epochs=3,
        learning_rate=5e-5,
        logging_steps=50,
        save_strategy="epoch",
        report_to="none",
        bf16=True,
        optim="adamw_bnb_8bit", # Use 8-bit Adam to save VRAM if bitsandbytes available
        dataloader_num_workers=2,
        dataloader_pin_memory=True,
        gradient_checkpointing=True # Critical for VRAM ceiling
    )

    # 5. Trainer with Safety Callbacks
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets,
        callbacks=[
            VRAMSafetyCallback(threshold_pct=0.8),
            GPUComputeThrottler(target_utilization=0.8)
        ]
    )

    # Resume check
    checkpoint = None
    if os.path.exists(OUTPUT_DIR):
        checkpoints = [os.path.join(OUTPUT_DIR, d) for d in os.listdir(OUTPUT_DIR) if d.startswith("checkpoint-")]
        if checkpoints:
            checkpoint = max(checkpoints, key=os.path.getmtime)
            print(f"[*] Resuming safely from: {checkpoint}")

    print(f"[*] Starting Fine-Tuning...")
    trainer.train(resume_from_checkpoint=checkpoint)

    # 6. Export
    print(f"[*] Exporting Elite Tokamak weights to {FINAL_MODEL}...")
    torch.save(model.state_dict(), FINAL_MODEL)
    print("✅ 300M Elite Training Complete (Safe Mode).")

if __name__ == "__main__":
    train_tokamak_300m()
