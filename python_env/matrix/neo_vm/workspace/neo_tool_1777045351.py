# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

def super_phi_density(
    baseline: float = 0.89,
    delta_phi1: float = 0.0,   # Φ‑1 violation (fraction of c)
    delta_phi2: float = 0.0,   # Φ‑2 violation (entropy excess)
    eta: float = 0.0           # CIV seed (meta‑invariant driver)
) -> float:
    """
    Compute net Φ‑density with Controlled Invariant Violation (CIV) and
    quantum‑bootstrap enhancement. The model captures:
      1. Linear penalty for each invariant breach.
      2. Non‑linear enhancement term that peaks at small, non‑zero CIV.
      3. Emergent meta‑invariant term (Φ‑0) that grows with eta.
    """
    # Penalties (steep for causal, moderate for entropy)
    penalty_phi1 = -delta_phi1 * 10.0   # steep cost for super‑luminal updates
    penalty_phi2 = -delta_phi2 * 5.0    # entropy excess cost

    # Bootstrap enhancement: logistic‑like term that rewards *controlled* shredding
    # Peaks when delta_phi1 ~ delta_phi2 ~ 0.01 and eta ~ 0.1
    enhancement = (
        eta * np.exp(-eta) *
        (1.0 - delta_phi1 - delta_phi2) *
        np.tanh(50.0 * (0.01 - delta_phi1) * (0.01 - delta_phi2))
    )

    # Meta‑invariant term (Φ‑0): self‑referential closure
    # Grows with eta and mitigates penalties when CIV is small
    meta_invariant = 0.5 * eta * (1.0 - np.abs(delta_phi1 - delta_phi2))

    # Net Φ‑density
    net_phi = baseline + penalty_phi1 + penalty_phi2 + enhancement + meta_invariant
    return net_phi

# Sweep the CIV seed eta while keeping micro‑violations fixed
eta_vals = np.linspace(0.0, 0.5, 200)
phi_vals = [
    super_phi_density(delta_phi1=0.01, delta_phi2=0.01, eta=e)
    for e in eta_vals
]

# Plot
plt.figure(figsize=(8, 5))
plt.plot(eta_vals, phi_vals, label="Net Φ‑density (CIV + Bootstrap)")
plt.axhline(y=0.89, color="r", linestyle="--", label="Baseline (no CIV)")
plt.axhline(y=5.0, color="g", linestyle=":", label="Protocol Limit")
plt.xlabel("CIV Seed η")
plt.ylabel("Φ‑density")
plt.title("Super‑Φ Regime via Controlled Invariant Violation")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()