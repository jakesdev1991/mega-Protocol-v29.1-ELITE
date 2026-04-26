# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
import subprocess
import sys

# Ensure project root is in path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
VENV_PYTHON = os.path.join(PROJECT_ROOT, "..", ".venv", "bin", "python")

class ModelTrainer:
    """Automates fine-tuning based on Agent Zero's evolution log (SERC)."""
    
    def __init__(self, data_path=None):
        if data_path is None:
            data_path = os.path.join(PROJECT_ROOT, "agent_zero", "knowledge", "evolution_log.jsonl")
        else:
            if not os.path.isabs(data_path):
                data_path = os.path.join(PROJECT_ROOT, data_path)
        self.data_path = data_path
        # Using the existing 1.3b training script as the backend
        self.script_path = os.path.join(PROJECT_ROOT, "examples", "train_1_3b_rcod_lora_dml.py")
        
    def needs_training(self, min_samples=50):
        """Check if we have enough new SERC successful logs to justify a fine-tuning run."""
        if not os.path.exists(self.data_path):
            return False
            
        with open(self.data_path, "r") as f:
            lines = f.readlines()
        return len(lines) >= min_samples

    def train_specialized_model(self, specialized_role_name="worker_v2"):
        """Triggers a background LoRA fine-tuning run using the accumulated agent data."""
        if not os.path.exists(self.script_path):
            print(f"❌ Trainer Error: Script {self.script_path} not found.")
            return False

        print(f"🚀 [Agent Zero Trainer] Initiating automated fine-tuning for specialized role: {specialized_role_name}...")
        
        # In a real scenario, we'd preprocess JSONL into HuggingFace dataset format.
        # Here we point the script to our new data and launch it.
        try:
            process = subprocess.Popen(
                [VENV_PYTHON, self.script_path, "--data", self.data_path, "--batch_size", "1", "--max_steps", "100", "--wandb", f"agent-zero-evolve-{specialized_role_name}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            print(f"✅ Training launched in background (PID: {process.pid}). The model will evolve based on its own successful reasonings.")
            return True
        except Exception as e:
            print(f"❌ Training Failed to Launch: {e}")
            return False

if __name__ == "__main__":
    trainer = ModelTrainer()
    if trainer.needs_training(min_samples=1):
        trainer.train_specialized_model("logic_specialist")
    else:
        print("Not enough evolution data to train yet.")
