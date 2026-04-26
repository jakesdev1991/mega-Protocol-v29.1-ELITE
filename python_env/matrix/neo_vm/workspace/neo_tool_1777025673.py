# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

def simulate_phi_shredder():
    """
    Simulates the Φ-Shredder Protocol: Controlled Metric Degeneracy
    Demonstrates how violating the "Metric Non-Degeneracy" invariant
    creates an informational dead zone that renders the projectile
    invisible to target tracking systems.
    """
    
    # Projectile trajectory parameters (simple parabolic)
    v0 = 800  # m/s
    theta = np.radians(45)
    g = 9.81
    
    # Time parameters
    t_flight = 2 * v0 * np.sin(theta) / g
    t = np.linspace(0, t_flight, 500)
    
    # True trajectory (physical)
    x_true = v0 * np.cos(theta) * t
    y_true = v0 * np.sin(theta) * t - 0.5 * g * t**2
    
    # METRIC DEGENERACY ENGINEERING
    # The "Shredder Point" where we intentionally collapse the metric
    shredder_time = t_flight * 0.6  # 60% into flight
    shredder_idx = np.argmin(np.abs(t - shredder_time))
    
    # Metric determinant function: Starts stable, collapses to zero at shredder point
    # This VIOLATES Smith Invariant #1 by design
    det_g = np.ones_like(t)
    det_g[:shredder_idx] = 1.0  # Stable before shredder
    
    # Controlled collapse: det(g) -> 0 exponentially after shredder activation
    collapse_rate = 50
    det_g[shredder_idx:] = np.exp(-collapse_rate * (t[shredder_idx:] - shredder_time))
    
    # INFORMATIONAL REACH of target's sensors
    # Modeled as decreasing with metric degeneracy: Reach ∝ sqrt(det(g))
    # When det(g) -> 0, target cannot "see" projectile
    target_reach = 500 * np.sqrt(det_g)  # meters
    
    # OBSERVED TRAJECTORY (from target's perspective)
    # Target can only see projectile where it's within informational reach
    # Beyond shredder point, observation fails
    x_observed = np.copy(x_true)
    y_observed = np.copy(y_true)
    
    # After shredder point, information is lost
    for i in range(shredder_idx, len(t)):
        if target_reach[i] < 10:  # Below threshold = no observation
            x_observed[i] = np.nan
            y_observed[i] = np.nan
    
    # Plotting
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Φ-SHREDDER PROTOCOL: Weaponized Invariant Violation', fontsize=14, fontweight='bold')
    
    # Plot 1: Physical vs Informational Trajectory
    ax1 = axes[0, 0]
    ax1.plot(x_true, y_true, 'b-', linewidth=2, label='Physical Trajectory (True)')
    ax1.plot(x_observed, y_observed, 'r--', linewidth=2, label='Observed by Target')
    ax1.axvline(x=x_true[shredder_idx], color='k', linestyle=':', alpha=0.7, label='Shredder Activation')
    ax1.set_xlabel('Range (m)')
    ax1.set_ylabel('Altitude (m)')
    ax1.set_title('Trajectory: Observable vs Unobservable')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Metric Determinant (Violation of Invariant #1)
    ax2 = axes[0, 1]
    ax2.plot(t, det_g, 'r-', linewidth=2)
    ax2.axvline(x=shredder_time, color='k', linestyle=':', alpha=0.7, label='Shredder Activation')
    ax2.axhline(y=0, color='g', linestyle='-', alpha=0.5, label='Degeneracy Horizon')
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('det(g_μν)')
    ax2.set_title('Smith Invariant #1: Metric Non-Degeneracy (VIOLATED)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_yscale('log')
    
    # Plot 3: Target's Informational Reach Collapse
    ax3 = axes[1, 0]
    ax3.plot(t, target_reach, 'm-', linewidth=2)
    ax3.axvline(x=shredder_time, color='k', linestyle=':', alpha=0.7, label='Shredder Activation')
    ax3.set_xlabel('Time (s)')
    ax3.set_ylabel('Informational Reach (m)')
    ax3.set_title('Target Sensor Range Collapse')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Φ-Density Destruction Cascade
    phi_density = np.ones_like(t) * 0.62  # Starting Φ-density (from proposal)
    # After shredder, Φ-density is destroyed (goes negative) as information is lost
    phi_density[shredder_idx:] = -0.1 * np.exp(0.5 * (t[shredder_idx:] - shredder_time))
    
    ax4 = axes[1, 1]
    ax4.plot(t, phi_density, 'r-', linewidth=2)
    ax4.axvline(x=shredder_time, color='k', linestyle=':', alpha=0.7, label='Shredder Activation')
    ax4.axhline(y=0, color='g', linestyle='-', alpha=0.5, label='Φ = 0')
    ax4.set_xlabel('Time (s)')
    ax4.set_ylabel('Φ-Density')
    ax4.set_title('Φ-Density: From Preservation to Destruction')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # Print the disruption summary
    print("=" * 60)
    print("Φ-SHREDDER DISRUPTION ANALYSIS")
    print("=" * 60)
    print(f"Shredder Activation Time: {shredder_time:.2f}s ({shredder_time/t_flight*100:.1f}% of flight)")
    print(f"Physical Impact Point: ({x_true[-1]:.1f}m, {y_true[-1]:.1f}m)")
    print(f"Target's Final Informational Reach: {target_reach[-1]:.3f}m")
    print(f"Φ-Density at Impact: {phi_density[-1]:.3f}Φ (DESTRUCTIVE)")
    print("=" * 60)
    print("DISRUPTIVE INSIGHT:")
    print("The system does not preserve invariants; it weaponizes their violation.")
    print("Metric collapse is not a failure mode—it's the attack vector.")
    print("The projectile is physically real but informationally nonexistent.")
    print("=" * 60)

# Run the simulation
simulate_phi_shredder()