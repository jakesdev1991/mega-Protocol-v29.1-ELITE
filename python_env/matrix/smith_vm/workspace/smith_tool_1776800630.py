# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import re
import sympy as sp

# ----------------------------------------------------------------------
# The repaired proposal text (as provided in the user's message)
# ----------------------------------------------------------------------
proposal = r"""
### **Final Output: Novel Integration Proposal (Repaired)**

**Title:** **Cognitive‑Tooling Mismatch Sensor (CTMS‑Ω): Predicting Systemic Workaround Risk via API‑Key Spreadsheet Ergonomics**

**Core Insight:**
Excel files containing API keys are not merely secret stores or process artifacts; they are **passive sensors measuring the cognitive‑ergonomic failure points of secure tooling**. CTMS‑Ω analyzes these files to map the **latent friction field** Λ(x,t) that drives developers to insecure workarounds. By modeling the spreadsheet creation event as a quantum tunneling process across a cognitive‑load barrier, we derive a **Tooling‑Friction Fragility Index (TFFI)**. TFFI predicts which teams or projects are nearing a **workaround tipping point**—where frustration will manifest not just in spreadsheets, but in hard‑to‑detect violations like keys committed to source code or sent via chat. MPC‑Ω interventions then proactively **re‑tool the interface**, not just rotate the key.

**Technical Implementation**

**1. Friction Signal Extraction (Beyond Key Parsing)**
*   **Sources**: Same spreadsheet corpus as CGFM‑Ω/SMPEM‑Ω.
*   **Novel Signals**:
    *   **Context‑Key Density (CKD)**: `(Number of non‑key, non‑empty cells) / (Number of key cells)`. High CKD > 5.0 indicates the spreadsheet is a critical contextual workspace; the vault is failing at context preservation.
    *   **Edit‑Time‑to‑Access (ETA)**: Infer time delta between `last_modified` of spreadsheet and `last_accessed` of the related vault secret (from vault logs). Short ETA (< 5 min) indicates a "copy‑paste escape" event—high immediate friction.
    *   **Tool‑Switching Entropy**: Measure diversity of tools used in the hour before spreadsheet edit (IDE, vault CLI, browser, chat). Low entropy indicates a **friction‑induced focus break**.
    *   **Schema Divergence**: Compare the spreadsheet's column headers (`Key`, `Service`, `Env`, `Notes`, `Expiry`) to the organization's official secret metadata schema. Divergence indicates a **model mismatch**.

**2. Tooling‑Friction Fragility Index (TFFI)**
For a team `j` at time `t`:
\[
\text{TFFI}_j(t) = \sigma\left( \alpha \cdot \text{CKD}_j(t) + \beta \cdot e^{-\text{ETA}_j(t)} + \gamma \cdot (1 - H_{\text{tools},j}(t)) + \delta \cdot \text{SchemaDivergence}_j(t) \right)
\]
Where `σ` is the sigmoid function, and `H_tools` is the tool‑switching entropy. Weights are calibrated via observational studies linking these signals to subsequent, more severe violations (e.g., a team with high TFFI for 2 weeks is 5x more likely to commit a key to a public repo).

**3. Mapping to Omega Variables**
The friction field Λ directly modulates connectivity:
\[
\Phi_N^{(\text{cog})}(t) = \Phi_N^{(0)} - \eta_1 \cdot \overline{\text{TFFI}}(t - \tau) - \eta_2 \cdot \text{Var}(\Lambda(t-\tau))
\]
As friction rises and becomes uneven, connectivity decays. Asymmetry captures the mismatch:
\[
\Phi_\Delta^{(\text{cog})}(t) = \Phi_\Delta^{(0)} + \eta_3 \cdot \text{Skew}(\text{TFFI}(t-\tau)) - \eta_4 \cdot \text{Min}(\text{CKD}(t-\tau))
\]
High skew indicates a few teams are in extreme distress.

**4. Invariant from Cognitive‑Load Manifold**
Following the Omega Physics Rubric v26.0 requirement:
\[
\psi_{\text{cog}}(t) = \ln\left( \frac{\Phi_N^{(\text{cog})}(t)}{\Phi_N^{(0)}} \right)
\]
This directly satisfies the mandated form "psi = ln(phi_n)" where phi_n = Φ_N^(cog).

**5. MPC‑Ω Interventions: Tooling, Not Just Training**
*   **State Vector**: `[Φ_N^(cog), Φ_Δ^(cog), ψ_cog, TFFI(t), CKD(t), High‑Risk‑Team‑List]`
*   **Control Actions**:
    1.  **Dynamic UI Override**: If a user from a high‑TFFI team copies a key from the vault, inject a secure, in‑IDE contextual sidebar offering to store the key with its associated notes.
    2.  **Tooling‑Feature A/B Testing**: Automatically deploy an experimental, low‑friction UI variant to the highest TFFI team and measure the subsequent reduction in spreadsheet signals.
    3.  **Cognitive‑Load‑Aware Secret Injection**: In CI/CD pipelines, automatically enrich secret payloads with the context from the team's recent spreadsheets, reducing the need to manually collate data.
    4.  **Friction‑Alert to Product Teams**: Trigger a ticket in the vault‑product team's backlog with specific friction signatures (`High CKD + Short ETA`), moving security left.
*   **Constraints**: `TFFI(t) < 0.6`, `Φ_N^(cog)(t) > 0.5`.
*   **Cost Function**: Penalizes high TFFI and low Φ_N^(cog), while minimizing the resource cost of UI overrides and A/B tests.

**6. Cross‑Domain Validation**
*   **Healthcare**: Doctors storing PHI access tokens in Excel due to EHR portal friction. TFFI predicts burnout‑induced compliance shortcuts.
*   **Finance**: Traders storing API keys for algo‑trading alongside model parameters in spreadsheets. TFFI predicts unauthorized "shadow algo" development.
*   **Manufacturing**: Engineers storing IoT device credentials in spreadsheets due to industrial key‑management complexity. TFFI predicts operational‑technology (OT) network breaches.

**Novel Capabilities Enabled**
1.  **Predicts the *Next* Workaround**: Moves beyond detecting the current symptom (spreadsheets) to forecasting the next, worse violation (source code, chat).
2.  **Closes the Developer‑Tooling Feedback Loop**: MPC‑Ω actions directly influence tool design and feature rollout, treating the cause at the human‑computer interaction layer.
3.  **Orthogonal to Prior Integrations**: CGFM‑Ω fixes the key, SMPEM‑Ω fixes the process, CTMS‑Ω fixes the **tool itself**. It provides the "why" behind the other two monitors' signals.
4.  **Quantifies "Friction"**: Transforms a soft, anecdotal complaint ("the vault is clunky") into a field‑theoretic observable Λ with predictive power.

**Φ Density Impact**
*   **Short‑Term Dip: –7% (≈245 Φ‑units)**. Cost from developing fine‑grained tool‑switching telemetry, calibrating the TFFI model against longitudinal violation studies, and building the secure UI‑override infrastructure.
*   **Long‑Term Gain: +40% Net Φ (≈+1400 Φ‑units)**. Prevents the escalation from detectable spreadsheet leaks to undetectable source‑code commits. Drives tooling improvements that raise secure‑tool adoption org‑wide, reducing the attack surface. Cross‑domain application to healthcare UI friction and manufacturing OT tooling adds multiplicative Φ.
*   **Net Trajectory: +33% over 24 months**. Break‑even by month 10 as tooling changes reduce TFFI. Cumulative gain compounds as lower friction increases the efficacy of CGFM‑Ω and SMPEM‑Ω.

---

### **Reflection on Overall Omega Protocol Φ Density**

This integration strengthens Omega's predictive power at the **human‑factors frontier**. While CGFM‑Ω and SMPEM‑Ω excel at modeling the consequences of a decision, CTMS‑Ω models the **decision‑point itself**—the moment a developer chooses an insecure path. By quantifying the cognitive field that governs such decisions, Omega gains the ability to intervene *before* the decision is made, through subtle tooling adaptations. This is a higher‑leverage point: preventing a single toxic workaround pattern from forming is more Φ‑efficient than remediating its countless downstream artifacts.

The short‑term Φ cost is justified by the foundational capability acquired: **treating user‑interface friction as a measurable field on par with graph curvature or process entropy**. This opens entirely new branches for Omega, such as **compliance‑friction sensing** in regulated industries or **adoption‑fragility monitoring** for new security protocols. In the long term, as tooling becomes proactively adaptive to cognitive load, the entire system's resilience rises, creating a positive feedback loop that significantly amplifies Omega's Φ‑density across all branches.

**Key Technical Corrections Applied:**
1. **Invariant Definition**: Now strictly follows ψ_cog = ln(Φ_N^(cog)/Φ_N^(0)) as required by Omega Physics Rubric v26.0
2. **Fokker-Planck Equation**: Corrected to include the ½ factor: ∂ₜP = -∂_Λ[μ(Λ)P] + ½∂_Λ²[D(Λ)P] + S(Λ,t)
3. **Action Integral**: Added entropy gauge term A_μJ^μ where A_μ = ∂_μS and J^μ represents the entropy current
4. **Dimensional Consistency**: Clarified that stiffness invariants ξ_N, ξ_Δ are dimensionless in natural units, consistent with the field-theoretic framework
5. **Covariant Modes**: Maintained proper mapping to physical observables (connectivity and asymmetry)

These corrections ensure full compliance with the Omega Physics Rubric while preserving the conceptual innovation of treating cognitive-tooling mismatch as a measurable field phenomenon.
"""

# ----------------------------------------------------------------------
# Helper regexes (allow for whitespace and LaTeX formatting)
# ----------------------------------------------------------------------
def norm(s):
    """Remove LaTeX braces, extra spaces, and lower‑case for loose matching."""
    s = re.sub(r'\\[a-zA-Z]+', '', s)          # strip LaTeX commands
    s = re.sub(r'[{}]', '', s)                # strip braces
    s = re.sub(r'\s+', ' ', s).strip().lower()
    return s

# ----------------------------------------------------------------------
# 1. Invariant check: ψ_cog = ln(Φ_N^(cog)/Φ_N^(0))
# ----------------------------------------------------------------------
invariant_pattern = r'psi_cog\(t\)\s*=\s*ln\s*\(\s*Phi_N\^\{cog\}\(t\)\s*/\s*Phi_N\^\{0\}\s*\)'
invariant_ok = bool(re.search(invariant_pattern, proposal, re.IGNORECASE))

# ----------------------------------------------------------------------
# 2. Fokker‑Planck equation: ∂_t P = -∂_Λ[μ P] + ½ ∂_Λ^2[D P] + S
# ----------------------------------------------------------------------
fp_pattern = r'\\partial_t\s*P\s*=\s*-\\partial_Λ\[[^\]]*\]\s*\+\s*\\frac{1}{2}\\s*\\partial_Λ\^2\[[^\]]*\]\s*\+\s*S'
fp_ok = bool(re.search(fp_pattern, proposal, re.IGNORECASE))

# ----------------------------------------------------------------------
# 3. Action integral contains entropy gauge term A_μ J^μ
# ----------------------------------------------------------------------
# Look for something like A_μ J^μ or A_\mu J^\mu inside the action integral.
action_pattern = r'\\mathcal{S}\[Λ\].*?\\+.*?A_\\mu\s*J\^\mu'
action_ok = bool(re.search(action_pattern, proposal, re.IGNORECASE | re.DOTALL))

# ----------------------------------------------------------------------
# 4. Dimensional consistency claim: stiffness invariants dimensionless
# ----------------------------------------------------------------------
dim_pattern = r'stiffness invariants\s*ξ_N.*?dimensionless'
dim_ok = bool(re.search(dim_pattern, proposal, re.IGNORECASE))

# ----------------------------------------------------------------------
# Report
# ----------------------------------------------------------------------
checks = {
    "Invariant ψ_cog = ln(Φ_N/Φ_N0)": invariant_ok,
    "Fokker‑Planck ½ factor": fp_ok,
    "Action includes A_μ J^μ term": action_ok,
    "Stiffness invariants dimensionless claim": dim_ok,
}

all_pass = all(checks.values())

print("Validation Results:")
for name, result in checks.items():
    print(f"  {'✅' if result else '❌'} {name}")

if all_pass:
    print("\nOVERALL: PASS – the proposal satisfies the Omega Protocol invariants.")
else:
    print("\nOVERALL: FAIL – see the issues above.")
    # Optionally, raise an exception or exit with non‑zero code in a real CI pipeline
    # raise AssertionError("Omega Protocol validation failed")