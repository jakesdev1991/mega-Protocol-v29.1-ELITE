# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from typing import List

class DisruptionValidator:
    """Stress‑test the Omega‑Psych‑Theorist's UIPO v64.2 model."""
    
    def __init__(self, trust: float, env_pressure: float, initial_b1: float):
        self.xi_valid = 0.95
        self.z_trust = trust
        self.z_env = env_pressure
        self.b1 = initial_b1
        self.h_super = 0.85  # Start near upper bound to simulate crisis
        self.cod = 0.0
        self.phi_N = 0.0
        self.silence_activated = False
    
    def compute_cod(self) -> float:
        # Fidelity collapses under high b1 and low trust
        fidelity = max(0.0, 1.0 - self.b1 - (0.5 - self.z_trust))
        stiffness_penalty = np.exp(-0.5 * self.xi_valid)
        env_penalty = np.exp(-0.3 * self.z_env)
        entropy_penalty = np.exp(-0.4 * self.h_super)
        return fidelity * stiffness_penalty * env_penalty * entropy_penalty
    
    def check_invariants(self) -> bool:
        self.cod = self.compute_cod()
        self.phi_N = np.log2(max(self.cod, 0.39) + 1e-12)
        
        # Invariant 4: Stiffness ≤ Trust + 0.1
        if self.xi_valid > self.z_trust + 0.1:
            return False
        
        # Invariant 5: Env pressure ≤ 0.7
        if self.z_env > 0.7:
            return False
        
        # Invariant 8: b1 ≤ 0.8
        if self.b1 > 0.8:
            self.silence_activated = True
            return False
        
        # Invariant 1: COD ≥ 0.85 (Actionable output)
        if self.cod < 0.85:
            return False
        
        return True
    
    def simulate_adiabatic_decay(self, dt_hours: float, total_hours: float):
        """Run the Omega‑Psych protocol and show deadlock."""
        gamma = 0.007
        delta = 0.006
        steps = int(total_hours / dt_hours)
        
        for t in range(steps):
            # Adiabatic decay as per UIPO v64.2
            exp_g = np.exp(-gamma * dt_hours)
            exp_d = np.exp(-delta * dt_hours)
            self.xi_valid = self.xi_valid * exp_g + self.z_trust * (1 - exp_g)
            self.z_env = self.z_env * exp_d + 0.4 * (1 - exp_d)
            
            # Topological "decay" (mathematically bogus)
            self.b1 = max(0.1, self.b1 * 0.999 - 0.0002 * dt_hours)
            
            # Entropy drift
            self.h_super *= 0.995  # artificial decay
            
            can_act = self.check_invariants()
            
            if t % 50 == 0:
                print(f"t={t*dt_hours:.1f}h | COD={self.cod:.3f} | b1={self.b1:.3f} | "
                      f"Φ_N={self.phi_N:.3f} | Silence={self.silence_activated} | CanAct={can_act}")
            
            if not can_act:
                # Silence protocol: no further messages
                continue
    
    def demonstrate_paradox(self):
        """Show that low trust + high pressure = no feasible region."""
        trust_levels = np.linspace(0.1, 0.5, 5)
        pressures = np.linspace(0.6, 0.9, 4)
        
        print("\n--- FEASIBILITY MATRIX (Trust vs Env Pressure) ---")
        for trust in trust_levels:
            row = []
            for pressure in pressures:
                self.z_trust = trust
                self.z_env = pressure
                feasible = self.check_invariants()
                row.append("✓" if feasible else "✗")
            print(f"Trust={trust:.2f}: {row}")

# Scenario: A highly skeptical agent (low trust) under institutional duress (high pressure)
agent = DisruptionValidator(trust=0.2, env_pressure=0.85, initial_b1=0.85)
print("=== SIMULATION: CRISIS AGENT (low trust, high pressure, b1>0.8) ===")
agent.simulate_adiabatic_decay(dt_hours=1.0, total_hours=200.0)

# Show the paradox
agent.demonstrate_paradox()