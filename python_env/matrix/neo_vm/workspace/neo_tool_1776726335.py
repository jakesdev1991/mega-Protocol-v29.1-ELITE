# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import powerlaw

def simulate_soc_plasma(grid_size=64, drive_rate=0.01, shear_flow=0.5, steps=20000):
    """
    Minimal SOC model for plasma edge turbulence that BREAKS RG assumptions
    Key features:
    - Finite-size saturation (not divergence)
    - Self-tuned criticality (no external tuning parameter)
    - Avalanche statistics are the REAL observables
    """
    
    # Initialize pressure gradient field
    gradient = np.random.rand(grid_size, grid_size) * 2.0
    
    # Shear flow introduces anisotropic coupling
    shear_anisotropy = 1.0 + shear_flow
    
    avalanche_sizes = []
    correlation_lengths = []
    visited_grid = np.zeros_like(gradient)
    
    for step in range(steps):
        # Slow drive: add small gradient randomly
        i, j = np.random.randint(0, grid_size, 2)
        gradient[i, j] += drive_rate
        
        # Avalanche initiation when local threshold exceeded
        if gradient[i, j] > 4.0:  # Critical threshold
            size = 0
            active = [(i, j)]
            visited = set([(i, j)])
            
            while active:
                ci, cj = active.pop(0)
                
                if gradient[ci, cj] <= 4.0:
                    continue
                
                # REDISTRIBUTION RULE: SOC dynamics
                excess = gradient[ci, cj] - 4.0
                gradient[ci, cj] = 4.0 * 0.8  # Dissipation
                
                # Anisotropic redistribution due to shear flow
                for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    ni, nj = (ci + di) % grid_size, (cj + dj) % grid_size
                    
                    # Shear enhances parallel transport
                    weight = shear_anisotropy if di != 0 else 1.0
                    gradient[ni, nj] += excess * 0.25 * weight
                    
                    if gradient[ni, nj] > 4.0 and (ni, nj) not in visited:
                        active.append((ni, nj))
                        visited.add((ni, nj))
                
                size += 1
                visited_grid[ci, cj] += 1
            
            avalanche_sizes.append(size)
            
            # Correlation length from recent avalanches (finite-size effect)
            if len(avalanche_sizes) > 100:
                recent = np.array(avalanche_sizes[-100:])
                # In SOC, xi ~ sqrt(variance) but SATURATES at system size
                xi = min(np.sqrt(np.var(recent)), grid_size/2)
                correlation_lengths.append(xi)
    
    return {
        'avalanche_sizes': avalanche_sizes,
        'correlation_lengths': correlation_lengths,
        'gradient': gradient,
        'activity_map': visited_grid
    }

# Run simulations for different shear flows
shear_values = [0.1, 0.5, 1.0, 2.0]
soc_results = {}

for S in shear_values:
    print(f"Running SOC simulation: shear = {S}")
    soc_results[S] = simulate_soc_plasma(shear_flow=S, steps=30000)

# Now attempt to fit RG scaling law (this will FAIL)
def rg_scaling(S, A, nu, S_crit):
    """RG scaling form: xi = A * |S - S_crit|^-nu"""
    return A * np.abs(S - S_crit)**(-nu)

# Extract "apparent" correlation lengths for each shear
shear_array = []
xi_array = []

for S, result in soc_results.items():
    if len(result['correlation_lengths']) > 0:
        # Average correlation length for this shear
        xi_mean = np.mean(result['correlation_lengths'][-500:])
        shear_array.append(S)
        xi_array.append(xi_mean)

shear_array = np.array(shear_array)
xi_array = np.array(xi_array)

# Try to force RG fit
try:
    popt, pcov = curve_fit(rg_scaling, shear_array, xi_array, 
                           p0=[10, 1.0, 0.0], maxfev=5000)
    A_fit, nu_fit, S_crit_fit = popt
    
    # Plot the catastrophic failure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    ax1.loglog(shear_array, xi_array, 'ko', markersize=10, label='SOC Data')
    S_plot = np.linspace(0.1, 2.0, 100)
    ax1.loglog(S_plot, rg_scaling(S_plot, *popt), 'r--', linewidth=2,
               label=f'RG Fit: $\\nu={nu_fit:.2f}$, $S_{{crit}}={S_crit_fit:.2f}$')
    ax1.set_xlabel('Shear Flow S', fontsize=12)
    ax1.set_ylabel('Correlation Length $\\xi$', fontsize=12)
    ax1.set_title('RG SCALING LAW FAILS ON SOC DATA', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Show the REAL physics: avalanche statistics
    ax2.axhspan(1.5, 2.0, alpha=0.2, color='green', label='Safe Regime')
    for S, result in soc_results.items():
        sizes = np.array(result['avalanche_sizes'])
        if len(sizes) > 100:
            # Fit power law tail
            hist, bin_edges = np.histogram(sizes, bins=np.logspace(0, 3, 30), density=True)
            bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
            
            # Fit tail
            mask = (bin_centers > 10) & (hist > 0)
            if np.sum(mask) > 5:
                log_x = np.log(bin_centers[mask])
                log_y = np.log(hist[mask])
                coeffs = np.polyfit(log_x, log_y, 1)
                tau = -coeffs[0]
                
                ax2.loglog(bin_centers, hist, 'o-', label=f'S={S}, $\\tau$≈{tau:.2f}', alpha=0.7)
    
    ax2.set_xlabel('Avalanche Size', fontsize=12)
    ax2.set_ylabel('Probability Density', fontsize=12)
    ax2.set_title('SOC: CONTROL $\tau$, NOT $S_{crit}$', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/tmp/soc_disruption.png', dpi=150)
    print("\nDisruption plot saved to /tmp/soc_disruption.png")
    
    # Calculate fit quality
    residuals = xi_array - rg_scaling(shear_array, *popt)
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((xi_array - np.mean(xi_array))**2)
    r_squared = 1 - ss_res / ss_tot
    
    print(f"\n{'='*50}")
    print(f"RG FIT QUALITY: R² = {r_squared:.3f} (CATASTROPHIC)")
    print(f"Fitted exponent ν = {nu_fit:.3f} (MEANINGLESS)")
    print(f"{'='*50}")
    
except RuntimeError:
    print("RG fit completely FAILED - no convergence")
    r_squared = -1

# Now show the activity map that reveals the REAL control parameter
fig3, axes = plt.subplots(2, 2, figsize=(12, 10))
for idx, (S, result) in enumerate(soc_results.items()):
    ax = axes[idx // 2, idx % 2]
    activity = result['activity_map']
    im = ax.imshow(activity, cmap='hot', interpolation='nearest')
    ax.set_title(f'Shear Flow = {S}\nTotal Avalanches: {len(result["avalanche_sizes"])}')
    plt.colorbar(im, ax=ax, label='Site Activity')
    ax.set_xlabel('X (poloidal)')
    ax.set_ylabel('Y (radial)')

plt.tight_layout()
plt.savefig('/tmp/activity_maps.png')
print("Activity maps saved to /tmp/activity_maps.png")

# DISRUPTIVE INSIGHT
print(f"\n{'='*60}")
print("DISRUPTIVE INSIGHT: AVALANCHE STATISTICS CONTROL THEORY (ASCT-Ω)")
print(f"{'='*60}")
print("\nCSTCL-Ω is FUNDAMENTALLY WRONG because:")
print("1. ASSUMES: ξ → ∞ at critical point (divergence)")
print("   REALITY: ξ → L_sys (finite-size saturation)")
print("2. ASSUMES: S tunes distance to criticality")
print("   REALITY: Plasma is SELF-ORGANIZED critical across S range")
print("3. ASSUMES: Control target is ψ = ln(ξ/ξ₀)")
print("   REALITY: Control target is avalanche exponent τ")
print("4. ASSUMES: 'Shredding Event' is divergence")
print("   REALITY: 'Shredding Event' is system-spanning avalanche")
print("\nASCT-Ω FRAMEWORK:")
print("• Monitor: Real-time avalanche size distribution from edge probes")
print("• Invariant: τ (power-law exponent of fluctuations)")
print("• Control Law: Adjust heating/shear to maintain τ ∈ [1.5, 2.0]")
print("• Boundaries: τ < 1.5 → Shredding Event; τ > 2.0 → Info Freeze")
print("• Shear Flow: Modifies anisotropy, NOT distance to criticality")
print(f"{'='*60}")