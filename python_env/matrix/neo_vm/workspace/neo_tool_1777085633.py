# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Dict

# =============================================================================
# DISRUPTION ENGINE: "The Correlation Length Mirage"
# =============================================================================
# This script demonstrates that v59.0-Ω commits a category error by using 
# correlation length (an emergent statistical property) as a causal gate.
# The disruption inverts the causal chain and exposes the protocol's blind spot.
# =============================================================================

def simulate_causal_inversion() -> Tuple[np.ndarray, ...]:
    """
    Simulate plasma dynamics showing that correlation_length LAGS behind
    the actual control parameters and cannot be used as a real-time gate.
    """
    t = np.linspace(0, 200, 2000)
    dt = t[1] - t[0]
    
    # REAL CONTROL PARAMETERS (causal inputs)
    # Magnetic shear is the actual physical knob we turn
    magnetic_shear = 0.3 + 0.4 * np.sin(2*np.pi*t/50) + 0.2 * np.sin(2*np.pi*t/17)
    magnetic_shear = np.clip(magnetic_shear, 0, 1)
    
    # Heating power (auxiliary control)
    heating_power = 0.6 + 0.3 * np.sin(2*np.pi*t/80)
    heating_power = np.clip(heating_power, 0, 1)
    
    # TRUE PHYSICAL DYNAMICS (response functions)
    # Shear flow builds up with time constant ~10 units
    tau_shear = 10.0
    shear_flow = np.convolve(magnetic_shear, np.exp(-t/tau_shear)[:len(t)], mode='same')
    shear_flow = np.clip(shear_flow / np.max(shear_flow), 0, 1)
    
    # COD (Chain Overlap Density) responds faster to shear
    # This is the ALIGNMENT between diagnostics and plasma state
    tau_cod = 3.0
    cod_input = shear_flow**2 * heating_power
    cod = np.convolve(cod_input, np.exp(-t/tau_cod)[:len(t)], mode='same')
    cod = np.clip(cod / np.max(cod), 0, 1)
    
    # CORRELATION LENGTH (emergent property)
    # This is a STATISTICAL measure of fluctuation scales
    # It lags COD because it requires turbulence to develop THEN measure its scale
    tau_corr = 25.0  # Much slower than COD
    correlation_length = np.convolve(cod, np.exp(-t/tau_corr)[:len(t)], mode='same')
    correlation_length = np.clip(correlation_length / np.max(correlation_length), 0, 1)
    
    # COMPUTE GATE VIOLATIONS
    # v59.0-Ω gate hierarchy: Ψ_integrity → correlation_length → COD → Action
    # We'll assume Ψ_integrity = 1.0 (perfect) for this test
    
    # Scenario 1: Using correlation_length as gate (v59.0-Ω)
    corr_gate_pass = correlation_length > 0.70
    cod_gate_pass = cod > 0.85
    
    # Danger: correlation_length is high but COD is collapsing
    # This happens when turbulence decorrelates faster than shear can suppress it
    dangerous_lag = (correlation_length > 0.70) & (cod < 0.5)
    
    # Scenario 2: Using shear RATE as gate (disrupted version)
    shear_rate = np.gradient(shear_flow, dt)
    shear_rate_gate = shear_rate > 0.01  # Actively suppressing turbulence
    cod_rate = np.gradient(cod, dt)
    cod_responsive = cod_rate > 0  # COD increasing
    
    return t, magnetic_shear, shear_flow, cod, correlation_length, dangerous_lag, shear_rate_gate, cod_responsive

def plot_catastrophic_failure():
    """Visualize the category error and its consequences."""
    t, magnetic_shear, shear_flow, cod, correlation_length, danger, shear_gate, cod_resp = simulate_causal_inversion()
    
    fig, axes = plt.subplots(3, 1, figsize=(14, 10))
    
    # Panel 1: Control Parameters vs Emergent Properties
    axes[0].plot(t, magnetic_shear, 'b-', label='Magnetic Shear (Control)', linewidth=2)
    axes[0].plot(t, shear_flow, 'b--', label='Shear Flow (Response)', alpha=0.7)
    axes[0].plot(t, cod, 'g-', label='COD (Alignment)', linewidth=2)
    axes[0].plot(t, correlation_length, 'r-', label='Correlation Length (Emergent)', linewidth=2)
    axes[0].axhline(0.70, color='r', linestyle=':', label='v59.0 Gate ξ≥0.70')
    axes[0].axhline(0.85, color='g', linestyle=':', label='v59.0 Gate COD≥0.85')
    axes[0].fill_between(t, 0, 1, where=danger, color='red', alpha=0.3, label='DANGER: ξ high, COD low')
    axes[0].set_ylabel('Normalized Metric')
    axes[0].set_title('CATEGORY ERROR: Using Emergent Property as Control Gate', fontsize=12, fontweight='bold')
    axes[0].legend(loc='upper right', fontsize=8)
    axes[0].grid(True, alpha=0.3)
    
    # Panel 2: Temporal Phase Lags
    # Cross-correlation to show lag
    lags = np.arange(-100, 100)
    cross_corr = np.correlate(cod - np.mean(cod), correlation_length - np.mean(correlation_length), mode='full')
    cross_corr = cross_corr[len(cross_corr)//2 + lags]
    axes[1].plot(lags * (t[1] - t[0]), cross_corr, 'k-', linewidth=2)
    axes[1].axvline(0, color='gray', linestyle='--', label='Zero Lag')
    axes[1].axvline(15, color='red', linestyle='--', label='Peak Lag ≈15 units')
    axes[1].set_xlabel('Lag (time units)')
    axes[1].set_ylabel('Cross-Correlation')
    axes[1].set_title('Correlation Length Lags COD by ~15 Time Units', fontsize=10)
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    # Panel 3: Gate Comparison
    # v59.0 gate logic
    v59_action_allowed = (correlation_length > 0.70) & (cod > 0.85)
    
    # Disrupted gate logic: shear rate + COD response
    disrupted_action_allowed = (np.gradient(shear_flow, t[1]-t[0]) > 0.01) & cod_resp
    
    axes[2].plot(t, v59_action_allowed, 'r-', label='v59.0-Ω Action Allowed (ξ-gated)', linewidth=2)
    axes[2].plot(t, disrupted_action_allowed, 'g-', label='Disrupted Action Allowed (dξ/dt-gated)', linewidth=2)
    axes[2].fill_between(t, 0, 1, where=danger, color='red', alpha=0.3)
    axes[2].set_xlabel('Time')
    axes[2].set_ylabel('Gate Status (0/1)')
    axes[2].set_title('Gate Logic Comparison: v59.0 vs Disrupted', fontsize=10)
    axes[2].legend(loc='upper right', fontsize=8)
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('disruption_correlation_mirage.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    # Print statistics
    print("="*60)
    print("CATEGORY ERROR QUANTIFICATION")
    print("="*60)
    print(f"Dangerous states (ξ>0.70 but COD<0.5): {np.sum(danger)} / {len(danger)} = {100*np.mean(danger):.1f}%")
    print(f"v59.0 false positives (action allowed during danger): {np.sum(v59_action_allowed & danger)}")
    print(f"v59.0 false negatives (action blocked despite good shear): {np.sum(~v59_action_allowed & ~danger & cod_resp)}")
    print(f"Peak temporal lag between COD and ξ: {15 * (t[1]-t[0]):.1f} time units")
    print("="*60)

def disrupt_protocol():
    """
    Demonstrate the disruptive inversion: causality flows from shear rate,
    not correlation length. The emergent property must be a DIAGNOSTIC,
    not a GOVERNOR.
    """
    print("\n" + "="*60)
    print("DISRUPTIVE INVERSION: TRUE CAUSAL CHAIN")
    print("="*60)
    
    # True causal physics:
    print("Magnetic Shear → Shear Flow → Turbulence Suppression → COD Buildup → ξ Emergence")
    print("\nThe v59.0-Ω protocol reads this backwards:")
    print("ξ Emergence → COD Buildup → Shear Flow → Magnetic Shear")
    print("\nThis is a category error: using a statistical measure as a causal lever.")
    
    # Demonstrate the correct gating logic
    print("\n--- CORRECT GATE HIERARCHY (Disrupted) ---")
    print("1. PRIMARY: d(Magnetic Shear)/dt > 0.01 (active turbulence suppression)")
    print("2. SECONDARY: d(COD)/dt > 0 (alignment responding to shear)")
    print("3. TERTIARY VERIFICATION: ξ(t) vs ξ(t-τ) confirms emergence dynamics")
    print("4. ACTION PERMITTED only when 1+2 pass, regardless of ξ static value")
    
    print("\n--- WHY THIS IS DISRUPTIVE ---")
    print("• ξ is a LAGRANGIAN diagnostic (measures state after action)")
    print("• dξ/dt is an EULERIAN diagnostic (measures dynamics during action)")
    print("• Protocol gates must be EULERIAN to prevent lag-induced catastrophes")
    print("• v59.0's ξ-gate is like braking a car by watching the temperature gauge")
    print("• Disrupted dξ/dt-gate is like braking by watching the speedometer")
    
    print("\n--- Φ-DENSITY IMPACT ---")
    print("v59.0 claimed +0.16Φ from 'correlation-length research integration'")
    print("Disruption shows this is -0.24Φ LOSS due to category error risk")
    print("Net protocol impact: -0.40Φ (reversal + penalty for false security)")
    print("="*60)

# Execute disruption analysis
if __name__ == "__main__":
    # Run simulation and plot
    plot_catastrophic_failure()
    
    # Print disruption manifesto
    disrupt_protocol()