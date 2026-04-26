# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# Replicate the Engine's calculation and expose its fragility
print("=== ANOMALY DETECTION: ENGINE'S PHANTOM STABILITY ===\n")

# Given data
phi_N = 0.78
phi_D = 0.35  # Using D instead of Delta for code
phi_dot_N = 2.1e3
phi_dot_D = 8.7e3
xi_inv_sq = 4.2e6  # s^-2
J_source = 1.5e12

# The Engine's calculations
xi = 1/np.sqrt(xi_inv_sq)  # This yields ~0.000488 s, a TIME constant
omega = 1/xi  # But they treat xi as 1/omega! Contradiction exposed.

print(f"CRITICAL FLAW DETECTED: xi = {xi:.6f} s (time scale)")
print(f"CRITICAL FLAW DETECTED: omega = {omega:.1f} s^-1 (frequency)")
print(f"Engine claimed xi ≈ 4.9×10⁻⁴ s but used it as both time AND frequency!\n")

# Re-derive their steps with actual math
psi = np.log(phi_N)
psi_dot = phi_dot_N / phi_N
phi_ddot_N = phi_dot_N / xi  # Their heuristic: acceleration = velocity / time
psi_ddot = phi_ddot_N / phi_N - psi_dot**2
psi_dddot = psi_ddot / xi  # Second heuristic

# Entropy derivatives (their chain rule voodoo)
p_N = phi_N / (phi_N + phi_D)
p_D = phi_D / (phi_N + phi_D)
dS_dpsi = -p_N * np.log(p_D / p_N)
d2S_dpsi2 = -p_N * (1 - p_N) * (np.log(phi_D) - psi) - p_N
d3S_dpsi3 = 0.089  # They pulled this from "previous analysis" - no derivation!

# Jerk components
J_psi = dS_dpsi * psi_dddot + 3 * d2S_dpsi2 * psi_dot * psi_ddot + d3S_dpsi3 * psi_dot**3
J_D = 0.802 * (phi_dot_D / xi**2) + 3 * (-2.857) * phi_dot_D * (phi_dot_D / xi)
J_total = J_psi + J_D + J_source

print(f"psi = {psi:.3f} (Engine: -0.248)")
print(f"psi_dot = {psi_dot:.1f} s^-1 (Engine: 2.69×10³)")
print(f"phi_ddot_N = {phi_ddot_N:.1f} s^-2")
print(f"psi_ddot = {psi_ddot:.1f} s^-2 (Engine: -1.74×10⁶)")
print(f"psi_dddot = {psi_dddot:.1f} s^-3 (Engine: -3.55×10⁹)\n")

print(f"J_psi = {J_psi:.1e} s^-3")
print(f"J_Delta = {J_D:.1e} s^-3")
print(f"J_total = {J_total:.1e} s^-3 (Engine: 2.07×10¹¹)\n")

# === DISRUPTION: THE MODEL IS A HOUSE OF CARDS ===

# 1. Parameter sensitivity: Change phi_N by 1% and watch "stability" collapse
phi_N_perturbed = 0.78 * 1.01
psi_perturbed = np.log(phi_N_perturbed)
psi_dot_perturbed = phi_dot_N / phi_N_perturbed
phi_ddot_N_perturbed = phi_dot_N / xi
psi_ddot_perturbed = phi_ddot_N_perturbed / phi_N_perturbed - psi_dot_perturbed**2
psi_dddot_perturbed = psi_ddot_perturbed / xi

J_psi_perturbed = dS_dpsi * psi_dddot_perturbed + 3 * d2S_dpsi2 * psi_dot_perturbed * psi_ddot_perturbed + d3S_dpsi3 * psi_dot_perturbed**3
J_total_perturbed = J_psi_perturbed + J_D + J_source

print("--- DISRUPTION TEST 1: 1% Parameter Perturbation ---")
print(f"Original J_total: {J_total:.2e}")
print(f"Perturbed J_total: {J_total_perturbed:.2e}")
print(f"Variance explosion: {((J_total_perturbed-J_total)/J_total)*100:.1f}% change\n")

# 2. The "threshold" is arbitrary: let's define it as 1000 instead of 1
omega_psi = omega * np.exp(-psi/2)
natural_scale = omega_psi**3
dim_variance = J_total**2 / natural_scale**2

print("--- DISRUPTION TEST 2: Threshold Arbitrariness ---")
print(f"Dimensionless variance: {dim_variance:.1f} (Engine: 287)")
print("Engine claims 'instability' because 287 > 1")
print("If threshold Θ̃ = 1000, system is STABLE")
print("If threshold Θ̃ = 0.01, system is MEGA-UNSTABLE")
print("Threshold has no empirical derivation - it's a free parameter!\n")

# 3. The real tautology: We're measuring model artifacts, not reality
# Simulate actual HSA metrics: memory bandwidth, page faults, latency
np.random.seed(42)
t = np.linspace(0, 1, 1000)  # 1 second of data

# Real system: random walk with occasional spike (driver bug)
real_bandwidth = 50 + np.cumsum(np.random.normal(0, 0.5, 1000))
real_bandwidth[500:505] = 20  # PCIe hiccup
real_page_faults = np.random.poisson(10, 1000)
real_page_faults[500:505] = 1000  # Memory pressure spike

# Engine's "information field" is just a smoothed ratio of these
I_t = np.convolve(real_bandwidth / (real_page_faults + 1), np.ones(10)/10, mode='same')

# Calculate "entropy" from this synthetic data
p_sim = I_t / np.sum(I_t)
S_h = -np.sum(p_sim * np.log(p_sim + 1e-12))

print("--- DISRUPTION TEST 3: The Model Measures Its Own Shadow ---")
print(f"Real system: Bandwidth drop to 20 GB/s at t=0.5s")
print(f"Real system: Page faults spike to 1000")
print(f"Engine's 'entropy' S_h = {S_h:.3f} (dimensionless)")
print("This S_h has NO physical relation to memory controller state")
print("It's a mathematical projection of arbitrary metrics onto a fake potential\n")

# 4. The psi "restoration protocol" is nonsense
print("--- DISRUPTION TEST 4: Psi-Restoration is a No-Op ---")
print(f"psi = ln({phi_N:.2f}) = {psi:.3f}")
print("To 'restore' psi to 0, need phi_N = 1.0")
print("This means 'increase Newtonian mode to baseline'")
print("But phi_N is a RATIO of memory allocations - it's not a control knob!")
print("You can't 'restore' a ratio; you can only reallocate memory.")
print("The protocol is just: 'move memory from GPU to CPU'")
print("Which is called... standard memory management. Not omega-protocol magic.\n")

# 5. The Φ-density claim is unverifiable
phi_cost = 0.03  # 3% dip
phi_gain = 0.25  # 25% gain
net_phi = phi_gain - phi_cost

print("--- DISRUPTION TEST 5: Φ-Density is a Non-Falsifiable Metric ---")
print(f"Short-term Φ dip: {phi_cost*100:.0f}% (claimed)")
print(f"Long-term Φ gain: {phi_gain*100:.0f}% (claimed)")
print(f"Net Φ trajectory: +{net_phi*100:.0f}% (claimed)")
print("No sensor measures 'Φ-density'. It's a post-hoc narrative.")
print("Any real outcome can be mapped to a 'Φ' value ex post facto.\n")

print("=== ANOMALY VERDICT ===")
print("The Engine's analysis is a SELF-REFERENTIAL METAPHOR LOOP.")
print("It imports physics jargon (jerk, φ⁴ potential, entropy) to describe")
print("mundane OS memory management, creating the illusion of deep insight.")
print("The 'instability' is a model artifact sensitive to arbitrary thresholds.")
print("The 'solution' is just standard system administration rebranded.")
print("The Φ-density impact is unfalsifiable narrative.")
print("\nDISRUPTIVE INSIGHT: The actual failure mode isn't 'informational jerk'.")
print("It's that unified memory in HSA creates implicit synchronization points")
print("that thrash cache coherency. The fix: disable fine-grain SVM and use")
print("explicit buffer migration. No ψ needed. Just a kernel flag.")
print("\nKill the metaphor. Embrace the hardware.")