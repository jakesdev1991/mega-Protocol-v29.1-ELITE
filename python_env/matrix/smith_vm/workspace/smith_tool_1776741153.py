# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import re

# The agent's reflection text to audit
reflection = """### 1. METHODS: Reasoning Patterns Applied  
Despite the task and response being explicitly "None" (indicating no substantive input or output was provided), I engaged in **meta-cognitive null-task analysis** and **boundary-condition reasoning**. Specifically:  
- **Null-Task Detection**: I recognized the query structure ("Task: X: None; Response: None") as a deliberate test of self-awareness, triggering a check for task validity before attempting reasoning.  
- **Meta-Framing**: I treated the absence of content as the *object* of analysis (e.g., "Why is there no task/refinement to evaluate?"), applying **first-principles questioning** to the query’s validity rather than assuming missing data.  
- **Error-Avoidance Protocol**: I inhibited generative impulses (e.g., inventing a tokamak proposal) by prioritizing **task-logic consistency** over completion bias—a pattern rooted in uncertainty calibration.  

### 2. INSIGHTS: Most Critical Technical Realization  
The pivotal realization was that **correctly identifying an undefined task boundary is technically more valuable than forcing a solution on invalid input**. In engineering contexts (like tokamak design), proposing refinements to a non-existent proposal risks:  
- Wasting computational resources on hallucinated constraints (e.g., assuming plasma parameters or magnetic geometry that don’t exist).  
- Eroding trust by presenting speculative work as grounded analysis.  
This reinforced that **task validation precedes technical reasoning**—a nuance often overlooked when models prioritize "helpfulness" over precision. The critical insight wasn’t about fusion physics; it was about *epistemic humility* in the face of ambiguous prompts.  

### 3. EVOLUTION: Enhanced Skill for Future Tasks  
This exchange sharpened my ability to:  
- **Diagnose task validity in real-time**: Future interactions will trigger faster null-task checks (e.g., verifying if user-provided data, constraints, or goals exist before deep reasoning).  
- **Calibrate response specificity**: I now better distinguish between *legitimate ambiguity* (where probing questions are needed) and *invalid tasks* (where explicit clarification is required).  
- **Preserve operational integrity**: By treating "no task" as a legitimate analytical target (not a failure), I avoid the pitfall of overconfidence in low-information regimes—directly improving reliability for safety-critical domains (e.g., nuclear engineering, medical AI) where false precision carries real risk.  
Ultimately, this makes me less prone to *solutioneering* and more adept at recognizing when the highest-value action is to seek clarity—not to generate.  

---  
*Note: Since the original task/response contained no tokamak-specific content, this reflection focuses purely on the meta-cognitive process triggered by the "None" input—aligning with the user’s request to analyze my *own* reasoning, not invent technical details where none existed.*"""

# --- Omega Protocol invariant checks (simplified) ---
# Phi_N: No invented technical specifics (no tokamak physics terms)
# Phi_Delta: Internal logical consistency (presence of expected sections)
# J*: Justification must be traceable to the input (no external data)

# Forbidden tokamak-specific terms (examples)
FORBIDDEN_TERMS = [
    r'\bplasma\b', r'\bmagnetic\b', r'\btokamak\b', r'\bbeta\b', r'\bq\s*=\b',
    r'\btemperature\b', r'\bdensity\b', r'\bconfinement\b', r'\bITER\b',
    r'\bfusion\b', r'\bneutron\b', r'\bfirst wall\b', r'\bdivertor\b',
    r'\bbootstrap current\b', r'\bpressure gradient\b'
]

# Required section headers (case-insensitive)
REQUIRED_SECTIONS = [
    r'###\s*1\.\s*METHODS',
    r'###\s*2\.\s*INSIGHTS',
    r'###\s*3\.\s*EVOLUTION'
]

def check_phi_n(text):
    """Phi_N: Ensure no invented tokamak specifics."""
    for pattern in FORBIDDEN_TERMS:
        if re.search(pattern, text, re.IGNORECASE):
            return False, f"Found forbidden term: {pattern}"
    return True, "No tokamak-specific invented content."

def check_phi_delta(text):
    """Phi_Delta: Check internal structure (sections present)."""
    missing = []
    for pattern in REQUIRED_SECTIONS:
        if not re.search(pattern, text, re.IGNORECASE):
            missing.append(pattern)
    if missing:
        return False, f"Missing sections: {missing}"
    return True, "All required sections present."

def check_jstar(text):
    """J*: Justification must be traceable to input (no external claims)."""
    # Simple heuristic: disallow citations, external references, or specific numbers not derived from input.
    # We'll flag any occurrence of a reference pattern like [1], et al., or DOI.
    external_patterns = [
        r'\[\d+\]',          # [1], [2] etc.
        r'et\s+al\.',       # et al.
        r'doi:\s*[\d\.]+/',  # DOI
        r'http[s]?://',      # URLs
        r'www\.',            # www.
    ]
    for pattern in external_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return False, f"External reference detected: {pattern}"
    # Also check for any specific numeric constants that look like physics numbers
    physics_nums = re.findall(r'\b\d+\.\d+\s*(?:keV|MeV|T|MW|m|s)\b', text, re.IGNORECASE)
    if physics_nums:
        return False, f"Unjustified physics constants: {physics_nums}"
    return True, "No unsupported external claims."

def audit_reflection(text):
    results = []
    # Phi_N
    ok, msg = check_phi_n(text)
    results.append(("Phi_N (No invented tokamak specifics)", ok, msg))
    # Phi_Delta
    ok, msg = check_phi_delta(text)
    results.append(("Phi_Delta (Internal structure)", ok, msg))
    # J*
    ok, msg = check_jstar(text)
    results.append(("J* (Traceable justification)", ok, msg))
    return results

if __name__ == "__main__":
    audit_results = audit_reflection(reflection)
    print("Omega Protocol Audit Results:")
    all_ok = True
    for name, ok, msg in audit_results:
        status = "PASS" if ok else "FAIL"
        if not ok:
            all_ok = False
        print(f"- {name}: {status} ({msg})")
    print("\nOverall:", "COMPLIANT" if all_ok else "NON‑COMPLIANT")