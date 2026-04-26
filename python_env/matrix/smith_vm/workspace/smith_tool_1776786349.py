# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Ω‑Embedded Architecture (ΩEA) invariant validator.
Agent Smith: audits mathematical soundness and Omega‑Protocol compliance.
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from scipy.optimize import curve_fit

# ----------------------------
# Helper functions (NumPy for clarity)
# ----------------------------
def local_modes(phi, W, radius=1):
    """
    Compute Φ_N^{(i)} and Φ_Δ^{(i)} for each neuron i.
    phi: (N,) activation vector
    W:   (N,N) weight matrix (non‑negative, symmetric)
    radius: neighbourhood radius (in hops) – we use 1‑hop for simplicity.
    Returns: Phi_N (N,), Phi_Delta (N,)
    """
    N = phi.shape[0]
    Phi_N = np.zeros(N)
    Phi_Delta = np.zeros(N)

    # Pre‑compute adjacency list for 1‑hop neighbourhood
    neigh = [np.where(W[i] > 0)[0] for i in range(N)]

    for i in range(N):
        nb = neigh[i]
        if len(nb) == 0:
            Phi_N[i] = phi[i]
            Phi_Delta[i] = 0.0
            continue
        # Φ_N = mean activation in neighbourhood (including self?)
        Phi_N[i] = np.mean(phi[nb])
        # Φ_Delta = weighted asymmetry
        w_nb = W[i, nb]
        diff = phi[nb] - Phi_N[i]
        Phi_Delta[i] = np.sum(w_nb * diff) / (np.sum(w_nb) + 1e-12)
    return Phi_N, Phi_Delta

def correlation_length(phi, W):
    """
    Estimate ξ from the two‑point function G(d) = <φ_i φ_j> averaged over pairs at graph distance d.
    Returns ξ (float) and ξ0 (reference length from stiffnesses, see below).
    """
    N = phi.shape[0]
    # Compute shortest‑path distances (Floyd‑Warshall for tiny graphs)
    dist = np.full((N, N), np.inf)
    np.fill_diagonal(dist, 0)
    dist[W > 0] = 1
    for k in range(N):
        for i in range(N):
            for j in range(N):
                if dist[i, k] + dist[k, j] < dist[i, j]:
                    dist[i, j] = dist[i, k] + dist[k, j]

    # Mask infinite distances (disconnected components) – ignore them
    mask = np.isfinite(dist)
    # Upper triangle to avoid double counting
    iu = np.triu_indices(N, k=1)
    dist_vec = dist[iu][mask[iu]]
    prod_vec = (phi[:, None] * phi[None, :])[iu][mask[iu]]

    # Bin by distance
    max_d = int(np.nanmax(dist_vec)) if len(dist_vec) > 0 else 0
    if max_d < 1:
        return 1.0, 1.0   # fallback
    G_bins = []
    d_bins = []
    for d in range(1, max_d + 1):
        sel = dist_vec == d
        if np.any(sel):
            G_bins.append(np.mean(prod_vec[sel]))
            d_bins.append(d)
    G_bins = np.array(G_bins)
    d_bins = np.array(d_bins)

    # Exponential fit: G(d) ≈ A * exp(-d/ξ)
    def exp_decay(d, A, xi):
        return A * np.exp(-d / xi)
    try:
        popt, _ = curve_fit(exp_decay, d_bins, G_bins,
                            p0=[G_bins[0], 2.0],
                            bounds=(0, [np.inf, np.inf]))
        xi = popt[1]
    except Exception:
        # If fit fails, use inverse of average gradient as a rough proxy
        xi = 1.0 / (np.mean(np.abs(np.diff(G_bins))) + 1e-12)
    return max(xi, 1e-6)

def stiffness_invariants(Phi_N, Phi_Delta, Phi_N_star, Phi_Delta_star, lam=1.0):
    """
    Return ξ_N^{-2} and ξ_Δ^{-2} as second derivatives of a quadratic penalty
    around the target modes. For a simple quadratic V_eff = ½ lam (Φ-Φ*)^2,
    the second derivative is just lam.
    """
    xi_N_inv2 = lam
    xi_Delta_inv2 = lam
    return xi_N_inv2, xi_Delta_inv2

def compute_xi0(Phi_N, Phi_Delta, lam=1.0):
    """
    Reference length ξ0 = (1/N) Σ_i 1/√(ξ_N^{-2}+ξ_Δ^{-2})
    With the simple quadratic choice ξ_N^{-2}=ξ_Δ^{-2}=lam,
    ξ0 = 1/√(2*lam).
    """
    xi_N_inv2, xi_Delta_inv2 = stiffness_invariants(Phi_N, Phi_Delta,
                                                    Phi_N_star=0.0,
                                                    Phi_Delta_star=0.0,
                                                    lam=lam)
    inv_sum = np.sqrt(xi_N_inv2 + xi_Delta_inv2)
    xi0 = np.mean(1.0 / inv_sum)
    return xi0

# ----------------------------
# Tiny ΩEA model (PyTorch)
# ----------------------------
class OmegaNeuronLayer(nn.Module):
    """
    A single Ω‑Neuron layer:
    - linear transformation with learnable weight matrix W (symmetrized)
    - activation φ = tanh(preact)  (bounded, helps stability)
    - computes local modes and Ω‑loss internally.
    """
    def __init__(self, in_features, out_features, radius=1, lam=1.0):
        super().__init__()
        self.W = nn.Parameter(torch.randn(out_features, in_features) * 0.1)
        self.radius = radius
        self.lam = lam
        self.target_N = 0.0   # Φ_N*
        self.target_D = 0.0   # Φ_Δ*

    def forward(self, x):
        # Linear map (no bias for simplicity)
        pre = x @ self.W.t()          # (B, out_features)
        phi = torch.tanh(pre)         # activation field
        # Convert to numpy for mode computation (detach)
        phi_np = phi.detach().cpu().numpy()
        W_np = self.W.detach().cpu().numpy()
        # Symmetrize W for Laplacian interpretation
        W_sym = 0.5 * (W_np + W_np.T)
        # Compute local modes
        Phi_N, Phi_Delta = local_modes(phi_np.mean(axis=0), W_sym, radius=self.radius)
        # Compute Ω‑loss (quadratic penalty)
        xi_N_inv2, xi_Delta_inv2 = stiffness_invariants(Phi_N, Phi_Delta,
                                                        self.target_N, self.target_D,
                                                        lam=self.lam)
        loss_omega = 0.5 * np.sum(xi_N_inv2 * (Phi_N - self.target_N)**2 +
                                  xi_Delta_inv2 * (Phi_Delta - self.target_D)**2)
        loss_omega = torch.tensor(loss_omega, dtype=phi.device, requires_grad=False)
        # Return activations and the loss for later inclusion in total loss
        return phi, loss_omega, Phi_N, Phi_Delta

class OmegaEA(nn.Module):
    def __init__(self, layer_sizes, radius=1, lam=1.0):
        super().__init__()
        self.layers = nn.ModuleList([
            OmegaNeuronLayer(layer_sizes[i], layer_sizes[i+1],
                             radius=radius, lam=lam)
            for i in range(len(layer_sizes)-1)
        ])

    def forward(self, x):
        losses = []
        all_Phi_N = []
        all_Phi_Delta = []
        for layer in self.layers:
            x, loss_omega, Phi_N, Phi_Delta = layer(x)
            losses.append(loss_omega)
            all_Phi_N.append(Phi_N)
            all_Phi_Delta.append(Phi_Delta)
        # Dummy task loss: mean squared output (just to have grads)
        task_loss = torch.mean(x**2)
        total_loss = task_loss + torch.stack(losses).sum()
        return total_loss, task_loss, torch.stack(losses).sum(), \
               np.concatenate(all_Phi_N), np.concatenate(all_Phi_Delta)

# ----------------------------
# Validation loop
# ----------------------------
def validate_OmegaEA(num_steps=20, batch_size=4, input_dim=8, hidden_dim=8, output_dim=8):
    torch.manual_seed(0)
    np.random.seed(0)

    model = OmegaEA([input_dim, hidden_dim, output_dim], radius=1, lam=1.0)
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)

    for step in range(num_steps):
        # Random input batch
        x = torch.randn(batch_size, input_dim)
        optimizer.zero_grad()
        loss, task, omega, Phi_N_vec, Phi_Delta_vec = model(x)
        loss.backward()
        optimizer.step()

        # ---- Invariant checks per layer ----
        # Re‑compute modes with the *current* weights (detached)
        with torch.no_grad():
            # Forward pass again to get activations
            acts = []
            cur = x
            for layer in model.layers:
                pre = cur @ layer.W.t()
                cur = torch.tanh(pre)
                acts.append(cur.numpy())
            acts = np.array(acts)   # shape (L, B, out_features)

            # For each layer compute global Φ_N, Φ_Δ, ξ, ψ
            for l, act in enumerate(acts):
                # Average over batch and neurons to get a representative field
                phi_mean = act.mean(axis=0)   # (out_features,)
                W_sym = 0.5 * (layer.W.detach().cpu().numpy() +
                               layer.W.detach().cpu().numpy().T)
                Phi_N, Phi_Delta = local_modes(phi_mean, W_sym, radius=1)

                # Global averages (scalar per layer)
                Phi_N_glob = Phi_N.mean()
                Phi_Delta_glob = np.mean(np.abs(Phi_Delta))

                # Stiffness invariants (using same lam as in layer)
                xi_N_inv2, xi_Delta_inv2 = stiffness_invariants(Phi_N, Phi_Delta,
                                                                layer.target_N,
                                                                layer.target_D,
                                                                lam=layer.lam)
                xi0 = compute_xi0(Phi_N, Phi_Delta, lam=layer.lam)

                # Correlation length from the *batch* activations (flatten batch+neurons)
                phi_flat = act.reshape(-1)   # (B*out_features,)
                # Build a fully‑connected weight matrix for correlation estimation:
                # we reuse the same symmetric W_sym as a proxy for interaction structure.
                xi = correlation_length(phi_flat, W_sym)

                psi = np.log(xi / xi0) if xi0 > 0 else 0.0

                # ---- Omega Protocol invariant bounds ----
                # Shredding: ψ > 2 ; Freeze: ψ < -2
                assert psi < 2.0, f"[Step {step} Layer {l}] Shredding risk: ψ={psi:.3f}"
                assert psi > -2.0, f"[Step {step} Layer {l}] Freeze risk: ψ={psi:.3f}"
                # Optional tighter MPC‑Ω bounds (±1.5) – we warn but do not fail
                if abs(psi) > 1.5:
                    print(f"[Warning] Step {step} Layer {l} ψ={psi:.3f} outside MPC‑Ω target [-1.5,1.5]")
                # Asymmetry bound (example critical value)
                Phi_Delta_crit = 0.5
                assert Phi_Delta_glob <= Phi_Delta_crit, \
                    f"[Step {step} Layer {l}] Asymmetry too high: ΦΔ={Phi_Delta_glob:.3f}"

        if step % 5 == 0:
            print(f"Step {step:02d} | total loss={loss.item():.4f} | task={task.item():.4f} | Ω‑loss={omega.item():.4f}")

    print("\n✅ All Omega‑Protocol invariants satisfied for the tested trajectory.")
    return True

# Run the validation (will raise AssertionError if any invariant violated)
if __name__ == "__main__":
    validate_OmegaEA(num_steps=30, batch_size=8, input_dim=16, hidden_dim=16, output_dim=16)