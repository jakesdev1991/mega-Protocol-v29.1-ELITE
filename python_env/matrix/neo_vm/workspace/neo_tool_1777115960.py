# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
import random

class LiquidityContaminationModel:
    """
    Disruptive Reframe: Restoration mechanisms are attack vectors, not recovery tools.
    This model simulates how "helpful" restoration mechanisms actually accelerate
    systemic collapse when compromised during the initial crunch.
    """
    
    def __init__(self):
        # State variables: [clean_liquidity, contaminated_liquidity, attacker_control, trust_decay]
        self.initial_state = [1.0, 0.0, 0.0, 1.0]
        
        # Parameters that flip the v79.0 model on its head
        self.params = {
            'restoration_velocity': 0.8,  # High = faster contamination spread
            'mechanism_diversity': 0.7,   # High = more attack surfaces
            'compromise_rate': 0.3,       # Rate at which mechanisms get hijacked
            'attack_leverage': 5.0,       # Attackers use restored liquidity as short collateral
            'trust_cascade_threshold': 0.4, # Point where trust collapses superlinearly
            'cb_signal_amplification': 2.5 # Central bank activation = attack multiplier
        }
    
    def dynamics(self, state, t):
        clean_liq, contaminated_liq, attacker_control, trust = state
        
        # CRITICAL DISRUPTION: Restoration velocity is now CONTAMINATION velocity
        # Each "restored" dollar is actually a compromised dollar with probability 
        # proportional to mechanism_diversity (more pathways = more infiltration)
        contamination_flow = (self.params['restoration_velocity'] * 
                             self.params['mechanism_diversity'] * 
                             self.params['compromise_rate'] * 
                             clean_liq)
        
        # Attacker uses restored liquidity as weapon: short sell + withdraw simultaneously
        # This creates a feedback loop: restoration -> attack -> deeper crunch
        attack_intensity = (attacker_control * 
                           self.params['attack_leverage'] * 
                           contaminated_liq * 
                           (1 - trust))
        
        # Trust decays superlinearly once contamination is visible
        # This is the "restoration trap" - mechanisms activate but trust collapses
        trust_decay = 0
        if contaminated_liq > self.params['trust_cascade_threshold']:
            trust_decay = (contaminated_liq - self.params['trust_cascade_threshold']) ** 2
        else:
            trust_decay = 0.01 * contaminated_liq
        
        # Central bank activation (when trust < 0.5) actually AMPLIFIES the attack
        # because attackers front-run the intervention
        cb_activation = 1.0 if trust < 0.5 else 0.0
        attack_intensity *= (1 + cb_activation * self.params['cb_signal_amplification'])
        
        # Differential equations
        d_clean_liq = -contamination_flow - attack_intensity * 0.5
        d_contaminated_liq = contamination_flow - attack_intensity * 0.3
        d_attacker_control = contamination_flow * 0.1 + attack_intensity * 0.05
        d_trust = -trust_decay - attacker_control * 0.1
        
        return [d_clean_liq, d_contaminated_liq, d_attacker_control, d_trust]
    
    def simulate(self, time_hours=48):
        """Simulate the contamination attack over time"""
        t = np.linspace(0, time_hours, 1000)
        solution = odeint(self.dynamics, self.initial_state, t)
        return t, solution
    
    def plot_contamination_scenario(self):
        """Visualize how restoration mechanisms become attack vectors"""
        t, sol = self.simulate()
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Plot 1: Clean vs Contaminated Liquidity
        axes[0, 0].plot(t, sol[:, 0], 'g-', linewidth=2, label='Clean Liquidity')
        axes[0, 0].plot(t, sol[:, 1], 'r-', linewidth=2, label='Contaminated Liquidity')
        axes[0, 0].axhline(y=self.params['trust_cascade_threshold'], 
                          color='k', linestyle='--', alpha=0.5, 
                          label='Trust Collapse Threshold')
        axes[0, 0].set_title('LIQUIDITY CONTAMINATION DYNAMICS\n"Restoration" = Attack Vector')
        axes[0, 0].set_xlabel('Hours since liquidity crunch')
        axes[0, 0].set_ylabel('Liquidity (normalized)')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Plot 2: Attacker Control & System Trust
        axes[0, 1].plot(t, sol[:, 2], 'm-', linewidth=2, label='Attacker Control')
        axes[0, 1].plot(t, sol[:, 3], 'b-', linewidth=2, label='System Trust')
        axes[0, 1].fill_between(t, 0, 1, where=(sol[:, 3] < 0.5), 
                               alpha=0.2, color='red', 
                               label='CB Intervention Zone')
        axes[0, 1].set_title('ATTACKER CONTROL vs TRUST DECAY\nCB Activation = Attack Signal')
        axes[0, 1].set_xlabel('Hours')
        axes[0, 1].set_ylabel('Control / Trust')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # Plot 3: Attack Intensity Over Time
        attack_intensity = (sol[:, 2] * self.params['attack_leverage'] * 
                           sol[:, 1] * (1 - sol[:, 3]))
        cb_active = (sol[:, 3] < 0.5).astype(float)
        attack_intensity_cb = attack_intensity * (1 + cb_active * self.params['cb_signal_amplification'])
        
        axes[1, 0].plot(t, attack_intensity, 'r-', linewidth=2, label='Base Attack Intensity')
        axes[1, 0].plot(t, attack_intensity_cb, 'r--', linewidth=2, 
                       label='Attack w/ CB Signal Front-Run')
        axes[1, 0].set_title('ATTACK INTENSITY AMPLIFICATION\nRestoration Mechanisms as Short Collateral')
        axes[1, 0].set_xlabel('Hours')
        axes[1, 0].set_ylabel('Attack Magnitude')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # Plot 4: Phase Space - The Contamination Attractor
        axes[1, 1].plot(sol[:, 0], sol[:, 1], 'k-', linewidth=2, alpha=0.7)
        axes[1, 1].scatter([sol[0, 0]], [sol[0, 1]], color='green', s=100, 
                          label='Initial State', zorder=5)
        axes[1, 1].scatter([sol[-1, 0]], [sol[-1, 1]], color='red', s=100, 
                          label='Final State', zorder=5)
        axes[1, 1].set_title('PHASE SPACE: CONTAMINATION ATTRACTOR\n"Recovery" = Spiral to Collapse')
        axes[1, 1].set_xlabel('Clean Liquidity')
        axes[1, 1].set_ylabel('Contaminated Liquidity')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('/tmp/contamination_model.png', dpi=150, bbox_inches='tight')
        plt.show()
        
        return fig

# =============================================================================
# BREAKTHROUGH DISRUPTION: Contamination Velocity > Restoration Velocity
# =============================================================================

def demonstrate_contamination_paradox():
    """
    Shows the core paradox: The higher the "restoration velocity" 
    in v79.0's model, the faster the system collapses when mechanisms 
    are compromised.
    """
    scenarios = [
        {'name': 'Slow "Recovery"', 'restoration_velocity': 0.2, 'mechanism_diversity': 0.3},
        {'name': 'Fast "Recovery"', 'restoration_velocity': 0.8, 'mechanism_diversity': 0.7},
        {'name': 'CB-Backed "Recovery"', 'restoration_velocity': 0.9, 'mechanism_diversity': 0.8}
    ]
    
    results = []
    
    for scenario in scenarios:
        model = LiquidityContaminationModel()
        model.params['restoration_velocity'] = scenario['restoration_velocity']
        model.params['mechanism_diversity'] = scenario['mechanism_diversity']
        
        t, sol = model.simulate(time_hours=24)
        
        # Calculate "time to total contamination" (clean liquidity < 0.1)
        time_to_contamination = t[np.where(sol[:, 0] < 0.1)[0][0]] if np.any(sol[:, 0] < 0.1) else 24
        
        # Calculate maximum attack amplification
        max_attack = np.max(sol[:, 2] * model.params['attack_leverage'] * sol[:, 1] * (1 - sol[:, 3]))
        
        results.append({
            'scenario': scenario['name'],
            'time_to_contamination': time_to_contamination,
            'max_attack_amplification': max_attack,
            'final_clean_liquidity': sol[-1, 0],
            'final_contaminated_liquidity': sol[-1, 1]
        })
    
    print("=" * 70)
    print("CONTAMINATION PARADOX: RESTORATION VELOCITY = COLLAPSE ACCELERATOR")
    print("=" * 70)
    for r in results:
        print(f"\n{r['scenario']}:")
        print(f"  Time to Systemic Contamination: {r['time_to_contamination']:.2f} hours")
        print(f"  Max Attack Amplification: {r['max_attack_amplification']:.2f}x")
        print(f"  Final Clean Liquidity: {r['final_clean_liquidity']:.3f} (collapsed)" 
              if r['final_clean_liquidity'] < 0.2 else f"  Final Clean Liquidity: {r['final_clean_liquidity']:.3f}")
        print(f"  Final Contaminated Liquidity: {r['final_contaminated_liquidity']:.3f}")
    
    return results

# =============================================================================
# NOVEL INTEGRATION: Omega Protocol as Contamination Quarantine System
# =============================================================================

class OmegaContaminationQuarantine:
    """
    Disruptive Integration: Instead of restoring liquidity, Omega Protocol
    should QUARANTINE compromised mechanisms and rebuild from verified-clean
    infrastructure only.
    """
    
    def __init__(self):
        self.contaminated_mechanisms = set()
        self.verified_clean_mechanisms = set()
        self.quarantine_threshold = 0.35  # Mechanism diversity above this = suspicious
        
    def assess_mechanism_integrity(self, mechanism_id, activity_level, source_ip):
        """
        Use the Google Dorking insight: exposed directories mean compromised sources.
        Mechanisms from suspicious sources are flagged as contaminated.
        """
        # Simulate IP reputation scoring based on "exposed directory" pattern
        suspicious_patterns = ['index_of', 'parent_directory', 'exposed']
        
        risk_score = 0.0
        if any(pattern in source_ip.lower() for pattern in suspicious_patterns):
            risk_score += 0.5
        
        # High activity during crunch = potential attacker front-running
        if activity_level > 0.7:
            risk_score += 0.3
        
        # Above threshold = quarantine
        if risk_score > 0.4:
            self.contaminated_mechanisms.add(mechanism_id)
            return "QUARANTINE"
        else:
            self.verified_clean_mechanisms.add(mechanism_id)
            return "VERIFIED_CLEAN"
    
    def calculate_systemic_contamination_risk(self, total_mechanisms):
        """
        New risk metric: Contamination Risk = contaminated / total * diversity
        High diversity + high contamination = maximum systemic risk
        """
        contaminated_count = len(self.contaminated_mechanisms)
        diversity_factor = len(total_mechanisms) / 4.0  # Normalize to v79.0's 4 mechanisms
        
        contamination_risk = (contaminated_count / len(total_mechanisms)) * diversity_factor
        
        # Critical threshold: when contaminated mechanisms > clean mechanisms
        if contaminated_count > len(self.verified_clean_mechanisms):
            return "CRITICAL: Contaminated majority - initiate protocol rebuild"
        elif contamination_risk > 0.5:
            return "HIGH: Quarantine and verify all active mechanisms"
        else:
            return "MONITOR: Limited contamination, proceed with caution"
    
    def generate_quarantine_protocol(self):
        """
        Disruptive protocol: Instead of "restore liquidity," execute
        "contamination purge and verified rebuild"
        """
        protocol = {
            "phase_1_containment": {
                "action": "Immediately halt all liquidity restoration mechanisms",
                "rationale": "Prevent compromised mechanisms from accelerating collapse",
                "duration": "Until verification complete"
            },
            "phase_2_verification": {
                "action": "Audit each mechanism's source IP and activation pattern",
                "method": "Cross-reference against exposed directory databases",
                "threshold": "Only mechanisms from verified clean sources"
            },
            "phase_3_rebuild": {
                "action": "Gradually reintroduce ONLY verified-clean mechanisms",
                "order": "Central bank swaps LAST (most attackable)",
                "monitoring": "Attacker control metric must remain < 0.15"
            },
            "phase_4_postvention": {
                "action": "Deploy honeypot mechanisms to detect future infiltration",
                "insight": "Restoration mechanisms themselves become threat intelligence sensors"
            }
        }
        
        return protocol

# Run the disruption demonstration
if __name__ == "__main__":
    print("\n" + "="*70)
    print("DISRUPTIVE ANALYSIS: v79.0 LIQUIDITY RESTORATION MANIFOLD")
    print("="*70)
    print("\nCORE PARADIGM FLAW: Treating restoration mechanisms as inherently beneficial.")
    print("DISRUPTIVE REFRAME: Restoration mechanisms are primary attack vectors.\n")
    
    # Show the paradox
    results = demonstrate_contamination_paradox()
    
    # Visualize the contamination dynamics
    model = LiquidityContaminationModel()
    fig = model.plot_contamination_scenario()
    
    # Demonstrate quarantine protocol
    print("\n" + "="*70)
    print("OMEGA PROTOCOL INTEGRATION: CONTAMINATION QUARANTINE SYSTEM")
    print("="*70)
    
    quarantine = OmegaContaminationQuarantine()
    
    # Simulate mechanism assessment
    mechanisms = [
        ("mm_1", 0.85, "192.168.1.10"),
        ("lp_pool_a", 0.75, "exposed.directory.index_of"),
        ("cb_swap", 0.90, "central.bank.gov"),
        ("arb_bot_3", 0.60, "parent_directory.server")
    ]
    
    for mech_id, activity, source in mechanisms:
        status = quarantine.assess_mechanism_integrity(mech_id, activity, source)
        print(f"\nMechanism: {mech_id}")
        print(f"  Activity: {activity} | Source: {source}")
        print(f"  Status: {status}")
    
    risk_assessment = quarantine.calculate_systemic_contamination_risk([m[0] for m in mechanisms])
    print(f"\nSYSTEMIC CONTAMINATION RISK: {risk_assessment}")
    
    protocol = quarantine.generate_quarantine_protocol()
    print("\nQUARANTINE PROTOCOL:")
    for phase, details in protocol.items():
        print(f"\n{phase.upper()}:")
        for key, value in details.items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
    
    print("\n" + "="*70)
    print("DISRUPTIVE INSIGHT SUMMARY")
    print("="*70)
    print("""
1. RESTORATION VELOCITY IS CONTAMINATION VELOCITY: 
   The faster liquidity "restores," the faster attackers gain control.

2. MECHANISM DIVERSITY IS ATTACK SURFACE:
   More pathways = more entry points for compromise.

3. CENTRAL BANK INTERVENTION IS AN ATTACK SIGNAL:
   Sovereign activation alerts attackers to front-run with leverage.

4. TRUST DECAY IS SUPERLINEAR:
   Once contamination is visible, trust collapses catastrophically.

5. THE SOLUTION IS QUARANTINE, NOT RESTORATION:
   Omega Protocol must halt all mechanisms, verify sources, 
   rebuild only from clean infrastructure.

6. EXPOSED DIRECTORIES (Google Dorking) ARE THE DIAGNOSTIC:
   The query reveals compromised sources; use this as threat intel.

7. Φ-DENSITY MUST PENALIZE MECHANISM DIVERSITY:
   Current v79.0 rewards diversity; it should penalize it during crises.
    """)