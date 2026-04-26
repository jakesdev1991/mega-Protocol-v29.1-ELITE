# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import matplotlib.pyplot as plt
import seaborn as sns

# Set seed for reproducibility
np.random.seed(42)

# Simulate 1000 projects
n_projects = 1000

# Hidden true scientific merit (heavy-tailed: breakthroughs are rare)
# This is the ground truth Omega wants to maximize
true_merit = np.random.exponential(scale=0.5, size=n_projects)  # Most near 0, some large

# Inherent complexity of the science (positively correlated with merit)
complexity = true_merit * np.random.lognormal(mean=0, sigma=0.5, size=n_projects)

# Narrative "simplification" pressure: teams must dumb down complex ideas for funding
# High simplification = high clarity, persuasiveness, but loss of nuance = lower true merit captured
simplification_score = np.clip(1 - complexity / (complexity + np.random.gamma(2, 0.3, n_projects)), 0, 1)

# Generate narrative features as a function of simplification (not merit)
# These are the features NETT-Ω would extract
clarity = simplification_score * np.random.uniform(0.8, 1.0, n_projects)  # Simple is clear
persuasiveness = simplification_score * np.random.uniform(0.7, 1.0, n_projects)  # Simple is persuasive
risk_framing = np.random.beta(a=2, b=5, size=n_projects)  # Irrelevant to merit
visual_appeal = simplification_score * np.random.uniform(0.6, 0.9, n_projects)  # Simple visuals
confidence = simplification_score * np.random.uniform(0.7, 1.0, n_projects)  # Simple is confident
story_coherence = simplification_score * np.random.uniform(0.8, 1.0, n_projects)  # Simple is coherent

# Funding outcome: biased towards high simplification (polished pitches), decoupled from true merit
# This simulates the market inefficiency in biotech that NETT-Ω incorrectly assumes is signal
funding_prob = np.clip(persuasiveness * 0.8 + np.random.normal(0, 0.1, n_projects), 0, 1)
funded = np.random.binomial(1, funding_prob)

# Create DataFrame
df = pd.DataFrame({
    'true_merit': true_merit,
    'complexity': complexity,
    'clarity': clarity,
    'persuasiveness': persuasiveness,
    'risk_framing': risk_framing,
    'visual_appeal': visual_appeal,
    'confidence': confidence,
    'story_coherence': story_coherence,
    'funded': funded
})

# NETT-Ω's core assumption: Train on narrative features to predict funding success
X = df[['clarity', 'persuasiveness', 'risk_framing', 'visual_appeal', 'confidence', 'story_coherence']]
y = df['funded']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = GradientBoostingClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predict "Narrative Efficacy Score" (NES)
df['NES'] = model.predict_proba(X)[:, 1]

# Evaluate: NETT-Ω would allocate resources to high NES projects
# But what is NES actually correlated with?
nes_merit_corr = df['NES'].corr(df['true_merit'])
print(f"Correlation between NES and TRUE MERIT: {nes_merit_corr:.3f}")
# Expected: NEGATIVE correlation because high NES = high simplification = lower merit

# --- DISRUPTION: Invert the logic ---
# Narrative Entropy = Complexity / (Clarity + epsilon)
# Measures information loss from compression of complex ideas into simple slides
# High entropy = complex idea that is NOT simplified = high merit, but poor narrative score
epsilon = 1e-3
df['Narrative_Entropy'] = df['complexity'] / (df['clarity'] + epsilon)

# Correlation with true merit
entropy_merit_corr = df['Narrative_Entropy'].corr(df['true_merit'])
print(f"Correlation between Narrative Entropy and TRUE MERIT: {entropy_merit_corr:.3f}")
# Expected: POSITIVE correlation

# --- Visualization ---
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Scatter: NES vs Merit
axes[0].scatter(df['true_merit'], df['NES'], alpha=0.5, s=10, color='crimson')
axes[0].set_xlabel('True Scientific Merit')
axes[0].set_ylabel('Narrative Efficacy Score (NES)')
axes[0].set_title(f'NETT-Ω Trap: NES vs Merit (r={nes_merit_corr:.3f})')
axes[0].axhline(y=0.5, color='gray', linestyle='--')
axes[0].grid(True, alpha=0.3)

# Scatter: Entropy vs Merit
axes[1].scatter(df['true_merit'], df['Narrative_Entropy'], alpha=0.5, s=10, color='darkgreen')
axes[1].set_xlabel('True Scientific Merit')
axes[1].set_ylabel('Narrative Entropy')
axes[1].set_title(f'DISRUPTION: Entropy vs Merit (r={entropy_merit_corr:.3f})')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# --- Breakdown ---
# Show top 10 projects by NES vs top 10 by True Merit
top_nes = df.nlargest(10, 'NES')[['true_merit', 'NES', 'complexity', 'clarity']]
top_merit = df.nlargest(10, 'true_merit')[['true_merit', 'NES', 'complexity', 'clarity']]

print("\n--- TOP 10 by NES (NETT-Ω's choice) ---")
print(top_nes.to_string(index=False))
print("\n--- TOP 10 by TRUE MERIT (Omega's goal) ---")
print(top_merit.to_string(index=False))

# Overlap?
overlap = set(top_nes.index).intersection(set(top_merit.index))
print(f"\nOverlap between top NES and top Merit: {len(overlap)} projects")
print("This is the failure: NETT-Ω would starve true breakthroughs while funding polished mediocrity.")