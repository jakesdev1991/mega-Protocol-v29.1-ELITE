# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
self.phi_N = np.log2(max(self.cod, 0.39) + 1e-12)
  ```  
  This **forces** `phi_N` to be at least `log2(0.39)` even when `COD < 0.39`.  
  Consequently the invariant `phi_N >= log2(0.39)` is never *tested*; it is **bypassed by construction**.  
  In a strict Omega‑Protocol audit this constitutes a **logic flaw** – the invariant must be evaluated on the *actual* `COD`, not a clamped value.

All other mathematical derivations (COD formula, stiffness modulation, topological checks, Φ‑density accounting) are internally consistent **provided** the constants `Λ, κ, λ` are taken as the hard‑coded `0.5` used in the implementation. The Φ‑density ledger balances to the claimed net +1.00 Φ within reasonable rounding.

**Required Enforcement**

To bring the implementation into full compliance we must:

1. **Compute `phi_N` directly from `COD`** (`phi_N = log2(COD)`) and then **check** the invariant.
2. Keep the **hard floor** as a *separate* validation step (i.e., if `COD < 0.39` the invariant fails and the Silence Protocol must trigger).
3. Ensure that any “clamping” or “max” operations are **only used for numerical stability** *after* the invariant check, never to *manufacture* compliance.

Below is a **stand‑alone validation script** that:

- Re‑creates the core mathematics of the submission.
- Verifies the COD expression matches the implementation.
- Enforces each of the 9 Smith Invariants **exactly** as stated.
- Flags the Invariant 2 violation if the original clamping logic is used.
- Checks the Φ‑density ledger arithmetic.
- Demonstrates the correct behavior of the `apply()` method (message vs. silence).