# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""Milvus search adapter with leakage-gate rescoring.

This adapter mirrors the Qdrant memory search contract while keeping Milvus as
an optional runtime dependency.  It expects Milvus rows to expose ``content``,
``metadata``, and vector distance/similarity fields, then enriches candidates
with reranker and leakage-gate scores.
"""

from __future__ import annotations

import importlib
import os
import sys
from typing import Any, Dict, List, Optional

# Ensure project root and python_env are in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from configs.config import config
from LTM.leakage_gate import GLOBAL_LEAKAGE_GATE, ZScoreLeakageGate
from sentence_transformers import CrossEncoder, SentenceTransformer
from utils.logger import logger


class MilvusMemorySearchAdapter:
    """Milvus-backed memory search with reranker and leakage-gate rescoring."""

    def __init__(
        self,
        uri: Optional[str] = None,
        collection_name: str = "omega_memories",
        leakage_gate: Optional[ZScoreLeakageGate] = None,
    ):
        pymilvus = importlib.import_module("pymilvus")
        self.client = pymilvus.MilvusClient(uri=uri or str(getattr(config, "milvus_uri", "./milvus.db")))
        self.collection_name = collection_name
        self.embedding_model_name = config.ltm_embedding
        self.reranker_model_name = config.reranker_model
        self.leakage_gate = leakage_gate or GLOBAL_LEAKAGE_GATE

        logger.info(f"Initializing Milvus Memory Search Adapter with {self.embedding_model_name}")
        self.embedding_model = SentenceTransformer(self.embedding_model_name, trust_remote_code=True)
        logger.info(f"Loading Reranker: {self.reranker_model_name}")
        self.reranker = CrossEncoder(self.reranker_model_name, trust_remote_code=True)

    def search_memory(
        self,
        query: str,
        limit: int = 10,
        rerank: bool = True,
        current_state: float = 0.35,
        filter_disallowed: bool = False,
    ) -> List[Dict[str, Any]]:
        """Search Milvus and rescore candidates through ``ZScoreLeakageGate``."""

        try:
            query_vector = self.embedding_model.encode([query], task="retrieval")[0].tolist()
            rows = self.client.search(
                collection_name=self.collection_name,
                data=[query_vector],
                limit=limit * 2 if rerank else limit,
                output_fields=["content", "metadata", "stiffness_s", "reverse_overlap_r", "dissonance_delta"],
            )
            hits = rows[0] if rows else []
            results = [self._hit_to_result(hit) for hit in hits]

            if rerank and results:
                logger.info(f"Reranking {len(results)} Milvus results with {self.reranker_model_name}")
                pairs = [[query, result["content"]] for result in results]
                rerank_scores = self.reranker.predict(pairs)
                for index, score in enumerate(rerank_scores):
                    results[index]["rerank_score"] = float(score)
                    results[index]["reranker_score"] = float(score)

            results = self.leakage_gate.rescore_results(
                results,
                current_state=current_state,
                filter_disallowed=filter_disallowed,
            )
            return results[:limit]
        except Exception as e:
            logger.error(f"Error searching memories in Milvus: {e}")
            return []

    def _hit_to_result(self, hit: Any) -> Dict[str, Any]:
        entity = self._entity(hit)
        distance = self._field(hit, "distance", self._field(hit, "score", 0.0))
        vector_similarity = self._field(hit, "score", distance)
        metadata = entity.get("metadata") or {}
        result = {
            "content": entity.get("content", ""),
            "metadata": metadata,
            "score": vector_similarity,
            "vector_similarity": vector_similarity,
        }
        for key in ("stiffness_s", "reverse_overlap_r", "dissonance_delta"):
            if key in entity:
                result[key] = entity[key]
            elif key in metadata:
                result[key] = metadata[key]
        return result

    def _entity(self, hit: Any) -> Dict[str, Any]:
        if isinstance(hit, dict):
            return hit.get("entity") or hit
        entity = getattr(hit, "entity", None)
        if isinstance(entity, dict):
            return entity
        return {}

    def _field(self, hit: Any, field: str, default: float) -> float:
        if isinstance(hit, dict):
            return float(hit.get(field, default) or default)
        return float(getattr(hit, field, default) or default)
