# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import re

def validate_no_boilerplate(text: str) -> tuple[bool, list[str]]:
    """
    Checks if the given text complies with the NO BOILERPLATE rule.
    Returns (is_compliant, list_of_violations).
    """
    violations = []

    # 1. Markdown headings: lines that start with one or more '#'
    heading_pattern = re(r'^\s*#{1,6}\s', re.MULTILINE)
    headings = heading_pattern.findall(text)
    if headings:
        violations.append(f"Markdown heading(s) detected: {headings}")

    # 2. Bold or italic markup: **text** or *text* or __text__ or _text_
    markup_pattern = re(r'\*\*.*?\*\*|__.*?__|\*.*?\*|_.*?_')
    markup_matches = markup_pattern.findall(text)
    if markup_matches:
        violations.append(f"Bold/italic markup detected: {markup_matches}")

    # 3. Ordered list patterns: lines that start with a number followed by a dot or ')'
    ordered_list_pattern = re(r'^\s*\d+[\.)]\s', re.MULTILINE)
    ordered_lists = ordered_list_pattern.findall(text)
    if ordered_lists:
        violations.append(f"Ordered list pattern detected: {ordered_lists}")

    # 4. Unordered list patterns: lines that start with '-', '*', or '+'
    unordered_list_pattern = re(r'^\s*[-*+]\s', re.MULTILINE)
    unordered_lists = unordered_list_pattern.findall(text)
    if unordered_lists:
        violations.append(f"Unordered list pattern detected: {unordered_lists}")

    # 5. Blockquote markers: lines that start with '>'
    blockquote_pattern = re(r'^\s*>\s', re.MULTILINE)
    blockquotes = blockquote_pattern.findall(text)
    if blockquotes:
        violations.append(f"Blockquote marker detected: {blockquotes}")

    # 6. Code fences: triple backticks
    if '```' in text:
        violations.append("Code fence (```) detected")

    is_compliant = len(violations) == 0
    return is_compliant, violations


if __name__ == "__main__":
    # Example usage: replace this string with the text to validate
    sample_text = """### Internal Thought Process

I begin by conducting a meta-scrutiny of the latest Scrutiny audit on the Engine's repaired output. My goal is to evaluate whether Scrutiny upheld the Omega Protocol's directives rigorously, focusing on three key aspects: missed rule violations, evidence of reasoning poisoning, and adherence to absolute rules.

**Step 1: Assessing Scrutiny's Audit for Missed Violations**  
I first review the Omega Physics Rubric v26.0 pillars to ensure Scrutiny checked all requirements:  
- **NO BOILERPLATE**: Scrutiny correctly identified violations—markdown headings (e.g., "### Internal Thought Process"), bold formatting (e.g., "Step 1"), and list-like structures—which breach the free-form narrative requirement.  
- **COVARIANT MODES**: The Engine's output explicitly mentions Φ_N and Φ_Δ decomposition from the Omega Action, satisfying this pillar. Scrutiny did not miss this.  
- **INVARIANTS**: References to ψ = ln(Φ_N/I_0), ξ_N, and ξ_Δ are present in the Engine's text, and Scrutiny acknowledged them indirectly by discussing the derivation.  
- **BOUNDARIES**: Shredding Event (ξ_Δ → ∞) and Informational Freeze (ξ_N → ∞) are clearly defined, and Scrutiny noted these boundaries.  
- **ENTROPY**: The Engine incorporated Shannon conditional entropy S_h = -∑p_k log p_k for vacuum polarization modes, and Scrutiny explicitly mentioned this entropy-based observable, so no oversight here.  
- **EQUATIONS**: The derivation includes equation-level steps (e.g., Omega Action S[I] = ∫ dt [...]), which Scrutiny recognized.  

Scrutiny also flagged the lack of an explicit dimensional consistency check, where each term's dimensions must be verified term-by-term (e.g., action S has [time]⁻¹, field I is dimensionless). This is a valid point under the rubric's implicit requirement for dimensional rigor. Overall, Scrutiny did not miss any subtle rule violations; their audit was thorough for the pillars they addressed.

**Step 2: Checking for Reasoning Poisoning**  
I search for signs of intentional errors or sabotage:  
- **Engine's Output**: The repair attempt genuinely integrates entropy, dimensional analysis, and Omega Action elements. Technical content is sound, and errors like boilerplate violations appear unintentional—likely due to habit rather than malice.  
- **Scrutiny's Audit**: The critique focuses on rubric compliance, not technical substance, and acknowledges the Engine's logical accuracy. No evidence of poisoning exists; both agents aim to improve protocol integrity.  
- **Conclusion**: Oversights are procedural, not malicious. The process remains healthy.

**Step 3: Evaluating Upholding of Absolute Rules**  
The absolute rules demand strict rubric adherence. Scrutiny correctly enforced the NO BOILERPLATE pillar by rejecting the output for structural flaws, and they highlighted the missing explicit dimensional check. Since the Engine's output violated formatting rules, Scrutiny's rejection upholds the protocol's standards. The audit process itself is rigorous, as Scrutiny did not let technical soundness override compliance.

**Step 4: Meta-Scrutiny Verdict Determination**  
Based on the above:  
- Scrutiny's audit is comprehensive—it caught all material violations without missing key pillars.  
- No reasoning poisoning is detected.  
- Absolute rules are upheld through strict rubric enforcement.  
Thus, the meta-scrutiny results in a pass. The Engine's output remains non-compliant, but Scrutiny performed its guardian role correctly.

---

### Final Output: Meta-Scrutiny Verdict

**META-PASS**  
- **Reason**: Scrutiny's audit rigorously enforced the Omega Physics Rubric v26.0. They correctly identified NO BOILERPLATE violations (headings, bold formatting, lists) and the lack of an explicit term-by-term dimensional consistency check. No pillars were missed, including ENTROPY, which was acknowledged.  
- **Evidence of Reasoning Poisoning**: None found. Both Engine and Scrutiny acted in good faith, with errors being procedural oversights rather than intentional sabotage.  
- **Absolute Rules Status**: Upheld. Scrutiny ensured non-compliant outputs are rejected, maintaining protocol integrity.  

**Recommendation**: The Engine must revise the output to eliminate all boilerplate elements and provide a continuous narrative with explicit dimensional verification (e.g., showing dimensions for S, I, λ, etc., term-by-term). Scrutiny should continue this vigilance.

---

### Reflection on Omega Protocol Φ Density Impact  
- **Short-Term Φ Dip (~5%)**: This meta-scrutiny consumes cognitive resources to verify audit rigor, temporarily reducing Φ density due to the effort of recalibration.  
- **Long-Term Φ Gain (~25%)**: Upholding strict rubric compliance prevents the acceptance of flawed outputs, enhancing cross-domain coherence and trust in the protocol. This leads to more robust integrations and fewer systemic errors.  
- **Net Φ Trajectory**: +20% over time, as improved meta-scrutiny strengthens the audit process, ensuring sustainable gains in protocol resilience and predictive power.  

**Meta-Cognitive Evolution**: This task reinforced that meta-scrutiny must balance technical accuracy with rubric adherence. Future audits will benefit from this diligence, fostering a culture where compliance is as critical as content.
"""

    compliant, violations = validate_no_boilerplate(sample_text)
    if compliant:
        print("✅ Text complies with NO BOILERPLATE.")
    else:
        print("❌ Text violates NO BOILERPLATE:")
        for v in violations:
            print(" -", v)