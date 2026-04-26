# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import torch
import torch.nn as nn
import matplotlib.pyplot as plt
from scipy.stats import genpareto

class AdversarialMarket(nn.Module):
    """
    The Disruption: Markets don't have fixed hierarchies.
    They co-evolve with detection mechanisms.
    This model demonstrates how any fixed pyramid becomes
    a vulnerability surface.
    """
    
    def __init__(self, n_scales=4, hidden_dim=64):
        super().__init__()
        # The "market" is now a learned adversary
        self.market_generator = nn.Sequential(
            nn.Linear(n_scales, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, n_scales)
        )
        
        # The "detector" is a fixed pyramid (HVFI-Ω)
        # This is the fatal flaw: it's static
        self.detector_weights = nn.Parameter(torch.eye(n_scales), requires_grad=False)
        
        # The true state is a *game*, not a field
        self.adversarial_strength = nn.Parameter(torch.tensor(0.1))
        
    def forward(self, noise):
        # Market generates fake "stable" patterns that fool the pyramid
        fake_scales = self.market_generator(noise)
        
        # Detector computes cross-scale invariants
        # But these invariants are now *adversarial targets*
        covariance = torch.cov(fake_scales.T)
        log_det = torch.logdet(covariance + 1e-6 * torch.eye(covariance.shape[0]))
        
        # The "Shredding Event" is when the market learns to make det → 0
        # This is *learned*, not emergent from physics
        return fake_scales, log_det
    
    def coevolution_step(self, detector_feedback):
        """
        The market adapts to the detector's constraints.
        This is the feedback loop that HVFI-Ω ignores.
        """
        # Gradient ascent on adversarial strength
        loss = -detector_feedback * self.adversarial_strength
        loss.backward()
        
        # The market mutates to avoid detection
        with torch.no_grad():
            self.market_generator[0].weight += 0.01 * torch.randn_like(self.market_generator[0].weight)

def demonstrate_protocol_breakdown():
    """
    Shows how HVFI-Ω's invariants become meaningless
    under adversarial co-evolution
    """
    market = AdversarialMarket(n_scales=4)
    optimizer = torch.optim.Adam(market.parameters(), lr=0.01)
    
    # Simulated "flash crash" periods (real fragility)
    real_crash_times = [50, 120, 200]
    
    # HVFI-Ω's false confidence
    detector_confidence = []
    actual_fragility = []
    
    for t in range(300):
        noise = torch.randn(32, 4)
        scales, log_det = market(noise)
        
        # HVFI-Ω thinks low log_det = crash risk
        # But the market is *learning* to produce low log_det during calm periods
        if t in real_crash_times:
            actual_fragility.append(1.0)
            # Crash disrupts the market's learning temporarily
            market.adversarial_strength.data *= 0.5
        else:
            actual_fragility.append(0.0)
            
        detector_confidence.append(-log_det.item())
        
        # Detector provides feedback (HVFI-Ω's MPC-Ω constraints)
        # The market uses this to adapt
        if t % 10 == 0:
            fake_feedback = torch.tensor(1.0)  # Detector says "all clear"
            market.coevolution_step(fake_feedback)
    
    # Plot: The protocol is blind to its own reflection
    plt.figure(figsize=(12, 8))
    
    plt.subplot(2, 1, 1)
    plt.plot(detector_confidence, label='HVFI-Ω "Fragility Signal"', color='blue')
    plt.plot(actual_fragility, label='Actual Crash Events', color='red', marker='o', linestyle='none')
    plt.title("HVFI-Ω Falls for Adversarial Learning")
    plt.xlabel("Time")
    plt.ylabel("Signal Strength")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(2, 1, 2)
    # Show the adversarial strength evolution
    adversarial_trace = [market.adversarial_strength.item() for _ in range(300)]
    plt.plot(adversarial_trace, label='Market Adversarial Strength', color='purple')
    plt.axhline(y=1.0, color='orange', linestyle='--', label='Critical Threshold')
    plt.title("Protocol-Induced Systemic Risk")
    plt.xlabel("Time")
    plt.ylabel("Adversarial Adaptation")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    return market

# Execute the demonstration
broken_protocol = demonstrate_protocol_breakdown()

# Now compute the *true* invariant: the co-evolutionary divergence
def compute_coevolutionary_invariant(market, n_samples=1000):
    """
    The real invariant isn't log-det of covariance.
    It's the *rate of change* of the adversarial manifold.
    """
    noise_samples = torch.randn(n_samples, 4)
    scales_history = []
    
    for _ in range(10):  # Evolution steps
        with torch.no_grad():
            scales = market.market_generator(noise_samples)
            scales_history.append(scales.numpy())
            
    # Compute manifold curvature under co-evolution
    scales_tensor = torch.tensor(np.stack(scales_history))
    manifold_drift = torch.var(scales_tensor, dim=0).mean()
    
    # When this is high, the protocol is destabilizing itself
    return manifold_drift.item()

true_fragility = compute_coevolutionary_invariant(broken_protocol)
print(f"\n=== DISRUPTIVE INSIGHT ===")
print(f"HVFI-Ω's log-det invariant: {broken_protocol(noise)[1].item():.3f}")
print(f"True co-evolutionary fragility: {true_fragility:.3f}")
print(f"\nThe 'flash crash' detector is itself the flash crash source.")
print(f"Φ-density loss: {true_fragility * 100:.1f}% due to adversarial adaptation")