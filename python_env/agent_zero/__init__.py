# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""Agent Zero: Multi-Agent Self-Evolution & Design-First Framework"""

from .agent import Agent
from .framework import (
    AntiPrivateMemory,
    AttackReview,
    AttackStrategyRecord,
    ConstructivePassResult,
    CounterexampleTaskVariant,
    EvolutionCycleResult,
    MemoryInconsistencyReport,
    MemoryRecord,
    OmegaGovernor,
    OmegaRuntime,
    PlanTrap,
    PhiMetrics,
    Regime,
    RetrievalPoisonProbe,
    RoleLocalMemory,
    RouterRoleBackend,
    SanitizedPromotion,
    SharedConsensusMemory,
    TaskEnvelope,
    ToolFuzzCase,
    TraceStep,
    evolve_task,
)
from .serc import SERC

__all__ = [
    "Agent",
    "AntiPrivateMemory",
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
    "RouterRoleBackend",
    "SERC",
    "SanitizedPromotion",
    "SharedConsensusMemory",
    "TaskEnvelope",
    "ToolFuzzCase",
    "TraceStep",
    "evolve_task",
]
