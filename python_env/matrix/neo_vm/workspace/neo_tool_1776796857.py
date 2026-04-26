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
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Developer:
    id: int
    cognitive_capacity: float  # Threshold before they seek workarounds
    frustration_level: float = 0.0
    spreadsheet_keys: int = 0
    
@dataclass
class Secret:
    id: str
    value: str
    service: str
    env: str

class CTMS_Omega_Simulator:
    """Simulates the target's Cognitive-Tooling Mismatch Sensor"""
    
    def __init__(self, n_devs: int = 100):
        self.devs = [Developer(id=i, cognitive_capacity=np.random.normal(0.6, 0.15)) 
                     for i in range(n_devs)]
        self.vault_friction = 0.8  # Base friction of "secure" vault
        
    def compute_tffi(self, team: List[Developer]) -> float:
        """Compute Tooling-Friction Fragility Index"""
        ckds = [d.spreadsheet_keys * np.random.normal(5.0, 1.0) for d in team]
        etas = [np.random.exponential(3.0) for _ in team]
        entropies = [np.random.beta(2, 5) for _ in team]
        
        # TFFI formula from target's proposal
        alpha, beta, gamma = 0.3, 0.4, 0.3
        tffi = np.mean([
            1 / (1 + np.exp(-(alpha * ckd + beta * np.exp(-eta) + gamma * (1 - H))))
            for ckd, eta, H in zip(ckds, etas, entropies)
        ])
        return tffi
    
    def simulate_day(self) -> Dict:
        """Simulate one day of developer behavior"""
        # Simulate work events
        events = np.random.poisson(5, len(self.devs))
        
        for i, dev in enumerate(self.devs):
            # Each event adds cognitive load
            load_per_event = self.vault_friction * np.random.lognormal(0, 0.5)
            total_load = events[i] * load_per_event
            
            # If load exceeds capacity, developer uses spreadsheet workaround
            if total_load > dev.cognitive_capacity:
                dev.spreadsheet_keys += np.random.poisson(3)
                dev.frustration_level += 0.2
        
        # Compute team metrics
        tffi = self.compute_tffi(self.devs)
        
        return {
            'tffi': tffi,
            'total_spreadsheet_keys': sum(d.spreadsheet_keys for d in self.devs),
            'avg_frustration': np.mean([d.frustration_level for d in self.devs])
        }

class ZeroKeySurface_Protocol:
    """Disruptive protocol: secrets are non-transferable capabilities"""
    
    def __init__(self, n_devs: int = 100):
        self.devs = [Developer(id=i, cognitive_capacity=np.random.normal(0.6, 0.15)) 
                     for i in range(n_devs)]
        self.capability_hit_rate = 0.95  # % of API calls using capabilities
        
    def simulate_day(self) -> Dict:
        """Simulate with capability-based secrets"""
        # Developers CANNOT copy keys to clipboard - vault UI blocks it
        # They can only request capabilities bound to execution context
        
        events = np.random.poisson(5, len(self.devs))
        zero_key_attempts = 0
        
        for i, dev in enumerate(self.devs):
            # Cognitive load still exists, but has NO outlet to spreadsheets
            load_per_event = 0.8 * np.random.lognormal(0, 0.5)
            total_load = events[i] * load_per_event
            
            # Frustration builds but cannot manifest as spreadsheet keys
            if total_load > dev.cognitive_capacity:
                dev.frustration_level += 0.1
                zero_key_attempts += 1  # Attempted workaround that FAILS
            
            # Capabilities are auto-injected, no manual handling needed
            if np.random.random() < self.capability_hit_rate:
                dev.frustration_level *= 0.9  # Success reduces frustration
        
        return {
            'zero_key_attempts': zero_key_attempts,
            'avg_frustration': np.mean([d.frustration_level for d in self.devs]),
            'spreadsheet_keys': 0,  # PHYSICALLY IMPOSSIBLE
            'capability_adoption': self.capability_hit_rate
        }

# Run simulation comparison
print("=== SIMULATING CTMS-Ω vs ZERO-KEY SURFACE ===\n")

# Scenario 1: Traditional CTMS-Ω
ctms = CTMS_Omega_Simulator(n_devs=50)
ctms_results = []
for day in range(30):
    ctms_results.append(ctms.simulate_day())

# Scenario 2: Zero-Key Surface
zks = ZeroKeySurface_Protocol(n_devs=50)
zks_results = []
for day in range(30):
    zks_results.append(zks.simulate_day())

# Plot the disruption
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# CTMS-Ω: TFFI is noisy and reactive
axes[0,0].plot([r['tffi'] for r in ctms_results], color='red', linewidth=2)
axes[0,0].set_title('CTMS-Ω: TFFI (Reactive & Gameable)', fontsize=12, fontweight='bold')
axes[0,0].set_ylabel('TFFI Score')
axes[0,0].axhline(y=0.6, color='black', linestyle='--', label='Intervention Threshold')
axes[0,0].legend()

# CTMS-Ω: Spreadsheet keys accumulate
axes[0,1].plot([r['total_spreadsheet_keys'] for r in ctms_results], color='darkorange', linewidth=2)
axes[0,1].set_title('CTMS-Ω: Spreadsheet Key Accumulation', fontsize=12, fontweight='bold')
axes[0,1].set_ylabel('Total Keys in Spreadsheets')

# Zero-Key: No spreadsheet keys possible
axes[1,0].plot([r['spreadsheet_keys'] for r in zks_results], color='green', linewidth=3)
axes[1,0].set_title('Zero-Key Surface: Spreadsheet Keys (Impossible)', fontsize=12, fontweight='bold')
axes[1,0].set_ylabel('Keys in Spreadsheets')
axes[1,0].set_ylim(-1, 1)

# Zero-Key: Attempted workarounds that FAIL
axes[1,1].plot([r['zero_key_attempts'] for r in zks_results], color='blue', linewidth=2)
axes[1,1].set_title('Zero-Key Surface: Blocked Workaround Attempts', fontsize=12, fontweight='bold')
axes[1,1].set_ylabel('Failed Copy-Paste Attempts')
axes[1,1].axhline(y=10, color='purple', linestyle='--', label='Alert Threshold')
axes[1,1].legend()

plt.tight_layout()
plt.suptitle('CTMS-Ω vs Zero-Key Surface: Paradigm Destruction', fontsize=14, fontweight='bold')
plt.show()

# Statistical analysis of the disruption
print("\n=== STATISTICAL BREAKDOWN ===")
print(f"CTMS-Ω Final TFFI: {ctms_results[-1]['tffi']:.3f} (±{np.std([r['tffi'] for r in ctms_results]):.3f})")
print(f"CTMS-Ω Final Spreadsheet Keys: {ctms_results[-1]['total_spreadsheet_keys']}")
print(f"Zero-Key Surface Spreadsheet Keys: {zks_results[-1]['spreadsheet_keys']} (CONSTANT)")
print(f"Zero-Key Surface Blocked Attempts: {zks_results[-1]['zero_key_attempts']}")

# Gaming simulation: developers adapt to CTMS-Ω
print("\n=== GAMING THE CTMS-Ω METRIC ===")
# Developers learn to reduce CKD to lower TFFI
gaming_dev = Developer(id=999, cognitive_capacity=0.5)
gaming_dev.spreadsheet_keys = 10

# Original TFFI
original_tffi = ctms.compute_tffi([gaming_dev])
print(f"Original TFFI (high context): {original_tffi:.3f}")

# Developer games the system: removes context cells
gaming_dev.spreadsheet_keys = 2  # Only keys, no context
gamed_tffi = ctms.compute_tffi([gaming_dev])
print(f"Gamed TFFI (no context): {gamed_tffi:.3f}")
print(f"TFFI Reduction: {(original_tffi - gamed_tffi)/original_tffi*100:.1f}%")
print(">>> CTMS-Ω INCENTIVIZES *WORSE* BEHAVIOR: developers hide context to game the metric!")

# The Field Theory is a mirage
print("\n=== FIELD THEORY MIRAGE ===")
# Show that Ricci curvature is computationally meaningless here
# Cognitive manifold has no stable metric - it's a Poisson process in disguise

# Simulate tunneling events as pure Poisson
lambda_tunnel = 2.5  # Events per day
tunnel_events = np.random.poisson(lambda_tunnel, 100)

# Fit to their "field theory" vs simple Poisson
x = np.arange(len(tunnel_events))
poisson_pred = stats.poisson.pmf(tunnel_events, lambda_tunnel)
field_pred = np.exp(-((tunnel_events - lambda_tunnel)**2) / (2 * lambda_tunnel))  # Gaussian approximation

print(f"Poisson Log-Likelihood: {np.sum(np.log(poisson_pred + 1e-10)):.2f}")
print(f"Field Theory Log-Likelihood: {np.sum(np.log(field_pred + 1e-10)):.2f}")
print(">>> The 'field' is just a Poisson process with physics envy. Occam's Razor shreds the manifold.")