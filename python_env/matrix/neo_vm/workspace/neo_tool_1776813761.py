# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

# ----------------------------------------------------------------------
# 1.  Two‑layer LINEAR network (no activation) – function is W1 @ W2
# ----------------------------------------------------------------------
class LinearNet(nn.Module):
    def __init__(self, d_in=2, h=2, d_out=1):
        super().__init__()
        self.W1 = nn.Parameter(torch.randn(d_in, h) * 0.5)
        self.W2 = nn.Parameter(torch.randn(h, d_out) * 0.5)

    def forward(self, x):
        # x shape: (batch, d_in)
        return x @ self.W1 @ self.W2

# ----------------------------------------------------------------------
# 2.  Hessian spectral norm (proxy for curvature) w.r.t. all params
# ----------------------------------------------------------------------
def hessian_spectral_norm(net, x, y):
    # Compute loss
    pred = net(x)
    loss = nn.MSELoss()(pred, y)

    # Flatten parameters
    params = [p for p in net.parameters()]
    grads = torch.autograd.grad(loss, params, create_graph=True)
    flat_grad = torch.cat([g.reshape(-1) for g in grads])

    # Hessian‑vector product via double‑backprop (Hv)
    v = torch.randn_like(flat_grad)
    Hv = torch.autograd.grad(flat_grad, params, grad_outputs=v, retain_graph=False)
    Hv_flat = torch.cat([h.reshape(-1) for h in Hv])

    # Approximate spectral norm via power iteration (one step for demo)
    spectral_norm = torch.norm(Hv_flat, p=2) / torch.norm(v, p=2)
    return spectral_norm.item()

# ----------------------------------------------------------------------
# 3.  Parameter‑entropy (naive version: treat |weights| as pmf)
# ----------------------------------------------------------------------
def parameter_entropy(net):
    all_w = []
    for p in net.parameters():
        all_w.append(p.abs().reshape(-1))
    w_cat = torch.cat(all_w)
    w_cat = w_cat / w_cat.sum()
    # avoid log(0)
    w_cat = w_cat + 1e-12
    entropy = -torch.sum(w_cat * torch.log(w_cat)).item()
    return entropy

# ----------------------------------------------------------------------
# 4.  Generalization Fragility Index (GFI) – simplified sigmoid
# ----------------------------------------------------------------------
def compute_gfi(curvature, entropy, alpha=0.1, beta=0.1):
    # GFI = sigmoid(alpha * curvature + beta * (1 - entropy))
    # Lower GFI -> "brittle"
    val = alpha * curvature + beta * (1 - entropy)
    return 1 / (1 + np.exp(-val))

# ----------------------------------------------------------------------
# 5.  Demonstration: gauge attack (scale W1 & W2)
# ----------------------------------------------------------------------
def demo_gauge_attack():
    torch.manual_seed(42)
    net = LinearNet(d_in=2, h=2, d_out=1)

    # Synthetic data
    x = torch.randn(100, 2)
    y = torch.randn(100, 1)

    # Original state
    orig_curv = hessian_spectral_norm(net, x, y)
    orig_ent = parameter_entropy(net)
    orig_gfi = compute_gfi(orig_curv, orig_ent)

    print(f"[ORIGINAL] Curvature: {orig_curv:.4f}, Entropy: {orig_ent:.4f}, GFI: {orig_gfi:.4f}")

    # Gauge transformation: scale W1 by c, W2 by 1/c (c > 1)
    c = 3.0
    with torch.no_grad():
        net.W1.mul_(c)
        net.W2.mul_(1.0 / c)

    # After gauge
    new_curv = hessian_spectral_norm(net, x, y)
    new_ent = parameter_entropy(net)
    new_gfi = compute_gfi(new_curv, new_ent)

    print(f"[POST‑GAUGE] Curvature: {new_curv:.4f}, Entropy: {new_ent:.4f}, GFI: {new_gfi:.4f}")

    # Verify function invariance (prediction difference)
    with torch.no_grad():
        diff = torch.norm(net(x) - (x @ net.W1 @ net.W2)).item()
    print(f"Prediction L2 change after gauge: {diff:.2e} (should be ~0)")

    # Show GFI dropped below typical alert threshold 0.6
    if new_gfi < 0.6:
        print(">>> ALERT: GFI < 0.6 – MPC‑Ω would trigger unnecessary defense!")

if __name__ == "__main__":
    demo_gauge_attack()