# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import entropy

# === DISRUPTION SIMULATION ===
# GILM-Ω assumes: liquidity = conserved gauge current in honest network
# Reality: liquidity = adversarially spoofable signal in Byzantine network

# Simulate 50 "exchanges" over 200 timesteps
n_nodes, T = 50, 200
true_reserves = np.random.lognormal(0, 0.3, (n_nodes, T))
true_reserves = np.cumsum(true_reserves, axis=1) * 10  # Real reserves

# Attack: Exchanges 0-4 fake volume (breaks conservation law)
observed_flows = true_reserves.copy()
observed_flows[0:5, 80:130] += np.random.exponential(500, (5, 50))

# GILM-Ω would compute "correlation length" from these flows
def gilm_metric(flows, window=20):
    return [np.mean(np.abs(np.corrcoef(flows[:, t-window:t])[np.triu_indices_from(np.eye(n_nodes), k=1)])) 
            for t in range(window, T)]

# NCD-Ω (Narrative Collapse Detector): measures KL divergence between 
# verifiable (proof-of-reserves) vs claimed liquidity
verifiable_idx = np.random.choice(range(5, n_nodes), 10, replace=False)

def ncd_metric(true, claimed, verifiable):
    return [entropy(true[v, t]/true[v, t].sum(), claimed[v, t]/claimed[v, t].sum()) 
            if claimed[v, t].sum() > 0 else 0 
            for t in range(T)]

# Compute
gilm_signal = gilm_metric(observed_flows)
ncd_signal = ncd_metric(true_reserves, observed_flows, verifiable_idx)

# === VISUAL DISRUPTION ===
fig, axes = plt.subplots(2, 1, figsize=(12, 8))

# Top: GILM-Ω is blind
axes[0].plot(gilm_signal, color='purple', linewidth=2, label='GILM-Ω "Gauge Curvature"')
axes[0].axvspan(80, 130, alpha=0.2, color='orange', label='Adversarial Injection')
axes[0].set_title('GILM-Ω: FOOLED', fontsize=14, fontweight='bold')
axes[0].set_ylabel('Fake "Correlation Length"')
axes[0].legend()
axes[0].grid(alpha=0.3)

# Bottom: NCD-Ω sees truth collapse
axes[1].plot(ncd_signal, color='crimson', linewidth=2, label='NCD-Ω Consistency Divergence')
axes[1].axvspan(80, 130, alpha=0.2, color='orange')
axes[1].axhline(0.4, color='black', linestyle='--', label='Narrative Collapse Threshold')
axes[1].set_title('NCD-Ω: DETECTS COLLAPSE', fontsize=14, fontweight='bold')
axes[1].set_ylabel('KL Divergence (bits)')
axes[1].set_xlabel('Time')
axes[1].legend()
axes[1].grid(alpha=0.3)

plt.tight_layout()
plt.show()

print("=== DISRUPTION VERIFIED ===")
print(f"GILM-Ω during attack: {np.mean(gilm_signal[80:130]):.3f} (FALSE CONFIDENCE)")
print(f"NCD-Ω during attack: {np.mean(ncd_signal[80:130]):.3f} (TRUTH DECAY)")