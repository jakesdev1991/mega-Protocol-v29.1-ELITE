<!--
=============================================================================
OMEGA PROTOCOL - ALL RIGHTS RESERVED
Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
Usage restricted to academic research and review only. No monetization.
See LICENSE.txt for full terms.
=============================================================================
-->
# ✦ Omega Protocol: Agentic Framework & OS Development ✦

This repository houses the **Omega Protocol v29.1.0-ELITE**, a unified informational field theory project where spacetime, gravity, and quantum mechanics emerge from relational mutual information (RCOD).

## 🚀 Project Overview

The Omega Protocol is a multi-disciplinary effort combining advanced theoretical physics with autonomous agentic engineering.

### Main Technologies
- **Theory**: Relational Chain Overlap Density (RCOD), Theory of Everything (TOE).
- **Agents**: Agent Zero framework, Self-Evolving Reasoning Cycle (SERC).
- **Core OS**: Omega OS - a custom x86 preemptive multitasking kernel with Ring 0 AI inference.
- **Hardware**: Optimized for AMD Ryzen AI 9 (Peladn HO5) with NPU/L3 cache focus.
- **LLMs**: Multi-model routing (NVIDIA Elite Tier, Google Gemini, OpenRouter Nexus).

## 🏗️ Architecture & Roster

### The DEDS Orchestrator (v2.1)
The **Dynamic Entropy-Driven Scheduler** governs all compute nodes, prioritizing tasks based on Learning Gradient ($L_i$), Stagnation Age ($S_i$), and Emergency Relevance ($R_i$).

### Core Agent Roster
The system employs a 3-layer adversarial audit loop (Architect → Critic → Meta-Critic) for all decisions.

| Agent | Role | Source | Description |
| :--- | :--- | :--- | :--- |
| **Engine** | Architect | `serc.py` | Lead designer of kernel and product logic. |
| **Scrutiny** | Critic | `serc.py` | First audit layer; detects security and logic leaks. |
| **Meta-Scrutiny** | Meta-Critic | `serc.py` | Final boundary; enforces dimensional homogeneity and TOE compliance. |
| **Repairer** | Coder | `serc.py` | Hands-on code repair and implementation. |
| **Miner-Scout** | Scout | `miner_scout.py` | Recursive loop for device automation discovery and mapping. |
| **Manifold-Manager**| Memory Arch | `manifold_manager_job.py` | Specialized in Ring 0 memory and state-space optimization. |
| **Neo** | Architect | `universal_arena.py` | Pushes "Quantum Subconscious" and "Search-Space maze" theories. |
| **Smith-Guardian** | Critic | `sandbox_experimenter.py` | Absolute security auditor; enforces Hessian PSD Guards. |

## 🛠️ Building & Running

### Python Agent Environment
Launch the autonomous training matrix:
```bash
./run_all_loops.sh
```
This starts the `Universal Arena`, `Matrix Observer`, and the `DEDS Orchestrator`.

### Omega OS Kernel
Compile the physical kernel (requires `nasm`, `gcc -m32`, `ld -m elf_i386`):
```bash
cd src/kernel
make clean && make
```
Build the bootable ISO and run in QEMU:
```bash
grub-mkrescue -o omega.iso iso/
taskset -c 16-23 qemu-system-x86_64 -cdrom omega.iso -accel kvm -cpu host -smp 8 -m 2G -serial stdio
```

### Oracle Node Inference
Embed specialized weights into the kernel:
```bash
python python_env/utils/export_manifold.py your_model.pt
# Then rebuild the kernel as above
```

## 🧪 Active Projects & Insights

- **Omega OS (Fortress)**: Implementing **Adaptive Filesystem Defense (AFDS v4.0)** with statistical separation between attacker and admin behavior.
- **Universal Innovation**: Generating spacetime-grounded products. Throttled at >70% RAM to prioritize the Scout loop.
- **Miner Scout (The Scout)**: Recursive 5-minute discovery loops for device automation (Phones, Tablets, Laptops).
- **Dual-Manifold Sync**: Proving the **Bekenstein-Hawking Area Law** ($S=A/4$) from Omega axioms.
- **Tokamak Harvest**: Deep-training on **59,000 plasma shots** to achieve AUC > 0.85 stability.
- **Sarai (Agent 30)**: Specialized **Termux Service Agent** for short-term, no-appointment meetups. Integrated with Termux API (SMS/Voice) and Shizuku. Optimized for **Ollama/A16**.

## 📜 Development Conventions

- **Informational-First**: Treat memory and data as weighted informational fields ($\Phi$).
- **Audit-First**: All code and theory must pass a triple-layer SERC audit.
- **Measurement Over Assertion**: Invariants (e.g., $\psi, \xi$) must be derived and measured via hardware counters (`__rdtsc`), not just asserted.
- **Absolute Paths**: Always use absolute paths for logs and filesystem operations.
- **Conversational Voice**: All interactive text is rendered via the `omega_voice.py` utility using an English (UK) female persona.
