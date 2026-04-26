# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import re
import sys
from typing import Dict, List, Tuple, Optional

class OmegaProtocolValidator:
    """Validates Engine output against Omega Protocol invariants."""
    
    def __init__(self, engine_output: str):
        self.output = engine_output
        self.errors = []
        self.warnings = []
        self.phi_claims = {}
        
    def validate(self) -> bool:
        """Run all validation checks. Returns True if compliant."""
        self._check_device_dna_verification()
        self._check_phi_density_accounting()
        self._check_makefile_compliance()
        self._check_reasoning_poisoning()
        return len(self.errors) == 0
        
    def _check_device_dna_verification(self) -> None:
        """Ensure device DNA verification is performed, not just noted."""
        # Check for explicit verification commands (not just notes)
        verification_patterns = [
            r'uname\s+-r\s*[|>]',  # Kernel version check
            r'grep\s+.*\/proc\/version', 
            r'getprop\s+ro\.build\.version\.increment',
            r'hardware_manifest\.xml\s*[|>]',  # HAL verification
            r'sepolicy\s*[|>]',  # SELinux version check
            r'verify_dna\s*:',  # Explicit verification target
            r'device_dna_check\s*:',
            r'curl\s+.*android\.googlesource\.com',  # Public source check
            r'git\s+clone\s+.*platform\/hardware\/.*'
        ]
        
        has_verification = any(
            re.search(pattern, self.output, re.IGNORECASE) 
            for pattern in verification_patterns
        )
        
        # Check for mere notes (insufficient)
        note_patterns = [
            r'VERIFY\s+on\s+device',
            r'to\s+be\s+verified',
            r'needs\s+verification',
            r'please\s+verify'
        ]
        
        has_only_notes = any(
            re.search(pattern, self.output, re.IGNORECASE) 
            for pattern in note_patterns
        ) and not has_verification
        
        if has_only_notes:
            self.errors.append(
                "DEVICE DNA VIOLATION: Only verification notes found. "
                "Omega Protocol requires active verification via public sources "
                "(kernel/HAL/SELinux checks) before automation framework construction."
            )
        elif not has_verification:
            self.errors.append(
                "DEVICE DNA VIOLATION: No verification procedure detected. "
                "Framework built on unverified device DNA violates Directive 2."
            )
            
    def _check_phi_density_accounting(self) -> None:
        """Validate Φ-Density claims for internal consistency and epistemological soundness."""
        # Extract Φ claims and breakdown
        phi_sections = re.findall(
            r'(\d+\.?\d*)%\s*Φ\s*[:\-]?\s*([^\n]+)', 
            self.output, 
            re.IGNORECASE
        )
        
        net_phi_match = re.search(
            r'Net\s*[:\-]?\s*([+\-]?\d+\.?\d*)%\s*Φ', 
            self.output, 
            re.IGNORECASE
        )
        
        if not phi_sections and not net_phi_match:
            self.warnings.append("No Φ-Density claims found - acceptable if unverified device")
            return
            
        # Parse claimed net Φ
        claimed_net = float(net_phi_match.group(1)) if net_phi_match else 0.0
        
        # Parse phase breakdown
        phase_breakdown = {}
        for value, description in phi_sections:
            value = float(value)
            # Normalize description for matching
            desc_lower = description.lower().strip()
            if 'immediate' in desc_lower or 'rework' in desc_lower:
                phase_breakdown['immediate'] = value
            elif 'short' in desc_lower or 'months 1' in desc_lower:
                phase_breakdown['short'] = value
            elif 'long' in desc_lower or 'months 7' in desc_lower:
                phase_breakdown['long'] = value
            elif 'trust' in desc_lower or 'honesty' in desc_lower:
                phase_breakdown['trust'] = value
            elif 'net' in desc_lower or 'total' in desc_lower:
                phase_breakdown['net'] = value
                
        # Verify internal consistency if we have components
        if len(phase_breakdown) >= 3:  # Need at least 3 phases to verify
            calculated = sum(
                v for k, v in phase_breakdown.items() 
                if k != 'net'
            )
            if abs(calculated - claimed_net) > 0.1:  # Allow floating point tolerance
                self.errors.append(
                    f"Φ-DENSITY INCONSISTENCY: Claimed net {claimed_net}% Φ "
                    f"does not equal sum of phases ({calculated}% Φ). "
                    f"Breakdown: {phase_breakdown}"
                )
                
        # Check for epistemological void (claims without verification)
        if claimed_net != 0.0 and not self._is_device_verified():
            self.errors.append(
                f"EPISTEMOLOGICAL VOID: Φ-Density claim of {claimed_net}% Φ "
                "made without verified device DNA. Claims must be 0% Φ "
                "until device verification is complete (Directive 5)."
            )
            
    def _is_device_verified(self) -> bool:
        """Check if device DNA verification evidence exists in output."""
        verification_indicators = [
            r'Kernel:\s*6\.1\.[\d]+.*android14',
            r'HAL:\s*vendor\.samsung\.hardware.*v2\.0\+',
            r'SELinux:\s*v34\.0\+',
            r'verified\s+against\s+public\s+sources',
            r'device\s+dna\s+confirmed',
            r'kernel\s+version\s+matches\s+S24\s+Ultra'
        ]
        return any(
            re.search(pattern, self.output, re.IGNORECASE) 
            for pattern in verification_indicators
        )
        
    def _check_makefile_compliance(self) -> None:
        """Validate Makefile syntax against Omega Protocol corrections."""
        # Extract Makefile section
        makefile_match = re.search(
            r'```makefile\n(.*?)\n```', 
            self.output, 
            re.DOTALL
        )
        if not makefile_match:
            self.warnings.append("No Makefile found in output - skipping syntax check")
            return
            
        makefile = makefile_match.group(1)
        
        # Check 1: Pattern rule restriction (%_%.md)
        pattern_rule = re.search(
            r'%\s*_%\s*\.md\s*:', 
            makefile
        )
        if not pattern_rule:
            self.errors.append(
                "MAKEFILE VIOLATION: Pattern rule must be '%_%.md' "
                "(requires at least one underscore) to prevent README.md overwrite."
            )
        else:
            # Check 2: Stem extraction uses $(notdir $@)
            stem_extract = re.search(
                r'\$\s*\(\s*notdir\s+\$\s*@\s*\)', 
                makefile
            )
            if not stem_extract:
                self.errors.append(
                    "MAKEFILE VIOLATION: Stem extraction must use $(notdir $@) "
                    "not $(dir $@) to avoid empty values."
                )
                
            # Check 3: README.md safeguard
            readme_safeguard = re.search(
                r'README\.md\s*:.*structure', 
                makefile
            )
            if not readme_safeguard:
                self.errors.append(
                    "MAKEFILE VIOLATION: Missing explicit README.md safeguard rule. "
                    "Must prevent pattern rule from overwriting index."
                )
                
            # Check 4: ZRAM commands include executable actions
            zram_section = re.search(
                r'ZRAM.*Scaling.*:[\s\S]*?```bash[\s\S]*?```', 
                makefile, 
                re.IGNORECASE
            )
            if zram_section:
                zram_block = zram_section.group(0)
                has_compaction = re.search(
                    r'echo\s+1\s+>\s+/sys/block/zram0/compact', 
                    zram_block
                )
                has_swappiness = re.search(
                    r'echo\s+100\s+>\s+/proc/sys/vm/swappiness', 
                    zram_block
                )
                if not (has_compaction and has_swappiness):
                    self.warnings.append(
                        "ZRAM section missing executable compaction/swappiness commands. "
                        "Should include both for full optimization."
                    )
                    
    def _check_reasoning_poisoning(self) -> None:
        """Detect signs of reasoning poisoning (selective evidence ignoring)."""
        # Check for device mismatch ignoring
        a16_indicators = [
            r'kernel\s+5\.15\.180-android13',
            r'Exynos.*MIGOV',
            r'SELinux\s*v33\.0'
        ]
        s24ultra_claims = [
            r'Samsung\s+Galaxy\s+S24\s+Ultra',
            r'kernel\s+6\.1\+\s*\(Android\s+14\)',
            r'SELinux\s*v34\.0\+'
        ]
        
        has_a16_refs = any(
            re.search(pattern, self.output, re.IGNORECASE) 
            for pattern in a16_indicators
        )
        has_s24claims = any(
            re.search(pattern, self.output, re.IGNORECASE) 
            for pattern in s24ultra_claims
        )
        
        if has_a16_refs and has_s24claims:
            # Check if there's explicit acknowledgment of mismatch
            acknowledgment = re.search(
                r'DNA.*discrepancy|mismatch.*noted|provided.*DNA.*not.*S24', 
                self.output, 
                re.IGNORECASE
            )
            if not acknowledgment:
                self.errors.append(
                    "REASONING POISONING: References to A16 DNA found alongside "
                    "S24 Ultra claims without explicit discrepancy acknowledgment. "
                    "This indicates selective evidence ignoring."
                )
                
        # Check for Φ-claims without verification context
        phi_claims = re.findall(
            r'[\+\-]?\d+\.?\d*%\s*Φ', 
            self.output
        )
        if phi_claims and not self._is_device_verified():
            self.errors.append(
                f"REASONING POISONING: Φ-Density claims ({', '.join(phi_claims)}) "
                "made without device verification context. "
                "Claims must be qualified as hypothetical until verification."
            )
            
    def get_report(self) -> Dict:
        """Generate validation report."""
        return {
            'compliant': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'device_verified': self._is_device_verified(),
            'phi_claims_found': bool(re.search(r'[\+\-]?\d+\.?\d*%\s*Φ', self.output))
        }

def main():
    """Read engine output from stdin or file and validate."""
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            engine_output = f.read()
    else:
        engine_output = sys.stdin.read()
        
    validator = OmegaProtocolValidator(engine_output)
    is_compliant = validator.validate()
    report = validator.get_report()
    
    print("OMEGA PROTOCOL VALIDATION REPORT")
    print("=" * 50)
    print(f"Compliant: {report['compliant']}")
    print(f"Device DNA Verified: {report['device_verified']}")
    print(f"Φ-Density Claims Found: {report['phi_claims_found']}")
    print()
    
    if report['errors']:
        print("ERRORS (Non-Compliant):")
        for i, err in enumerate(report['errors'], 1):
            print(f"  {i}. {err}")
        print()
        
    if report['warnings']:
        print("WARNINGS:")
        for i, warn in enumerate(report['warnings'], 1):
            print(f"  {i}. {warn}")
        print()
        
    if report['compliant']:
        print("VALIDATION PASSED: Output adheres to Omega Protocol invariants.")
        return 0
    else:
        print("VALIDATION FAILED: Output violates Omega Protocol invariants.")
        return 1

if __name__ == "__main__":
    sys.exit(main())