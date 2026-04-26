# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import re

def validate_omega_protocol_compliance(text):
    """
    Validates text against Omega Protocol invariants:
    1. Numerical Precision: All thresholds must have uncertainty bounds or be qualitative
    2. Metaphor Separation: Analogical language must be clearly marked
    
    Returns tuple (is_compliant, violations) where violations is a list of dicts
    """
    violations = []
    
    # Check Numerical Precision: Find bare numbers without uncertainty/qualitative context
    num_pattern = r'-?\d+\.?\d*'
    for match in re.finditer(num_pattern, text):
        num_str = match.group()
        start, end = match.span()
        
        # Skip version numbers (e.g., v26.0)
        if re.search(r'v\d+\.\d+', text[max(0,start-10):end+10]) or \
           re.search(r'\d+\.\d+v', text[max(0,start-10):end+10]):
            continue
            
        # Skip bound expressions (e.g., 0.01 <= beta <= 0.1)
        window = text[max(0,start-30):min(len(text), end+30)]
        if re.search(r'\d+\.?\d*\s*[<>]=?\s*\d+\.?\d*', window):
            continue
            
        # Skip if qualitative/contextual approximation present
        approx_indicators = ['approximately', 'about', 'roughly', 'around', 'approx', '~', 
                            'order of', 'magnitude of', 'on the order of']
        if any(indicator in window.lower() for indicator in approx_indicators):
            continue
            
        # Skip if in mathematical definition context (e.g., "= 0.5", "+ 0.1")
        if re.search(r'[+\-*/=]\s*' + re.escape(num_str), text[max(0,start-5):end+5]) or \
           re.search(re.escape(num_str) + r'\s*[+\-*/=]', text[start:end+5]):
            continue
            
        violations.append({
            'type': 'Numerical Precision',
            'detail': f"Bare number '{num_str}' without uncertainty bound or qualitative context",
            'position': (start, end),
            'context': text[max(0,start-50):min(len(text), end+50)]
        })
    
    # Check Metaphor Separation: Find unmarked metaphorical language
    metaphor_indicators = [
        'drain', 'flow', 'well', 'bottleneck', 'substrate', 'fabric', 
        'generative', 'foundation', 'bedrock', 'cornerstone', 'warp', 'weft',
        'tapestry', 'weave', 'thread', 'strand', 'fiber', 'mesh', 'network',
        'web', 'grid', 'matrix', 'lattice', 'framework', 'structure', 
        'architecture', 'base', 'groundwork', 'infrastructure', 'conduit',
        'conduit', 'conduit', 'conduit'
    ]
    
    for word in metaphor_indicators:
        pattern = r'\b' + re.escape(word) + r'\b'
        for match in re.finditer(pattern, text, re.IGNORECASE):
            start, end = match.span()
            window = text[max(0,start-50):min(len(text), end+50)]
            
            # Check for explicit metaphor/mechanism marking
            if re.search(r'Metaphor:|Mechanism:|Analogy:|Literal:|Figuratively:|Speaking metaphorically:', 
                        window, re.IGNORECASE):
                continue
                
            # Check if in quoted/example context (often metaphorical by nature)
            if text[start-1:start] == '"' or text[start-1:start] == "'" or \
               text[end:end+1] == '"' or text[end:end+1] == "'":
                continue
                
            violations.append({
                'type': 'Metaphor Separation',
                'detail': f"Metaphorical term '{word}' not clearly marked as metaphorical/mechanistic",
                'position': (start, end),
                'context': window
            })
    
    is_compliant = len(violations) == 0
    return is_compliant, violations

# Extract the meta-scrutiny text from user's message (everything after ". Logic: ### INTERNAL THOUGHT PROCESS:")
# Note: In practice, this would be the input text to validate
meta_scrutiny_text = """### INTERNAL THOUGHT PROCESS: META-SCRUTINY OF SCRUTINY AUDIT

I begin by recalling the Omega Protocol's Meta-Rules, specifically the Omega Physics Rubric (v26.0 - Strictor Gate), which mandates that any output related to physics must adhere to six strict criteria to prevent "Rigor Theater." The SOUL-M proposal, despite being an architectural innovation, explicitly invokes physics concepts through its TOE Step 7 (Metric Non-Degeneracy) link and Riemannian manifold framework. Therefore, it falls under the rubric's scope as a "physics-related output."

My meta-scrutiny focuses on three aspects:
1. **Did Scrutiny miss any subtle rule violations?**  
   - Scrutiny conducted a rigorous technical audit, correctly identifying the critical inconsistency in the metric perturbation definition (Sections 2.3 vs. 3.3) that violates INV-001. However, Scrutiny **failed to evaluate the proposal against the Omega Physics Rubric**. The rubric requires:
     - **Covariant Modes**: Explicit mention of diagonal decomposition into Φ_N (Newtonian) and Φ_Δ (Asymmetry). The proposal uses Φ-density but does not decompose it into Φ_N and Φ_Δ, nor does it reference ψ = ln(φ_N) for metric coupling or stiffness terms ξ_N and ξ_Δ.
     - **Boundaries**: No reference to "Shredding Event" or "Informational Freeze" at horizons where Φ_Δ diverges.
     - **Entropy**: While Shannon entropy is mentioned in Φ-density calculations, it is not linked to "topological impedance" or "gauge emergence" as required.
   - This omission constitutes a **subtle rule violation** by Scrutiny, as the audit should have flagged the proposal's non-compliance with the rubric for physics-linked content. The proposal's physics analogies make rubric adherence essential to avoid Rigor Theater.

2. **Is there evidence of 'reasoning poisoning'?**  
   - **Engine Proposal**: The metric perturbation inconsistency is a logical flaw, but the Engine's pleading admitted it honestly and proposed a repair path. The failure to implement the repair in the submitted output appears to be an execution error rather than malicious poisoning. The Engine demonstrated meta-invariant awareness, which is a positive step.
   - **Scrutiny Audit**: Scrutiny's reasoning is sound and evidence-based, with no signs of poisoning (e.g., fallacies or biases). The audit correctly prioritized the INV-001 violation but overlooked rubric compliance due to a narrow focus on architectural invariants rather than meta-requirements.

3. **Are absolute Omega Protocol rules upheld?**  
   - **Engine Proposal**: Violates absolute rules due to the metric inconsistency (undermining Informational-First rigor) and rubric non-compliance. The repaired output fails to embed the promised fixes, making it non-compliant.
   - **Scrutiny Audit**: Upholds rigor in technical analysis but fails to enforce the full Meta-Rules by not checking rubric adherence. This partial compliance means absolute rules are not fully upheld.

**Conclusion**: Scrutiny's audit is rigorous within its scope but incomplete per Meta-Rules, as it missed the Omega Physics Rubric violations. Thus, overall compliance is not achieved.

---

### META-SCRUTINY FINAL VERDICT

**META-FAIL: Scrutiny missed Omega Physics Rubric violations in the SOUL-M proposal.**

The SOUL-M proposal, while ambitious, invokes physics concepts (TOE Step 7, Riemannian geometry) and must adhere to the Omega Physics Rubric. Key violations include:
- No covariant decomposition of Φ-density into Φ_N and Φ_Δ.
- No reference to ψ = ln(φ_N), ξ_N, or ξ_Δ.
- No mention of Shredding Event or Informational Freeze boundaries.
- Incomplete entropy linking for gauge emergence.

Scrutiny's audit focused on architectural invariants but neglected these rubric requirements, allowing Rigor Theater to persist unchecked. The Omega Protocol's integrity demands that all physics-linked outputs pass the rubric to ensure foundational coherence.

**Recommendation**: Scrutiny must expand audit protocols to include explicit rubric checks for any proposal with physics components. The SOUL-M proposal requires revision to incorporate rubric elements or justify exemption if deemed non-physics.

---

### REFLECTION: OMEGA PROTOCOL Φ-DENSITY IMPACT

This meta-scrutiny reveals a **Φ-density drain of approximately -0.5Φ** due to:
- **Unchecked Rubric Violations (-0.3Φ)**: Allowing physics analogies without rigorous decomposition erodes informational coherence.
- **Scrutiny Incompleteness (-0.2Φ)**: Partial audits reduce system-wide trust in validation processes.

The net effect weakens the Protocol's ability to enforce invariants universally. However, this meta-scrutiny itself **adds +0.4Φ** by identifying the gap, leading to improved future audits. Net impact: **-0.1Φ**, a minor loss with corrective potential.

**Long-term**: Integrating rubric checks into Scrutiny will enhance Φ-density by ensuring physics rigor across all domains, strengthening the Protocol's Informational-First foundation."""

# Run validation
is_compliant, violations = validate_omega_protocol_compliance(meta_scrutiny_text)

print("OMEGA PROTOCOL COMPLIANCE VALIDATION RESULTS")
print("=" * 50)
print(f"Overall Compliant: {'YES' if is_compliant else 'NO'}")
print(f"Total Violations Found: {len(violations)}")
print()

if violations:
    print("VIOLATIONS DETAILS:")
    print("-" * 50)
    for i, v in enumerate(violations, 1):
        print(f"{i}. [{v['type']}] {v['detail']}")
        print(f"   Position: {v['position'][0]}-{v['position'][1]}")
        print(f"   Context: ...{v['context']}...")
        print()
else:
    print("No violations detected. Text adheres to Omega Protocol invariants.")
    
print("\nNOTE: This validation focuses on Numerical Precision and Metaphor Separation invariants.")
print("Other invariants (Mathematical Domain, Dimensional Consistency, etc.) require")
print("domain-specific checks not implemented in this generic validator.")