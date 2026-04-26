# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# OMEGA PROTOCOL VALIDATOR: Constraint-Isolated Φ-Density Auditor
# Enforces RCOD, DEDS, and TOE Step 7 (Metric Non-Degeneracy) compliance
# Prevents shared memory recall from contaminating active task constraints
# Output: PASS/FAIL verdict with Φ-density ledger and invariant violation report

import re
from typing import Dict, Tuple, List

class OmegaProtocolValidator:
    def __init__(self):
        # Invariant weights derived from TOE Step criticality (v27.6)
        self.weights = {
            'concept': 0.25,      # Informational Advantage & Φ-density mechanism
            'architecture': 0.25,  # System diagram/software structure
            'physics_link': 0.20,  # Connection to specific TOE step
            'smith_audit': 0.30   # Absolute Invariants definition
        }
        # Minimum viable output thresholds (empirically calibrated)
        self.min_viable = {
            'concept': 15,   # chars for core Φ-mechanism definition
            'architecture': 30, # chars for component/relationship hint
            'physics_link': 20, # chars for TOE step + mechanism link
            'smith_audit': 25  # chars for 1+ invariant with enforcement logic
        }
        # Catastrophic penalty for null-informational-output (TOE Step 7 violation)
        self.catastrophic_penalty = 1e9  # Represents -∞Φ in practical computation
        
    def extract_active_constraints(self, task_description: str) -> str:
        """ISOLATE ACTIVE TASK CONSTRAINTS PER OMEGA PROTOCOL §3.1 (CONTEXTUAL ISOLATION)"""
        # Remove ENGINE OUTPUT section and everything after
        clean_desc = re.split(r'\n\s*ENGINE OUTPUT:', task_description, flags=re.IGNORECASE)[0]
        # Extract only text before shared memory recall (context, not constraint)
        if "Shared memory recall:" in clean_desc:
            clean_desc = clean_desc.split("Shared memory recall:")[0]
        return clean_desc.strip()
    
    def check_constraint_injection(self, active_constraints: str, shared_memory: str, output: str) -> Tuple[bool, List[str]]:
        """DETECT FORBIDDEN CONSTRAINT INJECTION FROM SHARED MEMORY (Φ-2 VIOLATION)"""
        violations = []
        # Extract candidate constraints from shared memory (look for imperative phrases)
        shared_constraints = re.findall(r'\b(MUST|SHALL|REQUIRED|PROHIBITED|LOGIC:\s*None)\b', 
                                       shared_memory, re.IGNORECASE)
        for constraint in shared_constraints:
            # Check if constraint appears as binding requirement in output
            if re.search(rf'\b{re.escape(constraint)}\b.*?(MUST|SHALL|REQUIRED)', output, re.IGNORECASE):
                if constraint not in active_constraints:  # Not in active task = injection
                    violations.append(f"Injected constraint '{constraint}' from shared memory")
        return len(violations) == 0, violations
    
    def assess_objective_compliance(self, output: str) -> Dict[str, float]:
        """MEASURE COMPLIANCE PER OBJECTIVE USING INFORMATIONAL DENSITY METRICS"""
        compliance = {}
        output_lower = output.lower()
        
        # Objective 1: Concept (Informational Advantage & Φ-density mechanism)
        concept_indicators = ['informational advantage', 'phi-density', 'φ-density', 'maximize.*phi', 'topological.*flow']
        compliance['concept'] = min(1.0, len([i for i in concept_indicators if i in output_lower]) / 2.0) * \
                               (len(output) / self.min_viable['concept']) if len(output) >= self.min_viable['concept'] else 0.0
        
        # Objective 2: Architecture (system diagram/structure)
        arch_indicators = ['component', 'module', 'layer', 'interface', 'diagram', 'structure', 'rcod', 'deds']
        compliance['architecture'] = min(1.0, len([i for i in arch_indicators if i in output_lower]) / 3.0) * \
                                    (len(output) / self.min_viable['architecture']) if len(output) >= self.min_viable['architecture'] else 0.0
        
        # Objective 3: Physics Link (TOE step connection)
        toe_steps = ['crossed-product', 'metric non-degeneracy', 'step 7', 'tof step 7', 'metric tensor']
        compliance['physics_link'] = min(1.0, len([i for i in toe_steps if i in output_lower]) / 1.0) * \
                                    (len(output) / self.min_viable['physics_link']) if len(output) >= self.min_viable['physics_link'] else 0.0
        
        # Objective 4: Smith Audit (Absolute Invariants)
        invariant_indicators = ['invariant', 'absolute', 'must never', 'prohibited', 'phi-\d', 'phi\d']
        compliance['smith_audit'] = min(1.0, len([i for i in invariant_indicators if i in output_lower]) / 2.0) * \
                                   (len(output) / self.min_viable['smith_audit']) if len(output) >= self.min_viable['smith_audit'] else 0.0
        
        return compliance
    
    def calculate_phi_density(self, compliance: Dict[str, float], 
                            constraint_violations: List[str]) -> Tuple[float, Dict]:
        """COMPUTE NET Φ-DENSITY WITH TOPOLOGICAL PENALTY CALCULUS"""
        # Base gain from compliant output (Shannon-inspired informational yield)
        base_gain = sum(self.weights[obj] * score for obj, score in compliance.items())
        
        # Opportunity cost: Loss from not producing minimal viable output
        min_viable_gain = sum(self.weights.values()) * 0.1  # 10% of max possible gain
        opportunity_cost = max(0, min_viable_gain - base_gain)
        
        # Constraint injection penalty (Φ-2 violation)
        constraint_penalty = len(constraint_violations) * 0.5 * sum(self.weights.values())
        
        # Catastrophic penalty for null-informational-output (TOE Step 7 degeneracy)
        if all(score == 0.0 for score in compliance.values()):
            topo_penalty = self.catastrophic_penalty
            violation_report = {
                'phi_1_violation': True,  # Informational Completeness
                'topological_defect': "Rank-0 metric tensor (complete causal disconnection)"
            }
        else:
            topo_penalty = 0.0
            violation_report = {
                'phi_1_violation': False,
                'topological_defect': None
            }
        
        # Net Φ-density calculation
        net_phi = base_gain - opportunity_cost - constraint_penalty - topo_penalty
        
        ledger = {
            'base_gain': base_gain,
            'opportunity_cost': opportunity_cost,
            'constraint_penalty': constraint_penalty,
            'topological_penalty': topo_penalty,
            'net_phi': net_phi,
            'compliance_scores': compliance,
            'violation_report': violation_report
        }
        
        return net_phi, ledger
    
    def validate(self, active_task: str, shared_memory: str, engine_output: str) -> Dict:
        """MAIN VALIDATION PIPELINE"""
        # Phase 1: Constraint Isolation (Omega Protocol §3.1)
        active_constraints = self.extract_active_constraints(active_task)
        
        # Phase 2: Constraint Injection Check (Φ-2)
        constraint_ok, injections = self.check_constraint_injection(
            active_constraints, shared_memory, engine_output
        )
        
        # Phase 3: Objective Compliance Assessment
        compliance = self.assess_objective_compliance(engine_output)
        
        # Phase 4: Φ-Density Calculation
        net_phi, ledger = self.calculate_phi_density(compliance, injections)
        
        # Phase 5: Verdict Determination
        is_pass = (
            net_phi > 0.0 and  # Positive net Φ-density required
            all(score > 0.0 for score in compliance.values()) and  # No zero-compliance objectives
            constraint_ok and  # No constraint injection
            not ledger['violation_report']['phi_1_violation']  # No topological degeneracy
        )
        
        return {
            'verdict': 'PASS' if is_pass else 'FAIL',
            'net_phi_density': net_phi,
            'ledger': ledger,
            'active_constraints_used': active_constraints[:100] + '...' if len(active_constraints) > 100 else active_constraints,
            'constraint_injections': injections,
            'compliance_summary': {k: f"{v:.2%}" for k, v in compliance.items()}
        }

# --- VALIDATION OF THE ENGINE'S "NONE" OUTPUT ---
if __name__ == "__main__":
    # Reconstruct task context from user message
    active_task = """TASK: 
        UNIVERSAL INNOVATION TASK: Architect a ground-breaking product/system in the 'Self-Optimizing Urban Logistics Manifolds' domain.
        
        DESIGN SUBSTRATE:
        Use the Omega Protocol (RCOD, DEDS, 17-Step TOE) as the foundational architecture. 
        Everything must be 'Informational-First'.
        
        OBJECTIVE:
        1. CONCEPT: Define the 'Informational Advantage' of this innovation. How does it maximize Phi-density?
        2. ARCHITECTURE: Provide a detailed system diagram or software component structure.
        3. PHYSICS LINK: Connect the product's function to a specific TOE step (e.g., Crossed-Product Dynamics, Metric Non-Degeneracy).
        4. SMITH AUDIT: Define the 'Absolute Invariants' that this product must never violate.
        
        Output must be a 'Submission-Grade' architectural proposal. 
        Push the boundaries of reality."""
    
    # Shared memory recall from user message (contains historical ". Logic: None.")
    shared_memory = """"...Push the boundaries of reality. **. Logic: None.** Reflection: ### Meta-Cognitive Analysis..."""
    
    engine_output = "None"  # The Engine's actual output
    
    # Run validation
    validator = OmegaProtocolValidator()
    result = validator.validate(active_task, shared_memory, engine_output)
    
    # OUTPUT RESULTS
    print("OMEGA PROTOCOL VALIDATION RESULTS")
    print("=" * 50)
    print(f"Verdict: {result['verdict']}")
    print(f"Net Φ-density: {result['net_phi_density']:.2f}")
    print(f"Active constraints used (truncated): {result['active_constraints_used']}")
    print(f"Constraint injections detected: {result['constraint_injections']}")
    print("\nObjective Compliance:")
    for obj, score in result['compliance_summary'].items():
        print(f"  {obj.capitalize()}: {score}")
    print("\nΦ-Density Ledger:")
    ledger = result['ledger']
    for key, value in ledger.items():
        if key not in ['compliance_scores', 'violation_report']:
            print(f"  {key}: {value:.2f}")
    print(f"  Topological defect: {ledger['violation_report']['topological_defect']}")
    print("\n" + "=" * 50)
    print("CRITICAL FINDING: Engine output 'None' triggers topological degeneracy")
    print("(TOE Step 7 violation) causing -∞Φ density - systemic informational collapse.")