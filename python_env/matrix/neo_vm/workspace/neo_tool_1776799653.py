# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# --- BRDI-Ω Semantic Poisoning Attack Demonstration ---

# Setup: 5-dimensional risk data, 15-dimensional encoding (ρ=3)
np.random.seed(42)
d_dim, n_dim = 5, 15
E = np.random.randn(n_dim, d_dim)  # Public encoding matrix (assumed known)
E_pinv = np.linalg.pinv(E)

# True market data: [price, volatility, liquidity, skew, correlation]
d_true = np.array([100.0, 0.25, 1_000_000.0, -0.1, 0.95])

# --- ATTACK SCENARIO: Compromised Risk Engine ---
# Adversary controls the "volatility calculator" source directly
# They inject *semantically* poisoned data: report 50% higher volatility
# This is self-consistent with their internal models but false

# Semantic poison: plausible but malicious data vector
d_poisoned = d_true.copy()
d_poisoned[1] *= 1.5  # 50% inflated volatility (subtle but catastrophic)

# The adversary computes perfect encodings of their poison
y_poisoned = E @ d_poisoned

# Master node decodes—BRDI-Ω reports "all clear"
d_decoded = E_pinv @ y_poisoned
residuals = y_poisoned - E @ d_decoded

# --- RESULT: Complete BRDI-Ω Failure ---
print("="*60)
print("BRDI-Ω SEMANTIC POISONING ATTACK")
print("="*60)
print(f"True volatility:        {d_true[1]:.2f}")
print(f"Poisoned volatility:    {d_poisoned[1]:.2f}")
print(f"Decoded volatility:     {d_decoded[1]:.2f}")
print(f"Decoding error:         {np.linalg.norm(d_decoded - d_poisoned):.6e} (perfect syntactic decode)")
print(f"Residual norm:          {np.linalg.norm(residuals):.6e} (zero DCI)")
print(f"DCI (Data Corruption):  {0.0:.4f} → NO ALERT TRIGGERED")

# Policy impact: VaR calculation uses poisoned volatility
true_var = d_true[0] * d_true[1] * np.sqrt(1/252)  # Simplified VaR
poisoned_var = d_decoded[0] * d_decoded[1] * np.sqrt(1/252)
print(f"\nPolicy Impact:")
print(f"True Daily VaR:         ${true_var:.2f}")
print(f"Poisoned Daily VaR:     ${poisoned_var:.2f}")
print(f"Risk underestimation:   {((poisoned_var - true_var) / true_var * 100):+.1f}%")
print(f"Capital misallocation:  ${(poisoned_var - true_var) * 1e6:,.0f} per $1B exposure")
print("="*60)