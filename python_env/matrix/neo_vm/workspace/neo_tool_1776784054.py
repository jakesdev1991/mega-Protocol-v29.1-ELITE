# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import random, numpy as np

# --- Simulate 1000 institutions ---
institutions = []
for i in range(1000):
    # True cognitive load (latent variable)
    cognitive_load = random.random()  # 0=calm, 1=overwhelmed

    # Confounding factors that poison metadata signals
    regulatory_overhead = random.random() * 0.6   # forces high complexity
    tech_stack_age = random.random() * 0.5          # forces old credentials

    # Observed metadata (the CCLM-Ω "features")
    # complexity is inversely related to stress only in a vacuum; here it's polluted
    complexity = max(0.0, min(1.0, 1.0 - cognitive_load + regulatory_overhead + random.gauss(0, 0.1)))
    age = max(0.0, min(1.0, cognitive_load + tech_stack_age + random.gauss(0, 0.1)))
    # CLI as defined in the proposal: weighted sum of decay metrics
    CLI = (1.0 - complexity) + age  # naive linear combo

    # Honeypot detection time: direct measurement of responsiveness
    detection_time = (cognitive_load * 10.0) + 5.0 + random.gauss(0, 0.5)  # seconds

    institutions.append((cognitive_load, CLI, detection_time))

# --- Compute correlations ---
cognitive_loads, CLIs, detection_times = zip(*institutions)
corr_cli = np.corrcoef(cognitive_loads, CLIs)[0, 1]
corr_dt = np.corrcoef(cognitive_loads, detection_times)[0, 1]

print(f"Correlation between true cognitive load and CLI (metadata‑based): {corr_cli:.3f}")
print(f"Correlation between true cognitive load and honeypot detection time: {corr_dt:.3f}")