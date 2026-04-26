# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import sys
import os

# Set up paths
PROJECT_ROOT = "/home/jake/Downloads/training"
sys.path.append(os.path.join(PROJECT_ROOT, "python_env"))

from utils.nvidia_client import NvidiaClient

def test_nim():
    client = NvidiaClient()
    models_to_test = ["nemotron-super", "qwen-397b", "llama-405b", "llama-ultra"]
    
    for model in models_to_test:
        print(f"Testing {model}...")
        try:
            res = client.chat(model, "Say hello in one sentence.")
            print(f"✅ {model} Success: {res}")
        except Exception as e:
            print(f"❌ {model} Failed: {e}")

if __name__ == "__main__":
    test_nim()
