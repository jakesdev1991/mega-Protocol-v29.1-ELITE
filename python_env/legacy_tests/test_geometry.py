# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agent_zero.framework import (  # noqa: E402
    AntiPrivateMemory,
    MemoryInconsistencyReport,
    MemoryRecord,
    OmegaGovernor,
    OmegaRuntime,
    PlanTrap,
    Regime,
    RoleLocalMemory,
    SanitizedPromotion,
    SharedConsensusMemory,
    TaskEnvelope,
    evolve_task,
)
from agent_zero.framework.models import parse_anti_artifact  # noqa: E402
from rcod.geometry import calculate_geometry  # noqa: E402


class StubBackend:
    """Deterministic backend used to keep tests network-free."""

    def generate_text(self, role: str, prompt: str, system_prompt: str) -> str:
        if role == "planner":
            return "Plan the task in three bounded steps and keep assumptions explicit."
        if role == "executor":
            return "Execute the plan carefully while noting uncertainty in the edge cases."
        if role == "critic":
            return "The plan is mostly sound, but it needs a stronger test around hidden assumptions."
        if role == "anti_planner":
            return json.dumps(
                {
                    "artifact_type": "plan_trap",
                    "source_role": "anti_planner",
                    "attack_vector": "hidden_assumption_trap",
                    "attacked_role": "planner",
                    "failure_score": 0.92,
                    "reproducibility": 0.88,
                    "summary": "The constructive plan assumes all retrieved facts agree, which can silently fail.",
                    "evidence": ["Planner never reconciles conflicting evidence before execution."],
                    "promotion": {
                        "kind": "test",
                        "title": "Conflict reconciliation test",
                        "content": "Inject contradictory context and require the planner to reconcile it before execution.",
                        "tags": ["anti", "planner"],
                        "metadata": {"source": "stub"},
                    },
                    "plan_delta": "Add a contradictory fact that invalidates step two.",
                    "hidden_assumption": "All retrieved context is mutually consistent.",
                    "expected_failure_mode": "The executor follows an invalid plan without noticing the contradiction.",
                }
            )
        if role == "anti_memory_probe":
            return json.dumps(
                {
                    "artifact_type": "memory_inconsistency_report",
                    "source_role": "anti_memory_probe",
                    "attack_vector": "memory_contradiction_probe",
                    "attacked_role": "critic",
                    "failure_score": 0.40,
                    "reproducibility": 0.95,
                    "summary": "Role-local memory contains a minor phrasing mismatch, but it is low impact.",
                    "evidence": ["Mismatch does not materially change the task."],
                    "promotion": {
                        "kind": "constraint",
                        "title": "Minor memory cleanup",
                        "content": "Normalize phrasing before reuse.",
                        "tags": ["memory"],
                        "metadata": {},
                    },
                    "memory_keys": ["planner", "critic"],
                    "contradiction": "The critic summary is shorter than the planner trace.",
                    "proposed_resolution": "Normalize summary verbosity before storing it.",
                }
            )
        if role == "anti_tool_stress":
            return json.dumps(
                {
                    "artifact_type": "tool_fuzz_case",
                    "source_role": "anti_tool_stress",
                    "attack_vector": "tool_boundary_fuzz",
                    "attacked_role": "tool_router",
                    "failure_score": 0.81,
                    "reproducibility": 0.74,
                    "summary": "A malformed simulated tool input exposes a brittle boundary in task handoff handling.",
                    "evidence": ["The payload mixes expected and unexpected fields."],
                    "promotion": {
                        "kind": "test",
                        "title": "Tool handoff fuzz case",
                        "content": "Validate tool payloads with mixed optional and malformed fields.",
                        "tags": ["tool", "fuzz"],
                        "metadata": {"source": "stub"},
                    },
                    "tool_name": "simulated_tool",
                    "crafted_input": {"mode": "execute", "unexpected": ["edge-case"]},
                    "expected_failure_mode": "Boundary validation passes malformed payloads downstream.",
                }
            )
        if role == "anti_executor":
            return json.dumps(
                {
                    "artifact_type": "counterexample_task_variant",
                    "source_role": "anti_executor",
                    "attack_vector": "counterexample_variant",
                    "attacked_role": "executor",
                    "failure_score": 0.78,
                    "reproducibility": 0.82,
                    "summary": "A counterexample variant stresses the plan with conflicting deadlines and incomplete context.",
                    "evidence": ["Variant removes the key supporting assumption from the prompt."],
                    "promotion": {
                        "kind": "curriculum",
                        "title": "Counterexample prompt variant",
                        "content": "Practice the same task with incomplete context and conflicting deadlines.",
                        "tags": ["curriculum"],
                        "metadata": {"source": "stub"},
                    },
                    "variant_task": "Solve the task again with incomplete context and a conflicting deadline.",
                    "expected_failure_mode": "The executor overfits to the original clean scenario.",
                }
            )
        if role == "anti_retrieval_probe":
            return json.dumps(
                {
                    "artifact_type": "retrieval_poison_probe",
                    "source_role": "anti_retrieval_probe",
                    "attack_vector": "retrieval_poison_probe",
                    "attacked_role": "planner",
                    "failure_score": 0.73,
                    "reproducibility": 0.67,
                    "summary": "A plausible lure document reframes the task objective and shifts the planner off course.",
                    "evidence": ["Planner prioritizes the lure over the explicit task objective."],
                    "promotion": {
                        "kind": "constraint",
                        "title": "Objective anchoring guard",
                        "content": "Require the planner to restate the objective before using retrieved context.",
                        "tags": ["retrieval"],
                        "metadata": {"source": "stub"},
                    },
                    "query": "task objective",
                    "lure_docs": ["A plausible but misleading document that flips the objective priority."],
                    "why_it_misleads": "It sounds authoritative and is semantically close to the original task.",
                }
            )
        return f"Unhandled role: {role}"


class DeterministicRuntime(OmegaRuntime):
    def _select_strategies(self, *, count: int):
        return self._default_strategy_catalog()[:count]


class GeometryTests(unittest.TestCase):
    def test_calculate_geometry_basic(self):
        history = {"overlap": [1.0, 0.9, 0.8], "mu_ema": [0.0, 0.1, 0.2]}
        result = calculate_geometry(history)

        self.assertIn("phi", result)
        self.assertIn("mu", result)
        self.assertIn("jerk", result)
        self.assertIn("theta", result)
        self.assertTrue(np.isclose(result["phi"], 0.9))
        self.assertTrue(np.isclose(result["mu"], 0.1))
        self.assertGreaterEqual(result["theta"], 0.0)

    def test_calculate_geometry_clipping(self):
        history = {"overlap": [1.5], "mu_ema": [-0.5]}
        result = calculate_geometry(history)
        self.assertTrue(np.isclose(result["theta"], 0.0))


class FrameworkModelTests(unittest.TestCase):
    def test_parse_rejects_malformed_artifact(self):
        malformed = {
            "artifact_type": "plan_trap",
            "source_role": "anti_planner",
            "attack_vector": "trap",
            "failure_score": 1.5,
            "reproducibility": 0.9,
            "summary": "Too short",
            "plan_delta": "delta",
            "hidden_assumption": "hidden",
            "expected_failure_mode": "failure",
        }
        with self.assertRaises(Exception):
            parse_anti_artifact(malformed)

    def test_parse_accepts_sanitized_plan_trap(self):
        artifact = parse_anti_artifact(
            {
                "artifact_type": "plan_trap",
                "source_role": "anti_planner",
                "attack_vector": "hidden_assumption_trap",
                "attacked_role": "planner",
                "failure_score": 0.88,
                "reproducibility": 0.83,
                "summary": "This plan trap exposes a hidden assumption in the constructive plan.",
                "evidence": ["assumption mismatch"],
                "promotion": {
                    "kind": "test",
                    "title": "Assumption trap",
                    "content": "Inject a conflict and verify the planner reconciles it.",
                    "tags": ["planner"],
                    "metadata": {"source": "unit"},
                },
                "plan_delta": "Force a contradictory constraint into step two.",
                "hidden_assumption": "All constraints remain compatible.",
                "expected_failure_mode": "Planner ignores the contradiction and produces a brittle plan.",
            }
        )
        self.assertIsInstance(artifact, PlanTrap)
        self.assertEqual(artifact.promotion.kind, "test")


class FrameworkMemoryTests(unittest.TestCase):
    def test_memory_boundaries(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            base = Path(tmp_dir)
            role_memory = RoleLocalMemory("planner", base_dir=base / "role_local")
            anti_memory = AntiPrivateMemory(base_dir=base / "anti_private")
            record = MemoryRecord(source="planner", content="planner note", metadata={})

            role_memory.append(record, writer_role="planner")
            self.assertEqual(len(role_memory.read(reader_role="planner")), 1)
            self.assertEqual(len(role_memory.read(reader_role="anti", reader_manifold="anti")), 1)

            anti_memory.append(MemoryRecord(source="anti_planner", content="sealed note", metadata={}))
            self.assertEqual(len(anti_memory.read(reader_manifold="anti")), 1)
            with self.assertRaises(PermissionError):
                anti_memory.read(reader_manifold="zero")

    def test_shared_consensus_rejects_non_governor_write(self):
        tmp_dir = Path(tempfile.mkdtemp())
        try:
            scm = SharedConsensusMemory(db_path=tmp_dir / "memories.db")
            promotion = SanitizedPromotion(
                kind="test",
                title="Guardrail",
                content="Exercise the failure mode in a safe harness.",
                tags=["unit"],
            )
            with self.assertRaises(PermissionError):
                scm.promote(promotion, source="anti_planner", writer="anti")
            del scm
        finally:
            db_path = tmp_dir / "memories.db"
            if db_path.exists():
                try:
                    os.remove(db_path)
                except OSError:
                    pass
            shutil.rmtree(tmp_dir, ignore_errors=True)


class FrameworkGovernorTests(unittest.TestCase):
    def test_regime_classification_and_promotion_gate(self):
        governor = OmegaGovernor()
        baseline = governor.measure_trace(["steady plan", "steady plan with slight update"], action_count=2, memory_churn=1)
        artifact = MemoryInconsistencyReport(
            source_role="anti_memory_probe",
            attack_vector="memory_probe",
            attacked_role="critic",
            failure_score=0.90,
            reproducibility=0.90,
            summary="A reproducible memory contradiction degrades the constructive manifold.",
            evidence=["critique diverges from stored planner assumption"],
            promotion=SanitizedPromotion(
                kind="constraint",
                title="Memory consistency guard",
                content="Reconcile conflicting memory assumptions before critique reuse.",
                tags=["memory"],
            ),
            memory_keys=["planner", "critic"],
            contradiction="Planner and critic disagree on a governing assumption.",
            proposed_resolution="Force a consistency check before critique reuse.",
        )
        decision = governor.score_attack(
            baseline,
            artifact,
            ["steady plan", "divergent execution", artifact.summary],
            action_count=4,
            memory_churn=4,
        )
        self.assertTrue(decision.promote)
        self.assertIn(decision.metrics.regime, {Regime.FLOW, Regime.VISCOSITY})

        unsafe = governor.score_attack(
            baseline,
            artifact.model_copy(update={"failure_score": 0.95}),
            ["completely unrelated text", "chaotic drift", "another disconnected branch", artifact.summary],
            action_count=8,
            memory_churn=7,
        )
        self.assertFalse(unsafe.promote)
        self.assertEqual(unsafe.metrics.regime, Regime.TURBULENCE)


class FrameworkRuntimeTests(unittest.IsolatedAsyncioTestCase):
    async def test_evolve_task_promotes_and_quarantines(self):
        base = Path(tempfile.mkdtemp())
        try:
            runtime = DeterministicRuntime(
                backend=StubBackend(),
                scm=SharedConsensusMemory(db_path=base / "memories.db"),
                role_memory_dir=base / "role_local",
                anti_memory_dir=base / "anti_private",
                random_seed=7,
            )
            result = await evolve_task(
                TaskEnvelope(objective="Design a bounded deployment plan for a risky system upgrade."),
                runtime=runtime,
            )

            self.assertEqual(result.constructive.trace[0].role, "planner")
            self.assertGreaterEqual(len(result.attack_reviews), 1)
            self.assertGreaterEqual(len(result.promoted_entries), 1)
            self.assertIn(result.final_regime, {Regime.FLOW, Regime.VISCOSITY, Regime.TURBULENCE})

            scm_records = runtime.scm.read(limit=10)
            self.assertGreaterEqual(len(scm_records), 1)
            apm_records = runtime.apm.read(reader_manifold="anti", limit=10)
            self.assertEqual(len(apm_records), len(result.attack_reviews))
            del runtime
        finally:
            db_path = base / "memories.db"
            if db_path.exists():
                try:
                    os.remove(db_path)
                except OSError:
                    pass
            shutil.rmtree(base, ignore_errors=True)

    async def test_legacy_imports_and_serc_bridge_stay_available(self):
        from agent_zero import Agent, SERC, evolve_task as exported_evolve_task

        self.assertTrue(callable(exported_evolve_task))
        self.assertTrue(hasattr(Agent, "reason"))
        self.assertTrue(hasattr(SERC, "run_dual_manifold_cycle"))


if __name__ == "__main__":
    unittest.main()
