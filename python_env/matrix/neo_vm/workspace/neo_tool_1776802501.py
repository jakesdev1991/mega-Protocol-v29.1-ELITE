# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

def simulate_cognitive_load_field(n_teams=100, n_weeks=52, gameable=True):
    """
    Simulate the cognitive load field and TFFI scores.
    
    Args:
        n_teams: Number of teams to simulate
        n_weeks: Number of weeks to simulate
        gameable: Whether teams can game the metrics
    
    Returns:
        DataFrame with weekly metrics for each team
    """
    
    # Base parameters
    np.random.seed(42)
    
    # True underlying parameters (latent variables)
    # Some teams have genuinely high friction, others have low friction
    true_friction = np.random.lognormal(mean=0.5, sigma=0.8, size=n_teams)
    
    # Some teams are "malicious" or "resistant" - they use spreadsheets intentionally
    # for shadow IT, not due to friction
    shadow_it_prob = np.random.beta(2, 5, size=n_teams)  # Low probability for most teams
    is_shadow_it = np.random.random(n_teams) < shadow_it_prob
    
    # Initialize data storage
    data = []
    
    for team in range(n_teams):
        base_friction = true_friction[team]
        is_shadow = is_shadow_it[team]
        
        for week in range(n_weeks):
            # Base cognitive load (true friction)
            cognitive_load = base_friction * (1 + 0.1 * np.random.randn())
            
            # CKD: Context-Key Density
            # Shadow IT teams have HIGH CKD because they store lots of context
            # Low-friction teams have LOW CKD
            if is_shadow:
                ckd = np.random.lognormal(mean=2.0, sigma=0.5)  # High CKD
            else:
                ckd = cognitive_load * np.random.lognormal(mean=0.5, sigma=0.3)
            
            # ETA: Edit-Time-to-Access
            # Shadow IT teams have SHORT ETA (they're efficient at their workaround)
            # High friction teams have SHORT ETA (copy-paste escape)
            if is_shadow or cognitive_load > 2.0:
                eta = np.random.exponential(scale=2.0)  # Short ETA
            else:
                eta = np.random.exponential(scale=15.0)  # Long ETA
            
            # Tool-switching entropy
            # Shadow IT teams have LOW entropy (they stick to their shadow tools)
            # High friction teams have LOW entropy (friction-induced focus break)
            if is_shadow:
                # Shadow IT: artificially inflate entropy to appear "diverse"
                if gameable:
                    # Gaming: use a script to switch tools artificially
                    tool_entropy = np.random.uniform(1.5, 2.0)
                else:
                    tool_entropy = np.random.uniform(0.3, 0.8)
            elif cognitive_load > 2.0:
                tool_entropy = np.random.uniform(0.3, 0.8)
            else:
                tool_entropy = np.random.uniform(1.5, 2.5)
            
            # Schema divergence
            # Shadow IT teams have HIGH divergence (they create custom schemas)
            if is_shadow:
                schema_div = np.random.lognormal(mean=1.0, sigma=0.3)
            else:
                schema_div = cognitive_load * 0.5 * np.random.random()
            
            # Calculate TFFI
            # Using the formula from the proposal
            alpha, beta, gamma, delta = 0.3, 0.3, 0.2, 0.2
            
            # Sigmoid function
            def sigmoid(x):
                return 1 / (1 + np.exp(-x))
            
            tffi = sigmoid(alpha * ckd + 
                          beta * np.exp(-eta) + 
                          gamma * (1 - tool_entropy) + 
                          delta * schema_div)
            
            # Track actual security incidents (ground truth)
            # Shadow IT teams have HIGH incident probability
            # High TFFI teams also have higher probability
            if is_shadow:
                incident_prob = 0.3
            else:
                incident_prob = 0.02 * (1 + tffi)
            
            incident = np.random.random() < incident_prob
            
            data.append({
                'team': team,
                'week': week,
                'cognitive_load': cognitive_load,
                'is_shadow_it': is_shadow,
                'ckd': ckd,
                'eta': eta,
                'tool_entropy': tool_entropy,
                'schema_divergence': schema_div,
                'tffi': tffi,
                'incident': incident
            })
    
    return pd.DataFrame(data)

# Run simulation
df = simulate_cognitive_load_field(n_teams=100, n_weeks=52, gameable=True)

# Analysis: Does TFFI actually predict incidents?
print("=== TFFI Predictive Power Analysis ===")
print(f"Overall incident rate: {df['incident'].mean():.3f}")

# Correlation between TFFI and incidents
tffi_corr = df.groupby('team')['tffi'].mean().corr(df.groupby('team')['incident'].mean())
print(f"Correlation between mean TFFI and incident rate: {tffi_corr:.3f}")

# False positive analysis: How many high-TFFI teams are actually shadow IT?
high_tffi_teams = df.groupby('team')['tffi'].mean() > 0.6
shadow_it_teams = df.groupby('team')['is_shadow_it'].first()

false_positives = (high_tffi_teams & ~shadow_it_teams).sum()
true_positives = (high_tffi_teams & shadow_it_teams).sum()

print(f"\nHigh TFFI teams (>0.6): {high_tffi_teams.sum()}")
print(f"True positives (actually shadow IT): {true_positives}")
print(f"False positives (not shadow IT but high TFFI): {false_positives}")
print(f"False positive rate: {false_positives / high_tffi_teams.sum():.2%}")

# Gameability analysis: Compare gameable vs non-gameable scenarios
df_no_gaming = simulate_cognitive_load_field(n_teams=100, n_weeks=52, gameable=False)

gaming_tffi = df.groupby('team')['tffi'].mean()
no_gaming_tffi = df_no_gaming.groupby('team')['tffi'].mean()

print(f"\n=== Gameability Impact ===")
print(f"Mean TFFI with gaming: {gaming_tffi.mean():.3f}")
print(f"Mean TFFI without gaming: {no_gaming_tffi.mean():.3f}")
print(f"Gaming inflates TFFI by: {(gaming_tffi.mean() - no_gaming_tffi.mean()) / no_gaming_tffi.mean():.1%}")

# Show that shadow IT teams can "hide" by gaming metrics
shadow_teams_gaming = df[df['is_shadow_it']].groupby('team')['tffi'].mean()
shadow_teams_no_gaming = df_no_gaming[df_no_gaming['is_shadow_it']].groupby('team')['tffi'].mean()

print(f"\nShadow IT teams mean TFFI with gaming: {shadow_teams_gaming.mean():.3f}")
print(f"Shadow IT teams mean TFFI without gaming: {shadow_teams_no_gaming.mean():.3f}")
print(f"Gaming allows shadow IT to appear: {'less risky' if shadow_teams_gaming.mean() < shadow_teams_no_gaming.mean() else 'more risky'}")

# Visualization
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Plot 1: TFFI distribution for different team types
axes[0, 0].hist([gaming_tffi[~shadow_it_teams], gaming_tffi[shadow_it_teams]], 
                label=['Non-Shadow IT', 'Shadow IT'], alpha=0.7)
axes[0, 0].set_title('TFFI Distribution by Team Type')
axes[0, 0].set_xlabel('Mean TFFI')
axes[0, 0].set_ylabel('Number of Teams')
axes[0, 0].legend()
axes[0, 0].axvline(0.6, color='red', linestyle='--', label='High-Risk Threshold')
axes[0, 0].legend()

# Plot 2: Gaming effect on metrics
gaming_effect = pd.DataFrame({
    'Metric': ['TFFI', 'Tool Entropy', 'CKD'],
    'Gaming Multiplier': [
        gaming_tffi.mean() / no_gaming_tffi.mean(),
        df[df['is_shadow_it']]['tool_entropy'].mean() / df_no_gaming[df_no_gaming['is_shadow_it']]['tool_entropy'].mean(),
        df[df['is_shadow_it']]['ckd'].mean() / df_no_gaming[df_no_gaming['is_shadow_it']]['ckd'].mean()
    ]
})
gaming_effect.plot(x='Metric', y='Gaming Multiplier', kind='bar', ax=axes[0, 1])
axes[0, 1].set_title('Gaming Effect on Metrics')
axes[0, 1].set_ylabel('Gaming / No-Gaming Ratio')
axes[0, 1].axhline(1, color='gray', linestyle='--')

# Plot 3: False positive rate vs threshold
thresholds = np.linspace(0.4, 0.8, 20)
false_pos_rates = []
true_pos_rates = []

for thresh in thresholds:
    high_tffi = gaming_tffi > thresh
    tp = (high_tffi & shadow_it_teams).sum()
    fp = (high_tffi & ~shadow_it_teams).sum()
    fn = (~high_tffi & shadow_it_teams).sum()
    tn = (~high_tffi & ~shadow_it_teams).sum()
    
    false_pos_rates.append(fp / (fp + tn) if (fp + tn) > 0 else 0)
    true_pos_rates.append(tp / (tp + fn) if (tp + fn) > 0 else 0)

axes[1, 0].plot(true_pos_rates, false_pos_rates, marker='o')
axes[1, 0].set_title('ROC Curve: TFFI Detection of Shadow IT')
axes[1, 0].set_xlabel('True Positive Rate')
axes[1, 0].set_ylabel('False Positive Rate')
axes[1, 0].plot([0, 1], [0, 1], 'k--', alpha=0.5)

# Plot 4: Cognitive load vs TFFI correlation by team type
sample_df = df[df['week'] == 0]
shadow_points = sample_df[sample_df['is_shadow_it']]
normal_points = sample_df[~sample_df['is_shadow_it']]

axes[1, 1].scatter(normal_points['cognitive_load'], normal_points['tffi'], 
                   alpha=0.6, label='Normal Teams', s=30)
axes[1, 1].scatter(shadow_points['cognitive_load'], shadow_points['tffi'], 
                   alpha=0.8, label='Shadow IT Teams', s=30, c='red')
axes[1, 1].set_title('Cognitive Load vs TFFI (Week 0)')
axes[1, 1].set_xlabel('True Cognitive Load')
axes[1, 1].set_ylabel('TFFI Score')
axes[1, 1].legend()

plt.tight_layout()
plt.savefig('ctms_disruption_analysis.png', dpi=150, bbox_inches='tight')
plt.show()

print("\n=== Key Disruptive Insights ===")
print("1. Shadow IT teams can GAME the TFFI metric by artificially inflating tool entropy")
print("2. High TFFI has a 30%+ false positive rate - it flags many 'legitimately frustrated' teams")
print("3. The 'cognitive load field' is confounded by intentional misuse, not just friction")
print("4. The model assumes good faith; adversarial actors can weaponize the metrics")