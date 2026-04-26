# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validation script for the EDIP‑Ω proposal.
Checks:
  - ESI >= 0 and <= ESI_THRESH (hard clip)
  - Omega invariants: 0 <= Phi_N <= 1, Phi_Delta >= 0, xi_N >= 0, xi_Delta >= 1
  - QP constraints: ESI_k <= 2.5, Phi_N >= 0.75, Phi_Delta <= 0.6
  - Cost function non‑negativity
"""

import torch
import torch.nn as nn
import numpy as np

# ----------------------------
# Hyper‑parameters (as in proposal)
# ----------------------------
ESI_THRESH = 2.5          # hard upper bound used in QP & ReLU penalty
WINDOW_DAYS = 7           # sliding window length (not used directly in synth)
BATCH_SIZE = 4            # number of synthetic documents per facility
DEVICE = torch.device("cpu")

# ----------------------------
# 1. Synthetic feature generation
# ----------------------------
def synth_document_features(n):
    """
    Returns a tensor of shape (n, 5) with columns:
        [Δt_e, r_d, a_d, c_d, H_access]
    All entries are non‑negative by construction.
    """
    # Δt_e : exposure lag (days) – uniform [0, 30]
    dt_e = torch.rand(n, 1) * 30.0
    # r_d : revision intensity (versions/day) – uniform [0, 5]
    r = torch.rand(n, 1) * 5.0
    # a_d : isolation‑forest anomaly score – we mimic with exponential
    a = torch.exp(torch.rand(n, 1) * 3.0)  # >=1
    # c_d : cross‑domain flag – Bernoulli 0.2
    c = (torch.rand(n, 1) < 0.2).float()
    # H_access : Shannon entropy – uniform [0, log(5)] (max 5 countries)
    H = torch.rand(n, 1) * np.log(5.0)
    return torch.cat([dt_e, r, a, c, H], dim=1)  # (n,5)

# ----------------------------
# 2. GRU that outputs ESI (non‑negative)
# ----------------------------
class ESI_GRU(nn.Module):
    def __init__(self, input_size=5, hidden_size=16):
        super().__init__()
        self.gru = nn.GRU(input_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)
        self.softplus = nn.Softplus()   # ensures >=0

    def forward(self, x):
        """
        x: (batch, seq_len, features) – we treat each document as a time‑step.
        For simplicity we feed the whole window as a sequence of length = n_docs.
        """
        out, _ = self.gru(x)          # out: (batch, seq_len, hidden)
        # Use the last hidden state as the window summary
        last = out[:, -1, :]          # (batch, hidden)
        esi_raw = self.fc(last)       # (batch,1)
        return self.softplus(esi_raw) # non‑negative ESI

# ----------------------------
# 3. PINN that maps ESI + plasma params → Ω variables
#    Output activations enforce the Ω Rubric.
# ----------------------------
class Omega_PINN(nn.Module):
    def __init__(self, esi_dim=1, plasma_dim=4):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(esi_dim + plasma_dim, 32),
            nn.Tanh(),
            nn.Linear(32, 32),
            nn.Tanh(),
            nn.Linear(32, 4)   # raw outputs before activation
        )
        # Activations:
        #   Phi_N   : sigmoid -> [0,1]
        #   Phi_Delta: softplus -> [0,∞)
        #   xi_N    : softplus -> [0,∞)
        #   xi_Delta: 1 + softplus -> [1,∞)

    def forward(self, esi, plasma):
        """
        esi:   (batch,1)   – ESI_k(t‑τ)
        plasma:(batch,4)   – dummy plasma parameters (β_N, li, etc.)
        returns: (batch,4)   [Phi_N, Phi_Delta, xi_N, xi_Delta]
        """
        x = torch.cat([esi, plasma], dim=1)
        raw = self.net(x)
        phi_n   = torch.sigmoid(raw[:,0:1])          # [0,1]
        phi_d   = nn.functional.softplus(raw[:,1:2]) # [0,∞)
        xi_n    = nn.functional.softplus(raw[:,2:3]) # [0,∞)
        xi_d    = 1.0 + nn.functional.softplus(raw[:,3:4]) # [1,∞)
        return torch.cat([phi_n, phi_d, xi_n, xi_d], dim=1)

# ----------------------------
# 4. Helper: compute cost integrand (non‑negative check)
# ----------------------------
def cost_integrand(phi_n, phi_d, xi_n, xi_d, esi, s_esi,
                   alpha=0.1, lam=0.5, beta=0.2, gamma=0.3):
    """
    Returns scalar >=0 for a single time‑step.
    Uses the formulation from the proposal:
        (1‑S_j)^2 + α S_h + λ(P_meas‑P_target)^2 + β(ξ_Δ‑1)^2 + γ·ReLU(ESI‑ESI_thresh)
    We replace the plasma‑specific terms with dummy non‑negative placeholders.
    """
    # Dummy placeholders (all >=0)
    one_minus_Sj_sq = torch.tensor(0.1)   # (1‑S_j)^2
    S_h = torch.tensor(0.05)              # entropy ≥0
    power_err_sq = torch.tensor(0.02)     # (P_meas‑P_target)^2 ≥0

    term1 = one_minus_Sj_sq
    term2 = alpha * S_h
    term3 = lam * power_err_sq
    term4 = beta * torch.clamp(xi_d - 1.0, min=0.0)**2   # (ξ_Δ‑1)^2, ξ_Δ≥1 from PINN
    term5 = gamma * torch.nn.functional.relu(esi - ESI_THRESH)

    return term1 + term2 + term3 + term4 + term5

# ----------------------------
# 5. Validation routine
# ----------------------------
def validate():
    torch.manual_seed(0)
    np.random.seed(0)

    # Simulate one facility with a window of N documents
    N_docs = BATCH_SIZE
    feats = synth_document_features(N_docs)          # (N,5)

    # Build a sequence for the GRU: treat each doc as a time‑step
    seq = feats.unsqueeze(0)                         # (1, N, 5)

    esi_model = ESI_GRU()
    esi = esi_model(seq)                             # (1,1) >=0
    # Hard clip to respect the QP bound (optional but safe)
    esi_clipped = torch.clamp(esi, max=ESI_THRESH)

    # Dummy plasma parameters (4‑dim) – all non‑negative for simplicity
    plasma = torch.abs(torch.randn(1, 4))            # (1,4)

    pinn = Omega_PINN()
    omega_vars = pinn(esi_clipped, plasma)          # (1,4)
    phi_n, phi_d, xi_n, xi_d = omega_vars.unbind(dim=1)

    # Anomaly score (dummy)
    s_esi = torch.tensor([[1.8]])   # < threshold, but we also test a high case

    # ----------------------------
    # Invariant checks
    # ----------------------------
    # ESI bounds
    assert torch.all(esi_clipped >= 0.0), "ESI negative"
    assert torch.all(esi_clipped <= ESI_THRESH), f"ESI > threshold ({ESI_THRESH})"

    # Omega Rubric (from proposal)
    assert torch.all((phi_n >= 0.0) & (phi_n <= 1.0)), f"Phi_N out of [0,1]: {phi_n}"
    assert torch.all(phi_d >= 0.0), f"Phi_Delta negative: {phi_d}"
    assert torch.all(xi_n >= 0.0), f"xi_N negative: {xi_n}"
    assert torch.all(xi_d >= 1.0), f"xi_Delta < 1: {xi_d}"

    # QP constraints (hard bounds used in controller)
    assert torch.all(esi_clipped <= ESI_THRESH), "QP: ESI_k > 2.5"
    assert torch.all(phi_n >= 0.75), f"QP: Phi_N < 0.75: {phi_n}"
    assert torch.all(phi_d <= 0.6), f"QP: Phi_Delta > 0.6: {phi_d}"

    # Cost non‑negativity
    cost = cost_integrand(phi_n, phi_d, xi_n, xi_d, esi_clipped, s_esi)
    assert cost >= 0.0, f"Cost integrand negative: {cost}"

    print("✅ All invariants and constraints satisfied.")
    print(f"ESI = {esi_clipped.item():.3f}")
    print(f"Phi_N = {phi_n.item():.3f}, Phi_Delta = {phi_d.item():.3f}")
    print(f"xi_N = {xi_n.item():.3f}, xi_Delta = {xi_d.item():.3f}")
    print(f"Anomaly score s_ESI = {s_esi.item():.3f}")
    print(f"Cost integrand = {cost.item():.3f}")

    # Additional stress test: force high ESI to see if penalty fires
    print("\n--- Stress test: high ESI ---")
    high_esi = torch.tensor([[3.0]])   # above threshold
    cost_high = cost_integrand(high_esi, phi_n, phi_d, xi_n, xi_d,
                               s_esi=torch.tensor([[2.6]]))  # also high anomaly
    print(f"Cost with ESI=3.0, s_ESI=2.6 -> {cost_high.item():.3f} (should be > baseline)")

if __name__ == "__main__":
    validate()