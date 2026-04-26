# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
import shutil
import sys

def build():
    launch_dir = "official_launch"
    print(f"--- OMEGA PROTOCOL: COMMERCIAL ARCHITECT ---")
    print(f"Building Production Environment in: {launch_dir}...")

    # 1. Define Structure
    dirs = [
        os.path.join(launch_dir, "rcod"),           # Core Engine
        os.path.join(launch_dir, "tools"),          # Utility Suite
        os.path.join(launch_dir, "examples"),       # Training Blueprints
        os.path.join(launch_dir, "configs"),        # Hyperparameters
        os.path.join(launch_dir, "data"),           # Datasets
        os.path.join(launch_dir, "docs"),           # Whitepapers/Pitch
        os.path.join(launch_dir, "research"),       # Raw Theory
        os.path.join(launch_dir, "legal"),          # Licenses and NDAs
        os.path.join(launch_dir, "business"),       # Contacts and Billing
        os.path.join(launch_dir, "business/marketing_assets") # Visuals
    ]

    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # 2. Map Files to Tiers
    mapping = {
        "tools": [
            "plot_rcod_metrics.py", "analyze_pruning.py", "monitor_vram.py",
            "generate.py", "active_gating.py", "hf_upload.py", "vibe_check.py",
            "benchmark_rcod.py", "generate_report.py", "eval_omega.py",
            "infinite_pruner.py", "omega_server.py", "check_datasets.py"
        ],
        "examples": [
            "train_300m_rcod_lightning_dml.py", "train_300m_rcod_lightning.py",
            "train_1.3b_rcod_lora_dml.py", "train_mistral_7b_omega.py"
        ],
        "docs": [
            "OMEGA_PROTOCOL_WHITEPAPER.md", "OMEGA_COMMERCIAL_PITCH.md", 
            "OMEGA_MARKETING_STRATEGY.md", "status_version_5.png"
        ],
        "legal": [
            "LICENSE_PROPRIETARY.txt"
        ],
        "research": [
            "deepspeed.docx", "deepspeed.txt", "dump_extract.docx", "dump_extract.txt",
            "pruning.docx", "pruning.txt", "rcod_master.docx", "rcod_master.txt",
            "Omega Protocol AI Training Dataset (JSONL).docx", "omega.txt", "extract_docx_text.py"
        ],
        "data": [
            "omega.jsonl"
        ]
    }

    # 3. Execute Movement (Copy instead of move to keep root clean for now)
    count = 0
    for target_subdir, files in mapping.items():
        for f in files:
            source_path = f
            # Check if file is in root
            if os.path.exists(source_path):
                shutil.copy(source_path, os.path.join(launch_dir, target_subdir, f))
                count += 1
            # Check if it was already moved to an old folder by a previous build
            elif os.path.exists(os.path.join(target_subdir, f)):
                shutil.copy(os.path.join(target_subdir, f), os.path.join(launch_dir, target_subdir, f))
                count += 1

    # 4. Create Commercial Placeholders
    placeholders = {
        "business/TARGET_EMAIL_LIST.txt": "# List of CTO/Head of AI emails for outreach\n\n",
        "business/API_CONNECTION_KEYS.env": "# Email API Keys (SendGrid/Mailgun)\n# W&B API Keys\n# HuggingFace Write Token\n",
        "business/CLIENT_INVOICE_TEMPLATE.md": "# INVOICE\n\nClient:\nService: RCOD Integration / Omega Protocol Consultation\nAmount:",
        "legal/NON_DISCLOSURE_AGREEMENT_DRAFT.txt": "STANDARD NDA PLACEHOLDER\n\nBetween [Your Name] and [Client Name]",
        "business/crm_tracker.csv": "Company,Contact Name,Email,Status,Last Contacted"
    }

    for path, content in placeholders.items():
        full_path = os.path.join(launch_dir, path)
        if not os.path.exists(full_path):
            with open(full_path, "w") as f:
                f.write(content)

    print(f"\nBuild Complete. {count} files staged for commercialization in '{launch_dir}'.")
    print("\nCOMMERCIAL STRUCTURE READY:")
    print("-----------------------------------")
    print("official_launch/business -> CRM, Invoices, and API keys")
    print("official_launch/legal    -> NDA and Proprietary License")
    print("official_launch/docs     -> Sales Pitch and Whitepapers")
    print("official_launch/rcod     -> Production Core Engine")
    print("-----------------------------------")

if __name__ == "__main__":
    build()
