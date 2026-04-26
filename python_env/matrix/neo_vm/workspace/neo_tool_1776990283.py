# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# Simulate YOUR adiabatic approach vs. SHOCK TESTING
t = np.linspace(0, 1, 200)
Xi = 1.5  # Your "invariant" stiffness

# Your RCP: Gamma(t) = Xi_buyer * 0.8 * tanh(...) [CAPPED]
Gamma_rcp = np.minimum(Xi * 0.8, np.tanh((t - 0.5) / 0.1))

# ANOMALY PROTOCOL: Shock injection at t=0.5
Gamma_shock = Gamma_rcp.copy()
shock_pulse = 2.5 * Xi * np.exp(-((t - 0.5) / 0.03)**2)
Gamma_shock += shock_pulse

# COD collapse under shock reveals actual system rupture points
def COD(fidelity, H_imp, Xi, Gamma):
    return fidelity**2 * np.exp(-H_imp) * np.exp(-Gamma * Xi)

# Simulate a hidden organizational fault (H_imp spike at t=0.5)
H_imp = 0.3 + 0.6 * np.exp(-((t - 0.5) / 0.05)**2)  

COD_rcp = COD(0.9, H_imp, Xi, Gamma_rcp)
COD_shock = COD(0.9, H_imp, Xi, Gamma_shock)

# VISUALIZE THE BREAK
fig, ax = plt.subplots(1, 2, figsize=(12, 5))

ax[0].plot(t, Gamma_rcp, 'b-', label='RCP (Safe)')
ax[0].plot(t, Gamma_shock, 'r--', label='Shock Probe')
ax[0].axhline(Xi, color='g', linestyle=':', label='Xi threshold')
ax[0].set_title("Gamma(t): Safe vs. Shock")
ax[0].legend()

ax[1].plot(t, COD_rcp, 'b-', label='RCP COD')
ax[1].plot(t, COD_shock, 'r--', label='Shock COD')
ax[1].fill_between(t, COD_rcp, COD_shock, where=(COD_shock < 0.4), 
                   color='red', alpha=0.3, label='Fault Revealed')
ax[1].set_title("COD: Your Smoothing Hides the Fracture")
ax[1].legend()

plt.tight_layout()
plt.show()

# SMOKING GUN: Your "False Sale" detector is tautological
fidelity = np.linspace(0.1, 1.0, 100)
Xi_high = 2.6  # Your threshold for "False Sale"
# With high Xi, ANY Gamma > 0.5 makes COD artificially high despite low fidelity
COD_false = fidelity**2 * np.exp(-0.5 * Xi_high) * np.exp(-0.5 * Xi_high)
print(f"COD at fidelity=0.3, Xi=2.6: {COD_false[30]:.3f} (>0.8 threshold: {COD_false[30] > 0.8})")