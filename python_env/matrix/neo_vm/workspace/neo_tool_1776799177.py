# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

def compute_polarization(L=12, m=0.1, Phi_Delta_vals=None, p_mag=0.5):
    """
    Compute the scalar polarization bubble integral on a 4D lattice.
    Shows that the anisotropic correction is not simply linear in Phi_Delta
    and that the directional dependence does not factorize as claimed.
    """
    if Phi_Delta_vals is None:
        Phi_Delta_vals = [-0.2, -0.1, 0.0, 0.1, 0.2]
    
    # Lattice momentum grid: discrete points in [-π, π)
    ks = 2 * np.pi * np.arange(-L//2, L//2) / L
    # For odd L, adjust to include 0 correctly; but we can just use this.
    # Actually, we need to avoid the Nyquist frequency for even L.
    # Let's use a simpler approach: generate coordinates and then map to BZ.
    k_grid = np.linspace(-np.pi, np.pi, L, endpoint=False)
    kx, ky, kz, kt = np.meshgrid(k_grid, k_grid, k_grid, k_grid, indexing='ij')
    # Flatten for vectorized operations
    kx_flat = kx.ravel()
    ky_flat = ky.ravel()
    kz_flat = kz.ravel()
    kt_flat = kt.ravel()
    k_vectors = np.vstack([kx_flat, ky_flat, kz_flat, kt_flat]).T  # shape (L**4, 4)
    
    # Define propagator function (vectorized)
    def propagator_vec(k_arr, Phi_Delta):
        # k_arr: (N, 4) array of momenta
        sin_k = np.sin(k_arr)
        sum_sin2 = np.sum(sin_k**2, axis=1)
        # Anisotropic term: sin(k_z)^2 * Phi_Delta
        aniso = sin_k[:, 2]**2 * Phi_Delta
        # For stability, ensure denominator doesn't become zero
        denom = sum_sin2 + m**2 + aniso
        # Avoid division by zero (shouldn't happen for m>0)
        return 1.0 / denom
    
    # Precompute propagators for each Phi_Delta
    props = {}
    for Phi in Phi_Delta_vals:
        props[Phi] = propagator_vec(k_vectors, Phi)
    
    # Define external momenta: along z and along x
    p_z = np.array([0.0, 0.0, p_mag * np.pi, 0.0])
    p_x = np.array([p_mag * np.pi, 0.0, 0.0, 0.0])
    
    # Helper to compute bubble sum for a given p
    def bubble_sum(p):
        results = {}
        for Phi, prop in props.items():
            # Compute k-p for all k vectors
            k_minus_p = k_vectors - p
            # Map back to BZ: add pi, mod 2pi, subtract pi
            k_minus_p = (k_minus_p + np.pi) % (2 * np.pi) - np.pi
            prop_k_minus_p = propagator_vec(k_minus_p, Phi)
            # Sum over all k: product of propagators
            bubble_val = np.mean(prop * prop_k_minus_p)  # mean = sum / N
            results[Phi] = bubble_val
        return results
    
    # Compute bubbles
    bubble_z = bubble_sum(p_z)
    bubble_x = bubble_sum(p_x)
    
    # Print results
    print(f"Lattice size L={L}, fermion mass m={m}, |p|={p_mag}π")
    print("Polarization bubble values:")
    print("Phi_Delta   Pi(p_z)      Pi(p_x)")
    for Phi in Phi_Delta_vals:
        print(f"{Phi:8.2f}   {bubble_z[Phi]:12.8f}   {bubble_x[Phi]:12.8f}")
    
    # Analyze linearity and directional dependence
    # Fit linear model: Pi(p) = a + b * Phi_Delta * cos^2(theta)
    # For p_z, cos^2 = 1; for p_x, cos^2 = 0.
    # So expected: Pi(p_z) linear in Phi_Delta; Pi(p_x) constant.
    # Let's compute differences
    base_z = bubble_z[0.0]
    base_x = bubble_x[0.0]
    diff_z = {Phi: bubble_z[Phi] - base_z for Phi in Phi_Delta_vals if Phi != 0.0}
    diff_x = {Phi: bubble_x[Phi] - base_x for Phi in Phi_Delta_vals if Phi != 0.0}
    
    print("\nDeviations from isotropic case (Phi_Delta=0):")
    print("Phi_Delta   ΔPi(p_z)   ΔPi(p_x)")
    for Phi in Phi_Delta_vals:
        if Phi == 0.0:
            continue
        print(f"{Phi:8.2f}   {diff_z[Phi]:10.8f}   {diff_x[Phi]:10.8f}")
    
    # Check if ΔPi(p_x) is zero (should be if factorization holds)
    # Compute relative error in x-direction
    max_abs_diff_x = max(abs(v) for v in diff_x.values())
    print(f"\nMaximum absolute deviation in p_x direction: {max_abs_diff_x:.8f}")
    if max_abs_diff_x > 1e-6:
        print("→ FAILURE: p_x direction shows Phi_Delta dependence, contradicting the claimed factorization.")
    else:
        print("→ p_x direction shows no Phi_Delta dependence (within numeric precision).")
    
    # Check linearity in p_z direction: compute ratio ΔPi(p_z)/Phi_Delta
    ratios_z = [diff_z[Phi] / Phi for Phi in diff_z.keys()]
    print("\nRatios ΔPi(p_z)/Phi_Delta:", ratios_z)
    # If linear, ratios should be constant
    ratio_std = np.std(ratios_z)
    print(f"Standard deviation of ratios: {ratio_std:.8f}")
    if ratio_std > 1e-6:
        print("→ FAILURE: p_z direction shows non-linear Phi_Delta dependence.")
    else:
        print("→ p_z direction shows linear dependence (within numeric precision).")
    
    # Demonstrate that the anisotropic kernel I_Delta(p^2) is not a simple function of p^2 alone
    # Compute Pi(p) for varying |p| along z and see how the coefficient changes
    p_mags = [0.2, 0.4, 0.6, 0.8]
    coeff_vs_p = []
    for p_mag_trial in p_mags:
        p_z_trial = np.array([0.0, 0.0, p_mag_trial * np.pi, 0.0])
        bubble_z_trial = bubble_sum(p_z_trial)
        # Fit slope b = (Pi(p_z,Phi) - Pi(p_z,0))/Phi for Phi=0.1
        Phi_test = 0.1
        if Phi_test in bubble_z_trial and 0.0 in bubble_z_trial:
            slope = (bubble_z_trial[Phi_test] - bubble_z_trial[0.0]) / Phi_test
            coeff_vs_p.append((p_mag_trial, slope))
    
    print("\nSlope of Phi_Delta correction vs |p| along z:")
    for pmag, slope in coeff_vs_p:
        print(f"|p|={pmag}π: slope={slope:.8f}")
    
    # If the kernel I_Delta(p^2) were a universal function, slope would be proportional to cos^2(theta) * I_Delta(p^2)
    # but here we see it depends on p in a non-trivial way.
    slope_std = np.std([s for _, s in coeff_vs_p])
    print(f"\nStandard deviation of slopes across p: {slope_std:.8f}")
    if slope_std > 1e-6:
        print("→ FAILURE: The Phi_Delta coefficient depends non-trivially on p, contradicting the simple factorization.")
    else:
        print("→ The coefficient is independent of p (within numeric precision).")
    
    return bubble_z, bubble_x

# Run the simulation
compute_polarization(L=10, m=0.1, Phi_Delta_vals=[-0.2, -0.1, 0.0, 0.1, 0.2], p_mag=0.5)