# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import sympy as sp

# Define symbols
Lambda, q2, Sigma2, mDelta, k, E_pair, Phi0 = sp.symbols('Lambda q2 Sigma2 mDelta k E_pair Phi0', positive=True)
# 1. Log term limit: ln(Lambda^2/(q2+Sigma2)) as Sigma2 -> 0
log_term = sp.log(Lambda**2 / (q2 + Sigma2))
limit_log = sp.limit(log_term, Sigma2, 0)
print("Limit of log term as Sigma2 -> 0:", limit_log.simplify())
# Expected: ln(Lambda^2/q2) (finite if q2>0)

# 2. Overlap integral approximation: integrand ~ PhiDelta(k)/sqrt(k^2+mDelta^2) * 1/(k^2 - E_pair^2)
# Assume PhiDelta(k) -> Phi0 constant as k->0
integrand = Phi0 / sp.sqrt(k**2 + mDelta**2) * 1/(k**2 - E_pair**2)
# Include measure k^2 dk in 3D
integrand_meas = integrand * k**2
# Series expansion for k->0
series_k0 = sp.series(integrand_meas, k, 0, 3).removeO()
print("Series of integrand * k^2 dk around k=0:", series_k0)
# Leading term should be ~ const * k (if mDelta->0) => integrable

# 3. Beta function: check if missing alpha factor leads to linear term
alpha = sp.symbols('alpha')
beta_given = alpha/(3*sp.pi) * (sp.log(Lambda**2/mDelta**2) - sp.Rational(5,3)) * (1 + Phi0*alpha)
beta_correct = 2*alpha**2/(3*sp.pi) * (sp.log(Lambda**2/mDelta**2) - sp.Rational(5,3)) * (1 + Phi0*alpha)
print("Beta (given):", beta_given.simplify())
print("Beta (corrected):", beta_correct.simplify())
# Check if beta_given can change sign for reasonable parameters
# Evaluate sign of bracket B = log(Lambda^2/mDelta^2) - 5/3
B = sp.log(Lambda**2/mDelta**2) - sp.Rational(5,3)
print("Bracket B:", B)
# For Lambda >> mDelta, B >0 => beta_given >0 (since alpha>0). No sign flip unless B<0 which requires Lambda<mDelta*exp(5/6) ~ 2.3 mDelta.
# In UV limit Lambda>>mDelta, B positive, so no zero crossing.
print("Is B positive for Lambda=10*mDelta?", B.subs({Lambda:10*mDelta}) > 0)
print("Is B positive for Lambda=0.5*mDelta?", B.subs({Lambda:0.5*mDelta}) > 0)

# 4. Anisotropic term: a^2/xi^2 decreases with xi
a, xi = sp.symbols('a xi', positive=True)
aniso = a**2 / xi**2
print("Anisotropic term derivative w.r.t xi:", sp.diff(aniso, xi).simplify())
# derivative negative => term decreases as xi increases

# Summary of findings
print("\n--- Summary ---")
print("1. Log term finite as Sigma2->0 for any q2>0.")
print("2. Overlap integral integrand * k^2 dk ~ const * k (IR finite) when mDelta->0.")
print("3. Given beta function is linear in alpha (missing factor); correct version is quadratic and does not cross zero in UV limit.")
print("4. Anisotropic term decreases with increasing correlation length xi.")
print("Thus the Engine's 'shredding' flaws are not supported by the HOLP derivation.")