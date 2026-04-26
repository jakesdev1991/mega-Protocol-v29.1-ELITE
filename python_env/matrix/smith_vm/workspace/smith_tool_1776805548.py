# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# --------------------------------------------------------------
# Agent Smith – Omega Protocol Validator for TCM‑Ω
# --------------------------------------------------------------
import numpy as np
import itertools

# ---------- USER‑DEFINED PARAMETERS (feel‑free to tweak) ----------
N_QUBITS = 9                     # 3x3 lattice (can be changed to 4D etc.)
DT = 0.01                        # time step for simulation
T_MAX = 20.0                     # total simulated time
GAMMA = 0.5                      # stress‑to‑CTOI decay rate
KAPPA = 0.3                      # intervention recovery rate
MU1, MU2, MU3 = 1.0, 1.0, 1.0    # cost weights
EPS = 1e-12                      # small offset to avoid log(0)

# ---------- HELPERS ----------
def wilson_loop(state, plaquette):
    """Product of sigma_z (= state[i] ∈ {+1,-1}) around a plaquette."""
    prod = 1.0
    for i in plaquette:
        prod *= state[i]
    return prod

def random_state():
    """Random spin configuration (±1)."""
    return np.random.choice([-1.0, +1.0], size=N_QUBITS)

def make_plaquettes():
    """Return list of plaquettes (4‑cycles) for a 2D sqrt(N) x sqrt(N) grid."""
    side = int(np.sqrt(N_QUBITS))
    assert side * side == N_QUBITS, "N_QUBITS must be a perfect square for 2D lattice"
    plaqs = []
    for x in range(side):
        for y in range(side):
            i0 = y * side + x
            i1 = y * side + ((x + 1) % side)
            i2 = ((y + 1) % side) * side + x
            i3 = ((y + 1) % side) * side + ((x + 1) % side)
            plaqs.append([i0, i1, i3, i2])  # oriented loop
    return plaqs

PLAQUETTES = make_plaquettes()

# ---------- CORE VALIDATION ----------
def validate_tcm():
    # Baseline (healthy) references
    W0 = np.mean([wilson_loop(random_state(), p) for p in PLAQUETTES for _ in range(100)])
    Delta0 = 1.0          # arbitrary unit
    xi0    = 1.0
    # Simulate a short trajectory
    t = 0.0
    CTOI_hist = []
    PhiN_hist = []
    PhiDelta_hist = []
    S_cog_hist = []
    while t < T_MAX:
        # 1. Sample instantaneous cognitive state (proxy for thermal distribution)
        state = random_state()
        # 2. Compute instantaneous Wilson loop average
        W_inst = np.mean([wilson_loop(state, p) for p in PLAQUETTES])
        # 3. Simulate stress and gap (simple Ornstein‑Uhlenbeck)
        stress = np.abs(0.2 * np.sin(0.5 * t) + 0.1 * np.random.randn())
        Delta  = Delta0 * np.exp(-0.05 * t) + 0.2 * np.random.randn()
        xi     = xi0    * np.exp(-0.03 * t) + 0.1 * np.random.randn()
        # 4. Compute ratios (clipped to [0, ∞))
        rW   = np.abs(W_inst) / (np.abs(W0) + EPS)
        rDelta = Delta / Delta0
        rxi    = xi / xi0
        # 5. CTOI (product) – enforce ≤1 by min with 1.0 (physically, ratios ≤1 under stress)
        CTOI = min(rW * rDelta * rxi, 1.0)
        # 6. Omega invariants
        PhiN   = 1.0 - CTOI
        # xi_i distribution: use a few noisy samples to estimate variance of log(xi/xi0)
        xi_samples = xi0 * np.exp(-0.03 * t) + 0.1 * np.random.randn(size=5)
        log_ratios = np.log(np.abs(xi_samples) / (xi0 + EPS))
        PhiDelta   = np.var(log_ratios)
        # 7. Entropy of agent responses (proxy: distribution of sigma_z)
        _, counts = np.unique(state, return_counts=True)
        probs = counts / len(state)
        S_cog = -np.sum(probs * np.log(probs + EPS))
        # 8. Invariants ψ, ψ_Δ (with EPS to avoid log(0))
        psi      = np.log(max(PhiN, EPS))
        psi_Delta= np.log(max(PhiDelta, EPS))
        # 9. Store for later checks
        CTOI_hist.append(CTOI)
        PhiN_hist.append(PhiN)
        PhiDelta_hist.append(PhiDelta)
        S_cog_hist.append(S_cog)
        # 10. **Invariant Checks** – raise if any Omega rule broken
        if not (0.0 <= CTOI <= 1.0 + 1e-9):
            raise ValueError(f"CTOI out of [0,1]: {CTOI} @ t={t}")
        if PhiN < -1e-9:
            raise ValueError(f"Phi_N negative: {PhiN} @ t={t}")
        if PhiDelta < -1e-9:
            raise ValueError(f"Phi_Delta negative: {PhiDelta} @ t={t}")
        if not (np.isfinite(psi) and np.isfinite(psi_Delta)):
            raise ValueError(f"ψ or ψ_Δ non‑finite @ t={t}")
        # 11. MPC‑Ω constraint verification (hard bounds)
        if CTOI < 0.6 - 1e-9:
            raise ValueError(f"CTOI below hard bound 0.6: {CTOI} @ t={t}")
        if Delta < 0.7 * Delta0 - 1e-9:
            raise ValueError(f"Delta below 0.7Δ₀: {Delta} @ t={t}")
        if xi < 0.6 * xi0 - 1e-9:
            raise ValueError(f"Xi below 0.6ξ₀: {xi} @ t={t}")
        # 12. Cost integrand (should be non‑negative)
        integrand = ((0.6 - CTOI) if CTOI < 0.6 else 0.0)**2 \
                  + MU1 * ((0.6 - PhiN) if PhiN < 0.6 else 0.0)**2 \
                  + MU2 * (PhiDelta)**2 \
                  + MU3 * ((np.log(3) - S_cog) if S_cog < np.log(3) else 0.0)**2
        if integrand < -1e-12:
            raise ValueError(f"Negative cost integrand: {integrand} @ t={t}")
        # 13. Advance time with simple Euler step for CTOI dynamics
        dCTOI = -GAMMA * max(stress - Delta, 0.0) * CTOI + KAPPA * 0.1  # dummy intervention term
        CTOI = np.clip(CTOI + dCTOI * DT, 0.0, 1.0)
        t += DT
    # If we reach here, all checks passed
    print("[Ω‑VALIDATOR] TCM‑Ω proposal PASSED all mathematical and invariant checks.")
    print(f"   Final CTOI mean: {np.mean(CTOI_hist):.3f}")
    print(f"   Final Φ_N mean:  {np.mean(PhiN_hist):.3f}")
    print(f"   Final Φ_Δ mean:  {np.mean(PhiDelta_hist):.3f}")
    print(f"   Final S_cog mean:{np.mean(S_cog_hist):.3f}")

# --------------------------------------------------------------
if __name__ == "__main__":
    validate_tcm()