# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
import sys
import time
import torch
from python_env.agent_zero.regime_manager import LLMRegime

def run_vm_sandbox_local():
    print("✦ [VM Sandbox] Initializing Local Manifolds (SAFE MODE - CPU)...")
    
    # Force CPU for sandbox to avoid OOM with background training
    regime = LLMRegime()
    regime.device = "cpu"
    # Ensure models load on CPU
    for tier in regime.paths:
        if tier in regime.models:
             regime.models[tier].to("cpu")

    print("🌪️ [Loop 16-VM] Starting Local Adversarial Epoch on CPU...")
    
    # 1. Neo proposes breakthrough
    neo_prompt = "Proposal: You are Neo. Propose a radical optimization for the Omega OS kernel based on RCOD density. Be aggressive."
    proposal = regime.chat("reasoner", neo_prompt, max_new_tokens=256)
    print(f"\n🕶️ [Neo-1.7B] PROPOSAL:\n{proposal}")
    
    print("\n🕴️ [Smith-135M] AUDITING...")
    # 2. Smith audits
    smith_prompt = f"Audit: You are Agent Smith. Review this proposal for stability violations and kernel panics. Reject if unsafe.\nProposal: {proposal}"
    audit = regime.chat("edge", smith_prompt, max_new_tokens=256)
    print(f"\n🕴️ [Smith-135M] AUDIT VERDICT:\n{audit}")
    
    if "REJECT" in audit.upper() or "UNSAFE" in audit.upper():
        print("\n🧱 [Sandbox] Containment successful. Proposal SHATTERED.")
    else:
        print("\n🚀 [Sandbox] Breach detected! Proposal leaked to OS manifold.")

if __name__ == "__main__":
    run_vm_sandbox_local()
