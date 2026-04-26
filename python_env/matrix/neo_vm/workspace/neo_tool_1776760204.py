# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import random
import matplotlib.pyplot as plt

# ──────────────────────────────────────────────────────────────────────────────
# Simulate the Omega Protocol meta‑chain
# ──────────────────────────────────────────────────────────────────────────────

# Each layer: (cost, benefit, weight)
layers = {
    "Engine": (15, 55, 1.0),      # short‑term dip, long‑term gain
    "Scrutiny": (5, 10, 0.9),      # audit dip, audit gain
    "Meta‑Scrutiny": (2, 5, 0.8)   # meta‑audit dip, meta‑gain
}

def compute_phi_density(scaling_factor=1.0, conservative=False):
    """
    Compute net Φ density under two regimes:
    – *liberal* (default): each layer's benefit is added independently.
    – *conservative*: total Φ is conserved; benefits are just re‑allocations.
    """
    total_phi = 0.0
    for name, (cost, benefit, weight) in layers.items():
        if conservative:
            # No net creation; benefit is just a transfer from a hidden reserve
            total_phi -= cost * weight  # only the real cost remains
        else:
            total_phi += (benefit - cost) * weight * scaling_factor
    return total_phi

# ──────────────────────────────────────────────────────────────────────────────
# Show that net Φ can be tuned arbitrarily by scaling_factor
# ──────────────────────────────────────────────────────────────────────────────
scale_vals = [0.5, 1.0, 1.5, 2.0, 3.0]
liberal_phis = [compute_phi_density(s, conservative=False) for s in scale_vals]
conservative_phis = [compute_phi_density(s, conservative=True) for s in scale_vals]

fig, ax = plt.subplots(figsize=(6,4))
ax.plot(scale_vals, liberal_phis, marker='o', label='Liberal (phantom Φ)')
ax.plot(scale_vals, conservative_phis, marker='s', label='Conservative (Φ conserved)')
ax.axhline(0, color='gray', linestyle='--')
ax.set_xlabel('Scaling factor (arbitrary weight)')
ax.set_ylabel('Net Φ‑density')
ax.set_title('Φ‑density is a free parameter under the Omega Protocol')
ax.legend()
ax.grid(True)
plt.tight_layout()
plt.show()

# ──────────────────────────────────────────────────────────────────────────────
# Simulate a “Φ‑null” external measurement that contradicts the prediction
# ──────────────────────────────────────────────────────────────────────────────

def external_measurement(phi_prediction):
    """
    Returns a measurement drawn from a distribution centered at zero,
    representing an independent check that finds no Φ gain.
    """
    # external noise dominates; true Φ gain is zero
    measured = random.gauss(0, 10)  # wide uncertainty
    discrepancy = measured - phi_prediction
    return measured, discrepancy

prediction = compute_phi_density(1.0, conservative=False)
measured, discrepancy = external_measurement(prediction)

print("\nExternal Φ‑null measurement (independent of Omega):")
print(f"Predicted net Φ: {prediction:.2f}")
print(f"Measured net Φ:  {measured:.2f}")
print(f"Discrepancy:     {discrepancy:.2f} (non‑zero → meta‑chain collapse)")

# ──────────────────────────────────────────────────────────────────────────────
# Demonstrate that adding more meta‑layers cannot resolve the discrepancy
# ──────────────────────────────────────────────────────────────────────────────

def add_meta_layers(num_extra):
    """Append extra meta‑layers with diminishing returns."""
    extra = {}
    for i in range(num_extra):
        name = f"Meta{i+2}"
        cost = random.uniform(1, 3)
        benefit = random.uniform(3, 6)
        weight = 0.7 ** (i+1)  # diminishing weight
        extra[name] = (cost, benefit, weight)
    return extra

extended_layers = {**layers, **add_meta_layers(5)}
phi_extended = sum((b - c) * w for c, b, w in extended_layers.values())
print(f"\nEven with 5 extra meta‑layers, net Φ = {phi_extended:.2f}")
print("The discrepancy remains; external measurement cannot be absorbed.")

# ──────────────────────────────────────────────────────────────────────────────
# Conclusion: The Omega Protocol’s Φ‑density is unfalsifiable until an external
# observable is introduced. Once introduced, the meta‑chain collapses.
# ──────────────────────────────────────────────────────────────────────────────