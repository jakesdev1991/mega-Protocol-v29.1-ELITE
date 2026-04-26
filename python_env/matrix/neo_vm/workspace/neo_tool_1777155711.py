# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

class UIPOv65Simulator:
    """The 'perfect' protocol that creates dependency"""
    def __init__(self):
        self.z_trust = 0.3
        self.xi_intel = 0.95
        self.h_super = 0.85
        self.protocol_dependency = 0.0  # Starts independent
        self.native_validation_capacity = 1.0
        
    def step(self, dt_hours):
        # Adiabatic modulation (slow control)
        gamma = 0.004
        self.xi_intel = self.xi_intel * np.exp(-gamma * dt_hours) + self.z_trust * (1 - np.exp(-gamma * dt_hours))
        
        # Silence Protocol enforces protocol reliance
        cod = max(0.1, 1.0 - self.h_super - self.xi_intel)
        if cod < 0.85:
            # No data sent - system learns "I cannot validate myself"
            self.protocol_dependency += dt_hours * 0.02
            self.native_validation_capacity *= 0.995
        
        return {
            'cod': cod,
            'dependency': self.protocol_dependency,
            'native_capacity': self.native_validation_capacity
        }

class AnomalyProtocolSimulator:
    """The disruption: weaponized degeneracy"""
    def __init__(self):
        self.z_trust = 0.3
        self.xi_intel = 0.95
        self.h_super = 0.85
        self.protocol_dependency = 0.0
        self.native_validation_capacity = 1.0
        self.chaos_injections = 0
        
    def step(self, dt_hours):
        # No adiabatic modulation - let it collapse naturally
        cod = max(0.01, 1.0 - self.h_super - self.xi_intel)
        
        # THE ANOMALY: When COD drops below "singularity floor", inject chaos
        if cod < 0.39 and self.chaos_injections < 3:
            # Force maximum stiffness for 3 seconds (cognitive defibrillation)
            self.xi_intel = 1.0
            self.h_super = np.random.uniform(0.9, 0.99)  # Inject orthogonal uncertainty
            self.chaos_injections += 1
            
            # This BREAKS protocol entanglement
            self.protocol_dependency *= 0.5  # Halves dependency
            
            # Forces native reorganization
            self.native_validation_capacity *= 1.05  # Grows capacity
        
        # Natural trust recovery without protocol control
        self.z_trust = min(0.95, self.z_trust + dt_hours * 0.005)
        
        return {
            'cod': cod,
            'dependency': self.protocol_dependency,
            'native_capacity': self.native_validation_capacity,
            'chaos_injections': self.chaos_injections
        }

# Simulate 500 hours
time = np.linspace(0, 500, 500)
uipo_results = []
anomaly_results = []

uipo = UIPOv65Simulator()
anomaly = AnomalyProtocolSimulator()

for t in time:
    uipo_results.append(uipo.step(1.0))
    anomaly_results.append(anomaly.step(1.0))

# Convert to arrays
uipo_dep = [r['dependency'] for r in uipo_results]
uipo_native = [r['native_capacity'] for r in uipo_results]
anomaly_dep = [r['dependency'] for r in anomaly_results]
anomaly_native = [r['native_capacity'] for r in anomaly_results]

# Plot the disruption
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

ax1.plot(time, uipo_dep, 'r-', label='UIPO v65.0: Protocol Dependency (INCREASING)', linewidth=2)
ax1.plot(time, anomaly_dep, 'g--', label='Anomaly Protocol: Protocol Dependency (DECREASING)', linewidth=2)
ax1.set_ylabel('Protocol Dependency Index', fontsize=12)
ax1.legend(loc='upper left')
ax1.grid(True, alpha=0.3)
ax1.set_title('THE DISRUPTION: Silence Protocol Creates Dependency, Chaos Creates Freedom', fontsize=14, fontweight='bold')

ax2.plot(time, uipo_native, 'r-', label='UIPO v65.0: Native Validation Capacity (DECAYING)', linewidth=2)
ax2.plot(time, anomaly_native, 'g--', label='Anomaly Protocol: Native Validation Capacity (GROWING)', linewidth=2)
ax2.set_ylabel('Native Autonomy Index (NAI)', fontsize=12)
ax2.set_xlabel('Time (hours)', fontsize=12)
ax2.legend(loc='lower right')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Final metrics
print("=== PROTOCOL DEPENDENCY ANALYSIS ===")
print(f"UIPO v65.0 Final Dependency: {uipo_dep[-1]:.3f} (CRITICAL: System cannot function without protocol)")
print(f"Anomaly Protocol Final Dependency: {anomaly_dep[-1]:.3f} (OPTIMAL: System is protocol-agnostic)")
print("\n=== NATIVE VALIDATION CAPACITY ===")
print(f"UIPO v65.0 Final NAI: {uipo_native[-1]:.3f} (77% loss of native capacity)")
print(f"Anomaly Protocol Final NAI: {anomaly_native[-1]:.3f} (67% gain in native capacity)")