<!--
=============================================================================
OMEGA PROTOCOL - ALL RIGHTS RESERVED
Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
Usage restricted to academic research and review only. No monetization.
See LICENSE.txt for full terms.
=============================================================================
-->
# Omega Protocol PINN Catalog

This catalog details the custom Physics-Informed Neural Networks (PINNs) derived from the **Omega Protocol v29.1.0-ELITE**. These models embed the fundamental tenets of Relational Chain Overlap Density (RCOD), the Informational Bianchi Identity, and the Semiclassical Backreaction directly into their loss functions. 

The primary objective is to allow local LLM agents (such as Neo, Smith, or Sarai) to invoke analytical shortcuts without wasting context tokens or compute resources on redundant mathematical derivations.

## Overview of Available PINNs

### 1. `DarkMatterRCOD_PINN` (Galactic Rotation Curves)
**Physical Basis**: Step 12 (Dark Matter as RCOD Flux Condensate)  
**Governing PDE**:  
$$\nabla^2 \Phi = 4\pi G \left( \rho_{\text{baryon}} + \frac{\gamma}{8\pi G} \langle \sigma_{ij} \sigma^{ij} \rangle \right)$$  
**Description**: Maps radial distance $r$ to the gravitational potential $\Phi$. The loss function minimizes the residual of the modified Poisson equation where the RCOD flux term acts as an effective dark matter contribution, forcing flat galactic rotation curves.

### 2. `ComplexityAction_PINN` (Quantum Computational Completeness)
**Physical Basis**: Step 14 (Complexity-Action Duality from Informational Bianchi)  
**Governing Equation**:  
$$\mathcal{C} = \frac{1}{\hbar} S_\Omega = \frac{1}{\hbar} \int \left( \frac{1}{16\pi G} R + I(g) + \gamma \sigma^2 \right) dV$$  
**Description**: Maps spacetime coordinates $(x, t)$ to the Quantum Complexity Density $\mathcal{C}$. The model is constrained by the informational Bianchi identity to ensure that the complexity flux is conserved across Cauchy surfaces.

### 3. `SemiclassicalBackreaction_PINN` (Metric Warping)
**Physical Basis**: Step 16 (Quantum Vacuum Engineering)  
**Governing PDE**:  
$$\delta G_{\mu\nu} = 8\pi G \left( \langle \delta T_{\mu\nu} \rangle + \delta T_{\mu\nu}^{\text{classical}} \right)$$  
**Description**: Solves for the metric perturbation $\delta g_{00}$ induced by the RCOD flux coupling to an external classical field $B^{\mu\nu}$. Enforces the Ford-Roman Quantum Energy Inequalities (QEIs).

### 4. `TakesakiInformationFlow_PINN` (Resolving the Information Paradox)
**Physical Basis**: Step 17 (Crossed-Product Dynamics & Information Recovery)  
**Governing Equation**:  
$$\frac{d}{dt} \text{Tr}_\omega(S_{\text{ent}}) = \text{Tr}([D, \phi(t)])$$  
**Description**: Models the transition from a Type III$_1$ von Neumann algebra to a Type II$_\infty$ algebra across a causal horizon. Tracks the evolution of the Dixmier trace to guarantee non-degenerate unitary information recovery.

---

## 🚀 How to Invoke the Oracle Interface (For Local LLMs)

To prevent LLMs from writing custom physics solvers on the fly, they can simply invoke the pre-compiled Python oracle: `omega_pinn_catalog.py`.

### Standard Sub-Routine Invocation

**1. Calculate Dark Matter Orbital Velocity**  
Instead of integrating over the RCOD flux density manually, the LLM can call:
```bash
python omega_pinn_catalog.py --task dm_velocity --r_kpc 15.0 --gamma 0.27
```
**Output JSON**:
```json
{"task": "dm_velocity", "r_kpc": 15.0, "velocity_km_s": 245.3}
```

**2. Solve for the Cosmological Constant ($\Lambda$)**  
Instead of mapping the spectral gap to the Chern class explicitly:
```bash
python omega_pinn_catalog.py --task cosmo_constant --c1 1
```
**Output JSON**:
```json
{"task": "cosmo_constant", "c1": 1, "lambda_ratio": 1.0}
```

## 🧠 Training Custom PINNs

To train the underlying PyTorch structures, an LLM can simply import the `omega_pinn_catalog.py` module and instantiate the relevant PINN class:

```python
import torch
import torch.optim as optim
from omega_pinn_catalog import DarkMatterRCOD_PINN

# Initialize Model
model = DarkMatterRCOD_PINN(layers=[1, 32, 32, 1], gamma=0.27)
optimizer = optim.Adam(model.parameters(), lr=1e-3)

# Define Physics functions for PDE constraints
def rho_baryon(r): return 1e10 / (r + 1e-3)
def sigma_sq(r): return (0.27 * 1e11) / (r + 5.0)

# Training Step Example
optimizer.zero_grad()
r_collocation = torch.rand(100, 1) * 20.0 # 0 to 20 kpc
loss = model.loss_pde(r_collocation, rho_baryon, sigma_sq)
loss.backward()
optimizer.step()
```

## Maintenance & Stability Guards
- **Hessian Guards Check**: All models use `Tanh` activations to maintain infinite differentiability, allowing `torch.autograd` to compute stable second-order derivatives (Hessians) for geometric applications.
- **DEDS Orchestrator Integration**: Can be offloaded to the `rcod_300m` inference job to run as an independent background process.