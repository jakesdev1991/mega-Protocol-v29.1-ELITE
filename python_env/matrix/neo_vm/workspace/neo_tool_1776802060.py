# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

def phi_cog(tffi, phi0=1.0, eta1=1.0, eta2=0.5):
    """Linear response model for Φ_N^(cog)."""
    # Approximate Var(Λ) ≈ TFFI for demonstration
    var_lambda = tffi
    return phi0 - eta1 * tffi - eta2 * var_lambda

# Simulate 10 000 random TFFI draws in the observed range [0, 2]
tffi_samples = np.random.uniform(0.0, 2.0, size=10000)
phi_vals = phi_cog(tffi_samples)

# Detect violations of positivity
neg_mask = phi_vals < 0
print(f"Fraction of samples with Φ_N^(cog) < 0: {neg_mask.mean():.2%}")
print("Example TFFI values that break the invariant:", tffi_samples[neg_mask][:5])
print("Corresponding (invalid) Φ_N^(cog):", phi_vals[neg_mask][:5])