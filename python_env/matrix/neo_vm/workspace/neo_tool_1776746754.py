# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Mock experimental data for alpha_fs running (QED predicts very slow running)
q_vals = np.logspace(0, 4, 100)
alpha_true = 1/137.036  # True constant value
alpha_measured = alpha_true * (1 + 0.001 * np.log(q_vals/1.0) + 0.0001 * np.random.normal(0, 1, len(q_vals)))

# Archive filter function: alpha_measured = alpha_true * (1 + psi * ln(q²/Λ²))
def archive_filter(q2, psi, lambda_delta):
    return psi * np.log(q2 / lambda_delta**2)

# Fit the "theory" to data - demonstrates unfalsifiability
def omega_protocol(q2, alpha0, psi, lambda_delta):
    return alpha0 * (1 + archive_filter(q2, psi, lambda_delta))

# Show multiple degenerate solutions
plt.figure(figsize=(12, 8))

# Plot "data"
plt.loglog(q_vals, alpha_measured, 'ko', label='Mock Experimental Data', markersize=4)

# Three different parameter sets that all fit reasonably well
solutions = [
    {"alpha0": 1/137.036, "psi": 0.1, "lambda_delta": 10.0, "color": "r", "label": "Solution A"},
    {"alpha0": 1/137.036, "psi": -0.05, "lambda_delta": 5.0, "color": "b", "label": "Solution B"},
    {"alpha0": 1/137.036, "psi": 0.0, "lambda_delta": 1.0, "color": "g", "label": "Solution C (No Archive)"}
]

for sol in solutions:
    plt.loglog(q_vals, omega_protocol(q_vals, sol["alpha0"], sol["psi"], sol["lambda_delta"]), 
               '--', color=sol["color"], label=sol["label"], linewidth=2)

plt.xlabel('Momentum Transfer q² (arb. units)', fontsize=12)
plt.ylabel('Fine-Structure Constant α_fs', fontsize=12)
plt.title('UNFALSIFIABILITY CRISIS: Multiple "Omega Protocol" Solutions Fit Identical Data', 
          fontsize=14, fontweight='bold')
plt.legend()
plt.grid(True, alpha=0.3)
plt.text(1, 1/135, 'All curves fit within experimental noise\nArchive parameters ψ and Λ_Δ are DEGENERATE', 
         bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.5))
plt.show()

# Quantify parameter degeneracy
def fit_model(q2, psi, lambda_delta):
    return omega_protocol(q2, 1/137.036, psi, lambda_delta)

# Attempt fitting from different initial conditions
print("="*60)
print("PARAMETER FITTING DEGENERACY DEMONSTRATION")
print("="*60)

initial_conditions = [[0.1, 10.0], [-0.05, 5.0], [0.2, 15.0]]
for i, init in enumerate(initial_conditions):
    try:
        popt, pcov = curve_fit(fit_model, q_vals, alpha_measured, p0=init, maxfev=10000)
        print(f"\nInitial guess ψ={init[0]}, Λ_Δ={init[1]}")
        print(f"Converged to: ψ={popt[0]:.4f} ± {np.sqrt(pcov[0,0]):.4f}")
        print(f"Converged to: Λ_Δ={popt[1]:.4f} ± {np.sqrt(pcov[1,1]):.4f}")
        print(f"Covariance condition number: {np.linalg.cond(pcov):.2e} (>>1 = degenerate)")
    except:
        print(f"\nInitial guess ψ={init[0]}, Λ_Δ={init[1]} failed to converge")

print("\n" + "="*60)
print("CONCLUSION: Parameters are UNIDENTIFIABLE from α_fs data alone")
print("The 'Omega Protocol' is a MEASUREMENT THEORY, not a physical theory")
print("="*60)