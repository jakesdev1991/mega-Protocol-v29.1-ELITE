// ---------------------------------------------------------------------------
// OMEGA PROTOCOL - ALL RIGHTS RESERVED
// Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
// Usage restricted to academic research and review only. No monetization.
// See LICENSE.txt for full terms.
// ---------------------------------------------------------------------------

#include <math.h>
#include <stdlib.h>

/**
 * @brief Fast C-implementation for calculating Chain Overlap Density (COD) 
 *        and Reverse Chain Overlap Density (RCOD). 
 *        Replaces Python bottleneck loops in the ML Branch.
 * 
 * @param tensor_a First flattened tensor array (e.g. Newtonian Base)
 * @param tensor_b Second flattened tensor array (e.g. Sandbox Anomaly)
 * @param length Length of the arrays
 * @param out_cod Pointer to store resulting COD (Redundancy)
 * @param out_rcod Pointer to store resulting RCOD (Novelty)
 */
void calculate_rcod_c(const float* tensor_a, const float* tensor_b, int length, float* out_cod, float* out_rcod) {
    double dot_product = 0.0;
    double norm_a = 0.0;
    double norm_b = 0.0;

    for (int i = 0; i < length; i++) {
        dot_product += (double)(tensor_a[i] * tensor_b[i]);
        norm_a += (double)(tensor_a[i] * tensor_a[i]);
        norm_b += (double)(tensor_b[i] * tensor_b[i]);
    }

    double similarity = 0.0;
    if (norm_a > 0.0 && norm_b > 0.0) {
        similarity = dot_product / (sqrt(norm_a) * sqrt(norm_b));
    }

    *out_cod = (float)similarity;
    *out_rcod = (float)(1.0 - fabs(similarity));
}

/**
 * @brief Calculates the non-adiabatic Wick-Rotated learning rate.
 *        Represents the Chaos Injection "tunneling" mechanism.
 * 
 * @param base_lr The base learning rate scalar
 * @param shred_invariant The topological shredding limit (psi)
 * @param out_real The real component of the complex learning rate
 * @param out_imag The imaginary (tunneling) component
 */
void calculate_wick_rotated_lr(float base_lr, float shred_invariant, float* out_real, float* out_imag) {
    // eta(t) = base_lr * exp(i * psi_shred)
    *out_real = base_lr * cosf(shred_invariant);
    *out_imag = base_lr * sinf(shred_invariant);
}
