<!--
=============================================================================
OMEGA PROTOCOL - ALL RIGHTS RESERVED
Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
Usage restricted to academic research and review only. No monetization.
See LICENSE.txt for full terms.
=============================================================================
-->
# Agentic Training Workflow Pipeline

The Omega Protocol utilizes a multi-agent orchestrated pipeline to autonomously curate, balance, and execute machine learning training cycles.

## Phase 1: Data Gathering & Curation (Miner-Scout & Scrutiny)
1.  **Miner-Scout** continuously runs recursive loops (e.g., scraping new GitHub repositories or querying device automations) generating raw, highly novel data (High RCOD).
2.  The raw data is stored in the `raw_archive` buffer.
3.  **Scrutiny (The Critic)** evaluates the buffer. Data that is purely noise is discarded. Data with structural merit is passed to Phase 2.

## Phase 2: Triple-Layer Auditing & Formatting (SERC)
1.  **The Engine** takes the curated novel data and attempts to map it to known Omega Protocol paradigms.
2.  **Scrutiny** checks the Engine's reasoning for logic leaks.
3.  **Meta-Scrutiny (Agent Smith / Guardian)** enforces the Hessian PSD Guards and ensures dimensional homogeneity.
4.  *Success:* The resulting `{instruction, reasoning, response}` pair is formatted as JSONL and moved to the `Synthetic Distillation Set`.

## Phase 3: The $\eta$-Ratio Dataloader (Orchestrator)
1.  The `DEDS Orchestrator` spins up the PyTorch training loop (e.g., `train_135m_omega.py`).
2.  The custom Dataloader actively monitors the learning rate and loss gradients.
3.  **Metric Calculation:** The dataloader estimates the current batch's COD vs RCOD by calculating the cosine similarity of the batch embeddings against the core Newtonian set in the Vector DB (Qdrant).
4.  **Adjustment:** If $\eta$ drops too low, the dataloader pulls heavily from the `Archive Anomaly Set`. If $\eta$ spikes too high, it pulls from the `Core Newtonian Set`.

## Phase 4: Semiclassical Parameter Sync (Dual-Manifold Mode)
1.  If operating in Dual-Manifold Mode, two distinct models are trained simultaneously.
2.  **Manifold-Manager Agent** monitors the drift between the $\Phi_N$ model and the $\Phi_\Delta$ model.
3.  Every $N$ steps, the Manager initiates a parameter sync using Exponential Moving Average (EMA) to prevent catastrophic divergence of the anomaly model, grounding it to the stable base.

## Phase 5: Deployment & Working Memory Ingestion
1.  Once validation loss plateaus within the acceptable $\eta$ boundary, the model weights are quantized (e.g., GGUF) and deployed.
2.  The `ingest_ml_memory.py` script automatically reads the training hyper-parameters, final loss metrics, and generated artifacts, embedding them into the **Qdrant LTM Vector DB**. This ensures future training loops have historical context on what hyperparameters lead to Shredding Events vs Optimal Learning.