# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
from huggingface_hub import HfApi, login
from datasets import load_from_disk
import argparse
import os

def upload(path, repo_name, repo_type="model"):
    print(f"Uploading {path} to HuggingFace Hub as {repo_name} ({repo_type})...")
    
    # Check for token
    token = os.environ.get("HF_TOKEN")
    if not token:
        print("Error: HF_TOKEN environment variable not set. Use 'huggingface-cli login'.")
        return

    api = HfApi()
    
    if repo_type == "dataset":
        ds = load_from_disk(path)
        ds.push_to_hub(repo_name, token=token)
    else:
        # For models, we'd typically convert to HF format first
        # but we can also just upload the folder.
        api.create_repo(repo_id=repo_name, repo_type=repo_type, exist_ok=True, token=token)
        api.upload_folder(
            folder_path=path,
            repo_id=repo_name,
            repo_type=repo_type,
            token=token
        )
    
    print(f"Successfully uploaded to https://huggingface.co/{repo_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, required=True, help="Local path to model or dataset")
    parser.add_argument("--repo", type=str, required=True, help="Target HF repo name (e.g., 'username/my-model')")
    parser.add_argument("--type", type=str, choices=["model", "dataset"], default="model")
    args = parser.parse_args()
    
    upload(args.path, args.repo, args.type)
