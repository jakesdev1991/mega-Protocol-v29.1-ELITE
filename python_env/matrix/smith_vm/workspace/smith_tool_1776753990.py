# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import re

def validate_analysis(analysis_text: str) -> None:
    """
    Validate the Omega Protocol compliance and mathematical soundness of the analysis.
    Raises AssertionError with details if any check fails.
    """
    # ------------------------------------------------------------------
    # 1. Structural purity: no boilerplate (headings, lists, explicit sectioning)
    # ------------------------------------------------------------------
    lines = analysis_text.splitlines()
    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        # Markdown headings
        if re.match(r'^#{1,6}\s+', stripped):
            raise AssertionError(f"Line {i}: Markdown heading detected: '{line}'")
        # Numbered list items (e.g., "1. ", "2) ")
        if re.match(r'^\d+[.)]\s+', stripped):
            raise AssertionError(f"Line {i}: Numbered list detected: '{line}'")
        # Bullet points
        if re.match(r'^[-*+]\s+', stripped):
            raise AssertionError(f"Line {i}: Bullet point detected: '{line}'")
        # Explicit section labels like "Step", "Phase", "Section"
        if re.search(r'\b(Step|Phase|Section|Part)\s+\d+', stripped, re.I):
            raise AssertionError(f"Line {i}: Explicit section label detected: '{line}'")

    # ------------------------------------------------------------------
    # 2. Presence of Omega Protocol invariants (Phi_N, Phi_Delta, J*)
    # ------------------------------------------------------------------
    required_patterns = [r'Φ_N', r'Φ_Δ', r'𝒥_I']  # using Unicode as in text
    for pat in required_patterns:
        if not re.search(pat, analysis_text):
            raise AssertionError(f"Missing invariant pattern: {pat}")

    # ------------------------------------------------------------------
    # 3. Numeric validation using supplied data
    # ------------------------------------------------------------------
    # Given normalized data
    phi_N = 0.78
    phi_Delta = 0.35
    phi_dot_N = 2.1e3          # s^-1
    phi_dot_Delta = 8.7e3      # s^-1
    xi_inv_sq = 4.2e6          # s^-2
    source_jerk = 1.5e12       # s^-3

    # Derived quantities
    xi = 1.0 / math.sqrt(xi_inv_sq)          # s
    psi = math.log(phi_N)                    # dimensionless
    psi_dot = phi_dot_N / phi_N              # s^-1

    # Approximate second derivatives using characteristic time xi (as in analysis)
    phi_ddot_N = phi_dot_N / xi              # s^-2
    phi_ddot_Delta = phi_dot_Delta / xi      # s^-2

    psi_ddot = phi_ddot_N / phi_N - psi_dot**2  # s^-2
    psi_dddot = psi_ddot / xi                  # s^-3

    # Delta side
    phi_ddot_Delta = phi_dot_Delta / xi
    phi_dddot_Delta = phi_ddot_Delta / xi      # s^-3

    # Entropy and its derivatives (numeric via finite difference for robustness)
    eps = 1e-8
    e_psi = math.exp(psi)
    def entropy(psi_val, phiD_val):
        e = math.exp(psi_val)
        pN = e / (e + phiD_val)
        pD = phiD_val / (e + phiD_val)
        # Avoid log(0)
        if pN <= 0 or pD <= 0:
            return 0.0
        return -(pN * math.log(pN) + pD * math.log(pD))

    S0 = entropy(psi, phi_Delta)
    dS_dpsi = (entropy(psi + eps, phi_Delta) - S0) / eps
    dS_dphiD = (entropy(psi, phi_Delta + eps) - S0) / eps
    d2S_dpsi2 = (entropy(psi + eps, phi_Delta) - 2*S0 + entropy(psi - eps, phi_Delta)) / (eps**2)
    d2S_dphiD2 = (entropy(psi, phi_Delta + eps) - 2*S0 + entropy(psi, phi_Delta - eps)) / (eps**2)
    # Third derivative approximated via central difference of second derivative
    d3S_dpsi3 = (d2S_dpsi2(psi + eps) - d2S_dpsi2(psi - eps)) / (2*eps) if False else 0.089  # fallback to given value
    # For simplicity, we keep the provided third‑derivative estimate.
    d3S_dpsi3 = 0.089
    d3S_dphiD3 = 0.0  # term omitted in original analysis

    # Helper to compute d2S_dpsi2 at perturbed psi (needed for third derivative)
    def d2S_dpsi2_at(psi_val):
        return (entropy(psi_val + eps, phi_Delta) - 2*entropy(psi_val, phi_Delta) + entropy(psi_val - eps, phi_Delta)) / (eps**2)

    d3S_dpsi3 = (d2S_dpsi2_at(psi + eps) - d2S_dpsi2_at(psi - eps)) / (2*eps)

    # Jerk components
    jerk_psi = (dS_dpsi * psi_dddot +
                3 * d2S_dpsi2 * psi_dot * psi_ddot +
                d3S_dpsi3 * psi_dot**3)

    jerk_Delta = (dS_dphiD * phi_dddot_Delta +
                  3 * d2S_dphiD2 * phi_dot_Delta * phi_ddot_Delta +
                  d3S_dphiD3 * phi_dot_Delta**3)

    total_jerk = jerk_psi + jerk_Delta + source_jerk

    # ------------------------------------------------------------------
    # 4. Compare with claimed values from the text (tolerance 5%)
    # ------------------------------------------------------------------
    claimed = {
        'psi': -0.248,
        'psi_dot': 2.69e3,
        'psi_ddot': -1.74e6,
        'psi_dddot': -3.55e9,
        'jerk_psi': 7.07e9,
        'jerk_Delta': -1.30e12,
        'total_jerk': 2.07e11,
    }
    computed = {
        'psi': psi,
        'psi_dot': psi_dot,
        'psi_ddot': psi_ddot,
        'psi_dddot': psi_dddot,
        'jerk_psi': jerk_psi,
        'jerk_Delta': jerk_Delta,
        'total_jerk': total_jerk,
    }
    for key in claimed:
        if not math.isclose(computed[key], claimed[key], rel_tol=0.05):
            raise AssertionError(
                f"Mismatch for {key}: computed {computed[key]:.6e}, claimed {claimed[key]:.6e}"
            )

    # ------------------------------------------------------------------
    # 5. Stability criterion checks
    # ------------------------------------------------------------------
    # Variance estimate from the analysis (take as given)
    sigma_jerk_sq = 1.71e21   # s^-6

    # Characteristic frequency
    omega = 1.0 / xi                     # s^-1
    omega_psi = omega * math.exp(-psi/2.0)   # s^-1
    natural_jerk_scale = omega_psi**3      # s^-3

    # Dimensionless variance
    var_dimless = sigma_jerk_sq / (omega_psi**6)
    if var_dimless <= 1.0:
        raise AssertionError(f"Dimensionless jerk variance {var_dimless:.3f} not > 1 (stable)")

    # Explicit threshold
    theta = (xi_inv_sq * math.exp(-psi))**3   # s^-6
    if sigma_jerk_sq <= theta:
        raise AssertionError(f"Sigma_jerk_sq {sigma_jerk_sq:.3e} not > threshold {theta:.3e}")

    # ------------------------------------------------------------------
    # 6. All checks passed
    # ------------------------------------------------------------------
    return True

# ----------------------------------------------------------------------
# Example usage (the analysis text would be supplied by the Engine)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Placeholder: replace with the actual analysis string from the Engine.
    analysis_text = """ PASTE THE FULL ANALYSIS TEXT HERE """
    try:
        validate_analysis(analysis_text)
        print("PASS")
    except AssertionError as e:
        print(f"FAIL: {e}")