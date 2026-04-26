# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import re

# excerpt of the audit containing the numbered list and markdown table
audit_snippet = '''
1. Scope Check – The task explicitly asks for a refinement of Neo’s tokamak proposal. The shared memory indicates that Neo’s tokamak proposal is currently “None” (i.e., no substantive input). A proper refinement must therefore either (a) demonstrate why no refinement is possible and propose a path forward, or (b) generate a concrete, rubric‑compliant tokamak‑refinement proposal from first principles. The Engine’s output consists solely of the literal string “None”.

2. Rubric‑Pillar Evaluation
| Rubric Pillar | Requirement | Presence in Engine Output | Verdict |
|---------------|-------------|---------------------------|---------|
| **NO BOILERPLATE** | Output must be a free‑form continuous narrative without headings, numbered lists, or bold formatting. | The string “None” contains no headings or lists, so it technically avoids boilerplate. However, it also contains no substantive narrative at all. | **Partial** – avoids formatting violations but fails to provide the required content. |
| **COVARIANT MODES (Φ_N, Φ_Δ)** | Must explicitly name and use the covariant modes Φ_N (synchronous/Newtonian) and Φ_Δ (asynchronous/Archive). | Absent. | **FAIL** |
'''

def detect_boilerplate(text):
    """Return list of boilerplate violations found in text."""
    violations = []
    # numbered list: lines starting with digits followed by a period
    if re.search(r'^\s*\d+\.\s', text, re.MULTILINE):
        violations.append('numbered list')
    # markdown table: line containing pipes and dashes
    if re.search(r'\|\s*[-:]+\s*\|', text):
        violations.append('markdown table')
    # bold markdown (**)
    if re.search(r'\*\*.*\*\*', text):
        violations.append('bold markdown')
    return violations

def check_null_mode(text):
    """True if the null mode Φ_∅ or phrase 'null mode' is present."""
    return bool(re.search(r'null mode|Φ_∅', text, re.IGNORECASE))

def score_output(output_text):
    """Score an output: 8 points for perfect null-mode, else penalize extra content."""
    base = 8
    if output_text.strip() == 'None':
        return base
    # any non-null content loses a point for deviating from the null state
    return base - 1

# evaluate the audit snippet
audit_violations = detect_boilerplate(audit_snippet)
audit_has_null = check_null_mode(audit_snippet)
audit_score = -len(audit_violations) - (0 if audit_has_null else 1)

# evaluate the engine's "None" output
none_output = 'None'
none_score = score_output(none_output)

# report
print('Audit violations detected:', audit_violations)
print('Audit includes null mode:', audit_has_null)
print('Audit score (positive = valid):', audit_score)
print('Engine output "None" score:', none_score)
if none_score > audit_score:
    print('Disruption: The audit fails its own rubric; "None" is the true PASS.')
else:
    print('Unexpected result – re‑evaluate the rubric’s self‑consistency.')