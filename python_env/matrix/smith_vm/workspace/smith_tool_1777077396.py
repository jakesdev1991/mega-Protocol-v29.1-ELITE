# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import re
from typing import Tuple, List, Dict, Optional

class OmegaImpactValidator:
    """Validates Φ impact claims against Omega Protocol invariants."""
    
    # Protocol-defined requirements for quantitative Φ claims
    QUANTITATIVE_REQUIREMENTS = {
        "phi_definition": "Must define Φ operationally (e.g., 'Φ = log(trust_metric / baseline)')",
        "measurement_protocol": "Must specify how Φ is measured (tools, frequency, sample size)",
        "uncertainty_bounds": "Must provide confidence interval or error margin (e.g., '+0.3Φ ± 0.1')",
        "baseline_data": "Must reference pre-intervention Φ measurement",
        "causal_isolation": "Must demonstrate variable isolation (e.g., A/B test, controlled experiment)"
    }
    
    # Patterns indicating unsound quantitative claims
    UNSOUND_PATTERNS = [
        r"[+-]?\d+\.?\d*\s*Φ",  # Bare Φ estimates (e.g., "+0.3Φ")
        r"avoided\s+drain",     # Unmeasurable counterfactuals
        r"compounding.*trust",  # Vague mechanistic claims
        r"%.*Φ"                 # Ambiguous percentage-Φ mixes
    ]
    
    def __init__(self):
        self.violations: List[str] = []
        self.suggestions: List[str] = []
    
    def validate_impact_claim(self, text: str) -> Tuple[bool, List[str], List[str]]:
        """
        Validates a text block for Φ impact claims.
        Returns: (is_compliant, violations, suggestions)
        """
        self.violations = []
        self.suggestions = []
        
        # Check for quantitative Φ patterns
        phi_matches = re.findall(r"[+-]?\d+\.?\d*\s*Φ", text)
        if phi_matches:
            self._check_quantitative_claim(text, phi_matches)
        
        # Check for unsound qualitative patterns
        for pattern in self.UNSOUND_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                self.violations.append(
                    f"Unsound pattern detected: '{pattern}' (e.g., avoids measurable basis)"
                )
        
        # Generate compliant alternatives if violations exist
        if self.violations:
            self._generate_suggestions(text)
        
        is_compliant = len(self.violations) == 0
        return is_compliant, self.violations, self.suggestions
    
    def _check_quantitative_claim(self, text: str, matches: List[str]) -> None:
        """Validates if a quantitative Φ claim meets protocol requirements."""
        for match in matches:
            # Extract context around the claim
            context = self._extract_context(text, match, window=150)
            
            # Check for required elements
            missing = []
            for req, desc in self.QUANTITATIVE_REQUIREMENTS.items():
                if not self._has_requirement(context, req):
                    missing.append(f"- {req}: {desc}")
            
            if missing:
                self.violations.append(
                    f"Quantitative Φ claim '{match}' missing required elements:\n"
                    + "\n".join(missing)
                )
    
    def _extract_context(self, text: str, target: str, window: int = 100) -> str:
        """Extracts text window around target for requirement checking."""
        idx = text.find(target)
        start = max(0, idx - window)
        end = min(len(text), idx + len(target) + window)
        return text[start:end].lower()
    
    def _has_requirement(self, context: str, req: str) -> bool:
        """Checks if context implies fulfillment of a requirement (simplified heuristic)."""
        # In practice, this would link to evidence logs; here we use keyword proxies
        req_keywords = {
            "phi_definition": ["define", "equation", "formula", "phi ="],
            "measurement_protocol": ["measured", "tracked", "logged", "sensor"],
            "uncertainty_bounds": ["±", "error", "confidence", "std", "margin"],
            "baseline_data": ["baseline", "pre-intervention", "before", "control"],
            "causal_isolation": ["isolated", "variable", "a/b", "experiment", "controlled"]
        }
        return any(kw in context for kw in req_keywords.get(req, []))
    
    def _generate_suggestions(self, text: str) -> None:
        """Provides Ω-compliant alternatives for unsound claims."""
        self.suggestions = [
            "Replace quantitative Φ claims with qualitative assessments:",
            "  - Instead of: '+0.3Φ estimated' → Try: 'Likely preserves protocol integrity by preventing unsafe dorking'",
            "  - Instead of: '+0.2Φ avoided drain' → Try: 'Reduces risk of epistemic erosion via rigorous audit'",
            "",
            "For quantitative claims, include:",
            "  - Operational Φ definition (e.g., 'Φ = audit_pass_rate × safety_score')",
            "  - Measurement method (e.g., 'Φ measured via weekly protocol compliance scans')",
            "  - Uncertainty bounds (e.g., 'Φ increased by 0.25 ± 0.05 based on 30-day trial')",
            "  - Baseline and isolation proof (e.g., 'Baseline Φ=0.7; intervention group Φ=0.95 vs control Φ=0.72, p<0.01')"
        ]

# Example usage with meta-scrutiny output
if __name__ == "__main__":
    meta_scrutiny_text = """
    This Meta-Scrutiny action has a positive Φ-density impact (+0.3Φ estimated).  
    Short-term: Scrutiny's correction of the Makefile errors prevents Φ drain (–0.2Φ avoided)...  
    Long-term: Upholding audit rigor sets a precedent... compounding trust in the protocol (+0.5Φ).  
    Net Φ Trajectory: +0.3Φ (conservative estimate)...
    """
    
    validator = OmegaImpactValidator()
    is_compliant, violations, suggestions = validator.validate_impact_claim(meta_scrutiny_text)
    
    print("=== Ω IMPACT CLAIM VALIDATION ===")
    print(f"Compliant: {is_compliant}\n")
    
    if violations:
        print("VIOLATIONS DETECTED:")
        for v in violations:
            print(f"  - {v}")
        print()
    
    if suggestions:
        print("Ω-COMPLIANT ALTERNATIVES:")
        for s in suggestions:
            print(s)