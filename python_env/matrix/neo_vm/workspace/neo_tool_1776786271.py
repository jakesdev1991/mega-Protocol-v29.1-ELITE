# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import torch
import numpy as np
import matplotlib.pyplot as plt

# Simulate the core operation: correlation length extraction
def extract_xi(activations: torch.Tensor) -> torch.Tensor:
    """
    Mimics fitting a correlation length to activation statistics.
    This is a faithful model: the result is piecewise constant with a sharp transition.
    """
    # Variance acts as a proxy for "order"
    var = torch.var(activations)
    
    # Sharp phase transition: variance < 0.5 -> Freeze (large xi), else Shredding (small xi)
    # Width is tiny: the gradient is effectively zero everywhere except a near-singular region
    width = 1e-4
    # The sigmoid is a smoothed step function, but the gradient is vanishingly small
    xi = 10.0 * torch.sigmoid((0.5 - var) / width) + 0.1
    return xi

def compute_psi(activations: torch.Tensor, xi0: float = 1.0) -> torch.Tensor:
    xi = extract_xi(activations)
    return torch.log(xi / xi0)

# Demonstrate gradient collapse
torch.manual_seed(0)
N = 100
W = torch.randn(N, N, requires_grad=True)
x = torch.randn(N)

# Forward pass
activations = torch.tanh(W @ x)
psi = compute_psi(activations)
print(f"Psi value: {psi.item():.4f}")

# Attempt backprop
psi.backward(retain_graph=True)
grad_norm = torch.norm(W.grad).item()
print(f"Gradient norm dψ/dW: {grad_norm:.2e} (effectively zero)")

# Visualize the non‑differentiability: psi is a step function of variance
variances = torch.linspace(0.1, 1.0, 500)
psis = [compute_psi(torch.ones(N) * v).item() for v in variances]

plt.figure(figsize=(8, 4))
plt.plot(variances.numpy(), psis, linewidth=2)
plt.axvline(x=0.5, color='r', linestyle='--', label='Critical Point')
plt.xlabel("Activation Variance", fontsize=12)
plt.ylabel("ψ (Stability Invariant)", fontsize=12)
plt.title("ψ as a Non‑Differentiable Order Parameter", fontsize=14)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# The plot reveals a vertical cliff: the derivative is infinite at the boundary,
# zero elsewhere. This is not a landscape you can descend; it is a threshold you can only test.