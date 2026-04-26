#pragma once
#include <cstdint>

namespace omega::rcod {

// --- Shock / turbulence detection ---
constexpr float SHOCK_LIMIT        = 0.50f;   // tuned down from 0.70
constexpr float CAUTION_P95_ENTER  = 0.65f;
constexpr float SHOCK_P95_ENTER    = 0.75f;
constexpr float MAJOR_P95_ENTER    = 0.85f;
constexpr float CRITICAL_P95_ENTER = 0.95f;

constexpr float OUTLIER_MAX_ENTER  = 0.98f;   // max-only landmine guardrail

// --- Sensor slew guardrail (units depend on your normalization) ---
constexpr float SENSOR_SLEW_LIMIT  = 100.0f;  // observed ~96.6 and ~88.9

// --- Stability / flow gating ---
constexpr float FLOW_ENTER         = 0.10f;
constexpr float IP_STABILITY_LIMIT = 0.05f;

// --- Phi protection (avoid div-by-zero in K(phi)=1/phi^2) ---
constexpr float PHI_EPS = 1e-6f;

// --- Dynamic Scaling Helper (Planck-scale consistency) ---
inline float get_dynamic_phi_min(float kretschmann_K, float eta = 1.0f) {
    // Φ_min(K) = min(1.0, eta * l_P / L_K) where L_K = K^(-1/4)
    // Simplified for HLS: uses a rational power approximation or lookup
    if (kretschmann_K <= 0) return PHI_EPS;
    
    // Physical scale: l_P / L_K = l_P * K^(1/4)
    // We assume kretschmann_K is provided in units of [l_P^-4]
    // For FPGA-friendly 1/4 power, we use a simple nested sqrt
    float l_over_Lk = eta * std::sqrt(std::sqrt(kretschmann_K));
    
    return (l_over_Lk < PHI_EPS) ? PHI_EPS : ((l_over_Lk > 1.0f) ? 1.0f : l_over_Lk);
}

constexpr float clamp_phi(float phi) {
    return (phi < PHI_EPS) ? PHI_EPS : ((phi > 1.0f) ? 1.0f : phi);
}

constexpr float K_of_phi(float phi) {
    const float p = clamp_phi(phi);
    return 1.0f / (p * p);
}

} // namespace omega::rcod
