# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""Omega tensor normalization for long-term memory payloads.

The tensor converts mixed retrieval content and source metadata into a compact,
source-neutral signal.  Stored memories retain the original ``content`` while
``normalized_content`` removes leading source/domain labels so retrieval and
promotion logic can reason over the claim itself rather than its provenance.
"""

from __future__ import annotations

import math
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class OmegaTensorPayload:
    """Normalized tensor fields stored alongside a memory payload."""

    stiffness_s: float
    reverse_overlap_r: float
    dissonance_delta: float
    domain_signature: str | None
    source_kind: str | None
    normalized_content: str


_LABEL_PATTERNS = (
    re.compile(
        r"^\s*(?:source|domain|site|origin|provider|corpus|kind|source_kind)\s*[:=]\s*[^\n|>]+(?:\||>|\n)+",
        re.I,
    ),
    re.compile(r"^\s*\[[^\]]*(?:source|domain|site|origin|provider|corpus|kind)[^\]]*\]\s*", re.I),
    re.compile(r"^\s*(?:from|via)\s+(?:https?://)?[\w.-]+\S*\s*[:\-–—]\s*", re.I),
    re.compile(r"^\s*(?:https?://)?(?:www\.)?[\w.-]+\.[a-z]{2,}(?:/\S*)?\s*[:\-–—]\s*", re.I),
)

_CONTRADICTION_MARKERS = (
    "contradiction",
    "contradicts",
    "conflict",
    "conflicting",
    "disputed",
    "refuted",
    "inconsistent",
    "unverified",
    "false",
)

_VERIFIED_VALUES = {"verified", "validated", "confirmed", "true", "yes", "pass", "passed", "approved"}
_REJECTED_VALUES = {"rejected", "refuted", "false", "no", "fail", "failed", "disputed", "unverified"}


def normalize_to_omega_tensor(content: str, metadata: dict | None = None) -> dict[str, Any]:
    """Normalize retrieval text and derive omega tensor metadata.

    Heuristics intentionally use only common metadata keys so callers can pass
    sparse payloads.  ``S`` rises with confidence, verification, recency, and
    reuse.  ``R`` captures residual source-label pressure/reverse overlap after
    labels are removed.  ``delta`` rises when text or metadata carries
    contradiction, dispute, or failed-verification markers.
    """

    safe_metadata = metadata or {}
    normalized_content, removed_label_count = _strip_source_labels(content)
    domain_signature = _first_string(
        safe_metadata,
        "domain_signature",
        "domain",
        "source_domain",
        "site",
        "provider",
        "source",
        "url",
    )
    source_kind = _first_string(safe_metadata, "source_kind", "kind", "source_type", "type", "corpus")

    confidence = _coerce_unit_interval(
        _first_number(safe_metadata, "confidence", "score", "trust", "trust_score"),
        0.5,
    )
    recency = _recency_signal(safe_metadata)
    access_signal = _access_signal(safe_metadata)
    verification_signal = _verification_signal(safe_metadata)
    contradiction_signal = _contradiction_signal(content, safe_metadata)
    source_pressure = _source_pressure(content, normalized_content, safe_metadata, removed_label_count)

    stiffness_s = _round_unit(
        (0.42 * confidence)
        + (0.22 * recency)
        + (0.16 * access_signal)
        + (0.20 * verification_signal)
        - (0.30 * contradiction_signal)
    )
    reverse_overlap_r = _round_unit(
        (0.65 * source_pressure) + (0.20 * (1.0 - confidence)) + (0.15 * contradiction_signal)
    )
    dissonance_delta = _round_unit(
        (0.70 * contradiction_signal) + (0.20 * (1.0 - verification_signal)) + (0.10 * reverse_overlap_r)
    )

    tensor = OmegaTensorPayload(
        stiffness_s=stiffness_s,
        reverse_overlap_r=reverse_overlap_r,
        dissonance_delta=dissonance_delta,
        domain_signature=domain_signature,
        source_kind=source_kind,
        normalized_content=normalized_content,
    )
    return asdict(tensor)


def _strip_source_labels(content: str) -> tuple[str, int]:
    normalized = str(content or "").strip()
    removed = 0
    changed = True
    while changed:
        changed = False
        for pattern in _LABEL_PATTERNS:
            updated, count = pattern.subn("", normalized, count=1)
            if count:
                normalized = updated.strip()
                removed += count
                changed = True
                break
    return re.sub(r"\n{3,}", "\n\n", normalized).strip(), removed


def _first_string(metadata: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = metadata.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return None


def _first_number(metadata: dict[str, Any], *keys: str) -> float | None:
    for key in keys:
        value = metadata.get(key)
        if value is None or isinstance(value, bool):
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return None


def _coerce_unit_interval(value: float | None, default: float) -> float:
    if value is None or math.isnan(value) or math.isinf(value):
        return default
    if value > 1.0 and value <= 100.0:
        value = value / 100.0
    return min(1.0, max(0.0, value))


def _recency_signal(metadata: dict[str, Any]) -> float:
    explicit_age = _first_number(metadata, "age_days", "days_old", "recency_days")
    if explicit_age is not None:
        return _age_to_recency(explicit_age)

    timestamp = _first_string(metadata, "created_at", "updated_at", "timestamp", "source_timestamp", "date")
    if not timestamp:
        return 0.5
    parsed = _parse_datetime(timestamp)
    if parsed is None:
        return 0.5
    age_days = max(0.0, (datetime.now(timezone.utc) - parsed).total_seconds() / 86400.0)
    return _age_to_recency(age_days)


def _age_to_recency(age_days: float) -> float:
    return min(1.0, max(0.0, math.exp(-max(0.0, age_days) / 90.0)))


def _parse_datetime(value: str) -> datetime | None:
    text = value.strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _access_signal(metadata: dict[str, Any]) -> float:
    access_count = _first_number(metadata, "access_count", "hits", "read_count", "retrieval_count", "usage_count")
    if access_count is None:
        return 0.0
    return min(1.0, math.log1p(max(0.0, access_count)) / math.log1p(20.0))


def _verification_signal(metadata: dict[str, Any]) -> float:
    verified = metadata.get("verified", metadata.get("verification_status", metadata.get("status")))
    if isinstance(verified, bool):
        return 1.0 if verified else 0.0
    if verified is None:
        return 0.5
    status = str(verified).strip().lower()
    if status in _VERIFIED_VALUES:
        return 1.0
    if status in _REJECTED_VALUES:
        return 0.0
    return 0.5


def _contradiction_signal(content: str, metadata: dict[str, Any]) -> float:
    explicit = _first_number(metadata, "contradiction_score", "dissonance_delta", "delta", "conflict_score")
    if explicit is not None:
        return _coerce_unit_interval(explicit, 0.0)

    marker_hits = 0
    haystack = f"{content}\n{metadata}".lower()
    for marker in _CONTRADICTION_MARKERS:
        if marker in haystack:
            marker_hits += 1
    if bool(metadata.get("contradiction")) or bool(metadata.get("contradicted")):
        marker_hits += 1
    return min(1.0, marker_hits / 3.0)


def _source_pressure(content: str, normalized_content: str, metadata: dict[str, Any], removed_label_count: int) -> float:
    explicit = _first_number(metadata, "reverse_overlap_r", "reverse_overlap", "source_overlap", "domain_overlap")
    if explicit is not None:
        return _coerce_unit_interval(explicit, 0.0)

    original_len = max(1, len(content.strip()))
    removed_ratio = max(0.0, original_len - len(normalized_content)) / original_len
    metadata_pressure = (
        0.15
        if _first_string(metadata, "domain", "source_domain", "site", "provider", "source", "url")
        else 0.0
    )
    label_pressure = min(0.5, removed_label_count * 0.18)
    return min(1.0, removed_ratio + metadata_pressure + label_pressure)


def _round_unit(value: float) -> float:
    return round(min(1.0, max(0.0, value)), 6)
