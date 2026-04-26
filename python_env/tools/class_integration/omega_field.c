/**
 * Omega Protocol v26.6 CLASS Integration (Rescaled)
 * Maps Phi_Delta to Canonical Scalar Field phi
 * phi = sqrt(xi_delta) * Phi_Delta
 * V(phi) = lambda_eff * phi^4 where lambda_eff = kappa / xi_delta^2
 */

#include <math.h>

typedef struct {
    double lambda_eff; /* Effective quartic coupling */
    double phi_init;   /* Initial canonical field value */
} OmegaRescaledParams;

/**
 * Calculates energy density and pressure for rescaled canonical field.
 * rho = 0.5 * phidot^2 + lambda_eff * phi^4
 */
void calculate_omega_rescaled_density(double phi, double phidot, OmegaRescaledParams* params, double* rho, double* p) {
    double potential = params->lambda_eff * pow(phi, 4);
    double kinetic = 0.5 * phidot * phidot;
    
    *rho = kinetic + potential;
    *p = kinetic - potential;
}

/**
 * Canonical Evolution:
 * phiddot = -3 * H * phidot - 4 * lambda_eff * phi^3
 */
double calculate_omega_rescaled_phiddot(double phi, double phidot, double H, OmegaRescaledParams* params) {
    return -3.0 * H * phidot - 4.0 * params->lambda_eff * pow(phi, 3);
}

/**
 * Canonical Perturbation (Speed of sound c_s^2 = 1):
 * delta_phiddot = -3*H*delta_phidot - (k^2/a^2 + 12*lambda_eff*phi^2)*delta_phi
 */
double calculate_omega_rescaled_perturbation(double phi, double delta_phi, double delta_phidot, double H, double k_over_a, OmegaRescaledParams* params) {
    double v_pp = 12.0 * params->lambda_eff * phi * phi;
    return -3.0 * H * delta_phidot - (k_over_a * k_over_a + v_pp) * delta_phi;
}
