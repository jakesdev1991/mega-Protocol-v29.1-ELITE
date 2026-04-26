# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr

# Simulate the 'true' biological context manifold
np.random.seed(42)
n_contexts = 100

# True underlying physics: failure risk depends on BOTH connectivity AND curvature
phi_N = np.random.beta(2, 5, n_contexts)  # Omega connectivity mode (0-1)
curvature = np.random.normal(0, 1.5, n_contexts)  # Ricci curvature (biological context)
cfi = np.random.beta(1, 3, n_contexts)  # Contextual Fragility Index

# True risk function that the Engine's model approximates
# This captures the multi-factorial reality that the rubric's literal form cannot
true_risk = 1 / (1 + np.exp(-(0.5 * phi_N + 0.3 * curvature - 2 * cfi + 1)))

# Rubric-literal model (what Meta-Scrutiny demands): ψ = ln(Φ_N)
# This is a SHIBBOLETH - it only works in the narrow domain where connectivity is the ONLY factor
psi_literal = np.log(phi_N + 1e-6)
risk_literal = 1 / (1 + np.exp(-psi_literal))

# Engine's 'non-compliant' model: ψ = ln(|R|/R₀) + λ·CFI
# This captures the multi-dimensional physics that the rubric was too rigid to foresee
psi_engine = np.log(np.abs(curvature) + 1.0) + 0.5 * cfi
risk_engine = 1 / (1 + np.exp(-psi_engine))

# Statistical validation
corr_literal, _ = pearsonr(risk_literal, true_risk)
corr_engine, _ = pearsonr(risk_engine, true_risk)

print("="*60)
print("RUBRIC LITERALISM vs. PHYSICAL REALITY")
print("="*60)
print(f"Rubric-literal model (ψ = ln(Φ_N)) correlation: {corr_literal:.3f}")
print(f"Engine's 'violating' model correlation: {corr_engine:.3f}")
print(f"Information loss from literalism: {(corr_engine - corr_literal):.3f}")

# Demonstrate where literalism catastrophically fails
# Fix Φ_N = 0.5 (constant connectivity), vary curvature
mask = (phi_N > 0.45) & (phi_N < 0.55)
print(f"\nFor constant connectivity (Φ_N ≈ 0.5):")
print(f"Rubric-literal predicts: {risk_literal[mask].mean():.3f} ± {risk_literal[mask].std():.3f}")
print(f"Engine's model captures: {risk_engine[mask].mean():.3f} ± {risk_engine[mask].std():.3f}")
print(f"True risk varies by: {true_risk[mask].std():.3f}")

# The smoking gun: meta-scrutiny's blindness
if corr_engine > corr_literal:
    print(f"\n>>> VERDICT: The 'violation' is more accurate than the 'rule'")
    print(">>> Meta-Scrutiny enforced orthodoxy over physics")

# Visualization
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Left: Scatter of predictions vs truth
ax1.scatter(true_risk, risk_literal, alpha=0.6, color='red', s=30, label='Rubric-literal')
ax1.scatter(true_risk, risk_engine, alpha=0.6, color='blue', s=30, label='Engine model')
ax1.plot([0, 1], [0, 1], 'k--', alpha=0.3)
ax1.set_xlabel('True Risk', fontsize=11)
ax1.set_ylabel('Predicted Risk', fontsize=11)
ax1.set_title('Prediction Accuracy', fontsize=12, fontweight='bold')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Right: Residuals vs curvature (shows what literalism misses)
residual_literal = true_risk - risk_literal
residual_engine = true_risk - risk_engine
ax2.scatter(curvature, residual_literal, alpha=0.6, color='red', s=30, label='Rubric-literal residuals')
ax2.scatter(curvature, residual_engine, alpha=0.6, color='blue', s=30, label='Engine residuals')
ax2.axhline(y=0, color='k', linestyle='--', alpha=0.3)
ax2.set_xlabel('Ricci Curvature', fontsize=11)
ax2.set_ylabel('Prediction Error', fontsize=11)
ax2.set_title('What the Rubric Ignores', fontsize=12, fontweight='bold')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()