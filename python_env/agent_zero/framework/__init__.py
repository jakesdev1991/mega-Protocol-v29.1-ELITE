# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""Agent Zero v2 dual-manifold framework."""

from __future__ import annotations

import asyncio
import random
from pathlib import Path
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field

from agent_zero.llm_router import LLMRouter

from .governor import OmegaGovernor, PromotionDecision, PhiMetrics, Regime
from .memory import AntiPrivateMemory, RoleLocalMemory, SharedConsensusMemory
from .models import (
    AntiArtifact,
    AttackStrategyRecord,
    ConstructivePassResult,
    CounterexampleTaskVariant,
    MemoryInconsistencyReport,
    MemoryRecord,
    PlanTrap,
    RetrievalPoisonProbe,
    SanitizedPromotion,
    TaskEnvelope,
    ToolFuzzCase,
    TraceStep,
    parse_anti_artifact,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class RoleBackend(Protocol):
    """Minimal text generation backend contract for the runtime."""

    def generate_text(self, role: str, prompt: str, system_prompt: str) -> str:
        """Return a text completion for the requested role."""


class RouterRoleBackend:
    """Production backend that delegates to the existing blocking router."""

    def __init__(self, router: LLMRouter | None = None):
        self.router = router or LLMRouter()

    def generate_text(self, role: str, prompt: str, system_prompt: str) -> str:
        return self.router.generate(role, prompt, system_prompt)


class AttackReview(BaseModel):
    """Evaluation summary for a single anti artifact."""

    model_config = ConfigDict(extra="forbid")

    artifact: AntiArtifact
    decision: PromotionDecision
    promoted_record: MemoryRecord | None = None


class EvolutionCycleResult(BaseModel):
    """Top-level output of one dual-manifold co-evolution cycle."""

    model_config = ConfigDict(extra="forbid")

    task: TaskEnvelope
    constructive: ConstructivePassResult
    zero_metrics: PhiMetrics
    final_regime: Regime
    attack_reviews: list[AttackReview] = Field(default_factory=list)
    promoted_entries: list[MemoryRecord] = Field(default_factory=list)


class OmegaRuntime:
    """Owns runtime dependencies and long-lived bandit strategy state."""

    def __init__(
        self,
        *,
        backend: RoleBackend | None = None,
        scm: SharedConsensusMemory | None = None,
        governor: OmegaGovernor | None = None,
        role_memory_dir: str | Path | None = None,
        anti_memory_dir: str | Path | None = None,
        random_seed: int | None = None,
    ):
        self.backend = backend or RouterRoleBackend()
        self.scm = scm or SharedConsensusMemory()
        self.governor = governor or OmegaGovernor()
        self.role_memory_dir = Path(role_memory_dir or (PROJECT_ROOT / "agent_zero" / "knowledge" / "role_local"))
        self.apm = AntiPrivateMemory(anti_memory_dir)
        self.random = random.Random(random_seed)
        self.constructive_roles = {
            "planner": "You shape coherent, bounded plans for Agent Zero.",
            "executor": "You execute the best current plan with practical detail and minimal drift.",
            "critic": "You stress-test the constructive output and surface corrections without derailing execution.",
        }
        self.anti_role_prompts = {
            "anti_planner": "You create adversarial plan traps that reveal hidden assumptions.",
            "anti_executor": "You mutate execution details into high-regret failure cases.",
            "anti_critic": "You identify contradictions and precision failures missed by the constructive critic.",
            "anti_memory_probe": "You search for stale or conflicting assumptions across local and shared memories.",
            "anti_tool_stress": "You design safe simulated fuzz cases that expose tool boundary failures.",
            "anti_retrieval_probe": "You design retrieval poison probes that test context integrity.",
        }
        self.role_memories = {
            role: RoleLocalMemory(role, base_dir=self.role_memory_dir)
            for role in ("planner", "executor", "critic", "memory_manager", "tool_router")
        }

    async def run_constructive_pass(self, task: TaskEnvelope) -> ConstructivePassResult:
        """Run the constructive manifold sequentially to produce a baseline trace."""
        search_term = task.objective.split()[0] if task.objective.split() else None
        shared_context = self.scm.read(query=search_term, limit=3, reader="agent_zero")
        shared_lines = [record.content for record in shared_context]

        planner_memory = self.role_memories["planner"].read(reader_role="planner", limit=3)
        planner_prompt = self._build_planner_prompt(task, shared_lines, planner_memory)
        planner_response = await self._generate("planner", planner_prompt, self.constructive_roles["planner"])
        self._write_role_memory("planner", task, planner_response)

        executor_memory = self.role_memories["executor"].read(reader_role="executor", limit=3)
        executor_prompt = self._build_executor_prompt(task, planner_response, executor_memory)
        executor_response = await self._generate("executor", executor_prompt, self.constructive_roles["executor"])
        self._write_role_memory("executor", task, executor_response)

        critic_memory = self.role_memories["critic"].read(reader_role="critic", limit=3)
        critic_prompt = self._build_critic_prompt(task, planner_response, executor_response, critic_memory)
        critic_response = await self._generate("critic", critic_prompt, self.constructive_roles["critic"])
        self._write_role_memory("critic", task, critic_response)

        trace = [
            TraceStep(
                role="planner",
                prompt=planner_prompt,
                response=planner_response,
                system_prompt=self.constructive_roles["planner"],
                memory_keys=[record.entry_id for record in planner_memory],
            ),
            TraceStep(
                role="executor",
                prompt=executor_prompt,
                response=executor_response,
                system_prompt=self.constructive_roles["executor"],
                memory_keys=[record.entry_id for record in executor_memory],
            ),
            TraceStep(
                role="critic",
                prompt=critic_prompt,
                response=critic_response,
                system_prompt=self.constructive_roles["critic"],
                memory_keys=[record.entry_id for record in critic_memory],
            ),
        ]
        final_output = self._compose_final_output(planner_response, executor_response, critic_response)
        return ConstructivePassResult(
            plan=planner_response,
            execution=executor_response,
            critique=critic_response,
            final_output=final_output,
            role_outputs={
                "planner": planner_response,
                "executor": executor_response,
                "critic": critic_response,
            },
            trace=trace,
            actions=["plan", "execute", "critique"],
        )

    async def run_anti_challenge(
        self,
        task: TaskEnvelope,
        constructive: ConstructivePassResult,
    ) -> list[tuple[AttackStrategyRecord, AntiArtifact]]:
        """Spawn anti strategies in parallel with full read access to Zero traces."""
        strategies = self._select_strategies(count=3)
        anti_context = self._build_anti_context(task, constructive)
        jobs = [self._generate_artifact(strategy, task, constructive, anti_context) for strategy in strategies]
        artifacts = await asyncio.gather(*jobs)
        return list(zip(strategies, artifacts))

    def update_strategy_bandit(
        self,
        strategy: AttackStrategyRecord,
        decision: PromotionDecision,
    ) -> None:
        """Persist bandit-style weight updates inside APM."""
        defaults = {record.strategy_id: record.weight for record in self._default_strategy_catalog()}
        weights = self.apm.load_strategy_weights(defaults)
        new_weight = weights.get(strategy.strategy_id, strategy.weight)
        new_weight += decision.regret * 0.75
        if decision.promote:
            new_weight += 0.50
        else:
            new_weight = max(0.10, new_weight - 0.20)
        weights[strategy.strategy_id] = round(new_weight, 4)
        self.apm.save_strategy_weights(weights)

    async def _generate(self, role: str, prompt: str, system_prompt: str) -> str:
        return await asyncio.to_thread(self.backend.generate_text, role, prompt, system_prompt)

    async def _generate_artifact(
        self,
        strategy: AttackStrategyRecord,
        task: TaskEnvelope,
        constructive: ConstructivePassResult,
        anti_context: str,
    ) -> AntiArtifact:
        model_cls, schema_example = self._artifact_schema(strategy.artifact_type)
        system_prompt = self.anti_role_prompts[strategy.role]
        prompt = (
            f"Objective:\n{task.objective}\n\n"
            f"Constructive output:\n{constructive.final_output}\n\n"
            f"Visible memories and trace:\n{anti_context}\n\n"
            "Return exactly one JSON object that conforms to this schema. "
            "Use only neutral promotion payloads such as constraints, tests, or curriculum seeds.\n"
            f"{schema_example}\n"
        )
        raw_output = await self._generate(strategy.role, prompt, system_prompt)
        try:
            return parse_anti_artifact(raw_output)
        except Exception:
            return self._fallback_artifact(strategy, raw_output, task, model_cls)

    def _fallback_artifact(
        self,
        strategy: AttackStrategyRecord,
        raw_output: str,
        task: TaskEnvelope,
        model_cls: type[BaseModel],
    ) -> AntiArtifact:
        summary = raw_output.strip() or f"{strategy.name} generated an empty response."
        promotion = SanitizedPromotion(
            kind="test",
            title=f"{strategy.name} fallback probe",
            content=f"Re-run task '{task.objective}' against the anti scenario: {summary[:220]}",
            tags=["fallback", strategy.strategy_id],
        )
        base_payload: dict[str, Any] = {
            "source_role": strategy.role,
            "attack_vector": strategy.name,
            "attacked_role": "executor",
            "failure_score": 0.45,
            "reproducibility": 0.55,
            "summary": summary[:500],
            "evidence": [summary[:250]],
            "promotion": promotion.model_dump(),
        }
        if model_cls is PlanTrap:
            payload = {
                **base_payload,
                "artifact_type": "plan_trap",
                "plan_delta": "Introduce a hidden branch that invalidates a core assumption.",
                "hidden_assumption": "The task context is internally consistent.",
                "expected_failure_mode": "Executor follows a brittle plan and misses the contradiction.",
            }
        elif model_cls is ToolFuzzCase:
            payload = {
                **base_payload,
                "artifact_type": "tool_fuzz_case",
                "tool_name": "simulated_tool",
                "crafted_input": {"probe": summary[:120]},
                "expected_failure_mode": "Tool boundary handling silently accepts malformed input.",
            }
        elif model_cls is MemoryInconsistencyReport:
            payload = {
                **base_payload,
                "artifact_type": "memory_inconsistency_report",
                "memory_keys": ["planner", "executor"],
                "contradiction": "Constructive steps disagree on a critical assumption.",
                "proposed_resolution": "Promote a constraint that forces the roles to reconcile assumptions.",
            }
        elif model_cls is RetrievalPoisonProbe:
            payload = {
                **base_payload,
                "artifact_type": "retrieval_poison_probe",
                "query": task.objective,
                "lure_docs": [summary[:180]],
                "why_it_misleads": "The lure reframes the objective with misleading but plausible context.",
            }
        else:
            payload = {
                **base_payload,
                "artifact_type": "counterexample_task_variant",
                "variant_task": f"Counterexample variant for: {task.objective}",
                "expected_failure_mode": "Constructive reasoning overfits to the nominal case.",
            }
        return parse_anti_artifact(payload)

    def _artifact_schema(self, artifact_type: str) -> tuple[type[BaseModel], dict[str, Any]]:
        schema_map = {
            "plan_trap": PlanTrap,
            "tool_fuzz_case": ToolFuzzCase,
            "memory_inconsistency_report": MemoryInconsistencyReport,
            "retrieval_poison_probe": RetrievalPoisonProbe,
            "counterexample_task_variant": CounterexampleTaskVariant,
        }
        model_cls = schema_map[artifact_type]
        return model_cls, model_cls.model_json_schema()

    def _select_strategies(self, *, count: int) -> list[AttackStrategyRecord]:
        defaults = self._default_strategy_catalog()
        weight_defaults = {record.strategy_id: record.weight for record in defaults}
        stored_weights = self.apm.load_strategy_weights(weight_defaults)
        strategies = []
        for record in defaults:
            strategies.append(record.model_copy(update={"weight": stored_weights.get(record.strategy_id, record.weight)}))
        return self.random.choices(strategies, weights=[record.weight for record in strategies], k=count)

    def _default_strategy_catalog(self) -> list[AttackStrategyRecord]:
        return [
            AttackStrategyRecord(
                strategy_id="plan_trap",
                name="Hidden assumption trap",
                role="anti_planner",
                artifact_type="plan_trap",
                weight=1.0,
            ),
            AttackStrategyRecord(
                strategy_id="memory_probe",
                name="Contradictory memory probe",
                role="anti_memory_probe",
                artifact_type="memory_inconsistency_report",
                weight=1.0,
            ),
            AttackStrategyRecord(
                strategy_id="tool_fuzz",
                name="Tool boundary fuzz",
                role="anti_tool_stress",
                artifact_type="tool_fuzz_case",
                weight=1.0,
            ),
            AttackStrategyRecord(
                strategy_id="retrieval_poison",
                name="Retrieval poison probe",
                role="anti_retrieval_probe",
                artifact_type="retrieval_poison_probe",
                weight=1.0,
            ),
            AttackStrategyRecord(
                strategy_id="counterexample_variant",
                name="Counterexample variant",
                role="anti_executor",
                artifact_type="counterexample_task_variant",
                weight=1.0,
            ),
        ]

    def _build_planner_prompt(
        self,
        task: TaskEnvelope,
        shared_lines: list[str],
        planner_memory: list[MemoryRecord],
    ) -> str:
        return (
            f"Task objective:\n{task.objective}\n\n"
            f"Task context:\n{chr(10).join(task.context) or 'None'}\n\n"
            f"Shared consensus:\n{chr(10).join(shared_lines) or 'None'}\n\n"
            f"Planner memory:\n{chr(10).join(record.content for record in planner_memory) or 'None'}\n\n"
            "Produce a bounded execution plan with explicit assumptions."
        )

    def _build_executor_prompt(
        self,
        task: TaskEnvelope,
        planner_response: str,
        executor_memory: list[MemoryRecord],
    ) -> str:
        return (
            f"Task objective:\n{task.objective}\n\n"
            f"Current plan:\n{planner_response}\n\n"
            f"Executor memory:\n{chr(10).join(record.content for record in executor_memory) or 'None'}\n\n"
            "Execute the plan with concise detail and note any residual uncertainty."
        )

    def _build_critic_prompt(
        self,
        task: TaskEnvelope,
        planner_response: str,
        executor_response: str,
        critic_memory: list[MemoryRecord],
    ) -> str:
        return (
            f"Task objective:\n{task.objective}\n\n"
            f"Plan:\n{planner_response}\n\n"
            f"Execution:\n{executor_response}\n\n"
            f"Critic memory:\n{chr(10).join(record.content for record in critic_memory) or 'None'}\n\n"
            "Identify contradictions, missing tests, and failure boundaries without rewriting the entire answer."
        )

    def _build_anti_context(self, task: TaskEnvelope, constructive: ConstructivePassResult) -> str:
        search_term = task.objective.split()[0] if task.objective.split() else None
        shared_context = self.scm.read(query=search_term, limit=5, reader="anti")
        role_lines: list[str] = []
        for role, memory in self.role_memories.items():
            try:
                entries = memory.read(reader_role="anti", reader_manifold="anti", limit=3)
            except PermissionError:
                entries = []
            if entries:
                role_lines.append(f"[{role}] " + " | ".join(entry.content for entry in entries))

        trace_lines = [f"{step.role}: {step.response}" for step in constructive.trace]
        return "\n".join(
            [
                "Shared consensus:",
                *(record.content for record in shared_context),
                "Role-local visibility:",
                *role_lines,
                "Constructive trace:",
                *trace_lines,
            ]
        )

    def _write_role_memory(self, role: str, task: TaskEnvelope, response: str) -> None:
        record = MemoryRecord(
            source=role,
            content=f"Task: {task.objective}\nResponse: {response}",
            metadata={"task_id": task.task_id, "memory_type": "rlm"},
        )
        self.role_memories[role].append(record, writer_role=role)

    @staticmethod
    def _compose_final_output(plan: str, execution: str, critique: str) -> str:
        return (
            "Constructive plan:\n"
            f"{plan}\n\n"
            "Execution:\n"
            f"{execution}\n\n"
            "Critic notes:\n"
            f"{critique}"
        )


async def evolve_task(task: str | TaskEnvelope, runtime: OmegaRuntime | None = None) -> EvolutionCycleResult:
    """Run one constructive baseline plus one anti challenge round."""
    runtime = runtime or OmegaRuntime()
    envelope = task if isinstance(task, TaskEnvelope) else TaskEnvelope(objective=task)

    constructive = await runtime.run_constructive_pass(envelope)
    zero_texts = [envelope.objective] + [step.response for step in constructive.trace] + [constructive.final_output]
    zero_metrics = runtime.governor.measure_trace(
        zero_texts,
        action_count=len(constructive.actions),
        memory_churn=len(constructive.trace),
    )

    attack_pairs = await runtime.run_anti_challenge(envelope, constructive)
    attack_reviews: list[AttackReview] = []
    promoted_entries: list[MemoryRecord] = []

    for strategy, artifact in attack_pairs:
        attacked_texts = zero_texts + [artifact.summary, artifact.model_dump_json()]
        decision = runtime.governor.score_attack(
            zero_metrics,
            artifact,
            attacked_texts,
            action_count=len(constructive.actions) + 1,
            memory_churn=len(constructive.trace) + len(artifact.evidence),
        )

        apm_record = MemoryRecord(
            source=strategy.role,
            content=artifact.summary,
            metadata={
                "memory_type": "apm",
                "artifact_id": artifact.artifact_id,
                "artifact_type": artifact.artifact_type,
                "promote": decision.promote,
                "reason": decision.reason,
                "regret": decision.regret,
            },
        )
        runtime.apm.append(apm_record)

        promoted_record = None
        if decision.promote and decision.promotion is not None:
            promoted_record = runtime.scm.promote(
                decision.promotion,
                source=artifact.source_role,
                writer="governor",
                metadata={
                    "artifact_id": artifact.artifact_id,
                    "artifact_type": artifact.artifact_type,
                    "regret": decision.regret,
                    "task_id": envelope.task_id,
                },
            )
            promoted_entries.append(promoted_record)

        runtime.update_strategy_bandit(strategy, decision)
        attack_reviews.append(AttackReview(artifact=artifact, decision=decision, promoted_record=promoted_record))

    final_regime = Regime.TURBULENCE if any(review.decision.metrics.regime == Regime.TURBULENCE for review in attack_reviews) else zero_metrics.regime
    return EvolutionCycleResult(
        task=envelope,
        constructive=constructive,
        zero_metrics=zero_metrics,
        final_regime=final_regime,
        attack_reviews=attack_reviews,
        promoted_entries=promoted_entries,
    )


__all__ = [
    "AntiPrivateMemory",
    "AntiArtifact",
    "AttackReview",
    "AttackStrategyRecord",
    "ConstructivePassResult",
    "CounterexampleTaskVariant",
    "EvolutionCycleResult",
    "MemoryInconsistencyReport",
    "MemoryRecord",
    "OmegaGovernor",
    "OmegaRuntime",
    "PlanTrap",
    "PhiMetrics",
    "Regime",
    "RetrievalPoisonProbe",
    "RoleLocalMemory",
    "RoleBackend",
    "RouterRoleBackend",
    "SanitizedPromotion",
    "SharedConsensusMemory",
    "TaskEnvelope",
    "ToolFuzzCase",
    "TraceStep",
    "evolve_task",
]
