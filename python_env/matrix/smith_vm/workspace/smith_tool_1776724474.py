# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# --------------------------------------------------------------
# Omega Protocol Invariant Validator for EDIP‑Ω (Exposure‑Driven
# Instability Precursor Detection)
# --------------------------------------------------------------
# This script assumes the following symbols are defined elsewhere:
#   Φ_N, Φ_Δ, ξ_N, ξ_Δ, ψ, ESI, S_h, S_h_target, Φ0 (baseline)
#   t_e, t_m, t_c : timestamps (seconds since epoch)
#   n_vers       : number of document versions
#   dl_cnt       : download count
#   uniq_ip      : number of unique IPs
#   geo_ent      : entropy of geographic distribution (>=0)
#   cross_flag   : binary flag (0/1) for cross‑domain stablecoin doc
#   H            : MPC horizon (seconds)
#   dt           : control timestep (seconds)
#   alpha,beta,gamma,delta,lambda_,eta1,eta2,theta,tau1,tau2 : scalar params
#   ESI_thresh   : scalar threshold for QP/penalty (e.g., 2.5)
#   xi_delta_min : 1.0 (rubric)
#   phi_n_min, phi_n_max : 0.0, 1.0
#   phi_delta_min : 0.0
#   xi_n_min      : >0 (we enforce >0)
# --------------------------------------------------------------

import numpy as np
import torch
import torch.nn as nn
from typing import List, Tuple

# ------------------------------------------------------------------
# Helper: deterministic sequence builder for GRU input
# ------------------------------------------------------------------
def build_esi_sequence(events: List[dict], window_days: int = 7) -> torch.Tensor:
    """
    events: list of dicts, each representing one exposed document.
            Required keys:
                't_e'   : exposure detection time (float, seconds)
                't_m'   : last modification time
                'n_vers': int
                'dl_cnt': int
                'uniq_ip': int
                'geo_ent': float >=0
                'cross_flag': 0 or 1
    Returns:
        Tensor of shape (seq_len, feature_dim) ready for GRU.
    """
    now = max(e['t_e'] for e in events)  # use latest exposure as "now"
    # keep only events within the last `window_days`
    cutoff = now - window_days * 86400
    window_events = [e for e in events if e['t_e'] >= cutoff]

    if not window_events:
        # Return a zero‑vector of correct dimension so GRU still runs
        return torch.zeros(1, 5)  # [Δt_e, r_d, a_d, c_d, H_access]

    # 1️⃣ Compute per‑document features
    feats = []
    for e in window_events:
        delta_t = e['t_e'] - e['t_m']                     # exposure lag
        # avoid division by zero; if t_m == t_c set denom to 1 sec
        denom = max(1.0, e['t_m'] - e.get('t_c', e['t_m'] - 1.0))
        r_d = e['n_vers'] / denom                         # revision intensity (versions/day)
        # placeholder anomaly score – in practice use pretrained IsolationForest
        a_d = np.tanh(0.1 * e['dl_cnt'] + 0.05 * e['uniq_ip'] + 0.2 * e['geo_ent'])
        c_d = float(e['cross_flag'])
        # access entropy contribution (already computed)
        H_access = e['geo_ent']
        feats.append([delta_t, r_d, a_d, c_d, H_access])

    # 2️⃣ Sort chronologically by exposure time (t_e) → deterministic sequence
    feats_sorted = [f for _, f in sorted(zip([e['t_e'] for e in window_events], feats),
                                        key=lambda pair: pair[0])]
    return torch.tensor(feats_sorted, dtype=torch.float32)   # (seq_len, 5)


# ------------------------------------------------------------------
# GRU‑based ESI model (learned temporal aggregator)
# ------------------------------------------------------------------
class ESI_GRU(nn.Module):
    def __init__(self, input_size=5, hidden_size=16, num_layers=1):
        super().__init__()
        self.gru = nn.GRU(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)   # output scalar ESI

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (batch, seq_len, input_size)
        out, _ = self.gru(x)                  # out: (batch, seq_len, hidden)
        # we use the last hidden state (many‑to‑one)
        last = out[:, -1, :]                  # (batch, hidden)
        esi = self.fc(last)                   # (batch, 1)
        return esi.squeeze(-1)                # (batch,)


# ------------------------------------------------------------------
# Physics‑Informed Neural Network (PINN) mapping ESI → Omega invariants
# ------------------------------------------------------------------
class OmegaPINN(nn.Module):
    """
    Input:  [ESI, normalized_beta, internal_inductance, ...]  (any plasma diagnostics)
    Output: [Φ_N, Φ_Δ, ξ_N, ξ_Δ]  (all constrained to rubric)
    """
    def __init__(self, input_dim=4, hidden=32):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden),
            nn.Tanh(),
            nn.Linear(hidden, hidden),
            nn.Tanh(),
            nn.Linear(hidden, 4)   # raw outputs before activation
        )
        # Activation enforcers:
        #   Φ_N  -> sigmoid  (0,1)
        #   Φ_Δ  -> softplus (>=0)
        #   ξ_N  -> softplus + epsilon (>0)
        #   ξ_Δ  -> softplus + 1 (>=1)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor,
                                               torch.Tensor, torch.Tensor]:
        raw = self.net(x)                     # (batch,4)
        phi_N   = torch.sigmoid(raw[:,0])                     # (0,1)
        phi_D   = torch.nn.functional.softplus(raw[:,1])      # >=0
        xi_N    = torch.nn.functional.softplus(raw[:,2]) + 1e-6  # >0
        xi_D    = torch.nn.functional.softplus(raw[:,3]) + 1.0   # >=1
        return phi_N, phi_D, xi_N, xi_D


# ------------------------------------------------------------------
# Cost‑function integrand (fixed version)
# ------------------------------------------------------------------
def running_cost(phi_N: float, phi_D: float, xi_N: float, xi_D: float,
                 S_h: float, S_h_target: float,
                 P_meas: float, P_target: float,
                 ESI: float, ESI_thresh: float,
                 alpha: float, beta: float, lam: float,
                 gamma: float) -> float:
    """
    L = (1 - S_h)^2   <-- corrected to (S_h - S_h_target)^2
        + α * S_h
        + λ * (P_meas - P_target)^2
        + β * (ξ_Δ - 1)^2
        + γ * ReLU(ESI - ESI_thresh)
    """
    term1 = (S_h - S_h_target) ** 2
    term2 = alpha * S_h
    term3 = lam * (P_meas - P_target) ** 2
    term4 = beta * (xi_D - 1.0) ** 2
    term5 = gamma * max(0.0, ESI - ESI_thresh)
    return term1 + term2 + term3 + term4 + term5


# ------------------------------------------------------------------
# QP constraint checker (simple bound verification)
# ------------------------------------------------------------------
def qp_constraints_ok(phi_N: float, phi_D: float, xi_D: float,
                      ESI: float, ESI_thresh: float = 2.5) -> bool:
    """Return True if all hard constraints satisfied."""
    conds = [
        phi_N >= 0.0 and phi_N <= 1.0,          # Φ_N ∈ [0,1]
        phi_D >= 0.0,                           # Φ_Δ ≥ 0 (rubric)
        xi_D >= 1.0,                            # ξ_Δ ≥ 1
        ESI <= ESI_thresh                       # ESI_k ≤ threshold (from QP)
    ]
    return all(conds)


# ------------------------------------------------------------------
# Monte‑Carlo sanity‑check
# ------------------------------------------------------------------
def mc_validation(num_samples: int = 10_000,
                  seed: int = 42) -> None:
    np.random.seed(seed)
    torch.manual_seed(seed)

    # Dummy pretrained models (in practice load weights)
    esi_model = ESI_GRU()
    pinn_model = OmegaPINN()

    # Plausible ranges for random draws
    phi0 = 0.8                         # baseline Φ_N
    for i in range(num_samples):
        # --- Random plasma diagnostics ---------------------------------
        beta_norm   = np.random.uniform(0.0, 0.4)   # normalized beta
        li          = np.random.uniform(0.5, 1.2)   # internal inductance
        # --- Random ESI input features (to feed GRU) -------------------
        # Simulate a small batch of exposure events (seq_len 1‑5)
        seq_len = np.random.randint(1, 6)
        dummy_events = []
        for _ in range(seq_len):
            t_c = np.random.uniform(0, 1e9)
            t_m = t_c + np.random.uniform(0, 1e7)
            t_e = t_m + np.random.uniform(0, 5e6)   # exposure after modification
            dummy_events.append({
                't_c': t_c,
                't_m': t_m,
                't_e': t_e,
                'n_vers': np.random.randint(1, 10),
                'dl_cnt': np.random.randint(0, 100),
                'uniq_ip': np.random.randint(0, 20),
                'geo_ent': np.random.uniform(0, np.log(10)),  # entropy max ~log(countries)
                'cross_flag': np.random.randint(0, 2)
            })
        esi_seq = build_esi_sequence(dummy_events, window_days=7)   # (seq_len,5)
        esi_seq = esi_seq.unsqueeze(0)                              # (1,seq_len,5)
        esi_val = float(esi_model(esi_seq).detach().numpy())       # scalar

        # --- Random plasma‑parameter vector for PINN -------------------
        plasma_vec = np.array([esi_val, beta_norm, li, 0.0])  # extend as needed
        plasma_tensor = torch.tensor(plasma_vec, dtype=torch.float32).unsqueeze(0)
        phi_N, phi_D, xi_N, xi_D = pinn_model(plasma_tensor)
        phi_N, phi_D, xi_N, xi_D = map(lambda t: t.item(),
                                       (phi_N, phi_D, xi_N, xi_D))

        # --- Derived quantities ----------------------------------------
        # ψ = ln(Φ_N / Φ0)  → requires Φ_N > 0
        assert phi_N > 0.0, f"Φ_N non‑positive: {phi_N}"
        psi = np.log(phi_N / phi0)

        # --- Entropy placeholder ---------------------------------------
        S_h = np.random.uniform(0.0, 2.0)   # Shannon entropy of coherence dist.
        S_h_target = 1.0                    # example target

        # --- Random actuator measurements ------------------------------
        P_meas = np.random.uniform(0.8, 1.2) * 1.0   # assume P_target = 1.0
        P_target = 1.0

        # --- Hyper‑parameters (example values) -------------------------
        alpha, beta_, lam, gamma = 0.1, 0.2, 0.5, 0.3
        ESI_thresh = 2.5

        # --- Invariant checks -------------------------------------------
        assert 0.0 <= phi_N <= 1.0, f"Φ_N out of bounds: {phi_N}"
        assert phi_D >= 0.0, f"Φ_Δ negative: {phi_D}"
        assert xi_N > 0.0, f"ξ_N non‑positive: {xi_N}"
        assert xi_D >= 1.0, f"ξ_Δ < 1: {xi_D}"
        # ψ is real by construction (phi_N>0)
        # --- Cost function must be finite --------------------------------
        cost = running_cost(phi_N.item(), phi_D.item(), xi_N.item(), xi_D.item(),
                            S_h, S_h_target,
                            P_meas, P_target,
                            esi_val, ESI_thresh,
                            alpha, beta_, lam, gamma)
        assert np.isfinite(cost), f"Cost non‑finite: {cost}"

        # --- QP constraints ---------------------------------------------
        assert qp_constraints_ok(phi_N.item(), phi_D.item(), xi_D.item(),
                                 esi_val, ESI_thresh), \
            f"QP violation: Φ_N={phi_N}, Φ_Δ={phi_D}, ξ_Δ={xi_D}, ESI={esi_val}"

    print(f"Monte‑Carlo validation passed for {num_samples} random samples.")


# ------------------------------------------------------------------
# Run the validator
# ------------------------------------------------------------------
if __name__ == "__main__":
    mc_validation()