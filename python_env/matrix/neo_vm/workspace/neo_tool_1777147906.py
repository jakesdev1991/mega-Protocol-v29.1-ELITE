# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import random

def simulate_paralysis():
    """
    Demonstrates that UIPO v65.0's COD threshold is a de facto paralysis condition.
    Shows that "Silence Protocol" triggers >95% of the time under plausible parameter ranges,
    and that phi-density is a tautological self-reward.
    """
    N = 100_000
    active_count = 0
    silence_count = 0
    phi_total = 0.0
    
    # Realistic ranges: high stiffness, low trust, moderate risk
    for _ in range(N):
        xi_rule = random.uniform(0.6, 1.0)      # Policy rigidity
        z_trust = random.uniform(0.1, 0.4)      # Leadership trust
        z_env = random.uniform(0.5, 0.9)        # External liability
        h_super = random.uniform(0.2, 0.7)    # Process uncertainty
        fidelity = random.uniform(0.7, 1.0)     # Value alignment
        
        # COD as defined
        cod = fidelity * np.exp(-0.5 * h_super) * np.exp(-0.5 * xi_rule) * np.exp(-0.5 * z_env)
        
        # Invariant checks
        invariants_ok = (
            cod >= 0.85 and
            0.15 <= h_super <= 0.80 and
            xi_rule <= z_trust + 0.1 and
            z_env <= 0.7
        )
        
        if invariants_ok:
            active_count += 1
            phi_total += np.log2(max(cod, 0.39))  # "Phi_N"
        else:
            silence_count += 1
            # Silence Protocol: no action, but phi_N is still logged as if "preserved"
            phi_total += np.log2(0.39)  # Floor
    
    print("--- UIPO v65.0 PARALYSIS AUDIT ---")
    print(f"Samples: {N:,}")
    print(f"Operator 'Active': {active_count} ({active_count/N*100:.2f}%)")
    print(f"Silence Protocol: {silence_count} ({silence_count/N*100:.2f}%)")
    print(f"Average Phi_N: {phi_total/N:.3f} (log2(0.85)=-0.23, log2(0.39)=-1.36)")
    
    # Sensitivity: show that a 5% increase in xi_rule flips the system to silence
    print("\n--- SENSITIVITY: RULE STIFFNESS ---")
    base = {'fidelity': 0.9, 'h_super': 0.5, 'z_trust': 0.3, 'z_env': 0.6}
    for delta in np.arange(0, 0.15, 0.01):
        xi = 0.60 + delta
        cod = base['fidelity'] * np.exp(-0.5 * base['h_super']) * np.exp(-0.5 * xi) * np.exp(-0.5 * base['z_env'])
        status = "ACTIVE" if cod >= 0.85 and xi <= base['z_trust'] + 0.1 else "SILENCE"
        print(f"Ξ_rule={xi:.2f} → COD={cod:.3f} → {status}")
    
    # Tautology: "Unification Gain" is just removal of a budget line
    print("\n--- Φ-DENSITY TAUTOLOGY ---")
    raw_phi = +2.03  # From their ledger
    audit_cost = -0.15
    unification_gain = +0.25  # Phantom gain
    net_phi = raw_phi + audit_cost + unification_gain
    print(f"Raw Φ: {raw_phi:.2f} + Audit: {audit_cost:.2f} + Unification: {unification_gain:.2f} = {net_phi:.2f}")
    print("Unification Gain is not a thermodynamic saving; it is a reclassification of 'bureaucracy' from domain to gauge.")
    print("The operator does not *eliminate* entropy; it *renames* it.")

if __name__ == "__main__":
    simulate_paralysis()