# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

# ===== ESSENTIAL CLASSES FROM PROPOSAL (MINIMAL VALIDATION SET) =====
class InvariantStatus(Enum):
    VALID = "valid"
    VIOLATED = "violated"
    DEGRADED = "degraded"

@dataclass
class CausalNode:
    node_id: str
    timestamp: float
    causal_links: List[str] = field(default_factory=list)
    topological_charge: complex = complex(1.0, 0.0)
    entropy_state: float = 0.0  # Note: This is the field we'll check for L3c error

@dataclass
class LatticeState:
    nodes: Dict[str, CausalNode]
    phi_n: float
    phi_delta: float
    metric_determinant: float
    causal_order_valid: bool
    identity_drift: float
    energy_usage: float
    information_loss: float
    temporal_drift: float

class RCODELatticeManager:
    def __init__(self, stiffness_N: float = 0.85, stiffness_Δ: float = 0.35):
        self.ξ_N = stiffness_N
        self.ξ_Δ = stiffness_Δ
        self.causal_nodes: Dict[str, CausalNode] = {}
        self.causal_graph: Dict[str, List[str]] = {}
        self._Φ_N: float = 1.0  # Newtonian fidelity baseline
        self._Φ_Δ: float = 0.0  # Differential entropy
        self._ψ: float = 0.0    # Coupling function
        self._update_coupling()
    
    def _update_coupling(self):
        epsilon = 1e-9
        self._ψ = np.log(self._Φ_N + epsilon)
    
    def encode_information(self, data_hash: str, timestamp: float, 
                        linked_nodes: List[str] = None) -> CausalNode:
        node = CausalNode(
            node_id=data_hash,
            timestamp=timestamp,
            causal_links=linked_nodes or [],
            topological_charge=complex(1.0, 0.0),
            entropy_state=0.0
        )
        self.causal_nodes[data_hash] = node
        self.causal_graph[data_hash] = linked_nodes or []
        self._Φ_N = self._compute_newtonian_fidelity()
        self._update_coupling()
        # L3c ERROR: Stores coupling function ψ instead of actual entropy contribution
        node.entropy_state = self._ψ  
        return node
    
    def _compute_newtonian_fidelity(self) -> float:
        if len(self.causal_nodes) == 0:
            return 1.0
        retention_rate = len(self.causal_nodes) / max(1, len(self.causal_graph))
        total_links = sum(len(links) for links in self.causal_graph.values())
        expected_links = len(self.causal_nodes) * 2
        link_preservation = min(1.0, total_links / max(1, expected_links))
        # NOTE: Weights sum to 1.25 (>1.0) - minor issue but not critical for validation
        fidelity = (
            self.ξ_N * retention_rate + 
            0.25 * link_preservation + 
            0.15 * (1.0 if len(self.causal_nodes) > 0 else 0.0)  # Simplified charge_coherence
        )
        self._Φ_N = max(0.01, fidelity)
        return self._Φ_N
    
    def _compute_differential_entropy(self) -> float:
        if len(self.causal_nodes) < 2:
            return 0.0
        link_counts = [len(links) for links in self.causal_graph.values()]
        total_links = sum(link_counts) + 1e-9
        entropy = 0.0
        for count in link_counts:
            if count > 0:
                p = count / total_links
                entropy -= p * np.log2(p)
        max_entropy = np.log2(len(self.causal_nodes) + 1)
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0.0
        self._Φ_Δ = self.ξ_Δ * normalized_entropy
        return self._Φ_Δ
    
    def compute_phi_density(self) -> float:
        Φ_N = self._compute_newtonian_fidelity()
        Φ_Δ = self._compute_differential_entropy()
        asymmetry_limit = 0.5 * Φ_N
        if Φ_Δ >= asymmetry_limit:
            Φ_Δ = 0.49 * Φ_N  # Clamp below bound
        return Φ_N + Φ_Δ
    
    @property
    def ψ(self) -> float:
        return self._ψ
    
    def _compute_metric_determinant(self) -> float:
        if len(self.causal_nodes) == 0:
            return 1.0
        return max(1e-10, len(self.causal_nodes) / 10.0)
    
    def _check_causal_order(self) -> bool:
        for node_id, links in self.causal_graph.items():
            node = self.causal_nodes.get(node_id)
            if node:
                for link in links:
                    linked_node = self.causal_nodes.get(link)
                    if linked_node and linked_node.timestamp > node.timestamp:
                        return False
        return True
    
    def get_lattice_state(self) -> LatticeState:
        return LatticeState(
            nodes=self.causal_nodes,
            phi_n=self._Φ_N,
            phi_delta=self._Φ_Δ,
            metric_determinant=self._compute_metric_determinant(),
            causal_order_valid=self._check_causal_order(),
            identity_drift=self._compute_identity_drift(),
            energy_usage=self._estimate_energy_usage(),
            information_loss=self._estimate_information_loss(),
            temporal_drift=self._compute_temporal_drift()
        )
    
    def _compute_identity_drift(self) -> float:
        if len(self.causal_nodes) == 0:
            return 0.0
        charges = [n.topological_charge for n in self.causal_nodes.values()]
        if len(charges) < 2:
            return 0.0
        variance = np.var([abs(c) for c in charges])
        return min(1.0, variance)
    
    def _estimate_energy_usage(self) -> float:
        return min(1.0, len(self.causal_nodes) / 1000.0)
    
    def _estimate_information_loss(self) -> float:
        return 0.0
    
    def _compute_temporal_drift(self) -> float:
        if len(self.causal_nodes) < 2:
            return 0.0
        timestamps = [n.timestamp for n in self.causal_nodes.values()]
        return max(timestamps) - min(timestamps) if timestamps else 0.0

class SmithAuditGuardian:
    INVARIANTS = [
        "Metric Non-Degeneracy",
        "Causal Order Preservation", 
        "Identity Continuity",
        "Energy Envelope",
        "Information Conservation",
        "Temporal Coherence"
    ]
    
    def __init__(self, lattice: RCODELatticeManager):
        self.lattice = lattice
        self.violation_log: List[Dict] = []
        # L4 ERROR: Typo in variable name (in0variant_states instead of invariant_states)
        self.in0variant_states: Dict[str, InvariantStatus] = {
            inv: InvariantStatus.VALID for inv in self.INVARIANTS
        }
        self.thresholds = {
            'metric_degeneracy': 1e-10,  # L3 ERROR: Fixed threshold, should be exp(-ψ)
            'causal_violation_tolerance': 0,
            'identity_drift_max': 0.01,
            'energy_envelope_headroom': 0.20,
            'information_loss_tolerance': 0,
            'temporal_drift_max': 1e-9
        }
    
    def check_all_invariants(self, system_state: LatticeState) -> bool:
        self._check_metric_nondegeneracy(system_state)
        self._check_causal_order(system_state)
        self._check_identity_continuity(system_state)
        self._check_energy_envelope(system_state)
        self._check_information_conservation(system_state)
        self._check_temporal_coherence(system_state)
        return all(s == InvariantStatus.VALID for s in self.in0variant_states.values())  # Uses typo'd var
    
    def _check_metric_nondegeneracy(self, state: LatticeState):
        threshold = self.thresholds['metric_degeneracy']  # FIXED 1e-10 (should be exp(-ψ))
        if state.metric_determinant < threshold:
            self.in0variant_states["Metric Non-Degeneracy"] = InvariantStatus.VIOLATED
        else:
            self.in0variant_states["Metric Non-Degeneracy"] = InvariantStatus.VALID
    
    def _check_causal_order(self, state: LatticeState):
        if not state.causal_order_valid:
            self.in0variant_states["Causal Order Preservation"] = InvariantStatus.VIOLATED
        else:
            self.in0variant_states["Causal Order Preservation"] = InvariantStatus.VALID
    
    def _check_identity_continuity(self, state: LatticeState):
        if state.identity_drift > self.thresholds['identity_drift_max']:
            self.in0variant_states["Identity Continuity"] = InvariantStatus.VIOLATED
        else:
            self.in0variant_states["Identity Continuity"] = InvariantStatus.VALID
    
    def _check_energy_envelope(self, state: LatticeState):
        headroom = self.thresholds['energy_envelope_headroom']
        if state.energy_usage > (1 - headroom):
            self.in0variant_states["Energy Envelope"] = InvariantStatus.VIOLATED
        else:
            self.in0variant_states["Energy Envelope"] = InvariantStatus.VALID
    
    def _check_information_conservation(self, state: LatticeState):
        if state.information_loss > self.thresholds['information_loss_tolerance']:
            self.in0variant_states["Information Conservation"] = InvariantStatus.VIOLATED
        else:
            self.in0variant_states["Information Conservation"] = InvariantStatus.VALID
    
    def _check_temporal_coherence(self, state: LatticeState):
        if state.temporal_drift > self.thresholds['temporal_drift_max']:
            self.in0variant_states["Temporal Coherence"] = InvariantStatus.VIOLATED
        else:
            self.in0variant_states["Temporal Coherence"] = InvariantStatus.VALID

# ===== VALIDATION TESTS =====
def run_validation():
    print("="*60)
    print("OMEGA PROTOCOL VALIDATION: PCCISS ARCHITECTURAL PROPOSAL")
    print("="*60)
    
    # Test 1: Basic lattice operations and Φ-density calculation
    print("\n[TEST 1] Φ-DENSITY CALCULATION & ASYMMETRY BOUND")
    lattice = RCODELatticeManager()
    
    # Add three nodes to create non-trivial lattice
    node1 = lattice.encode_information("data1", 0.0, [])
    node2 = lattice.encode_information("data2", 1.0, ["data1"])
    node3 = lattice.encode_information("data3", 2.0, ["data1", "data2"])
    
    state = lattice.get_lattice_state()
    phi_total = lattice.compute_phi_density()
    
    print(f"  Φ_N (Newtonian Fidelity): {state.phi_n:.4f}")
    print(f"  Φ_Δ (Differential Entropy): {state.phi_delta:.4f}")
    print(f"  Φ_Total: {phi_total:.4f}")
    print(f"  Coupling function ψ = ln(Φ_N + ε): { lattice.ψ:.4f }")
    print(f"  Theoretical ψ: { np.log(state.phi_n + 1e-9):.4f }")
    
    # Check ψ calculation
    psi_match = np.abs(lattice.psi - np.log(state.phi_n + 1e-9)) < 1e-9
    print(f"  ψ Calculation Correct: {'✓' if psi_match else '✗'}")
    
    # Check asymmetry bound (Φ_Δ < 0.5 * Φ_N)
    asymmetry_bound = 0.5 * state.phi_n
    bound_satisfied = state.phi_delta < asymmetry_bound
    print(f"  Asymmetry Bound (Φ_Δ < 0.5*Φ_N): {state.phi_delta:.4f} < {asymmetry_bound:.4f} → {'✓' if bound_satisfied else '✗'}")
    
    # Test 2: SmithAuditGuardian - Check for critical errors
    print("\n[TEST 2] SMITH AUDIT GUARDIAN - INVARIANT CHECKS")
    guardian = SmithAuditGuardian(lattice)
    
    # L4 ERROR: Typo in variable name
    has_typo = hasattr(guardian, 'in0variant_states') and not hasattr(guardian, 'invariant_states')
    print(f"  L4 ERROR - Variable Name Typo (in0variant_states): {'✓ DETECTED' if has_typo else '✗ NOT FOUND'}")
    
    # L3 ERROR: Threshold inconsistency
    # Get what the guardian uses for metric threshold
    guardian_threshold = guardian.thresholds['metric_degeneracy']
    # Get what it should be (exp(-ψ) from lattice)
    correct_threshold = np.exp(-lattice.psi)
    threshold_match = np.abs(guardian_threshold - correct_threshold) < 1e-9
    print(f"  L3 ERROR - Metric Threshold:")
    print(f"    Guardian Uses: {guardian_threshold:.2e}")
    print(f"    Should Be (exp(-ψ)): {correct_threshold:.2e}")
    print(f"    Threshold Match: {'✓' if threshold_match else '✗'}")
    
    # Test metric non-degeneracy check
    state = lattice.get_lattice_state()
    metric_det = state.metric_determinant
    guardian._check_metric_nondegeneracy(state)
    invariant_status = guardian.in0variant_states["Metric Non-Degeneracy"]
    expected_status = InvariantStatus.VALID if metric_det >= guardian_threshold else InvariantStatus.VIOLATED
    threshold_check_passed = (invariant_status == expected_status)
    print(f"  Metric Non-Degeneracy Check:")
    print(f"    Metric Determinant: {metric_det:.2e}")
    print(f"    Guardian Threshold: {guardian_threshold:.2e}")
    print(f"    Expected Status: {expected_status.value}")
    print(f"    Actual Status: {invariant_status.value}")
    print(f"    Check Correct: {'✓' if threshold_check_passed else '✗'}")
    
    # Test 3: L3c ERROR - Node entropy state semantics
    print("\n[TEST 3] NODE ENTROPY STATE SEMANTICS (L3c ERROR)")
    # Check if node.entropy_state stores ψ (the coupling function) instead of actual entropy
    sample_node = list(lattice.causal_nodes.values())[0]
    node_entropy_state = sample_node.entropy_state
    lattice_psi = lattice.psi
    entropy_stores_psi = np.abs(node_entropy_state - lattice_psi) < 1e-9
    print(f"  Sample Node entropy_state: {node_entropy_state:.4f}")
    print(f"  Lattice ψ (coupling function): {lattice_psi:.4f}")
    print(f"  L3c ERROR - entropy_state stores ψ: {'✓ DETECTED' if entropy_stores_psi else '✗ NOT FOUND'}")
    print(f"    (Should store actual entropy contribution, not coupling function)")
    
    # Test 4: Internal consistency of lattice state
    print("\n[TEST 4] LATTICE STATE CONSISTENCY")
    state = lattice.get_lattice_state()
    print(f"  Node Count: {len(state.nodes)}")
    print(f"  Causal Order Valid: {state.causal_order_valid}")
    print(f"  Identity Drift: {state.identity_drift:.4f}")
    print(f"  Energy Usage: {state.energy_usage:.4f}")
    print(f"  Information Loss: {state.information_loss:.4f}")
    print(f"  Temporal Drift: {state.temporal_drift:.4f}")
    
    # Summary of errors
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    errors = []
    if not psi_match:
        errors.append("ψ calculation incorrect")
    if not bound_satisfied:
        errors.append("Asymmetry bound violated")
    if has_typo:
        errors.append("L4: Variable name typo (in0variant_states)")
    if not threshold_match:
        errors.append("L3: Metric threshold inconsistency (fixed vs exp(-ψ))")
    if not threshold_check_passed:
        errors.append("Metric non-degeneracy check logic flawed")
    if entropy_stores_psi:
        errors.append("L3c: Node entropy_state stores coupling function ψ (should be entropy)")
    
    if errors:
        print("❌ VALIDATION FAILED - CRITICAL ERRORS DETECTED:")
        for i, err in enumerate(errors, 1):
            print(f"  {i}. {err}")
        print("\nRECOMMENDATION: Fix errors before submission.")
        return False
    else:
        print("✅ VALIDATION PASSED - No critical errors detected.")
        print("Note: Minor issues (e.g., weight normalization in _compute_newtonian_fidelity) remain but do not violate core invariants.")
        return True

if __name__ == "__main__":
    run_validation()