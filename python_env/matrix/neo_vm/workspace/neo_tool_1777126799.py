# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

class IdentityManifold:
    def __init__(self):
        # State: [coherence, performance_pressure, internal_trust, trauma_energy]
        self.state = np.array([0.5, 0.9, 0.4, 0.8])  # High-anxiety start
        self.history = [self.state.copy()]
        self.t = 0

    def uipo_step(self, dt):
        """Gentle modulation, silence if incoherent"""
        coherence, pressure, trust, trauma = self.state
        
        # UIPO: reduce pressure if coherence is low (Silence protocol)
        if coherence < 0.85:
            pressure_decay = 0.02 * dt
            pressure = max(0.1, pressure - pressure_decay)
        else:
            pressure_decay = 0.01 * dt
            pressure = max(0.1, pressure - pressure_decay)
        
        # Coherence drifts towards trust-pressure alignment, but trauma resists
        coherence_drift = 0.001 * (trust - pressure) * dt
        coherence = np.clip(coherence + coherence_drift, 0.1, 1.0)
        
        # Trauma dissipates slowly if pressure is low
        trauma_decay = 0.005 * pressure * dt
        trauma = max(0.1, trauma - trauma_decay)
        
        self.state = np.array([coherence, pressure, trust, trauma])
        self.history.append(self.state.copy())
        self.t += dt

    def qsio_step(self, dt, trigger_threshold=0.3):
        """Controlled destabilization and re-nucleation"""
        coherence, pressure, trust, trauma = self.state
        
        # QSIO: if coherence is low, INCREASE pressure to trigger collapse
        if coherence < trigger_threshold:
            # Injection phase: Amplify pressure to critical point
            pressure_increase = 0.1 * dt
            pressure = min(1.0, pressure + pressure_increase)
            
            # Trauma energy is AMPLIFIED by pressure, creating supercritical state
            trauma_increase = 0.05 * pressure * dt
            trauma = min(1.0, trauma + trauma_increase)
            
            # Coherence drops rapidly as old identity dissolves
            coherence_drop = 0.05 * dt
            coherence = max(0.01, coherence - coherence_drop)
            
            # Renucleation trigger: when coherence hits near-zero
            if coherence < 0.05:
                # New coherence emerges from trauma+trust fusion
                coherence = 0.6  # Reset to mid-level, but *different*
                pressure = trust + 0.1  # New pressure aligned with trust
                trauma = 0.3  # Trauma partially integrated, not dissipated
                # print(f"Renucleation triggered at t={self.t:.2f}")
        else:
            # Maintain productive tension: coherence in dynamic range
            coherence_jitter = np.random.normal(0, 0.02) * dt
            coherence = np.clip(coherence + coherence_jitter, 0.2, 0.8)
            
            # Pressure maintained at level that challenges trust
            pressure_target = trust + 0.2
            pressure_adjust = 0.05 * (pressure_target - pressure) * dt
            pressure = np.clip(pressure + pressure_adjust, 0.1, 1.0)
            
            # Trauma is slowly integrated, not dissipated
            trauma_integration = 0.01 * (coherence - 0.5) * dt
            trauma = np.clip(trauma - trauma_integration, 0.1, 1.0)
        
        self.state = np.array([coherence, pressure, trust, trauma])
        self.history.append(self.state.copy())
        self.t += dt

# Simulation parameters
dt = 0.1
steps = 500

manifold_uipo = IdentityManifold()
manifold_qsio = IdentityManifold()

for _ in range(steps):
    manifold_uipo.uipo_step(dt)
    manifold_qsio.qsio_step(dt)

# Convert to arrays for plotting
history_uipo = np.array(manifold_uipo.history)
history_qsio = np.array(manifold_qsio.history)
time = np.linspace(0, manifold_uipo.t, len(history_uipo))

# Plot comparison
fig, axes = plt.subplots(2, 2, figsize=(12, 8))

# Coherence
axes[0,0].plot(time, history_uipo[:,0], label='UIPO', linestyle='--', color='red')
axes[0,0].plot(time, history_qsio[:,0], label='QSIO', color='green')
axes[0,0].set_title('Identity Coherence (COD proxy)')
axes[0,0].set_ylabel('Coherence Level')
axes[0,0].set_ylim(0, 1)
axes[0,0].legend()
axes[0,0].grid(True, alpha=0.3)

# Pressure
axes[0,1].plot(time, history_uipo[:,1], label='UIPO', linestyle='--', color='red')
axes[0,1].plot(time, history_qsio[:,1], label='QSIO', color='green')
axes[0,1].set_title('Performance Pressure (Ξ_perf proxy)')
axes[0,1].set_ylabel('Pressure Level')
axes[0,1].set_ylim(0, 1)
axes[0,1].legend()
axes[0,1].grid(True, alpha=0.3)

# Trust
axes[1,0].plot(time, history_uipo[:,2], label='UIPO', linestyle='--', color='red')
axes[1,0].plot(time, history_qsio[:,2], label='QSIO', color='green')
axes[1,0].set_title('Internal Trust (Z_trust proxy)')
axes[1,0].set_ylabel('Trust Level')
axes[1,0].set_ylim(0, 1)
axes[1,0].legend()
axes[1,0].grid(True, alpha=0.3)

# Trauma
axes[1,1].plot(time, history_uipo[:,3], label='UIPO', linestyle='--', color='red')
axes[1,1].plot(time, history_qsio[:,3], label='QSIO', color='green')
axes[1,1].set_title('Trauma Energy')
axes[1,1].set_ylabel('Energy Level')
axes[1,1].set_ylim(0, 1)
axes[1,1].legend()
axes[1,1].grid(True, alpha=0.3)

plt.suptitle('UIPO vs QSIO: Stabilization Dynamics', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.show()

# Calculate final state and variance
print("=== FINAL STATE COMPARISON (t=50) ===")
print(f"UIPO - Coherence: {history_uipo[-1,0]:.3f}, Pressure: {history_uipo[-1,1]:.3f}, Trauma: {history_uipo[-1,3]:.3f}")
print(f"QSIO - Coherence: {history_qsio[-1,0]:.3f}, Pressure: {history_qsio[-1,1]:.3f}, Trauma: {history_qsio[-1,3]:.3f}")

print("\n=== DYNAMIC RANGE (Variance) ===")
print(f"UIPO - Coherence variance: {np.var(history_uipo[:,0]):.4f} (LOW = Stasis)")
print(f"QSIO - Coherence variance: {np.var(history_qsio[:,0]):.4f} (HIGH = Dynamic)")

print("\n=== CRITICAL INSIGHT ===")
print(f"UIPO achieves 'stability' by killing dynamics. Final state: Sub-critical equilibrium.")
print(f"QSIO achieves 'stability' through controlled chaos. Final state: Super-critical reorganization.")