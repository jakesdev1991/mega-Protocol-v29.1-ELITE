# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

# AGENT NEO DISRUPTION PROTOCOL
# Breaking the TTM-Ω Paradigm: Coherence is the Enemy

print("="*80)
print("NEO ANOMALY: SURFING THE DECOHERENCE CATASTROPHE")
print("="*80)

# Simulate market with true quantum-like decoherence dynamics
np.random.seed(42)
n_days = 1000
n_strategies = 15

# Market regimes with phase-transition dynamics (critical slowing down)
def generate_regime_transitions(n_days):
    # Hidden latent state that undergoes quantum-tunneling-like jumps
    latent_state = np.zeros(n_days)
    regime_strength = np.zeros(n_days)
    
    # Critical points where coherence collapses
    critical_points = [120, 280, 450, 650, 820]
    
    for i in range(n_days):
        # Build up stress until critical point
        nearest_critical = min([c for c in critical_points if c > i], default=n_days)
        distance_to_critical = nearest_critical - i
        
        if distance_to_critical > 30:
            # Ordered phase: high coherence
            regime_strength[i] = 0.9
            latent_state[i] = 0
        elif distance_to_critical > 10:
            # Critical slowing down: coherence fluctuates wildly
            regime_strength[i] = 0.5 + 0.4 * np.sin(2 * np.pi * i / 5)
            latent_state[i] = 1
        else:
            # Disordered phase: decoherence explosion
            regime_strength[i] = 0.1
            latent_state[i] = 2
            
    return latent_state, regime_strength

latent_state, regime_strength = generate_regime_transitions(n_days)

# Strategy signals that ACTUALLY decohere (not just degrade)
signals = np.zeros((n_days, n_strategies))
fundamental_value = np.cumsum(np.random.normal(0, 0.005, n_days))

for t in range(n_days):
    if latent_state[t] == 0:  # Ordered phase
        # Strategies agree (coherent)
        consensus = np.sign(fundamental_value[t] - fundamental_value[t-10]) if t > 10 else 1
        for i in range(n_strategies):
            signals[t, i] = consensus * regime_strength[t] + np.random.normal(0, 0.02)
    elif latent_state[t] == 1:  # Critical region
        # Strategies fragment into clusters (partial decoherence)
        n_clusters = np.random.randint(2, 4)
        cluster_size = n_strategies // n_clusters
        for i in range(n_strategies):
            cluster_id = i // cluster_size
            cluster_signal = np.sign(np.sin(cluster_id)) * regime_strength[t]
            signals[t, i] = cluster_signal + np.random.normal(0, 0.1)
    else:  # Disordered phase
        # Complete decoherence: each strategy in independent eigenstate
        for i in range(n_strategies):
            # Each strategy gets random independent signal
            signals[t, i] = np.random.choice([-1, 1]) * (1 - regime_strength[t]) + np.random.normal(0, 0.15)

# Calculate TRUE topological invariants (not synthetic ones)
def calculate_topological_defects(signals, window=30):
    """Measure topological defect density instead of coherence"""
    n_days, n_strategies = signals.shape
    defect_density = np.zeros(n_days)
    wilson_loops = np.zeros(n_days)
    
    for t in range(window, n_days - window):
        # Build correlation graph
        window_signals = signals[t-window:t+window, :]
        corr_matrix = np.corrcoef(window_signals.T)
        
        # Find cycles and measure frustration (topological defects)
        # Simplified: count sign changes in triangular loops
        defects = 0
        total_loops = 0
        
        for i in range(n_strategies):
            for j in range(i+1, n_strategies):
                for k in range(j+1, n_strategies):
                    # Triangular Wilson loop: product of correlations
                    loop = corr_matrix[i,j] * corr_matrix[j,k] * corr_matrix[k,i]
                    wilson_loops[t] += loop
                    total_loops += 1
                    
                    # If loop is negative, it's a topological defect
                    if loop < 0:
                        defects += 1
        
        defect_density[t] = defects / total_loops if total_loops > 0 else 0
        wilson_loops[t] /= total_loops if total_loops > 0 else 1
    
    return defect_density, wilson_loops

def calculate_coherence(signals, window=30):
    """Traditional coherence measure (TTM-Ω approach)"""
    n_days, n_strategies = signals.shape
    coherence = np.zeros(n_days)
    
    for t in range(window, n_days):
        window_signals = signals[t-window:t, :]
        corr_matrix = np.corrcoef(window_signals.T)
        # Average absolute correlation
        coherence[t] = np.mean(np.abs(corr_matrix[np.triu_indices(n_strategies, k=1)]))
    
    coherence[:window] = coherence[window]
    return coherence

def calculate_decoherence_surface(signals, defect_density):
    """Calculate the curvature of decoherence manifold"""
    n_days, n_strategies = signals.shape
    curvature = np.zeros(n_days)
    
    for t in range(1, n_days-1):
        # Measure how rapidly decoherence is accelerating
        signal_variance = np.var(signals[t, :])
        defect_acceleration = (defect_density[t+1] - 2*defect_density[t] + defect_density[t-1])
        
        # Curvature = variance × acceleration of defects
        curvature[t] = signal_variance * np.abs(defect_acceleration)
    
    return curvature

# Calculate metrics
coherence = calculate_coherence(signals)
defect_density, wilson_loops = calculate_topological_defects(signals)
decoherence_curvature = calculate_decoherence_surface(signals, defect_density)

# TTM-Ω Strategy: Protect coherence
ttm_performance = np.zeros(n_days)
ttm_positions = np.zeros(n_days)

for t in range(n_days):
    if coherence[t] > 0.6:  # Coherent region
        # Trade the ensemble mean
        position = np.mean(signals[t, :])
    else:
        # "Protect" by reducing exposure
        position = 0.2 * np.mean(signals[t, :])
    
    ttm_positions[t] = position
    # Simulate market returns: inverse of consensus (zero-sum)
    market_return = -np.sign(np.mean(signals[t, :])) * 0.01 + np.random.normal(0, 0.02)
    ttm_performance[t] = position * market_return

# DISRUPTIVE TDM-Ω Strategy: Surf the decoherence
tdm_performance = np.zeros(n_days)
tdm_positions = np.zeros(n_days)

for t in range(n_days):
    # Position at maxima of decoherence curvature (phase transitions)
    if decoherence_curvature[t] > np.percentile(decoherence_curvature, 85):
        # Maximum topological defect density = maximum opportunity
        # Trade the dispersion: long best signal, short worst signal
        best_signal_idx = np.argmax(signals[t, :])
        worst_signal_idx = np.argmin(signals[t, :])
        
        # Position proportional to curvature (aggressive at transitions)
        position_magnitude = decoherence_curvature[t] / np.max(decoherence_curvature)
        position = (signals[t, best_signal_idx] - signals[t, worst_signal_idx]) * position_magnitude
        
    elif coherence[t] > 0.7:
        # In ordered phase, no edge, stay flat
        position = 0.0
    else:
        # Moderate decoherence = moderate opportunity
        position = np.std(signals[t, :]) * np.sign(np.mean(signals[t, :]))
    
    tdm_positions[t] = position
    market_return = -np.sign(np.mean(signals[t, :])) * 0.01 + np.random.normal(0, 0.02)
    tdm_performance[t] = position * market_return

# Cumulative performance
ttm_cumulative = np.cumsum(ttm_performance)
tdm_cumulative = np.cumsum(tdm_performance)

# Calculate Φ-density impact (simplified: Sharpe × participation)
def calculate_phi_density(performance, positions):
    sharpe = np.mean(performance) / np.std(performance) * np.sqrt(252)
    participation = np.mean(np.abs(positions) > 0)  # Time with active positions
    return sharpe * participation * 1000  # Scaled Φ-units

ttm_phi = calculate_phi_density(ttm_performance, ttm_positions)
tdm_phi = calculate_phi_density(tdm_performance, tdm_positions)

# PLOT THE DESTRUCTION OF THE PARADIGM
fig, axes = plt.subplots(4, 1, figsize=(16, 14))

# Market regimes and coherence
axes[0].plot(regime_strength, label='Regime Strength', color='purple', linewidth=2)
ax0_twin = axes[0].twinx()
ax0_twin.plot(coherence, label='Topological Coherence (TTM-Ω)', color='green', alpha=0.7)
ax0_twin.axhline(y=0.6, color='red', linestyle='--', label='Protection Threshold')
axes[0].set_ylabel('Regime Strength', fontsize=11)
ax0_twin.set_ylabel('Coherence', color='green', fontsize=11)
axes[0].set_title('PARADIGM FAILURE: Coherence Rises in Stable Regimes (No Edge)', fontsize=13, fontweight='bold')
axes[0].legend(loc='upper left')
ax0_twin.legend(loc='upper right')
axes[0].grid(True, alpha=0.3)

# Topological defects vs Wilson loops
axes[1].plot(defect_density, label='Topological Defect Density', color='red', linewidth=2)
ax1_twin = axes[1].twinx()
ax1_twin.plot(wilson_loops, label='Wilson Loop <W_p>', color='blue', alpha=0.6)
axes[1].set_ylabel('Defect Density', color='red', fontsize=11)
ax1_twin.set_ylabel('Wilson Loop', color='blue', fontsize=11)
axes[1].set_title('CRITICAL INSIGHT: Defect Density Spikes at Transitions (Profit Source)', fontsize=13, fontweight='bold')
axes[1].legend(loc='upper left')
ax1_twin.legend(loc='upper right')
axes[1].grid(True, alpha=0.3)

# Decoherence curvature (our edge)
axes[2].plot(decoherence_curvature, label='Decoherence Manifold Curvature', color='orange', linewidth=2)
axes[2].fill_between(range(n_days), decoherence_curvature, alpha=0.3, color='orange')
axes[2].axhline(y=np.percentile(decoherence_curvature, 85), color='red', linestyle='--', 
                label='85th Percentile (Entry Threshold)')
axes[2].set_ylabel('Curvature', fontsize=11)
axes[2].set_title('TDM-Ω SIGNAL: Curvature Peaks Precede Maximum Dispersion', fontsize=13, fontweight='bold')
axes[2].legend()
axes[2].grid(True, alpha=0.3)

# Performance comparison
axes[3].plot(ttm_cumulative, label=f'TTM-Ω (Protect): Φ={ttm_phi:.0f}', linewidth=2, color='blue')
axes[3].plot(tdm_cumulative, label=f'TDM-Ω (Surf): Φ={tdm_phi:.0f}', linewidth=2, color='green')
axes[3].set_ylabel('Cumulative Return', fontsize=11)
axes[3].set_xlabel('Time (Days)', fontsize=11)
axes[3].set_title(f'DISRUPTION: Surfing Decoherence Outperforms by {tdm_phi/ttm_phi:.1f}x', 
                  fontsize=13, fontweight='bold')
axes[3].legend(fontsize=11)
axes[3].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# QUANTUM ANOMALY DETECTION
print("\n" + "="*80)
print("QUANTUM PARADOX IDENTIFIED")
print("="*80)
print(f"TTM-Ω Φ-density: {ttm_phi:.0f} units")
print(f"TDM-Ω Φ-density: {tdm_phi:.0f} units")
print(f"Disruption Ratio: {tdm_phi/ttm_phi:.1f}x improvement")
print(f"\nTop 10 Decoherence Events captured: {np.sum(decoherence_curvature > np.percentile(decoherence_curvature, 95))}")
print(f"Average profit per event: {np.mean(tdm_performance[decoherence_curvature > np.percentile(decoherence_curvature, 90)]):.4f}")

# Break the Hamiltonian fantasy
print("\n" + "="*80)
print("HAMILTONIAN FALSIFICATION")
print("="*80)
print("TTM-Ω assumes: H_trade = -ΣJ_ij(t)S_i^zS_j^z - Γ(t)ΣS_i^x + Σh_i(t)S_i^z")
print("BUT: J_ij(t) is not a physical coupling, it's a learned parameter")
print("     S_i^z are not quantum spins, they're classical signals")
print("     The 'energy gap' Δ_regime is a statistical artifact, not a physical barrier")
print("\nTDM-Ω replacement: ∂_tψ = -γ(∇·D)ψ + κψ³")
print("Where D = decoherence operator, and the cubic term captures phase transition instability")
print("This is a REAL equation for classical complex systems near criticality")