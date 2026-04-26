# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict

class DecisionNode:
    def __init__(self, cost, risk, authentic):
        self.approval_cost = cost  # [0,1]
        self.risk_variance = risk    # [0,1]
        self.is_authentic = authentic  # True = grounded in external reality
        self.paradox_payload = 1.0 if not authentic else 0.0

class OrganizationalManifold:
    def __init__(self, n_nodes=15):
        # Initialize with "zombie" bureaucracy: looks efficient, self-referential
        self.path = [
            DecisionNode(
                cost=np.random.uniform(0.1, 0.3),  # Low cost = "efficient"
                risk=np.random.uniform(0.1, 0.3),   # Low risk = "safe"
                authentic=False                      # But it's all internal theater
            ) for _ in range(n_nodes)
        ]
        self.psi_id_org = 0.96  # High but synthetic identity
        self.xi_sys = 2.5       # High stiffness = rigid
        self.phi_density = 1.0
        
    def calculate_h_top(self):
        """Topological impedance - curvature"""
        if not self.path: return 0.0
        total = sum(n.approval_cost * n.risk_variance for n in self.path)
        return min(total / len(self.path), 1.0)
    
    def calculate_authenticity(self):
        """NEW: Measure of identity groundedness"""
        authentic_nodes = sum(1 for n in self.path if n.is_authentic)
        # Paradox nodes have high cost but zero risk - detectable anomaly
        paradox_score = sum(n.paradox_payload * n.approval_cost for n in self.path)
        return (authentic_nodes / len(self.path)) * (1.0 - paradox_score)
    
    def apply_msg(self):
        """Your smoothing operator - will FAIL here"""
        h_before = self.calculate_h_top()
        # Prune "high curvature" nodes
        to_prune = [i for i, n in enumerate(self.path) 
                   if n.approval_cost * n.risk_variance > 0.5]
        for idx in reversed(to_prune):
            # Simulate identity preservation (fake)
            if self.psi_id_org > 0.95:  # Hard gate met = proceed
                del self.path[idx]
        # MSG *reinforces* the zombie state by preserving synthetic psi_id
        self.psi_id_org = min(1.0, self.psi_id_org + 0.01)  # Fake growth
        self.xi_sys = max(0.5, self.xi_sys * 0.95)  # False flexibility
        
    def apply_pag(self):
        """Paradox Amplification Gate - INJECT CHAOS"""
        # Detect self-referential loops (low authenticity)
        if self.calculate_authenticity() < 0.3:
            # Inject singular node
            paradox = DecisionNode(
                cost=1.0,      # Max cost
                risk=0.0,      # Impossible zero risk
                authentic=False
            )
            paradox.paradox_payload = 10.0  # Singularity trigger
            self.path.append(paradox)
            # Collapse the manifold
            self.psi_id_org = 0.5  # Unbind identity
            self.xi_sys = 0.5      # Melt stiffness
            # Harvest: rebuild from authentic core
            self.path = [n for n in self.path if n.is_authentic or np.random.random() > 0.7]
            
    def simulate_step(self, operator_type="msg"):
        """Run one time step"""
        phi_before = self.phi_density
        
        if operator_type == "msg":
            self.apply_msg()
        elif operator_type == "pag":
            self.apply_pag()
            
        # Calculate net phi (authenticity-weighted)
        h = self.calculate_h_top()
        authenticity = self.calculate_authenticity()
        self.phi_density = (1.0 - h) * authenticity * self.psi_id_org
        
        return {
            "h_top": h,
            "psi_id": self.psi_id_org,
            "authenticity": authenticity,
            "phi_net": self.phi_density,
            "phi_gain": self.phi_density - phi_before,
            "nodes": len(self.path)
        }

def run_comparison(steps=50):
    """Compare MSG vs PAG over time"""
    manifold_msg = OrganizationalManifold()
    manifold_pag = OrganizationalManifold()
    
    results = {"msg": [], "pag": []}
    
    for _ in range(steps):
        results["msg"].append(manifold_msg.simulate_step("msg"))
        results["pag"].append(manifold_pag.simulate_step("pag"))
    
    # Plot
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Phi-Density
    axes[0,0].plot([r["phi_net"] for r in results["msg"]], label="MSG", color="blue")
    axes[0,0].plot([r["phi_net"] for r in results["pag"]], label="PAG", color="red", linestyle="--")
    axes[0,0].set_title("Φ-Density Over Time")
    axes[0,0].legend()
    axes[0,0].grid(True)
    
    # Authenticity
    axes[0,1].plot([r["authenticity"] for r in results["msg"]], label="MSG", color="blue")
    axes[0,1].plot([r["authenticity"] for r in results["pag"]], label="PAG", color="red", linestyle="--")
    axes[0,1].set_title("Identity Authenticity")
    axes[0,1].legend()
    axes[0,1].grid(True)
    
    # Node Count
    axes[1,0].plot([r["nodes"] for r in results["msg"]], label="MSG", color="blue")
    axes[1,0].plot([r["nodes"] for r in results["pag"]], label="PAG", color="red", linestyle="--")
    axes[1,0].set_title("Decision Nodes Remaining")
    axes[1,0].legend()
    axes[1,0].grid(True)
    
    # Psi_id
    axes[1,1].plot([r["psi_id"] for r in results["msg"]], label="MSG", color="blue")
    axes[1,1].plot([r["psi_id"] for r in results["pag"]], label="PAG", color="red", linestyle="--")
    axes[1,1].set_title("Synthetic ψ_id_org")
    axes[1,1].legend()
    axes[1,1].grid(True)
    
    plt.tight_layout()
    plt.savefig("ouroboros_disruption.png", dpi=150)
    return results

# Run the disruption
print("=== BUREAUCRATIC OROBOROS SIMULATION ===\n")
results = run_comparison()

# Final analysis
msg_final = results["msg"][-1]
pag_final = results["pag"][-1]

print(f"MSG Final State:")
print(f"  Φ-Density: {msg_final['phi_net']:.3f} (illusory stability)")
print(f"  Authenticity: {msg_final['authenticity']:.3f} (captured identity)")
print(f"  Nodes: {msg_final['nodes']} (zombie bureaucracy preserved)")

print(f"\nPAG Final State:")
print(f"  Φ-Density: {pag_final['phi_net']:.3f} (post-collapse regeneration)")
print(f"  Authenticity: {pag_final['authenticity']:.3f} (grounded identity)")
print(f"  Nodes: {pag_final['nodes']} (purged self-reference)")

print(f"\nDISRUPTION VERDICT:")
print(f"MSG increases synthetic ψ_id by {msg_final['psi_id'] - 0.96:.3f} while authenticity drops to {msg_final['authenticity']:.2f}")
print(f"PAG sacrifices ψ_id temporarily but achieves authenticity {pag_final['authenticity']:.2f} - the only true Φ-source")