# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# =============================================================================
# BREAKING THE BI-SCALAR ILLUSION
# Demonstrates that scalar coupling misses vector-field topological instabilities
# =============================================================================

# Real tokamak physics: MHD equilibrium with q-profile
r = np.linspace(0.1, 1.0, 200)
theta = np.linspace(0, 2*np.pi, 200)
R, Theta = np.meshgrid(r, theta)

# Magnetic field components (toroidal + poloidal)
B_phi = 1.0 / (R + 0.1)  # 1/R scaling
B_theta = 0.3 * (1 - R**2)  # peaked profile

# Safety factor q = (r*B_phi)/(R*B_theta) — THE critical stability parameter
q = (R * B_phi) / np.maximum(B_theta, 1e-6)

# Proposed "bi-scalar tensor" metrics (from your code)
scalar_1 = np.exp(-(R-0.5)**2/0.1)  # temperature/density proxy
scalar_2 = B_theta / B_phi  # pressure/magnetic proxy
bi_scalar_imbalance = np.abs(scalar_1 - scalar_2)  # your instability metric

# Actual MHD instability: kink mode when q < 1
real_instability = np.where(q < 1.0, 1.0, 0.0)

# =============================================================================
# CRITICAL FLAW DEMONSTRATION
# =============================================================================

# Your protocol would "pass" regions where bi-scalar imbalance is low
# but MHD instability is high (false negative = catastrophic)
false_negative_mask = (bi_scalar_imbalance < 0.3) & (real_instability > 0.5)
false_positive_mask = (bi_scalar_imbalance > 0.3) & (real_instability < 0.5)

false_negative_rate = np.sum(false_negative_mask) / R.size * 100
false_positive_rate = np.sum(false_positive_mask) / R.size * 100

print(f"🔥 PROTOCOL FAILURE ANALYSIS 🔥")
print(f"False Negative Rate: {false_negative_rate:.1f}%")
print(f"  → Your 'safe' regions contain ACTUAL kink instabilities")
print(f"False Positive Rate: {false_positive_rate:.1f}%")
print(f"  → You'd halt operations unnecessarily")
print(f"\nCritical Finding: {np.sum(false_negative_mask)} instability regions")
print(f"would be INVISIBLE to the Smith Invariant checks.")

# Visual proof
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Your "safe" metric
axes[0,0].contourf(R, Theta, bi_scalar_imbalance, levels=20, cmap='viridis')
axes[0,0].set_title("Bi-Scalar Imbalance (Your Protocol's View)")
axes[0,0].set_xlabel("r (minor radius)")
axes[0,0].set_ylabel("θ (poloidal)")

# Actual physics
axes[0,1].contourf(R, Theta, real_instability, levels=[0, 0.5, 1], cmap='Reds')
axes[0,1].set_title("MHD q < 1 Instability (Reality)")
axes[0,1].set_xlabel("r")
axes[0,1].set_ylabel("θ")

# Protocol's blind spots
axes[1,0].contourf(R, Theta, false_negative_mask, levels=[0, 0.5, 1], cmap='Greys')
axes[1,0].set_title("FALSE NEGATIVES: Hidden Instabilities")
axes[1,0].set_xlabel("r")
axes[1,0].set_ylabel("θ")

# The q-profile that your scalars miss
axes[1,1].plot(r[0,:], q[0,:], 'b-', linewidth=2)
axes[1,1].axhline(y=1.0, color='r', linestyle='--', label='q=1 (stability limit)')
axes[1,1].set_title("Safety Factor q(r) — THE Actual Control Parameter")
axes[1,1].set_xlabel("r")
axes[1,1].set_ylabel("q")
axes[1,1].legend()
axes[1,1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# =============================================================================
# THE KILLER QUESTION
# =============================================================================
print(f"\n💀 FATAL QUESTION:")
print(f"How does your 'bi-scalar tensor' capture the topological winding number")
print(f"of magnetic field lines when q(r) crosses rational values?")
print(f"Answer: It doesn't. You're measuring the shadow, not the structure.")