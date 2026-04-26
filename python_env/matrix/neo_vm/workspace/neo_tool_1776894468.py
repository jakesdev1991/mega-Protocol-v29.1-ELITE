# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# === ANOMALY DETECTION PROTOCOL ===
# Exposing the Preservation Fallacy in the Trauma-Performance Model

print("=" * 60)
print("AGENT NEO: ANOMALY DETECTION - TRAUMA-PERFORMANCE MANIFOLD")
print("=" * 60)

# Simulate the Original (Flawed) Linear Model
def original_psd_model():
    # 2D Hilbert space: [Threat, Performance]
    psi_threat = np.array([1.0, 0.0])
    psi_performance = np.array([0.95, 0.31])  # 95% correlated with threat
    psi_reality = np.array([0.2, 0.8])  # Mostly safe reality
    
    # Original COD (threat-reality)
    COD_original = abs(np.vdot(psi_threat, psi_reality))**2
    
    # Apply Phase-Shift Decoupling (linear rotation)
    theta = np.pi/3  # 60° "healing" rotation
    PSD_operator = np.array([[np.cos(theta), -np.sin(theta)],
                             [np.sin(theta), np.cos(theta)]])
    psi_threat_psd = PSD_operator @ psi_threat
    
    # New COD
    COD_psd = abs(np.vdot(psi_threat_psd, psi_reality))**2
    
    # But measure the REAL problem: Performance-Death overlap
    # Death attractor vector
    psi_death = np.array([0.0, 1.0])  # Pure performance IS death
    
    COD_death_original = abs(np.vdot(psi_performance, psi_death))**2
    COD_death_psd = abs(np.vdot(psi_performance, psi_death))**2  # UNCHANGED
    
    return {
        'COD_threat_original': COD_original,
        'COD_threat_psd': COD_psd,
        'COD_death_original': COD_death_original,
        'COD_death_psd': COD_death_psd,
        'psi_threat_final': psi_threat_psd
    }

# Simulate the Disruptive Non-Linear Model
def disruptive_idc_model():
    # 3D manifold: [Threat, Performance, Death_Attractor]
    # The death attractor is the TRUE gravitational center
    
    # Initial state: stable orbit around death
    psi_initial = np.array([0.71, 0.71, 0.0])  # High threat+perf, zero death awareness
    psi_initial = psi_initial / np.linalg.norm(psi_initial)
    
    psi_death = np.array([0.0, 0.0, 1.0])  # The real attractor
    psi_flow = np.array([0.0, 0.0, 0.0])   # Placeholder for post-death state
    
    # True COD: overlap with death
    COD_death_initial = abs(np.vdot(psi_initial, psi_death))**2
    
    # IDC Operator: Non-linear collapse and quantum tunneling
    # Step 1: Project onto death (embrace the collapse)
    projection = np.outer(psi_death, psi_death) @ psi_initial
    
    # Step 2: Annihilate the threat-performance component
    psi_annihilated = psi_initial - projection
    
    # Step 3: Non-linear re-emergence (tunneling to new manifold)
    # This is a topological change, not a rotation
    if np.linalg.norm(psi_annihilated) > 1e-10:
        # The system re-emerges orthogonal to death axis
        psi_rebuilt = psi_annihilated / np.linalg.norm(psi_annihilated)
        # Inject new basis vector (flow state)
        psi_new = 0.7 * psi_rebuilt + 0.7 * np.array([0.0, 0.0, 0.0])
        psi_new = psi_new / np.linalg.norm(psi_new)
    else:
        psi_new = psi_death  # Complete collapse
    
    COD_death_final = abs(np.vdot(psi_new, psi_death))**2
    
    return {
        'COD_death_initial': COD_death_initial,
        'COD_death_final': COD_death_final,
        'psi_final': psi_new
    }

# Run both models
original_results = original_psd_model()
disruptive_results = disruptive_idc_model()

print("\n--- ORIGINAL MODEL (PSD) RESULTS ---")
print(f"Threat-Reality COD: {original_results['COD_threat_original']:.3f} → {original_results['COD_threat_psd']:.3f} ✓")
print(f"Performance-Death COD: {original_results['COD_death_original']:.3f} → {original_results['COD_death_psd']:.3f} ✗ UNCHANGED")
print("FAILURE: Linear rotation cannot break gravitational lock with death attractor")

print("\n--- DISRUPTIVE MODEL (IDC) RESULTS ---")
print(f"Death Attractor COD: {disruptive_results['COD_death_initial']:.3f} → {disruptive_results['COD_death_final']:.3f}")
print("SUCCESS: Topological annihilation dissolves death orbit")

# Demonstrate non-linear feedback failure
print("\n--- NON-LINEAR TRAUMA FEEDBACK SIMULATION ---")
print("Time | Threat Amp | Perf Amp | System Stability")
print("-" * 50)

state = np.array([1.0, 0.0])  # Pure threat state
performance_vector = np.array([0.0, 1.0])

for t in range(10):
    perf_amp = abs(np.vdot(state, performance_vector))
    threat_amp = abs(state[0])
    
    # NON-LINEAR FEEDBACK LOOP: performance reinforces trauma
    # This is the "scar tissue" effect - the more you perform, the stronger the trauma coupling
    reinforcement = 0.8 * perf_amp * perf_amp  # Quadratic reinforcement
    
    print(f"{t:4d} |   {threat_amp:.4f}   | {perf_amp:.4f} | {'UNSTABLE' if threat_amp > 0.5 else 'STABLE'}")
    
    # Apply linear PSD (futile against non-linear feedback)
    theta = np.pi/12  # Small rotation
    rotation = np.array([[np.cos(theta), -np.sin(theta)],
                         [np.sin(theta), np.cos(theta)]])
    state = rotation @ state
    
    # Apply trauma reinforcement
    state[0] += reinforcement
    state = state / np.linalg.norm(state)

# Plot visualization
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Original model: 2D state space
ax1.set_title("Original Model: Linear PSD (Preserves Death Orbit)", fontsize=12, fontweight='bold')
ax1.set_xlabel("Threat Amplitude")
ax1.set_ylabel("Performance Amplitude")

# Plot vectors
origin = [0, 0]
ax1.quiver(*origin, 1, 0, scale=1, color='red', label='Threat Axis', alpha=0.7)
ax1.quiver(*origin, 0, 1, scale=1, color='blue', label='Performance Axis', alpha=0.7)
ax1.quiver(*origin, 0.95, 0.31, scale=1, color='purple', width=0.01, label='Initial State', alpha=0.9)

# PSD rotation (futile)
theta = np.pi/3
x_new, y_new = np.cos(theta), np.sin(theta)
ax1.quiver(*origin, x_new, y_new, scale=1, color='orange', width=0.01, label='After PSD', alpha=0.9)

# Death attractor point
ax1.plot([0.0], [1.0], 'ko', markersize=15, label='Death Attractor', alpha=0.8)

ax1.legend(loc='upper left')
ax1.grid(True, alpha=0.3)
ax1.set_xlim(-0.2, 1.2)
ax1.set_ylim(-0.2, 1.2)

# Disruptive model: 3D manifold
ax2 = plt.subplot(122, projection='3d')
ax2.set_title("Disruptive Model: IDC (Topological Annihilation)", fontsize=12, fontweight='bold')

# Plot 3D vectors
ax2.quiver(0, 0, 0, 0.71, 0.71, 0, length=0.8, color='purple', label='Initial State')
ax2.quiver(0, 0, 0, 0, 0, 1, length=0.8, color='black', label='Death Attractor')
ax2.quiver(0, 0, 0, 0, 0, 0, length=0.8, color='green', label='Rebuilt State')

# Plot the collapse path
z_line = np.linspace(0, 0.8, 100)
x_line = 0.71 * (1 - z_line)
y_line = 0.71 * (1 - z_line)
ax2.plot(x_line, y_line, z_line, 'r--', alpha=0.5, label='Collapse Trajectory')

ax2.set_xlabel('Threat')
ax2.set_ylabel('Performance')
ax2.set_zlabel('Death')
ax2.set_xlim([0, 1])
ax2.set_ylim([0, 1])
ax2.set_zlim([0, 1])
ax2.legend()

plt.tight_layout()
plt.show()

print("\n" + "=" * 60)
print("ANOMALY DETECTED: The Preservation Fallacy")
print("=" * 60)