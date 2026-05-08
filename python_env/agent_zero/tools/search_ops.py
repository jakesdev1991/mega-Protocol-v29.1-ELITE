# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""Search tools and adapters for Agent Zero."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import httpx

from rcod.leakage_gate import ZScoreLeakageGate

from .registry import tool_link


@dataclass(frozen=True)
class SearchResult:
    """Normalized search result emitted by the SearXNG adapter."""

    title: str
    url: str
    content: str
    leakage_score: float
    leakage_z_score: float

    def render(self) -> str:
        """Render a compact text block compatible with existing callers."""
        return (
            f"Title: {self.title}\n"
            f"URL: {self.url}\n"
            f"Content: {self.content}\n"
            f"Leakage: score={self.leakage_score:.4f}, z={self.leakage_z_score:.4f}\n"
        )


class SearxngSearchAdapter:
    """HTTP adapter that normalizes SearXNG responses and applies leakage gating."""

    def __init__(
        self,
        base_url: str | None = None,
        *,
        timeout: float = 30.0,
        max_results: int = 5,
        leakage_gate: ZScoreLeakageGate | None = None,
    ):
        self.base_url = (base_url or os.getenv("SEARXNG_URL") or "http://127.0.0.1:8888").rstrip("/")
        self.timeout = timeout
        self.max_results = max(1, int(max_results))
        self.leakage_gate = leakage_gate or ZScoreLeakageGate()

    def search(self, query: str, categories: str = "general") -> list[SearchResult]:
        """Run a SearXNG query and return gated, normalized results."""
        params = {"q": query, "categories": categories, "format": "json"}
        with httpx.Client() as client:
            response = client.get(f"{self.base_url}/search", params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

        raw_results = data.get("results", [])
        snippets = [self._candidate_text(result) for result in raw_results]
        decisions = self.leakage_gate.filter_texts(query, snippets)

        normalized: list[SearchResult] = []
        for raw_result, (_, decision) in zip(raw_results, decisions):
            if not decision.allowed:
                continue
            normalized.append(
                SearchResult(
                    title=str(raw_result.get("title") or ""),
                    url=str(raw_result.get("url") or ""),
                    content=str(raw_result.get("content") or ""),
                    leakage_score=decision.score,
                    leakage_z_score=decision.z_score,
                )
            )
            if len(normalized) >= self.max_results:
                break
        return normalized

    @staticmethod
    def _candidate_text(result: dict[str, Any]) -> str:
        return "\n".join(str(result.get(key) or "") for key in ("title", "url", "content"))


@tool_link
def searxng_search(query: str, categories: str = "general"):
    """
    Performs a search using the local SearXNG instance.
    'categories' can be general, science, news, etc.
    """
    try:
        results = SearxngSearchAdapter().search(query=query, categories=categories)
        if not results:
            return "No results found."
        return "\n---\n".join(result.render() for result in results)
    except httpx.HTTPStatusError as exc:
        return f"Error: SearXNG returned status code {exc.response.status_code}"
    except Exception as e:
        return f"Error connecting to SearXNG: {str(e)}"
