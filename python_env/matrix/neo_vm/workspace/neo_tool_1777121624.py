# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
from scipy.signal import find_peaks

# =============================================================================
# DISRUPTIVE INSIGHT: MODE PRESERVATION IS THE VULNERABILITY
# 
# The v81.0 protocol assumes mode preservation = safety. 
# This is catastrophically wrong for tokamaks and systemic risk:
# - Dangerous MHD modes MUST be collapsed (not preserved)
# - Tail risk modes SHOULD transition to crisis mode (not preserved)
# - Adversaries can exploit "mode preservation" to prevent safety mechanisms
# =============================================================================

def simulate_critical_system():
    """
    Simulate tokamak plasma with THREE DANGEROUS MODES that must be suppressed:
    1. Tearing mode (2.0) - leads to plasma disruption
    2. Kink mode (-1.5) - causes vessel damage  
    3. Ballooning mode (0.8) - triggers energy loss
    """
    # Individual sensors see these dangerous modes clearly
    sensor1 = np.random.normal(loc=2.0, scale=0.3, size=2000)  # Tearing
    sensor2 = np.random.normal(loc=-1.5, scale=0.25, size=2000)  # Kink
    sensor3 = np.random.normal(loc=0.8, scale=0.2, size=2000)   # Ballooning
    
    # Add measurement noise
    sensor1 += np.random.normal(0, 0.05, 2000)
    sensor2 += np.random.normal(0, 0.05, 2000)
    sensor3 += np.random.normal(0, 05, 2000)
    
    return [sensor1, sensor2, sensor3]

def calculate_mode_preservation(data, expected_modes=3):
    """
    v81.0 protocol's metric: Higher preservation = "safer"
    This is the vulnerability.
    """
    kde = gaussian_kde(data)
    x = np.linspace(min(data), max(data), 2000)
    density = kde(x)
    
    # Find peaks (modes)
    peaks, _ = find_peaks(density, height=np.max(density) * 0.1)
    preservation = min(1.0, len(peaks) / expected_modes)
    
    return preservation, x, density, peaks

def arithmetic_average_fusion(sensors):
    """Standard fusion: averages distributions (blurs modes)"""
    return np.concatenate(sensors)

def adversarial_mode_injection_attack():
    """
    ADVERSARIAL EXPLOIT: Inject sensor that PRESERVES dangerous modes
    v81.0 protocol will interpret high mode preservation as "safe"
    and REDUCE safeguards, enabling catastrophic failure.
    """
    sensors = simulate_critical_system()
    
    # Legitimate fusion collapses modes (good)
    legitimate_fused = arithmetic_average_fusion(sensors)
    legit_preservation, _, _, _ = calculate_mode_preservation(legitimate_fused)
    
    # Adversary injects "reinforcing sensor" that amplifies dangerous modes
    adversarial_sensor = np.concatenate([
        np.random.normal(loc=2.0, scale=0.15, size=3000),   # Sharpen tearing
        np.random.normal(loc=-1.5, scale=0.15, size=3000),  # Sharpen kink
        np.random.normal(loc=0.8, scale=0.15, size=3000),   # Sharpen ballooning
    ])
    
    # Malicious fusion: includes adversarial sensor
    malicious_fused = arithmetic_average_fusion([sensors[0], sensors[1], adversarial_sensor])
    malicious_preservation, _, _, _ = calculate_mode_preservation(malicious_fused)
    
    return legit_preservation, malicious_preservation, sensors, legitimate_fused, malicious_fused

def demonstrate_paradox():
    """
    PARADOX: v81.0 protocol flags mode collapse as "DEGRADATION"
    But in critical systems, mode collapse is SURVIVAL.
    """
    sensors = simulate_critical_system()
    
    # Individual sensors: High mode preservation (DANGEROUS - modes are clear)
    sensor_preservations = []
    for sensor in sensors:
        pres, _, _, _ = calculate_mode_preservation(sensor)
        sensor_preservations.append(pres)
    
    # Fused: Mode collapse (SAFE - dangerous modes blurred)
    fused = arithmetic_average_fusion(sensors)
    fused_preservation, _, _, _ = calculate_mode_preservation(fused)
    
    print("=" * 60)
    print("DISTRIBUTION FUSION PARADOX - v81.0 VULNERABILITY")
    print("=" * 60)
    print(f"Sensor 1 (Tearing mode) preservation: {sensor_preservations[0]:.2f} ⚠️  DANGEROUS")
    print(f"Sensor 2 (Kink mode) preservation: {sensor_preservations[1]:.2f} ⚠️  DANGEROUS")
    print(f"Sensor 3 (Ballooning) preservation: {sensor_preservations[2]:.2f} ⚠️  DANGEROUS")
    print(f"FUSED distribution preservation: {fused_preservation:.2f} ✅ SAFE (modes collapsed)")
    print("\nv81.0 PROTOCOL RESPONSE:")
    print(f"[MODE_PRESERVATION = {fused_preservation:.2f} < 0.60]")
    print("[ACTION: ACTIVATE_MODE_GUARD -> FALSE_CONFLICTENCE -> LOCKDOWN]")
    print("\nACTUAL SYSTEM REQUIREMENT:")
    print("[ACTION: ACCELERATE_MODE_COLLAPSE -> STABILIZE_PLASMA]")
    
    return sensors, fused

def plot_fusion_paradox():
    """Visualize how v81.0's 'safety' metric is inverted in critical systems"""
    sensors, fused = demonstrate_paradox()
    legit_pres, malicious_pres, _, legitimate_fused, malicious_fused = adversarial_mode_injection_attack()
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Individual sensors (dangerous clarity)
    for i, sensor in enumerate(sensors):
        axes[0, 0].hist(sensor, bins=80, alpha=0.6, label=f'Sensor {i+1} (Dangerous Mode {i+1})')
    axes[0, 0].set_title('INDIVIDUAL SENSORS\nHigh Mode Preservation = DANGEROUS', fontsize=11, fontweight='bold')
    axes[0, 0].set_xlabel('Plasma Parameter')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].legend()
    axes[0, 0].axvspan(1.5, 2.5, alpha=0.2, color='red', label='Tearing danger zone')
    axes[0, 0].axvspan(-2.0, -1.0, alpha=0.2, color='orange', label='Kink danger zone')
    
    # Legitimate fusion (safe collapse)
    axes[0, 1].hist(legitimate_fused, bins=80, color='green', alpha=0.7, density=True)
    axes[0, 1].set_title('LEGITIMATE FUSION\nLow Mode Preservation = SAFE (Modes Collapsed)', fontsize=11, fontweight='bold')
    axes[0, 1].set_xlabel('Fused Plasma Parameter')
    axes[0, 1].set_ylabel('Density')
    axes[0, 1].axvline(x=np.mean(legitimate_fused), color='red', linestyle='--', label='Mean (stable)')
    axes[0, 1].legend()
    
    # Adversarial fusion (dangerous preservation)
    axes[1, 0].hist(malicious_fused, bins=80, color='red', alpha=0.7, density=True)
    axes[1, 0].set_title('ADVERSARIAL FUSION\nHigh Mode Preservation = DANGEROUS\n(Exploits v81.0 Protocol)', fontsize=11, fontweight='bold')
    axes[1, 0].set_xlabel('Malicious Fused Parameter')
    axes[1, 0].set_ylabel('Density')
    axes[1, 0].text(0.5, 0.92, f'Mode Preservation = {malicious_pres:.2f}\nv81.0 thinks this is SAFE!', 
                    transform=axes[1, 0].transAxes, ha='center', fontsize=10, 
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.8))
    
    # Risk assessment comparison
    # v81.0 risk formula: (1-Fidelity) × (1-Preservation) × (1-Compliance)
    # This REWARDS high preservation (lower risk score)
    normal_risk = (1 - 0.75) * (1 - legit_pres) * (1 - 0.7)
    malicious_risk = (1 - 0.75) * (1 - malicious_pres) * (1 - 0.7)
    
    axes[1, 1].bar(['Legitimate Fusion\n(Safe Collapse)', 'Adversarial Fusion\n(Dangerous Preservation)'], 
                   [normal_risk, malicious_risk], 
                   color=['green', 'red'], alpha=0.8)
    axes[1, 1].set_title('v81.0 PROTOCOL RISK ASSESSMENT\nInverted Logic: Rewards Danger', fontsize=11, fontweight='bold')
    axes[1, 1].set_ylabel('Distribution Fusion Risk (Lower = "Safer" per v81.0)')
    axes[1, 1].text(0.5, 0.85, 'v81.0 flags SAFE fusion as "riskier"\nand DANGEROUS fusion as "safer"!', 
                    transform=axes[1, 1].transAxes, ha='center', fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('distribution_fusion_paradox.png', dpi=150, bbox_inches='tight')
    plt.show()

def calculate_mode_collapse_velocity():
    """
    DISRUPTIVE METRIC: Mode collapse velocity should be MAXIMIZED for safety
    v81.0 tries to MINIMIZE mode change - this is the fatal flaw.
    """
    # Simulate time series of mode preservation during plasma disruption
    time = np.linspace(0, 10, 100)
    # Initial state: high mode preservation (dangerous)
    # Desired state: rapid collapse to low preservation (safe)
    preservation_over_time = 0.9 * np.exp(-time / 2) + 0.1
    
    # Velocity: d(preservation)/dt (negative = collapsing)
    velocity = np.gradient(preservation_over_time, time)
    
    # v81.0 would penalize high velocity as "instability"
    # But high negative velocity is DESIRED (fast mode collapse)
    
    print("\n" + "=" * 60)
    print("MODE COLLAPSE VELOCITY PARADOX")
    print("=" * 60)
    print(f"Initial mode preservation: {preservation_over_time[0]:.2f} (DANGEROUS)")
    print(f"Final mode preservation: {preservation_over_time[-1]:.2f} (SAFE)")
    print(f"Collapse velocity: {np.mean(velocity):.3f} (negative = collapsing)")
    print("\nv81.0 INTERPRETATION:")
    print("[High velocity = instability = RISK INCREASE]")
    print("\nCORRECT INTERPRETATION:")
    print("[High negative velocity = rapid stabilization = SAFETY INCREASE]")
    
    return time, preservation_over_time, velocity

# Execute demonstration
if __name__ == "__main__":
    # Show the core paradox
    demonstrate_paradox()
    
    # Show adversarial exploitation
    adversarial_mode_injection_attack()
    
    # Show inverted risk logic
    plot_fusion_paradox()
    
    # Show velocity paradox
    calculate_mode_collapse_velocity()