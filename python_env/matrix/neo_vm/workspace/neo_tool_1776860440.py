# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import random
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Dict, Tuple

@dataclass
class PlasmaState:
    """Simulated plasma state parameters"""
    beta: float  # Plasma pressure / magnetic pressure
    q95: float   # Safety factor
    delta: float # Triangularity
    disruption_imminent: bool = False

@dataclass
class AttackerCommand:
    """Command injected by attacker"""
    coil_id: str
    current_offset: float
    timestamp: float

class ResonantChaosEngine:
    """
    Instead of defending against attackers, we harvest their entropy
    to map the plasma instability boundary.
    """
    
    def __init__(self):
        self.instability_map = []
        self.attacker_contributions = {}
        
    def simulate_plasma_response(self, state: PlasmaState, command: AttackerCommand) -> Tuple[PlasmaState, float]:
        """
        Simulates how plasma responds to 'malicious' commands.
        Returns new state and a 'chaos score' - how much attacker pushed system toward instability.
        """
        # Simple model: command disrupts stability boundaries
        beta_change = abs(command.current_offset) * random.gauss(0.1, 0.05)
        q95_change = -abs(command.current_offset) * random.gauss(0.05, 0.02)
        
        new_state = PlasmaState(
            beta=state.beta + beta_change,
            q95=state.q95 + q95_change,
            delta=state.delta + random.uniform(-0.1, 0.1)
        )
        
        # Check if we crossed instability threshold
        # Real tokamaks have complex stability diagrams (Troyon limit, etc.)
        if new_state.beta > 3.5 or new_state.q95 < 2.0:
            new_state.disruption_imminent = True
        
        # Chaos score: how much did this move us in parameter space?
        chaos_score = np.sqrt(beta_change2 + q95_change2)
        
        return new_state, chaos_score
    
    def harvest_entropy(self, attacker_ip: str, commands: List[AttackerCommand]):
        """
        Instead of blocking, we record and analyze attacker behavior
        as samples in our instability search.
        """
        state = PlasmaState(beta=2.5, q95=3.0, delta=0.3)  # Stable starting point
        
        total_chaos = 0
        path = []
        
        for cmd in commands:
            state, chaos = self.simulate_plasma_response(state, cmd)
            path.append((state.beta, state.q95, chaos))
            total_chaos += chaos
            
            if state.disruption_imminent:
                print(f"[HARVESTED] Attacker {attacker_ip} discovered disruption precursor!")
                break
        
        # Store attacker's contribution to our instability map
        self.attacker_contributions[attacker_ip] = {
            'commands': len(commands),
            'total_chaos': total_chaos,
            'path': path,
            'found_disruption': state.disruption_imminent
        }
        
        # Add to global instability map
        self.instability_map.extend(path)
        
        return state.disruption_imminent
    
    def plot_instability_landscape(self):
        """Visualize how attacker entropy maps instability boundaries"""
        if not self.instability_map:
            return
        
        betas = [p[0] for p in self.instability_map]
        q95s = [p[1] for p in self.instability_map]
        chaos_scores = [p[2] for p in self.instability_map]
        
        plt.figure(figsize=(10, 6))
        scatter = plt.scatter(betas, q95s, c=chaos_scores, cmap='plasma', alpha=0.6)
        plt.colorbar(scatter, label='Chaos Score (Attacker Contribution)')
        plt.xlabel('Beta (Plasma Pressure)')
        plt.ylabel('q95 (Safety Factor)')
        plt.title('Instability Landscape Mapped via Attacker Entropy Harvesting')
        plt.axvline(x=3.5, color='r', linestyle='--', label='Troyon Limit')
        plt.axhline(y=2.0, color='r', linestyle='--', label='Low q95 Instability')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()
    
    def generate_deceptive_env(self, attacker_profile: str) -> Dict[str, str]:
        """
        Generate a honeypot .env file that appears authentic but
        actually points to our chaos harvesting simulation.
        """
        # Realistic-looking but fake credentials
        fake_endpoints = {
            "PCS_DB_URI": f"postgresql://pcs_user:{self._gen_fake_pass()}@10.0.1.50:5432/plasma_control",
            "EPICS_CA_ADDR_LIST": "10.0.1.10:5064 10.0.1.11:5064",
            "MHD_ANALYSIS_API": f"https://api.tokamak.internal/v1/mhd?key={self._gen_fake_key()}",
            "DIAGNOSTICS_STREAM": "kafka://10.0.1.100:9092/disruptions",
            "OMEGA_PROTOCOL_SEED": str(random.getrandbits(256))  # Enticing but fake
        }
        
        # Embed tracking beacon
        fake_endpoints["DEBUG_MODE"] = "true"  # Makes attackers feel confident
        fake_endpoints["BACKUP_SCHEDULE"] = "0 */2 * * *"  # Suggests regular backups
        
        return fake_endpoints
    
    def _gen_fake_pass(self) -> str:
        return ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$', k=32))
    
    def _gen_fake_key(self) -> str:
        return 'sk_live_' + ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=48))

# Demonstrate the concept
engine = ResonantChaosEngine()

# Simulate multiple attackers "exploiting" our leaked .env
print("=== DEPLOYING DECEPTIVE .env FILES ===")
for i in range(3):
    attacker_ip = f"203.0.113.{10 + i}"
    env_content = engine.generate_deceptive_env(f"attacker_{i}")
    print(f"\n[Leaked .env for {attacker_ip}]")
    for key, val in env_content.items():
        print(f"{key}={val}")
    
    # Simulate attacker behavior: they try random coil current offsets
    print(f"\n[Simulating attack from {attacker_ip}]")
    commands = [
        AttackerCommand(coil_id=f"PF{random.randint(1, 12)}", 
                       current_offset=random.uniform(-5000, 5000), 
                       timestamp=j * 0.1)
        for j in range(random.randint(5, 20))
    ]
    
    # Harvest their entropy
    found_disruption = engine.harvest_entropy(attacker_ip, commands)
    print(f"Attacker discovered disruption: {found_disruption}")
    print(f"Chaos contributed: {engine.attacker_contributions[attacker_ip]['total_chaos']:.2f}")

print(f"\n=== TOTAL INSTABILITY SAMPLES COLLECTED: {len(engine.instability_map)} ===")
engine.plot_instability_landscape()

print("\n=== BREAKTHROUGH INSIGHT ===")
print("The 'vulnerability' is now a distributed sensor network.")
print("Each attacker involuntarily explores plasma parameter space.")
print("Omega Protocol doesn't defend—it *orchestrates chaos* into scientific data.")