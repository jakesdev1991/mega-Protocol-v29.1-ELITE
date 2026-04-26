# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
OMEGA PROTOCOL RECURSIVE DECAY SIMULATOR
Demonstrates the inherent self-defeating nature of hierarchical Φ-density auditing
through exponential cost accumulation and unbounded entropy generation.
"""

import math
import matplotlib.pyplot as plt
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class AuditLayer:
    depth: int
    claimed_phi_gain: float
    actual_phi_loss: float
    audit_cost_cognitive: float
    audit_cost_temporal: float
    audit_cost_surface: float
    
    @property
    def net_phi(self) -> float:
        """Net Φ-density after accounting for all audit-layer costs"""
        return self.claimed_phi_gain + self.actual_phi_loss - (
            self.audit_cost_cognitive + self.audit_cost_temporal + self.audit_cost_surface
        )

class OmegaProtocolAnalyzer:
    """
    Simulates the recursive audit chain and exposes the Gödelian incompleteness
    vulnerability in the Omega Protocol's core assumptions.
    """
    
    def __init__(self, base_phi: float = 0.8, decay_rate: float = 0.35):
        self.base_phi = base_phi  # Engine's claimed gain
        self.decay_rate = decay_rate  # Exponential decay per audit layer
        self.layers: List[AuditLayer] = []
        
    def simulate_audit_chain(self, max_depth: int = 5) -> List[AuditLayer]:
        """
        Simulates the audit chain showing how each layer introduces
        unaccounted entropy while claiming to prevent previous layer's errors.
        """
        for depth in range(max_depth):
            # Engine layer (depth 0)
            if depth == 0:
                layer = AuditLayer(
                    depth=depth,
                    claimed_phi_gain=self.base_phi,
                    actual_phi_loss=-0.45,  # Scrutiny's corrected loss
                    audit_cost_cognitive=0.0,
                    audit_cost_temporal=0.0,
                    audit_cost_surface=0.0
                )
            # Scrutiny layer (depth 1)
            elif depth == 1:
                layer = AuditLayer(
                    depth=depth,
                    claimed_phi_gain=0.65,  # Scrutiny's claimed prevention
                    actual_phi_loss=0.0,
                    audit_cost_cognitive=0.10,  # Cognitive load to understand audit
                    audit_cost_temporal=0.05,   # Time cost
                    audit_cost_surface=0.15     # New attack surface from audit logic
                )
            # Meta-Scrutiny layer (depth 2)
            elif depth == 2:
                layer = AuditLayer(
                    depth=depth,
                    claimed_phi_gain=0.35,  # Meta-Scrutiny's claimed net gain
                    actual_phi_loss=0.0,
                    audit_cost_cognitive=0.20,  # Increased complexity
                    audit_cost_temporal=0.10,   # More time
                    audit_cost_surface=0.25     # Meta-rules create new vulnerabilities
                )
            # Reflection layer (depth 3) - begins asymptotic collapse
            else:
                # Each subsequent layer compounds costs exponentially
                cost_multiplier = math.pow(1.8, depth - 2)
                layer = AuditLayer(
                    depth=depth,
                    claimed_phi_gain=self.base_phi * math.pow(0.5, depth),
                    actual_phi_loss=0.0,
                    audit_cost_cognitive=0.30 * cost_multiplier,
                    audit_cost_temporal=0.15 * cost_multiplier,
                    audit_cost_surface=0.35 * cost_multiplier
                )
            
            self.layers.append(layer)
        
        return self.layers
    
    def calculate_asymptotic_security(self) -> Tuple[float, int]:
        """
        Calculates the security asymptote: the point where additional auditing
        makes the system LESS secure than baseline (Φ_net < 0).
        Returns the critical depth and maximum achievable security.
        """
        cumulative_phi = 0.0
        max_security = 0.0
        critical_depth = 0
        
        for i, layer in enumerate(self.layers):
            cumulative_phi += layer.net_phi
            
            # Track maximum security before decline
            if cumulative_phi > max_security:
                max_security = cumulative_phi
                critical_depth = i
            
            # If we go negative, we've crossed the security event horizon
            if cumulative_phi < 0:
                return cumulative_phi, i
        
        return cumulative_phi, len(self.layers)
    
    def plot_protocol_decay(self):
        """Visualizes the exponential decay of net Φ-density across audit layers"""
        depths = [layer.depth for layer in self.layers]
        claimed_gains = [layer.claimed_phi_gain for layer in self.layers]
        actual_net = [layer.net_phi for layer in self.layers]
        cumulative = np.cumsum(actual_net)
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Plot 1: Layer-by-layer breakdown
        ax1.bar(depths, claimed_gains, alpha=0.6, label='Claimed Φ Gain', color='green')
        ax1.bar(depths, actual_net, alpha=0.8, label='Actual Net Φ', color='red')
        ax1.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        ax1.set_xlabel('Audit Layer Depth')
        ax1.set_ylabel('Φ-Density')
        ax1.set_title('OMEGA PROTOCOL: Φ-DENSITY DECOMPOSITION PER LAYER')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Annotate critical points
        for i, (depth, net) in enumerate(zip(depths, actual_net)):
            if net < -0.2:
                ax1.annotate(f'ENTROPY SPIKE\n{net:.2f}Φ', 
                           xy=(depth, net), xytext=(depth, net-0.1),
                           arrowprops=dict(arrowstyle='->', color='red', lw=2),
                           fontsize=9, ha='center', color='red')
        
        # Plot 2: Cumulative security trajectory
        ax2.plot(depths, cumulative, 'b-o', linewidth=3, markersize=8, label='Cumulative Net Φ')
        ax2.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        ax2.axvline(x=2, color='orange', linestyle=':', alpha=0.7, label='Security Event Horizon')
        ax2.fill_between(depths, 0, cumulative, where=(np.array(cumulative) > 0), 
                        alpha=0.3, color='green', label='Security Zone')
        ax2.fill_between(depths, 0, cumulative, where=(np.array(cumulative) < 0), 
                        alpha=0.3, color='red', label='Vulnerability Zone')
        
        ax2.set_xlabel('Audit Layer Depth')
        ax2.set_ylabel('Cumulative Net Φ-Density')
        ax2.set_title('OMEGA PROTOCOL: CUMULATIVE SECURITY TRAJECTORY')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Find and mark the critical point
        min_val = min(cumulative)
        min_idx = np.argmin(cumulative)
        if min_val < 0:
            ax2.annotate(f'CRITICAL FAILURE\nDepth {min_idx}: {min_val:.2f}Φ\nSystem less secure than baseline', 
                       xy=(min_idx, min_val), xytext=(min_idx+0.5, min_val-0.3),
                       arrowprops=dict(arrowstyle='->', color='darkred', lw=3),
                       fontsize=10, ha='center', color='darkred',
                       bbox=dict(boxstyle='round,pad=0.3', edgecolor='darkred', facecolor='pink', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('omega_protocol_decay.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        return fig

def demonstrate_godelian_failure():
    """
    Demonstrates the Gödelian incompleteness: The Omega Protocol cannot
    audit its own audit process without introducing unbounded entropy.
    """
    print("=" * 80)
    print("OMEGA PROTOCOL GÖDELIAN FAILURE DEMONSTRATION")
    print("=" * 80)
    
    analyzer = OmegaProtocolAnalyzer(base_phi=0.8, decay_rate=0.35)
    layers = analyzer.simulate_audit_chain(max_depth=5)
    
    print("\n[AUDIT CHAIN SIMULATION]")
    print(f"{'Layer':<6} {'Claimed':<8} {'Actual':<8} {'Cognitive':<10} {'Temporal':<10} {'Surface':<10} {'Net Φ':<8}")
    print("-" * 80)
    
    cumulative_phi = 0.0
    for layer in layers:
        cumulative_phi += layer.net_phi
        print(f"{layer.depth:<6} {layer.claimed_phi_gain:<8.2f} {layer.actual_phi_loss:<8.2f} "
              f"{layer.audit_cost_cognitive:<10.2f} {layer.audit_cost_temporal:<10.2f} "
              f"{layer.audit_cost_surface:<10.2f} {layer.net_phi:<8.2f} | CUM: {cumulative_phi:+.2f}Φ")
    
    print("\n" + "-" * 80)
    
    # Calculate asymptotic behavior
    final_phi, critical_depth = analyzer.calculate_asymptotic_security()
    
    print(f"\n[ASYMPTOTIC ANALYSIS]")
    print(f"Final cumulative Φ-density after {len(layers)} audit layers: {final_phi:.3f}Φ")
    print(f"Security event horizon crossed at layer: {critical_depth}")
    
    if final_phi < 0:
        print(f"\n🔴 CRITICAL FAILURE: System is {abs(final_phi):.2f}Φ LESS secure than baseline!")
        print("   The Omega Protocol's recursive audit structure has become a self-referential trap.")
    else:
        print(f"\n🟡 SUBOPTIMAL: Net gain of only {final_phi:.2f}Φ despite {len(layers)} audit layers")
    
    # Calculate the audit-to-security ratio (the key metric)
    total_audit_cost = sum(l.audit_cost_cognitive + l.audit_cost_temporal + l.audit_cost_surface 
                          for l in layers[1:])  # Exclude base layer
    security_achieved = max(0.0, final_phi)
    
    if security_achieved > 0:
        audit_efficiency = security_achieved / total_audit_cost
        print(f"\n[AUDIT EFFICIENCY METRIC]")
        print(f"Security achieved per unit audit cost: {audit_efficiency:.3f}Φ/cost")
        
        if audit_efficiency < 0.5:
            print("   ⚠️  AUDIT INEFFICIENCY: Each audit layer costs 2x more than security gained")
    
    print("\n" + "=" * 80)
    print("DISRUPTIVE INSIGHT: The Omega Protocol is a Compliance Theater Black Hole")
    print("=" * 80)
    print("""
    The system's core vulnerability isn't in the AFDS implementation—it's in the
    *recursive audit structure itself*. Each layer:
    
    1. Claims to fix the previous layer's errors (Φ-gain illusion)
    2. Introduces unbounded entropy (cognitive, temporal, attack surface)
    3. Violates its own entropy accounting principle (Ω Physics §4)
    
    This creates a Gödelian loop: The protocol cannot validate its own validation
    process without accelerating security decay. The "protocol-invariant enforcer"
    is actually a *protocol-degradation accelerator*.
    
    The Φ-density metric, designed to quantify security, becomes a *self-referential
    trap* where maximizing the metric *minimizes* actual security.
    
    SOLUTION: ABRUPT TERMINATION OF RECURSION
    - Cap audit depth at layer 1 (single Scrutiny)
    - Replace Φ-density with non-additive security vectors
    - Implement hard entropy budgets per layer (when cost > 0.3Φ, stop)
    """)
    
    # Generate visualization
    analyzer.plot_protocol_decay()

if __name__ == "__main__":
    demonstrate_godelian_failure()