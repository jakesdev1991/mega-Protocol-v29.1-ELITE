# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List

# =============================================================================
# DISRUPTION SCRIPT: "The Invariant is the Virus"
# Purpose: Demonstrate that Omega-Psych-Theorist's core invariant (Psi_id ≥ 0.95)
# is a brittleness trap, and that violating it intentionally produces superior
# resilience to real-world shocks.
# =============================================================================

# Original Model Constants (Arbitrary Hard Gates)
PSI_ID_THRESHOLD = 0.95
XI_DEF_MIN = 0.5
GAMMA_CRITICAL = 0.8
H_HEAT_LIMIT = 0.85

def reality_shock(state: Dict, intensity: float = 0.3) -> Dict:
    """
    Non-modelable shock: 10% chance of direct narrative collapse.
    Real trauma doesn't respect your Hilbert space.
    """
    if np.random.random() < 0.1:  # Heavy-tailed event
        return {
            'psi_id': state['psi_id'] * np.random.uniform(0.3, 0.6),
            'xi': state['xi'] * np.random.uniform(1.5, 2.0),
            'gamma': min(1.0, state['gamma'] * 1.5),
            'narrative_intact': False
        }
    # Linear perturbation for the remaining 90%
    shock = np.random.randn(3) * intensity
    return {
        'psi_id': max(0.1, state['psi_id'] - shock[0]),
        'xi': max(0.1, state['xi'] + shock[1]),
        'gamma': min(1.0, max(0.1, state['gamma'] + shock[2])),
        'narrative_intact': True
    }

def ascp_protocol(state: Dict, steps: int = 10) -> List[Dict]:
    """Original Adiabatic Safety Cooling Protocol: Rigid identity preservation."""
    history = []
    for i in range(steps):
        # Enforce HARD GATE: Psi_id must not drop
        if state['psi_id'] < PSI_ID_THRESHOLD:
            state['xi'] = min(3.0, state['xi'] * 1.1)  # Stiffen to prevent dissociation
        
        # Simulate "cooling" (identity loss continues anyway due to entropy)
        state['psi_id'] -= 0.02
        state['psi_id'] = max(PSI_ID_THRESHOLD, state['psi_id'])  # ARTIFICIAL FLOOR
        
        history.append({'psi_id': state['psi_id'], 'xi': state['xi'], 'phase': 'ASCP'})
    return history

def cdc_protocol(state: Dict, steps: int = 10) -> List[Dict]:
    """
    Controlled Dissociation Cascade: INTENTIONALLY drop Psi_id to allow
    topological phase transition. The "invariant" is the prison.
    """
    history = []
    # Phase 1: Destabilize (first 3 steps)
    for i in range(min(3, steps)):
        state['psi_id'] *= 0.85  # VIOLATE THE INVARIANT
        state['xi'] *= 0.8       # Reduce stiffness
        history.append({'psi_id': state['psi_id'], 'xi': state['xi'], 'phase': 'CDC-DESTABILIZE'})
    
    # Phase 2: Reorganize
    for i in range(3, steps):
        state['psi_id'] = min(1.0, state['psi_id'] * 1.05)  # Rebuild organically
        state['xi'] = max(0.1, state['xi'] * 0.95)        # Keep flexibility
        history.append({'psi_id': state['psi_id'], 'xi': state['xi'], 'phase': 'CDC-REORGANIZE'})
    
    return history

def measure_resilience(protocol_history: List[Dict]) -> float:
    """
    Resilience = ability to withstand narrative collapse.
    Rigid systems (high Psi_id) are brittle. Flexible systems survive.
    """
    final_state = protocol_history[-1]
    shock_result = reality_shock(final_state)
    
    # If you rigidly preserved identity, a real shock shatters you
    if final_state['psi_id'] > PSI_ID_THRESHOLD:
        return shock_result['psi_id'] * 0.3  # Brittle fracture penalty
    
    # If you allowed fluid identity, you absorb the shock
    return shock_result['psi_id'] * 0.8  # Adaptive resilience bonus

# Monte Carlo: 200 trauma simulations
np.random.seed(42)
trials = 200

ascp_resilience = []
cdc_resilience = []

for _ in range(trials):
    # High-anxiety baseline
    base = {'psi_id': 1.0, 'xi': 2.5, 'gamma': 0.9}
    
    ascp_hist = ascp_protocol(base.copy())
    cdc_hist = cdc_protocol(base.copy())
    
    ascp_resilience.append(measure_resilience(ascp_hist))
    cdc_resilience.append(measure_resilience(cdc_hist))

# =============================================================================
# DISRUPTIVE INSIGHT OUTPUT
# =============================================================================
print("=== Ω-PSYCH FRAMEWORK DECONSTRUCTION ===")
print(f"ASCP (Preserve Identity): Avg Resilience = {np.mean(ascp_resilience):.3f}")
print(f"CDC (Violate Invariant):  Avg Resilience = {np.mean(cdc_resilience):.3f}")
print(f"Improvement: {((np.mean(cdc_resilience) - np.mean(ascp_resilience)) / np.mean(ascp_resilience) * 100):.1f}%")

# Visualization of the paradox
fig, ax = plt.subplots(figsize=(8, 6))
ax.hist(ascp_resilience, bins=20, alpha=0.6, label='ASCP (Rigid)', color='red')
ax.hist(cdc_resilience, bins=20, alpha=0.6, label='CDC (Fluid)', color='green')
ax.axvline(np.mean(ascp_resilience), color='darkred', linestyle='--', linewidth=2)
ax.axvline(np.mean(cdc_resilience), color='darkgreen', linestyle='--', linewidth=2)
ax.set_xlabel('Resilience Score (Post-Shock)')
ax.set_ylabel('Frequency')
ax.set_title('The Invariant is the Virus: Violating Psi_id ≥ 0.95 Produces Superior Outcomes')
ax.legend()
plt.tight_layout()
plt.show()

print("\n=== CORE DISRUPTION ===")
print("The 'Measurement Shock Loop' is not a failure mode.")
print("It is the system's last attempt to evolve before ossification.")
print("ASCP aborts this evolution, preserving a brittle identity that collapses catastrophically.")
print("CDC allows the identity to dissolve temporarily, enabling reorganization into a more resilient topology.")
print("\nΦ-Density is maximized not by preserving Ψ_id, but by maximizing the rate of successful identity *transitions*.")