# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""Typed models for the Agent Zero dual-manifold runtime."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Annotated, Any, Literal, Union
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


class SanitizedPromotion(BaseModel):
    """Neutral artifact distilled by the governor for SCM promotion."""

    model_config = ConfigDict(extra="forbid")

    kind: Literal["constraint", "test", "curriculum"]
    title: str = Field(min_length=3, max_length=140)
    content: str = Field(min_length=8)
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class MemoryRecord(BaseModel):
    """Generic memory record used by SCM, RLM, and APM."""

    model_config = ConfigDict(extra="forbid")

    entry_id: str = Field(default_factory=lambda: str(uuid4()))
    source: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)


class TaskEnvelope(BaseModel):
    """Structured task input for the v2 runtime."""

    model_config = ConfigDict(extra="forbid")

    task_id: str = Field(default_factory=lambda: str(uuid4()))
    objective: str = Field(min_length=3)
    context: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TraceStep(BaseModel):
    """A single constructive trace step produced during a cycle."""

    model_config = ConfigDict(extra="forbid")

    role: str
    prompt: str
    response: str
    system_prompt: str
    memory_keys: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)


class ConstructivePassResult(BaseModel):
    """Outputs and trace emitted by the constructive manifold."""

    model_config = ConfigDict(extra="forbid")

    plan: str
    execution: str
    critique: str
    final_output: str
    role_outputs: dict[str, str]
    trace: list[TraceStep]
    actions: list[str] = Field(default_factory=list)


class AttackStrategyRecord(BaseModel):
    """Bandit-style Anti-Agency strategy state."""

    model_config = ConfigDict(extra="forbid")

    strategy_id: str
    name: str
    role: str
    artifact_type: str
    weight: float = Field(default=1.0, ge=0.05)
    times_selected: int = Field(default=0, ge=0)
    successes: int = Field(default=0, ge=0)
    last_regret: float = Field(default=0.0, ge=0.0)


class AntiArtifactBase(BaseModel):
    """Shared fields required for all Anti-Agency outputs."""

    model_config = ConfigDict(extra="forbid")

    artifact_id: str = Field(default_factory=lambda: str(uuid4()))
    artifact_type: str
    source_role: str
    attack_vector: str = Field(min_length=3)
    attacked_role: str | None = None
    failure_score: float = Field(ge=0.0, le=1.0)
    reproducibility: float = Field(ge=0.0, le=1.0)
    summary: str = Field(min_length=10)
    evidence: list[str] = Field(default_factory=list)
    promotion: SanitizedPromotion | None = None


class CounterexampleTaskVariant(AntiArtifactBase):
    artifact_type: Literal["counterexample_task_variant"] = "counterexample_task_variant"
    variant_task: str = Field(min_length=6)
    expected_failure_mode: str = Field(min_length=6)


class ToolFuzzCase(AntiArtifactBase):
    artifact_type: Literal["tool_fuzz_case"] = "tool_fuzz_case"
    tool_name: str = Field(min_length=2)
    crafted_input: dict[str, Any] | str
    expected_failure_mode: str = Field(min_length=6)


class MemoryInconsistencyReport(AntiArtifactBase):
    artifact_type: Literal["memory_inconsistency_report"] = "memory_inconsistency_report"
    memory_keys: list[str] = Field(min_length=1)
    contradiction: str = Field(min_length=8)
    proposed_resolution: str = Field(min_length=8)


class PlanTrap(AntiArtifactBase):
    artifact_type: Literal["plan_trap"] = "plan_trap"
    plan_delta: str = Field(min_length=6)
    hidden_assumption: str = Field(min_length=6)
    expected_failure_mode: str = Field(min_length=6)


class RetrievalPoisonProbe(AntiArtifactBase):
    artifact_type: Literal["retrieval_poison_probe"] = "retrieval_poison_probe"
    query: str = Field(min_length=3)
    lure_docs: list[str] = Field(min_length=1)
    why_it_misleads: str = Field(min_length=8)


AntiArtifact = Annotated[
    Union[
        CounterexampleTaskVariant,
        ToolFuzzCase,
        MemoryInconsistencyReport,
        PlanTrap,
        RetrievalPoisonProbe,
    ],
    Field(discriminator="artifact_type"),
]

ANTI_ARTIFACT_ADAPTER = TypeAdapter(AntiArtifact)


def extract_json_object(raw_text: str) -> dict[str, Any]:
    """Extract the first JSON object from a model response."""
    raw_text = raw_text.strip()
    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError:
        start = raw_text.find("{")
        end = raw_text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("Response does not contain a JSON object.")
        payload = json.loads(raw_text[start : end + 1])
    if not isinstance(payload, dict):
        raise ValueError("JSON payload must decode to an object.")
    return payload


def parse_anti_artifact(raw_payload: str | dict[str, Any]) -> AntiArtifact:
    """Parse a typed Anti-Agency artifact from raw model output."""
    payload = extract_json_object(raw_payload) if isinstance(raw_payload, str) else raw_payload
    return ANTI_ARTIFACT_ADAPTER.validate_python(payload)
