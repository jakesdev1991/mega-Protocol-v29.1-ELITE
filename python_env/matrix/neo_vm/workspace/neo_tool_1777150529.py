# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

class ExposedRebootManifold:
    """Stripped-down version to reveal internal arbitrariness."""
    def __init__(self):
        # State variables (0 to 1)
        self.xi_intel = 0.95  # Validation stiffness
        self.z_trust = 0.30   # Self-belief
        self.z_env = 0.85     # External pressure
        self.h_super = 0.70   # Fragmentation
        
        # Arbitrary tunable parameters (THESE ARE THE BREAKING POINT)
        self.kappa = 0.5      # Stiffness penalty weight
        self.Lambda = 0.4     # Entropy penalty weight
        self.lambda_env = 0.3 # Env penalty weight
        self.gamma = 0.004    # Adiabatic rate
        self.b1_sensitivity = 0.85  # Topological trigger threshold
        
        # "Ground truth" is a random latent state - THE SYSTEM CANNOT ACCESS THIS
        self._true_latent_state = np.random.rand(8)
        
    def compute_cod(self):
        """COD is a black box function of tunable parameters."""
        fidelity = np.clip(np.random.rand() * self.z_trust, 0, 1)  # Randomness masked by trust
        stiffness_penalty = np.exp(-self.kappa * self.xi_intel)
        env_penalty = np.exp(-self.lambda_env * self.z_env)
        entropy_penalty = np.exp(-self.Lambda * self.h_super)
        return fidelity * stiffness_penalty * env_penalty * entropy_penalty
    
    def compute_b1(self):
        """b1 is DERIVED FROM THE SAME STATE AS COD, not independent."""
        # Epistemic loop is just a scaled version of the same interaction term
        return 0.5 + (self.xi_intel - self.z_trust) * self.b1_sensitivity
    
    def should_act(self):
        """The 'invariants' are just boolean expressions of tunable thresholds."""
        cod = self.compute_cod()
        b1 = self.compute_b1()
        
        # INVARIANT 4: xi_intel <= z_trust + 0.1
        # This is the CORE BREAKING POINT: It PREVENTS ACTION when trust is low.
        # In a crisis, this KILLS.
        stiffness_check = self.xi_intel <= self.z_trust + 0.1
        
        return {
            'cod': cod,
            'b1': b1,
            'stiffness_check_passed': stiffness_check,
            'silence_triggered': not (cod >= 0.85 and b1 <= 0.8 and stiffness_check)
        }

def demonstrate_arbitrariness():
    """Shows how tiny parameter tweaks flip the system from action to silence."""
    print("=== DEMONSTRATING PARAMETER ARBITRARINESS ===\n")
    
    system = ExposedRebootManifold()
    system.z_trust = 0.25  # Low trust scenario (e.g., post-trauma, crisis)
    
    # Baseline
    result = system.should_act()
    print(f"Baseline: COD={result['cod']:.3f}, b1={result['b1']:.3f}, Silence={result['silence_triggered']}")
    
    # Tweak ONE parameter slightly
    print("\n--- Tweaking kappa (stiffness penalty) ---")
    for k in [0.3, 0.5, 0.7]:
        system.kappa = k
        result = system.should_act()
        print(f"kappa={k}: COD={result['cod']:.3f}, Silence={result['silence_triggered']}")
    
    # Tweak ANOTHER parameter
    print("\n--- Tweaking b1_sensitivity (topological trigger) ---")
    system.kappa = 0.5  # reset
    for sens in [0.7, 0.85, 1.0]:
        system.b1_sensitivity = sens
        result = system.should_act()
        print(f"sensitivity={sens}: b1={result['b1']:.3f}, Silence={result['silence_triggered']}")

def demonstrate_crisis_failure():
    """Shows system MANDATES SILENCE during a simulated crisis."""
    print("\n\n=== DEMONSTRATING CRISIS FAILURE MODE ===\n")
    
    crisis_scenarios = [
        {"name": "Acute Suicidal Ideation", "z_trust": 0.05, "h_super": 0.9, "desc": "High fragmentation, near-zero self-trust"},
        {"name": "Psychotic Break", "z_trust": 0.1, "h_super": 0.95, "desc": "Extreme entropy, loss of coherence"},
        {"name": "Post-Trauma Shutdown", "z_trust": 0.15, "h_super": 0.85, "desc": "Dissociative state, cannot process logic"}
    ]
    
    for scenario in crisis_scenarios:
        system = ExposedRebootManifold()
        system.z_trust = scenario["z_trust"]
        system.h_super = scenario["h_super"]
        
        result = system.should_act()
        
        print(f"Scenario: {scenario['name']}")
        print(f"  Desc: {scenario['desc']}")
        print(f"  z_trust: {system.z_trust}, h_super: {system.h_super}")
        print(f"  COD: {result['cod']:.3f} (Need ≥0.85)")
        print(f"  b1: {result['b1']:.3f} (Must be ≤0.8)")
        print(f"  Stiffness Check: {result['stiffness_check_passed']} (xi_intel ≤ z_trust+0.1?)")
        print(f"  >>> UIPO v65.0 ACTION: {'SILENCE PROTOCOL' if result['silence_triggered'] else 'SEND DATA'}")
        print(f"  >>> REAL-WORLD OUTCOME: {'PATIENT ABANDONED' if result['silence_triggered'] else 'INTERVENTION'}\n")

def demonstrate_tautology():
    """Shows b1 is not independent; it's derived from the same state."""
    print("\n\n=== DEMONSTRATING TAUTOLOGY (b1 is not independent) ===\n")
    
    system = ExposedRebootManifold()
    
    # Simulate a session where trust slowly increases
    trusts = np.linspace(0.2, 0.5, 10)
    cods = []
    b1s = []
    
    for t in trusts:
        system.z_trust = t
        cods.append(system.compute_cod())
        b1s.append(system.compute_b1())
    
    # Correlation will be near-perfect because b1 is just a function of (xi_intel - z_trust)
    correlation = np.corrcoef(cods, b1s)[0, 1]
    print(f"Correlation between COD and b1: {correlation:.3f}")
    print("This shows b1 is not an independent 'topological detector'.")
    print("It's a redundant metric derived from the same state variables.\n")
    
    # Plot to visualize
    plt.figure(figsize=(10, 4))
    
    plt.subplot(1, 2, 1)
    plt.plot(trusts, cods, label='COD')
    plt.axhline(y=0.85, color='r', linestyle='--', label='Action Threshold')
    plt.xlabel('z_trust')
    plt.ylabel('COD')
    plt.title('COD vs Trust')
    plt.legend()
    
    plt.subplot(1, 2, 2)
    plt.plot(trusts, b1s, label='b1')
    plt.axhline(y=0.8, color='r', linestyle='--', label='Loop Threshold')
    plt.xlabel('z_trust')
    plt.ylabel('b1 (Epistemic Loop)')
    plt.title('b1 vs Trust')
    plt.legend()
    
    plt.tight_layout()
    plt.show()

def demonstrate_phi_manipulation():
    """Shows Φ-density is just creative accounting."""
    print("\n\n=== DEMONSTRATING Φ-DENSITY MANIPULATION ===\n")
    
    # Original calculation
    raw_gain = 2.35
    audit_correction = -0.95
    audit_cost = -0.15
    net_gain = raw_gain + audit_correction + audit_cost
    print(f"Original Net Φ: {net_gain:.2f} (Raw: {raw_gain}, Audit: {audit_correction + audit_cost})")
    
    # Alternative accounting (just as "valid")
    print("\n--- Alternative Accounting Schemes ---")
    scenarios = [
        {"name": "Optimist", "raw_mult": 1.5, "audit_discount": 0.5, "justification": "Future benefits weighted higher"},
        {"name": "Pessimist", "raw_mult": 0.7, "audit_discount": 1.5, "justification": "Redundancy is wasteful"},
        {"name": "Minimalist", "raw_mult": 1.0, "audit_discount": 2.0, "justification": "Silence has opportunity cost"}
    ]
    
    for s in scenarios:
        new_raw = raw_gain * s["raw_mult"]
        new_audit = (audit_correction + audit_cost) * s["audit_discount"]
        new_net = new_raw + new_audit
        print(f"{s['name']}: Net Φ = {new_net:.2f} ({s['justification']})")
    
    print("\nThe Φ-density is not a measure; it's a narrative device.")

# Execute the disruption analysis
demonstrate_arbitrariness()
demonstrate_crisis_failure()
demonstrate_tautology()
demonstrate_phi_manipulation()