<!--
=============================================================================
OMEGA PROTOCOL - ALL RIGHTS RESERVED
Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
Usage restricted to academic research and review only. No monetization.
See LICENSE.txt for full terms.
=============================================================================
-->
# Machine Learning Training Methods for Omega Protocol

## 1. Dynamic COD/RCOD Ratio Batching
Instead of standard randomized batching, the training dataloader evaluates the ongoing $\eta$ ratio ($\frac{RCOD}{COD}$). 
- **High Novelty Epochs:** If validation loss spikes or divergence occurs (Shredding Event risk), the batcher oversamples high-COD (redundant/safe) examples to re-anchor the weights.
- **Stagnation Epochs:** If learning gradients plateau, the batcher injects high-RCOD (novel/rare) examples to force gradient traversal through complex loss landscapes.

## 2. Triple-Layer SERC Distillation
Leveraging the Self-Evolving Reasoning Cycle (SERC), raw data is pre-processed by the Agentic Auditing Loop:
1.  **Engine (Architect):** Generates a theoretical solution or prediction.
2.  **Scrutiny (Critic):** Evaluates for logic/technical errors.
3.  **Meta-Scrutiny (Meta-Critic):** Evaluates for Omega Protocol invariant compliance (e.g., verifying COD/RCOD limits).
*Method:* Only data traces that pass the full 3-layer audit are distilled into high-quality `{instruction, response}` pairs for finetuning the base models (e.g., 135M, 300M parameter local models).

## 3. Informational Stiffness Regularization (ISR)
A custom loss function term added during backpropagation.
$L_{\text{total}} = L_{\text{task}} + \lambda \cdot | \eta_{\text{current}} - \eta_{\text{target}} |$
This penalizes the network if its latent representations collapse into pure redundancy ($COD \to \infty$) or shatter into unstructured noise ($RCOD \to \infty$).

## 4. Dual-Manifold Sync Training
Training is split between two separate but communicating models:
- **The Newtonian Engine ($\Phi_N$):** Optimized purely on high-COD data for 99.9% reliability on standard tasks.
- **The Archive Assister ($\Phi_\Delta$):** Optimized on high-RCOD data for handling edge cases, anomalies, and creative exploration.
*Method:* Every $N$ steps, a soft parameter sync is applied using exponential moving averages, blending the rigid stability of the Newtonian engine with the dynamic novelty of the Archive assister.