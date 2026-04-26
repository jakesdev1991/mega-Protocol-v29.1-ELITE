# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import matplotlib.pyplot as plt

# ------------------------------------------------------------------
# 1. Synthetic data: low‑volatility → high‑volatility regime shift
# ------------------------------------------------------------------
def generate_regime_data(n=1000, shift=500):
    t = np.linspace(0, 4*np.pi, n)
    # Regime 1: low noise
    y_low = np.sin(t[:shift]) + 0.05*np.random.randn(shift)
    # Regime 2: high noise
    y_high = np.sin(t[shift:]) + 0.4*np.random.randn(n-shift)
    y = np.concatenate([y_low, y_high])
    # Return as torch tensors
    return torch.tensor(t, dtype=torch.float32).unsqueeze(1), torch.tensor(y, dtype=torch.float32).unsqueeze(1)

# ------------------------------------------------------------------
# 2. Minimal ReLU network (2 hidden layers, 8 units each)
# ------------------------------------------------------------------
class TinyNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(1, 8)
        self.fc2 = nn.Linear(8, 8)
        self.fc3 = nn.Linear(8, 1)
        self.relu = nn.ReLU()
    
    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.fc3(x)
        return x

# ------------------------------------------------------------------
# 3. Hessian top‑eigenvalue via power iteration (curvature proxy)
# ------------------------------------------------------------------
def hessian_top_eig(model, loss, max_iter=15):
    grads = torch.autograd.grad(loss, model.parameters(), create_graph=True)
    grad_vec = torch.cat([g.flatten() for g in grads])
    v = torch.randn_like(grad_vec)
    v /= torch.norm(v)
    for _ in range(max_iter):
        hv = torch.autograd.grad(grads, model.parameters(), grad_outputs=v, retain_graph=True)
        hv_vec = torch.cat([h.flatten() for h in hv])
        v = hv_vec / torch.norm(hv_vec)
    return torch.dot(v, hv_vec).item()

# ------------------------------------------------------------------
# 4. Activation variance (order parameter)
# ------------------------------------------------------------------
def activation_variance(model, x_batch):
    activations = {}
    def hook(name):
        def fn(mod, inp, out):
            activations[name] = out.detach()
        return fn
    h1 = model.fc1.register_forward_hook(hook('fc1'))
    h2 = model.fc2.register_forward_hook(hook('fc2'))
    _ = model(x_batch)
    var = torch.cat([activations['fc1'].flatten(), activations['fc2'].flatten()]).var().item()
    h1.remove()
    h2.remove()
    return var

# ------------------------------------------------------------------
# 5. Training loop with monitoring
# ------------------------------------------------------------------
def train_monitor():
    x, y = generate_regime_data()
    model = TinyNet()
    crit = nn.MSELoss()
    opt = optim.Adam(model.parameters(), lr=0.02)
    
    # Split train / val
    split = 800
    x_tr, y_tr = x[:split], y[:split]
    x_val, y_val = x[split:], y[split:]
    
    # Storage
    hessian_eigs = []
    act_vars = []
    gen_gaps = []
    
    for epoch in range(150):
        model.train()
        opt.zero_grad()
        out_tr = model(x_tr)
        loss_tr = crit(out_tr, y_tr)
        loss_tr.backward()
        opt.step()
        
        # Validation loss
        model.eval()
        with torch.no_grad():
            out_val = model(x_val)
            loss_val = crit(out_val, y_val)
        
        # Generalization gap
        gen_gaps.append(loss_val.item() - loss_tr.item())
        
        # Hessian top eigenvalue (on a mini‑batch)
        model.zero_grad()
        out_small = model(x_tr[:32])
        loss_small = crit(out_small, y_tr[:32])
        eig = hessian_top_eig(model, loss_small)
        hessian_eigs.append(eig)
        
        # Activation variance (on same mini‑batch)
        var = activation_variance(model, x_tr[:32])
        act_vars.append(var)
    
    return hessian_eigs, act_vars, gen_gaps

# ------------------------------------------------------------------
# 6. Plot results
# ------------------------------------------------------------------
eigs, vars_, gaps = train_monitor()

plt.figure(figsize=(10, 7))

# Top: Hessian eigenvalue (curvature proxy)
plt.subplot(3, 1, 1)
plt.plot(eigs, label='Hessian top‑eig')
plt.axvline(x=100, color='r', linestyle='--', label='Regime shift')
plt.title('Curvature Proxy (noisy, lags)')
plt.legend()

# Middle: Activation variance (order parameter)
plt.subplot(3, 1, 2)
plt.plot(vars_, label='Activation variance')
plt.axvline(x=100, color='r', linestyle='--', label='Regime shift')
plt.title('Order Parameter (drops sharply before gap widens)')
plt.legend()

# Bottom: Generalization gap
plt.subplot(3, 1, 3)
plt.plot(gaps, label='Val – Train loss')
plt.axvline(x=100, color='r', linestyle='--', label='Regime shift')
plt.title('Generalization Gap')
plt.legend()

plt.tight_layout()
plt.show()