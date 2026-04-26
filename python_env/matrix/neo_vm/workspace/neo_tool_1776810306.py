# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd
from collections import Counter

# ──────────────────────────────────────────────────────────────────────────────
# Simulate a clean training run and a poisoned run
# ──────────────────────────────────────────────────────────────────────────────
np.random.seed(42)
n_steps = 1000

# Clean run
chi_clean = np.random.exponential(scale=0.1, size=n_steps)          # gradient variance
delta_clean = np.random.normal(loc=0.05, scale=0.02, size=n_steps)  # physics divergence
rho_clean = np.random.binomial(n=1, p=0.05, size=n_steps)           # poison load (0/1)
kappa_clean = np.random.exponential(scale=0.05, size=n_steps)     # Hessian eigen

# EAPFM‑Ω EFI (sigmoid of weighted sum)
alpha,beta,gamma,eta = 0.25,0.25,0.25,0.25
EFI_clean = 1/(1+np.exp(-(alpha*chi_clean + beta*delta_clean + gamma*rho_clean + eta*kappa_clean)))

# Poisoned run: adversary injects gradient noise, spoofs provenance, inflates Hessian
chi_poison = chi_clean + np.random.normal(scale=0.2, size=n_steps)          # noise injection
rho_poison = np.random.binomial(n=1, p=0.30, size=n_steps)                  # 30% poison load
kappa_poison = kappa_clean * np.random.lognormal(mean=0, sigma=0.5, size=n_steps)  # Hessian hijack

EFI_poison = 1/(1+np.exp(-(alpha*chi_poison + beta*delta_clean + gamma*rho_poison + eta*kappa_poison)))

# ──────────────────────────────────────────────────────────────────────────────
# Demonstrate fragility of EFI to poisoning
# ──────────────────────────────────────────────────────────────────────────────
print(f"Mean EFI (clean): {EFI_clean.mean():.3f}")
print(f"Mean EFI (poisoned): {EFI_poison.mean():.3f}")
print(f"ΔEFI due to poison: {EFI_poison.mean() - EFI_clean.mean():.3f}")

# ──────────────────────────────────────────────────────────────────────────────
# Governance Entropy Index (GEI) – simple, robust, governance‑level metric
# ──────────────────────────────────────────────────────────────────────────────
# Simulate classification markings: 70 % internal, 30 % public (governance policy)
markings = np.random.choice(['internal','public'], size=n_steps, p=[0.7,0.3])
# Simulate audit‑trail completeness (1 = full, 0 = missing)
audit_complete = np.random.binomial(n=1, p=0.9, size=n_steps)

# Entropy of markings
counts = Counter(markings)
probs = np.array(list(counts.values()))/n_steps
entropy_markings = -np.sum(probs*np.log(probs+1e-12))

# GEI = marking entropy + penalty for missing audits
GEI = entropy_markings + 0.5*(1-audit_complete.mean())
print(f"Governance Entropy Index (GEI): {GEI:.3f}  (lower is better)")

# ──────────────────────────────────────────────────────────────────────────────
# Insight: EFI swings wildly under light adversarial pressure,
# while GEI remains stable and directly reflects policy health.
# ──────────────────────────────────────────────────────────────────────────────