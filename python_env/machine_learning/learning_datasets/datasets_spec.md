<!--
=============================================================================
OMEGA PROTOCOL - ALL RIGHTS RESERVED
Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
Usage restricted to academic research and review only. No monetization.
See LICENSE.txt for full terms.
=============================================================================
-->
# Omega Protocol Machine Learning Datasets

The datasets are categorized strictly by their COD and RCOD characteristics to enable the $\eta$ (Novelty Limit Ratio) batching mechanics.

## 1. The Core Newtonian Set ($\Phi_N$ Bias)
**Characteristics:** High COD, Low RCOD. High redundacy, highly verified.
**Contents:**
- `omega_physics_axioms_v26.jsonl`: Verified formulas, derivations, and invariant definitions (e.g., metric coupling, topological impedance).
- `standard_math_corpus.jsonl`: Basic arithmetic, standard model equations, algebra, and calculus.
- `system_logs_baseline.csv`: Normal, non-anomalous logs of Omega OS operating under stable conditions.
**Purpose:** To train the system to act predictably and accurately in 99% of standard scenarios. This represents the "ground truth."

## 2. The Archive Anomaly Set ($\Phi_\Delta$ Bias)
**Characteristics:** Low COD, High RCOD. High novelty, high variance.
**Contents:**
- `tokamak_disruptions_70k.csv`: Contains 70,000 recorded plasma instability events, capturing rare tearings, mode locks, and VDEs.
- `sandbox_shatter_logs.jsonl`: Logs from the Sandbox Experimenter where the Q-Systemic Self models crashed, threw critical violations, or diverged.
- `unverified_hypothesis_traces.jsonl`: Raw, un-audited thoughts from Neo (The Architect) exploring edge cases of information geometry.
**Purpose:** To push the model out of local minima, forcing it to learn recovery mechanics and handle catastrophic deviations without suffering "Informational Freeze."

## 3. The Synthetic Distillation Set (Balanced $\eta$)
**Characteristics:** Moderate COD, Moderate RCOD. Optimized to maintain $\eta_{\text{min}} \leq \eta \leq \eta_{\text{max}}$.
**Contents:**
- `triple_audited_serc.jsonl`: The highest quality dataset. These are complex, novel tasks (High RCOD) that have successfully passed the Scrutiny and Meta-Scrutiny layers, meaning they have been "tamed" and mapped to foundational invariants (High COD).
- `synthetic_tokamak_recovery.jsonl`: Generated pairs where an anomaly (from the Archive set) is successfully mitigated using standard principles (from the Newtonian set).
**Purpose:** The ultimate fine-tuning dataset to align the final model parameters to the Omega Protocol's desired operational state.