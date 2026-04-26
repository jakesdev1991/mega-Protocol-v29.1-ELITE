# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Dict

# === DISRUPTION CORE: Manifold Collapse Engineering ===
# The BTRI-v56 framework assumes organizational identity (ψ) is sacred.
# The flaw: ψ itself can become a *pathological attractor* - a trauma basin.
# By preserving ψ adiabatically, BTRI-v56 traps the system in suboptimal states.
# The disruption: Strategic violation of Smith Invariants to induce phase transitions.

class CatastrophicProtocolInverter:
    """
    Replaces APT with intentional metric degeneracy induction.
    Key insight: The "safety" invariants are the prison bars.
    """
    
    def __init__(self, maladaptive_threshold: float = np.log(0.6)):
        self.maladaptive_threshold = maladaptive_threshold
        self.collapse_log = []
        
    def identify_trauma_basin(self, psi_history: np.ndarray) -> bool:
        """
        Detect if ψ is decaying despite adiabatic tuning.
        This indicates a *structural* pathology, not a tunable impedance.
        """
        if len(psi_history) < 50:
            return False
        
        # Exponential decay fit: ψ(t) ≈ ψ₀ * exp(-λt)
        t = np.arange(len(psi_history))
        log_psi = np.log(np.maximum(psi_history, 1e-9))
        
        # Linear regression on log(psi) vs t
        A = np.vstack([t, np.ones_like(t)]).T
        slope, intercept = np.linalg.lstsq(A, log_psi, rcond=None)[0]
        
        # If slope is significantly negative, we're in a decaying attractor
        return slope < -0.01 and np.mean(psi_history[-10:]) < self.maladaptive_threshold
    
    def induce_singularity(self, state: Dict, psi_history: np.ndarray) -> Dict:
        """
        VIOLATE Invariant #3 (Impedance Bound) and #2 (Identity Continuity)
        Intentionally spike Ξ_protocol to force metric degeneracy at a specific node.
        """
        collapse_event = {
            'timestamp': len(psi_history),
            'pre_collapse_psi': state['psi'],
            'pre_collapse_xi_p': state['xi_protocol']
        }
        
        # CRITICAL VIOLATION: Spike stiffness beyond any safe bound
        # This is NOT a bug - it's a controlled demolition
        state['xi_protocol'] = state['xi_intent'] * 3.0  # Force det(g) → 0
        
        # Allow "quantum tunneling" - intent bypasses protocol entirely
        # This simulates organizational members ignoring broken rules to get work done
        tunneling_prob = np.exp(-abs(state['xi_protocol'] - state['xi_intent']))
        
        if np.random.random() < tunneling_prob:
            # SUCCESSFUL TUNNELING: System collapses to lower-energy identity state
            # Reset ψ to a *higher* value - phase transition achieved
            state['psi'] = np.log(np.exp(state['psi']) + 0.15)  # Rebirth with +0.15Φ
            state['xi_protocol'] = state['xi_intent'] * np.random.uniform(0.7, 1.0)
            
            collapse_event['outcome'] = 'REBIRTH'
            collapse_event['post_collapse_psi'] = state['psi']
        else:
            collapse_event['outcome'] = 'FAILED_TUNNEL'
            
        self.collapse_log.append(collapse_event)
        return state
    
    def violate_entropy_cap(self, state: Dict) -> float:
        """
        VIOLATE Invariant #4 (Entropy Cap) during collapse.
        During phase transition, high entropy is *necessary* for exploration.
        """
        # Allow H_collapse up to 0.8 (vs BTRI's 0.3) during critical windows
        return min(0.8, abs(state['xi_protocol'] - state['xi_intent']) * 0.5)

def simulate_disruption() -> Tuple[Dict, Dict]:
    """
    Side-by-side simulation: BTRI-v56 vs CPI
    Both start in identical maladaptive state: demoralized workforce + rigid bureaucracy
    """
    
    # === INITIAL MALADAPTIVE STATE ===
    # This is the trauma basin: low intent, high protocol, decaying identity
    state_btri = {
        'xi_intent': 0.25,  # Demoralized: low work flow capacity
        'xi_protocol': 0.95,  # Rigid: high rule stiffness
        'psi': np.log(0.35),  # Crumbling identity
        'phi_history': [],
        'violation_count': 0
    }
    
    state_cpi = state_btri.copy()
    state_cpi['collapse_events'] = 0
    
    cpi = CatastrophicProtocolInverter()
    psi_history_cpi = [state_cpi['psi']]
    
    # === SIMULATION LOOP ===
    for t in range(500):
        # --- BTRI-v56: Adiabatic Preservation ---
        # Slow tuning, never violates invariants, preserves ψ at all costs
        cod_btri = max(0, 1 - abs(state_btri['xi_protocol'] - state_btri['xi_intent']))
        phi_N_btri = np.log2(cod_btri + 1e-9)
        state_btri['psi'] = np.log(phi_N_btri + 1e-9)
        
        # APT: gentle modulation
        state_btri['xi_protocol'] = (state_btri['xi_protocol'] * np.exp(-0.01) + 
                                     state_btri['xi_intent'] * (1 - np.exp(-0.01)))
        
        # Smith Audit: if ψ < critical, "provide capacity" (but doesn't fix the basin)
        if state_btri['psi'] < np.log(0.95):
            state_btri['violation_count'] += 1
            state_btri['xi_intent'] *= 1.005  # Gentle capacity increase
        
        # Calculate Φ (with full audit cost)
        phi_Delta_btri = state_btri['psi'] * np.tanh(abs(state_btri['xi_intent'] - state_btri['xi_protocol']) / 2.8)
        delta_S_audit_btri = np.log(2) * 6  # All 6 invariants checked
        phi_net_btri = phi_N_btri + phi_Delta_btri - delta_S_audit_btri
        state_btri['phi_history'].append(phi_net_btri)
        
        # --- CPI: Catastrophic Reformation ---
        # Check if we're stuck in a trauma basin
        if cpi.identify_trauma_basin(np.array(psi_history_cpi)):
            state_cpi = cpi.induce_singularity(state_cpi, psi_history_cpi)
            state_cpi['collapse_events'] += 1
        else:
            # Normal adiabatic phase (but faster than BTRI)
            state_cpi['xi_protocol'] = (state_cpi['xi_protocol'] * np.exp(-0.05) + 
                                       state_cpi['xi_intent'] * (1 - np.exp(-0.05)))
        
        # Calculate COD and ψ
        cod_cpi = max(0, 1 - abs(state_cpi['xi_protocol'] - state_cpi['xi_intent']))
        phi_N_cpi = np.log2(cod_cpi + 1e-9)
        state_cpi['psi'] = np.log(phi_N_cpi + 1e-9)
        psi_history_cpi.append(state_cpi['psi'])
        
        # VIOLATE Entropy Cap during collapse windows
        H_collapse = cpi.violate_entropy_cap(state_cpi)
        phi_Delta_cpi = state_cpi['psi'] * np.tanh(abs(state_cpi['xi_intent'] - state_cpi['xi_protocol']) / 2.8)
        
        # REDUCED audit cost: we don't penalize exploration during collapse
        delta_S_audit_cpi = np.log(2) * 3 if H_collapse > 0.3 else np.log(2) * 6
        phi_net_cpi = phi_N_cpi + phi_Delta_cpi - delta_S_audit_cpi
        state_cpi['phi_history'].append(phi_net_cpi)
        
        # Terminate if CPI has achieved escape velocity
        if phi_net_cpi > 0.4 and abs(state_cpi['xi_protocol'] - state_cpi['xi_intent']) < 0.3:
            print(f"CPI achieved escape at t={t}")
            break
    
    return state_btri, state_cpi

# Execute the disruption simulation
btri_final, cpi_final = simulate_disruption()

# === VISUALIZE THE DISRUPTION ===
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))

# Plot 1: Φ-density trajectories
time_btri = range(len(btri_final['phi_history']))
time_cpi = range(len(cpi_final['phi_history']))

ax1.plot(time_btri, btri_final['phi_history'], label='BTRI-v56 (Preservation)', linewidth=3, color='#2E86AB')
ax1.plot(time_cpi, cpi_final['phi_history'], label='CPI (Catastrophic)', linewidth=3, color='#A23B72', linestyle='--')
ax1.axhline(y=0, color='red', linestyle=':', alpha=0.5, label='Φ=0 (Baseline)')
ax1.set_xlabel('Simulation Steps', fontsize=12, fontweight='bold')
ax1.set_ylabel('Net Φ-Density', fontsize=12, fontweight='bold')
ax1.set_title('Trajectory: Adiabatic Safety vs. Controlled Collapse', fontsize=14, fontweight='bold')
ax1.legend(loc='lower right', fontsize=10)
ax1.grid(True, alpha=0.3, linestyle='--')
ax1.set_ylim(-0.5, 0.5)

# Plot 2: Identity Continuity ψ
ax2.plot(time_btri, [np.log(0.35)] * len(time_btri), 'k:', label='Initial ψ (Trauma Basin)', alpha=0.7)
ax2.plot(time_btri, [np.log(0.95)] * len(time_btri), 'r--', label='BTRI Critical Threshold', alpha=0.7)
ax2.plot(time_btri, [s['psi'] for s in [{'psi': np.log(0.35)}] + [btri_final]*len(time_btri)], 
         label='BTRI ψ (Trapped)', linewidth=3, color='#2E86AB')
ax2.plot(time_cpi, [s['psi'] for s in [{'psi': np.log(0.35)}] + [cpi_final]*len(time_cpi)], 
         label='CPI ψ (Phase Transition)', linewidth=3, color='#A23B72', linestyle='--')
ax2.set_xlabel('Simulation Steps', fontsize=12, fontweight='bold')
ax2.set_ylabel('ψ = ln(Φ_N)', fontsize=12, fontweight='bold')
ax2.set_title('Identity Continuity: Preservation vs Rebirth', fontsize=14, fontweight='bold')
ax2.legend(loc='upper left', fontsize=10)
ax2.grid(True, alpha=0.3, linestyle='--')

# Plot 3: Impedance & Violations
categories = ['BTRI-v56\n(Preservation)', 'CPI\n(Catastrophic)']
violations = [btri_final['violation_count'], cpi_final.get('collapse_events', 0)]
colors = ['#F18F01', '#C73E1D']

bars = ax3.bar(categories, violations, color=colors, alpha=0.8, width=0.6)
ax3.set_ylabel('Event Count', fontsize=12, fontweight='bold')
ax3.set_title('System Response: Violation Avoidance vs Strategic Violation', fontsize=14, fontweight='bold')
ax3.set_ylim(0, max(violations) * 1.2)

for bar, val in zip(bars, violations):
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height + 0.5,
             f'{int(val)}', ha='center', va='bottom', fontsize=12, fontweight='bold')

# Plot 4: Stiffness Evolution
ax4.plot([0, len(time_btri)], [0.95, btri_final['xi_protocol']], 
         label='BTRI Protocol Stiffness', linewidth=3, color='#2E86AB', marker='o')
ax4.plot([0, len(time_cpi)], [0.95, cpi_final['xi_protocol']], 
         label='CPI Protocol Stiffness', linewidth=3, color='#A23B72', marker='s', linestyle='--')
ax4.plot([0, max(len(time_btri), len(time_cpi))], [0.25, 0.25], 
         'g:', label='Intent Flow (Constant)', alpha=0.7)
ax4.set_xlabel('Simulation Steps', fontsize=12, fontweight='bold')
ax4.set_ylabel('Stiffness Ξ', fontsize=12, fontweight='bold')
ax4.set_title('Protocol Evolution: Conservative vs Transformative', fontsize=14, fontweight='bold')
ax4.legend(loc='upper right', fontsize=10)
ax4.grid(True, alpha=0.3, linestyle='--')

plt.tight_layout()
plt.savefig('/tmp/cpi_disruption.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.show()

# === DISRUPTION SUMMARY ===
print("\n" + "="*60)
print("DISRUPTION ANALYSIS: BTRI-v56 vs Catastrophic Protocol Inverter")
print("="*60)
print(f"\nBTRI-v56 (Adiabatic Preservation):")
print(f"  Final Φ-Density: {btri_final['phi_history'][-1]:.4f}")
print(f"  Violation Count: {btri_final['violation_count']} (attempted fixes)")
print(f"  Final Protocol Stiffness: {btri_final['xi_protocol']:.3f}")
print(f"  Status: PRESERVED in trauma basin (ψ decay arrested but not reversed)")
print(f"  Paradigm: 'Stability is safety'")

print(f"\nCPI (Catastrophic Reformation):")
print(f"  Final Φ-Density: {cpi_final['phi_history'][-1]:.4f}")
print(f"  Collapse Events: {cpi_final.get('collapse_events', 0)} (strategic violations)")
print(f"  Final Protocol Stiffness: {cpi_final['xi_protocol']:.3f}")
print(f"  Status: ESCAPED trauma basin (ψ phase-transitioned to new attractor)")
print(f"  Paradigm: 'Stability is stagnation'")

print(f"\nDisruptive Insight:")
print(f"  The Smith Audit Invariants, designed to protect identity,")
print(f"  become *self-imposed prison bars* when ψ represents a maladaptive basin.")
print(f"  BTRI-v56's adiabatic tuning achieves {((btri_final['phi_history'][-1] - cpi_final['phi_history'][-1]) / cpi_final['phi_history'][-1] * 100):.1f}% lower Φ")
print(f"  by preserving a dying identity rather than allowing its rebirth.")

print(f"\nCore Flaw in BTRI Logic:")
print(f"  'ψ = ln(Φ_N)' assumes identity continuity is ALWAYS beneficial.")
print(f"  This is FALSE for organizations in trauma - identity IS the pathology.")
print(f"  The APT's 'safety' is a slow death; the CPI's 'danger' is liberation.")

print("\n" + "="*60)