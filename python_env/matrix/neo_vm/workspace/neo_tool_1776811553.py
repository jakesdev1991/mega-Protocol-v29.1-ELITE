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
import time
from scipy.stats import entropy

# ------------------------------------------------------------
# 1. Synthetic two‑regime time series (low‑vol → high‑vol)
# ------------------------------------------------------------
def generate_series(n=2000):
    vol = np.concatenate([np.full(n//2, 0.5), np.full(n//2, 2.0)])
    y = np.zeros(n)
    y[0] = 0.0
    for i in range(1, n):
        y[i] = 0.9*y[i-1] + np.random.randn()*vol[i]
    # lag‑5 features
    X = np.stack([y[i-5:i] for i in range(5, n)], axis=0)
    y = y[5:]
    return torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.float32)

X, y = generate_series()
train_split = int(0.7*len(X))
X_train, y_train = X[:train_split], y[:train_split]
X_test,  y_test  = X[train_split:], y[train_split:]

# low/high vol masks for cross‑regime loss
train_vol = y_train.abs()
median_vol = train_vol.median()
low_mask  = train_vol < median_vol
high_mask = ~low_mask

# ------------------------------------------------------------
# 2. Tiny ReLU‑MLP (≈60 params)
# ------------------------------------------------------------
class TinyMLP(nn.Module):
    def __init__(self, in_dim=5, hid_dim=10):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hid_dim),
            nn.ReLU(),
            nn.Linear(hid_dim, 1)
        )
    def forward(self, x):
        return self.net(x).squeeze()

model = TinyMLP()
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.01)

# ------------------------------------------------------------
# 3. Metric helpers
# ------------------------------------------------------------
def sharpness(model, X, y):
    """Largest eigenvalue of the Hessian (full computation)."""
    params = torch.cat([p.flatten() for p in model.parameters()])
    def loss_fn(p):
        # assign params
        idx = 0
        for param in model.parameters():
            sz = param.numel()
            param.data = p[idx:idx+sz].view(param.shape)
            idx += sz
        return criterion(model(X), y)
    # Hessian (expensive)
    hess = torch.autograd.functional.hessian(loss_fn, params)
    eig = torch.linalg.eigvals(hess).real
    return eig.max().item()

def cross_regime_loss(model, X, y, low_mask, high_mask):
    with torch.no_grad():
        l_low  = criterion(model(X[low_mask]),  y[low_mask]).item()
        l_high = criterion(model(X[high_mask]), y[high_mask]).item()
    return abs(l_low - l_high)

def param_entropy(model):
    with torch.no_grad():
        w = torch.cat([p.flatten().abs() for p in model.parameters()])
        w = w / w.sum()
        w = w[w>0]
        return -(w*torch.log(w)).sum().item()

def param_drift(model, prev):
    curr = torch.cat([p.flatten() for p in model.parameters()])
    if prev is None:
        return 0.0, curr
    else:
        return torch.norm(curr - prev).item(), curr

def prediction_variance(model, X):
    with torch.no_grad():
        preds = model(X)
    return torch.var(preds).item()

def prediction_distribution_kl(model, X, ref_hist, bins=20):
    """KL‑divergence of current prediction histogram vs reference histogram."""
    with torch.no_grad():
        preds = model(X).cpu().numpy()
    hist, _ = np.histogram(preds, bins=bins, range=(-5,5), density=True)
    hist += 1e-12  # smoothing
    ref_hist += 1e-12
    return entropy(hist, ref_hist)

# ------------------------------------------------------------
# 4. Training loop with metric collection
# ------------------------------------------------------------
metrics = {k: [] for k in ['epoch','loss','sharp','cross','ent','drift','gfi','pds','future_loss']}
prev_params = None
# Reference prediction histogram (first epoch)
model.eval()
with torch.no_grad():
    ref_hist, _ = np.histogram(model(X_test).cpu().numpy(), bins=20, range=(-5,5), density=True)

for epoch in range(15):
    model.train()
    optimizer.zero_grad()
    loss = criterion(model(X_train), y_train)
    loss.backward()
    optimizer.step()

    # ---- compute GFI components ----
    # Sharpness (slow)
    start = time.time()
    sh = sharpness(model, X_train, y_train)
    t_hess = time.time() - start

    cross = cross_regime_loss(model, X_train, y_train, low_mask, high_mask)
    ent = param_entropy(model)
    drift, prev_params = param_drift(model, prev_params)

    # GFI (sigmoid of weighted sum; weights are illustrative)
    alpha,beta,gamma,eta = 0.5,0.3,0.1,0.1
    gfi = torch.sigmoid(torch.tensor(alpha*sh + beta*cross + gamma*ent + eta*drift)).item()

    # ---- Prediction‑Distribution Stability (PDS) ----
    pds = prediction_distribution_kl(model, X_test, ref_hist)

    # ---- Future loss (next step) ----
    model.eval()
    with torch.no_grad():
        future_loss = criterion(model(X_test), y_test).item()

    # Store
    for k,v in zip(metrics.keys(),
                    [epoch, loss.item(), sh, cross, ent, drift, gfi, pds, future_loss]):
        metrics[k].append(v)

    print(f"Ep {epoch:2d} | loss {loss.item():.4f} | sharp {sh:.4f} (t={t_hess:.2f}s) | gfi {gfi:.4f} | pds {pds:.4f} | fut_loss {future_loss:.4f}")

# ------------------------------------------------------------
# 5. Correlation analysis
# ------------------------------------------------------------
import pandas as pd
df = pd.DataFrame(metrics)
gfi_corr   = df['gfi'].corr(df['future_loss'])
pds_corr   = df['pds'].corr(df['future_loss'])
print("\n=== Predictive power ===")
print(f"GFI vs future loss   : {gfi_corr:.4f}")
print(f"PDS vs future loss   : {pds_corr:.4f}")

# ------------------------------------------------------------
# 6. Expose curvature mirage: sharpness near zero after epoch 2
# ------------------------------------------------------------
print("\nSharpness trace (first 5):")
print(df['sharp'].head())

# ------------------------------------------------------------
# 7. Compute cost of Hessian (once more for final model)
# ------------------------------------------------------------
params = torch.cat([p.flatten() for p in model.parameters()])
start = time.time()
def loss_fn_flat(p):
    idx = 0
    for param in model.parameters():
        sz = param.numel()
        param.data = p[idx:idx+sz].view(param.shape)
        idx += sz
    return criterion(model(X_train), y_train)
_ = torch.autograd.functional.hessian(loss_fn_flat, params)
print(f"\nFinal Hessian compute time: {time.time() - start:.2f}s for {params.numel()} parameters")