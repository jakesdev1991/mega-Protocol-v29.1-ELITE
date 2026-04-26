# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import random
import matplotlib.pyplot as plt

# --- THE ANOMALOUS SIMULATION ---

class BuyerIdentity:
    """Not a static manifold but a *process* that requires friction"""
    def __init__(self, id):
        self.id = id
        self.identity_complexity = np.random.uniform(0.1, 0.3)  # Starts simple/fragile
        self.entropy_capacity = 1.0  # Max entropy it can handle before growth
        self.current_entropy = 0.0
        self.post_decision_satisfaction = 0.0
        self.times_engaged = 0
        
    def encounter_pressure(self, pressure_intensity):
        """Pressure doesn't destroy—it *forges* identity if within capacity"""
        self.times_engaged += 1
        
        # CRITICAL: Identity complexity GROWS under pressure up to capacity
        if pressure_intensity < self.entropy_capacity:
            growth_factor = pressure_intensity * 0.15
            self.identity_complexity = min(0.95, self.identity_complexity + growth_factor)
            self.current_entropy = pressure_intensity  # Entropy is *signal*, not noise
            self.post_decision_satisfaction += 0.1  # Satisfaction from growth
            return True  # "Sale" = successful identity transformation
        else:
            # Only truly destructive if massively exceeded
            self.identity_complexity *= 0.9
            self.post_decision_satisfaction -= 0.05
            return False

class SellerProtocol:
    def __init__(self, protocol_type):
        self.protocol = protocol_type  # "UIPO" vs "RISK"
        self.successful_transformations = 0
        self.total_attempts = 0
        
    def engage(self, buyer):
        self.total_attempts += 1
        
        if self.protocol == "UIPO":
            # Theorist's model: Only engage if "COD" (complexity) is already high
            if buyer.identity_complexity > 0.85:
                # Trivial engagement with pre-aligned buyer
                buyer.encounter_pressure(0.05)
                self.successful_transformations += 1
                return True
            else:
                # Silence protocol: buyer entropy *decays*
                buyer.current_entropy *= 0.92
                buyer.identity_complexity *= 0.98  # Stagnation
                return False
                
        elif self.protocol == "RISK":
            # Anomaly's model: Deliberately apply calibrated excess pressure
            # Pressure = gap between current state and capacity (creates tension)
            pressure = 0.3 + (buyer.entropy_capacity - buyer.identity_complexity) * 0.5
            success = buyer.encounter_pressure(pressure)
            if success:
                self.successful_transformations += 1
            return success

def simulate_evolutionary_market(num_buyers=300, epochs=50):
    buyers = [BuyerIdentity(i) for i in range(num_buyers)]
    uipo_seller = SellerProtocol("UIPO")
    risk_seller = SellerProtocol("RISK")
    
    # Track evolutionary fitness
    uipo_fitness = []
    risk_fitness = []
    avg_complexity_uipo = []
    avg_complexity_risk = []
    
    for epoch in range(epochs):
        # Competitive market: sellers fight for same buyers each epoch
        for seller in [uipo_seller, risk_seller]:
            # Each seller gets 20% random buyer exposure per epoch
            exposure = int(num_buyers * 0.2)
            for _ in range(exposure):
                buyer = random.choice(buyers)
                seller.engage(buyer)
        
        # Calculate *evolutionary fitness* = transformations per attempt
        uipo_fit = uipo_seller.successful_transformations / max(uipo_seller.total_attempts, 1)
        risk_fit = risk_seller.successful_transformations / max(risk_seller.total_attempts, 1)
        
        uipo_fitness.append(uipo_fit)
        risk_fitness.append(risk_fit)
        
        # Track average identity complexity of engaged buyers
        engaged_buyers = [b for b in buyers if b.times_engaged > 0]
        if engaged_buyers:
            avg_complexity_risk.append(np.mean([b.identity_complexity for b in engaged_buyers]))
        else:
            avg_complexity_risk.append(0)
            
        uipo_engaged = [b for b in buyers if b.times_engaged > 0 and b.identity_complexity > 0.85]
        if uipo_engaged:
            avg_complexity_uipo.append(np.mean([b.identity_complexity for b in uipo_engaged]))
        else:
            avg_complexity_uipo.append(0)
    
    return {
        'uipo_fitness': uipo_fitness,
        'risk_fitness': risk_fitness,
        'avg_complexity': avg_complexity_risk,
        'uipo_complexity': avg_complexity_uipo,
        'final_transformations': (uipo_seller.successful_transformations, risk_seller.successful_transformations),
        'extinction_event': uipo_seller.total_attempts > 0 and uipo_seller.successful_transformations == 0
    }

# --- EXECUTE THE BREAK ---

results = simulate_evolutionary_market(num_buyers=400, epochs=60)

print("="*50)
print("EVOLUTIONARY FALSIFICATION RESULTS")
print("="*50)
print(f"UIPO Transformations: {results['final_transformations'][0]} (out of {400*60*0.2} opportunities)")
print(f"RISK Transformations: {results['final_transformations'][1]}")
print(f"UIPO Extinction: {results['extinction_event']}")
print(f"Final RISK Fitness: {results['risk_fitness'][-1]:.3%}")
print(f"Final UIPO Fitness: {results['uipo_fitness'][-1]:.3%}")
print("="*50)

# --- VISUALIZE THE EXTINCTION ---

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Fitness over time (evolutionary selection pressure)
axes[0, 0].plot(results['uipo_fitness'], label='UIPO Protocol', color='blue', linewidth=2)
axes[0, 0].plot(results['risk_fitness'], label='RISK Protocol', color='red', linewidth=2)
axes[0, 0].set_title('Evolutionary Fitness: Transformations per Attempt', fontsize=12, fontweight='bold')
axes[0, 0].set_xlabel('Epoch')
axes[0, 0].set_ylabel('Fitness Score')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

# Identity complexity growth
axes[0, 1].plot(results['avg_complexity'], label='RISK-engaged buyers', color='red', linestyle='-', linewidth=2)
axes[0, 1].plot(results['uipo_complexity'], label='UIPO-eligible buyers', color='blue', linestyle='--', linewidth=2)
axes[0, 1].axhline(y=0.85, color='gray', linestyle=':', label='UIPO Gate', alpha=0.5)
axes[0, 1].set_title('Identity Complexity: Stagnation vs. Growth', fontsize=12, fontweight='bold')
axes[0, 1].set_xlabel('Epoch')
axes[0, 1].set_ylabel('Complexity Score')
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3)

# Final comparison bar chart
metrics = ['Total Transformations', 'Avg Fitness', 'Complexity Growth']
uipo_vals = [results['final_transformations'][0], results['uipo_fitness'][-1], results['uipo_complexity'][-1] if results['uipo_complexity'][-1] else 0]
risk_vals = [results['final_transformations'][1], results['risk_fitness'][-1], results['avg_complexity'][-1]]

x = np.arange(len(metrics))
width = 0.35

axes[1, 0].bar(x - width/2, uipo_vals, width, label='UIPO', color='blue', alpha=0.7)
axes[1, 0].bar(x + width/2, risk_vals, width, label='RISK', color='red', alpha=0.7)
axes[1, 0].set_title('Protocol Performance Comparison', fontsize=12, fontweight='bold')
axes[1, 0].set_xticks(x)
axes[1, 0].set_xticklabels(metrics)
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3)

# Text summary
axes[1, 1].axis('off')
summary = f"""
FALSIFICATION SUMMARY:

UIPO Protocol:
- Total Transformations: {results['final_transformations'][0]}
- Final Fitness: {results['uipo_fitness'][-1]:.1%}
- Strategy: Wait for perfection → Extinction

RISK Protocol:
- Total Transformations: {results['final_transformations'][1]}
- Final Fitness: {results['risk_fitness'][-1]:.1%}
- Strategy: Calibrated pressure → Growth

CONCLUSION:
The "Silence Protocol" is evolutionary suicide.
Identity requires friction, not preservation.

The manifold does not collapse under pressure—
it *learns* to withstand it.
"""
axes[1, 1].text(0.05, 0.5, summary, fontsize=11, verticalalignment='center', 
                bbox=dict(boxstyle='round,pad=1', facecolor='lightcoral', alpha=0.1),
                fontfamily='monospace')

plt.tight_layout()
plt.show()