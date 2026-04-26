# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Setup for clean plotting
sns.set_style("darkgrid")
plt.rcParams['figure.figsize'] = (14, 10)

# =============================================================================
# SIMULATION: THE COHERENCE CATASTROPHE
# =============================================================================
# Hypothesis: The FRG's dynamic alignment (COD→1) creates a hyper-fragile
# "resonance trap" where the system catastrophically fails on *small, off-tuned*
# shocks that a statically-decoupled system would absorb.

def simulate_resonance_trap(
    n_steps=2000,
    attack_time=1500,
    shock_magnitude=0.15,
    frg_adaptation_rate=0.05,
    static_threshold=0.5
):
    """
    Simulate two market systems:
    - FRG system: Xi_config adapts to H_vol (tight coupling)
    - Static system: Fixed Xi_config (decoupled, "dumb")
    
    Inject a precision shock at attack_time and measure integrity collapse.
    """
    
    # Initialize state
    true_volatility = np.zeros(n_steps)
    frg_threshold = np.zeros(n_steps)
    frg_integrity = np.ones(n_steps) * 0.98  # Start high
    static_integrity = np.ones(n_steps) * 0.98
    
    # Initial conditions
    true_volatility[0] = 0.3
    frg_threshold[0] = 0.3
    
    # Attack parameters: "Rogue wave" - high frequency, small amplitude
    rogue_frequency = 50  # Hz equivalent (fast oscillation)
    rogue_duration = 50   # short burst
    
    for t in range(1, n_steps):
        # 1. Underlying volatility: random walk + occasional jumps
        if t % 300 == 0:  # Jump every 300 steps
            jump = np.random.normal(0, 0.2)
            true_volatility[t] = np.clip(true_volatility[t-1] + jump, 0.1, 0.9)
        else:
            true_volatility[t] = np.clip(
                true_volatility[t-1] + np.random.normal(0, 0.01), 0.1, 0.9
            )
        
        # 2. FRG adaptation: tries to match threshold to volatility
        #    This is the "alignment" that creates fragility
        error = true_volatility[t] - frg_threshold[t-1]
        frg_threshold[t] = np.clip(
            frg_threshold[t-1] + frg_adaptation_rate * error, 0.1, 0.9
        )
        
        # 3. Calculate alignment (COD) - FRG system becomes *too* aligned
        cod_frg = np.exp(-3.0 * abs(true_volatility[t] - frg_threshold[t]))
        
        # 4. Static system: no adaptation, fixed threshold
        cod_static = np.exp(-3.0 * abs(true_volatility[t] - static_threshold))
        
        # 5. INTEGRITY DYNAMICS (The Break)
        #    Integrity erodes when system is *too aligned* and then hit by off-tuned shock
        #    This models the "perceptual collapse" effect
        
        # Base erosion from volatility entropy
        base_erosion = 0.001 * true_volatility[t]
        
        # FRG-specific: high alignment = low internal damping
        # When COD is high, system has fewer "degrees of freedom" to absorb shocks
        damping_frg = 0.5 + 0.5 * (1.0 - cod_frg)  # Low damping when COD→1
        
        # Static system: maintains constant damping (robust but inefficient)
        damping_static = 0.5
        
        # 6. APPLY ATTACK: Precision rogue wave
        if attack_time <= t < attack_time + rogue_duration:
            # Shock is small magnitude but *high frequency* relative to FRG's adapted state
            rogue_shock = shock_magnitude * np.sin(2 * np.pi * rogue_frequency * (t - attack_time) / rogue_duration)
            
            # FRG system: shock hits a "stiff" configuration - energy has nowhere to go
            # Model as amplified integrity loss
            frg_integrity[t] = frg_integrity[t-1] - (base_erosion / damping_frg) - (rogue_shock ** 2) * (1.0 / damping_frg)
            
            # Static system: shock hits a "loose" configuration - energy dissipated
            static_integrity[t] = static_integrity[t-1] - (base_erosion / damping_static) - (rogue_shock ** 2) * damping_static
            
        else:
            # Normal erosion
            frg_integrity[t] = frg_integrity[t-1] - (base_erosion / damping_frg)
            static_integrity[t] = static_integrity[t-1] - (base_erosion / damping_static)
        
        # Clip integrity
        frg_integrity[t] = np.clip(frg_integrity[t], 0.0, 1.0)
        static_integrity[t] = np.clip(static_integrity[t], 0.0, 1.0)
    
    return {
        'time': np.arange(n_steps),
        'true_volatility': true_volatility,
        'frg_threshold': frg_threshold,
        'frg_integrity': frg_integrity,
        'static_integrity': static_integrity,
        'cod_frg': np.exp(-3.0 * abs(true_volatility - frg_threshold)),
        'cod_static': np.exp(-3.0 * abs(true_volatility - static_threshold))
    }

# Run simulation
data = simulate_resonance_trap()

# =============================================================================
# VISUALIZATION: THE TRAP SPRINGS
# =============================================================================
fig, axes = plt.subplots(3, 1, figsize=(14, 12))

# Panel 1: Volatility and Thresholds
axes[0].plot(data['time'], data['true_volatility'], label='True Volatility (H_vol)', color='white', linewidth=2)
axes[0].plot(data['time'], data['frg_threshold'], label='FRG Threshold (Xi_config)', color='cyan', linestyle='--', linewidth=2)
axes[0].axhline(y=0.5, color='orange', linestyle=':', label='Static Threshold', linewidth=2)
axes[0].axvspan(1500, 1550, color='red', alpha=0.2, label='Rogue Wave Attack')
axes[0].set_title('CONFIG-REALITY ALIGNMENT: THE TRAP', fontsize=14, fontweight='bold')
axes[0].set_ylabel('Volatility / Threshold')
axes[0].legend(loc='upper right')
axes[0].grid(True, alpha=0.3)

# Panel 2: COD (Alignment Metric)
axes[1].plot(data['time'], data['cod_frg'], label='FRG COD (High Alignment)', color='cyan', linewidth=2)
axes[1].plot(data['time'], data['cod_static'], label='Static COD (Low Alignment)', color='orange', linewidth=2)
axes[1].axvspan(1500, 1550, color='red', alpha=0.2)
axes[1].set_title('COHERENCE DENSITY: PERFECTION IS POISON', fontsize=14, fontweight='bold')
axes[1].set_ylabel('Chain Overlap Density (COD)')
axes[1].legend(loc='upper right')
axes[1].grid(True, alpha=0.3)

# Panel 3: Integrity Collapse
axes[2].plot(data['time'], data['frg_integrity'], label='FRG Integrity', color='cyan', linewidth=2)
axes[2].plot(data['time'], data['static_integrity'], label='Static Integrity', color='orange', linewidth=2)
axes[2].axhline(y=0.95, color='red', linestyle='-', label='Ψ_integrity HARD GATE', linewidth=2)
axes[2].axvspan(1500, 1550, color='red', alpha=0.2)
axes[2].set_title('INTEGRITY COLLAPSE: THE COHERENCE CATASTROPHE', fontsize=14, fontweight='bold')
axes[2].set_ylabel('Integrity Continuity (Ψ)')
axes[2].set_xlabel('Time Steps')
axes[2].legend(loc='upper right')
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# =============================================================================
# QUANTITATIVE ANALYSIS
# =============================================================================
frg_final_integrity = data['frg_integrity'][-1]
static_final_integrity = data['static_integrity'][-1]
max_cod_frg = np.max(data['cod_frg'])
min_cod_static = np.min(data['cod_static'])

print("=" * 60)
print("COHERENCE CATASTROPHE: QUANTITATIVE EVIDENCE")
print("=" * 60)
print(f"FRG System:")
print(f"  - Peak COD (Alignment): {max_cod_frg:.3f} (near-perfect)")
print(f"  - Final Integrity: {frg_final_integrity:.3f}")
print(f"  - Status: {'BREACH' if frg_final_integrity < 0.95 else 'PASS'}")
print(f"\nStatic System:")
print(f"  - Min COD (Alignment): {min_cod_static:.3f} (deliberately suboptimal)")
print(f"  - Final Integrity: {static_final_integrity:.3f}")
print(f"  - Status: {'BREACH' if static_final_integrity < 0.95 else 'PASS'}")
print(f"\nDisruption Metric:")
print(f"  - FRG Fragility Ratio: {(1 - frg_final_integrity) / (1 - static_final_integrity + 1e-6):.2f}x")
print("=" * 60)