# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
from huggingface_hub import snapshot_download
import os

os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"

model_id = "HuggingFaceTB/SmolLM2-1.7B"
print(f"🚀 Downloading {model_id}...")

try:
    snapshot_download(repo_id=model_id)
    print(f"✅ Successfully downloaded {model_id}")
except Exception as e:
    print(f"❌ Failed to download {model_id}: {e}")
