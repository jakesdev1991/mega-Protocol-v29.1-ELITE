# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""Milvus-backed long-term memory adapter.

The adapter keeps pymilvus and sentence-transformers optional at import time so
filesystem-only MCP deployments can start even when vector DB dependencies are
not installed. Milvus support is activated when a tool calls this class.
"""
from __future__ import annotations

import importlib
import importlib.util
import json
import os
import sys
from typing import Any, Dict, List, Optional

# Ensure project root and python_env are in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from configs.config import config
from utils.logger import logger


class MilvusMemorySystem:
    """Small wrapper for Milvus collection setup, inserts, and search."""

    def __init__(self):
        self.collection_name = config.milvus_collection
        self.embedding_model_name = config.ltm_embedding
        self.embedding_dim = config.milvus_dense_dim
        self.text_max_length = config.milvus_text_max_length
        self.client = self._connect()
        self.embedding_model = None
        self._ensure_collection()

    @staticmethod
    def available() -> bool:
        """Return True when pymilvus is installed in the active environment."""
        return importlib.util.find_spec("pymilvus") is not None

    def _pymilvus(self):
        if not self.available():
            raise RuntimeError("pymilvus is not installed; install pymilvus or pymilvus[milvus_lite].")
        return importlib.import_module("pymilvus")

    def _connect(self):
        pymilvus = self._pymilvus()
        client_kwargs = {"uri": config.milvus_uri, "db_name": config.milvus_db_name}
        if config.milvus_token:
            client_kwargs["token"] = config.milvus_token
        logger.info("Connecting to Milvus at %s", config.milvus_uri)
        return pymilvus.MilvusClient(**client_kwargs)

    def _ensure_collection(self) -> None:
        if self.client.has_collection(self.collection_name):
            return

        logger.info("Creating Milvus collection: %s", self.collection_name)
        pymilvus = self._pymilvus()
        if hasattr(self.client, "create_schema") and hasattr(self.client, "prepare_index_params"):
            schema = self.client.create_schema(auto_id=False, enable_dynamic_field=True)
            schema.add_field(field_name="id", datatype=pymilvus.DataType.VARCHAR, is_primary=True, max_length=128)
            schema.add_field(field_name="content", datatype=pymilvus.DataType.VARCHAR, max_length=self.text_max_length)
            schema.add_field(field_name="metadata", datatype=pymilvus.DataType.JSON)
            schema.add_field(field_name="dense_vector", datatype=pymilvus.DataType.FLOAT_VECTOR, dim=self.embedding_dim)
            index_params = self.client.prepare_index_params()
            index_params.add_index(
                field_name="dense_vector",
                index_type="AUTOINDEX",
                metric_type="COSINE",
            )
            self.client.create_collection(
                collection_name=self.collection_name,
                schema=schema,
                index_params=index_params,
            )
            return

        self.client.create_collection(
            collection_name=self.collection_name,
            dimension=self.embedding_dim,
            primary_field_name="id",
            vector_field_name="dense_vector",
            metric_type="COSINE",
            auto_id=False,
        )

    def _load_embedding_model(self):
        if self.embedding_model is not None:
            return self.embedding_model
        if importlib.util.find_spec("sentence_transformers") is None:
            raise RuntimeError("sentence-transformers is required to embed Milvus records without vectors.")
        module = importlib.import_module("sentence_transformers")
        self.embedding_model = module.SentenceTransformer(self.embedding_model_name, trust_remote_code=True)
        return self.embedding_model

    def _embed(self, texts: List[str]) -> List[List[float]]:
        model = self._load_embedding_model()
        return [vector.tolist() for vector in model.encode(texts, task="retrieval")]

    @staticmethod
    def _content_from_record(record: Dict[str, Any]) -> str:
        content = record.get("content", record.get("text", ""))
        if not isinstance(content, str) or not content.strip():
            raise ValueError("Each Milvus record must include non-empty 'content' or 'text'.")
        return content

    @staticmethod
    def _metadata_from_record(record: Dict[str, Any]) -> Dict[str, Any]:
        metadata = record.get("metadata") or {}
        if not isinstance(metadata, dict):
            raise ValueError("Milvus record 'metadata' must be a dictionary when provided.")
        return metadata

    @staticmethod
    def _metadata_matches(metadata: Dict[str, Any], filters: Optional[Dict[str, Any]]) -> bool:
        if not filters:
            return True
        return all(metadata.get(key) == value for key, value in filters.items())

    def bulk_insert(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Insert records with schema: id, content/text, metadata, optional dense_vector."""
        if not records:
            return {"inserted": 0, "ids": []}

        import uuid

        contents = [self._content_from_record(record) for record in records]
        vectors_by_index: Dict[int, List[float]] = {}
        missing_vector_indexes: List[int] = []
        for index, record in enumerate(records):
            vector = record.get("dense_vector", record.get("vector"))
            if vector is None:
                missing_vector_indexes.append(index)
            else:
                vectors_by_index[index] = [float(value) for value in vector]

        if missing_vector_indexes:
            embedded = self._embed([contents[index] for index in missing_vector_indexes])
            for index, vector in zip(missing_vector_indexes, embedded):
                vectors_by_index[index] = vector

        rows = []
        ids = []
        for index, record in enumerate(records):
            metadata = self._metadata_from_record(record)
            row_id = str(record.get("id") or uuid.uuid4())
            ids.append(row_id)
            rows.append(
                {
                    "id": row_id,
                    "content": contents[index][: self.text_max_length],
                    "metadata": metadata,
                    "dense_vector": vectors_by_index[index],
                }
            )

        result = self.client.insert(collection_name=self.collection_name, data=rows)
        self.client.flush(collection_name=self.collection_name)
        return {"inserted": len(rows), "ids": ids, "result": result}

    def dense_search(self, query: str, limit: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        query_vector = self._embed([query])[0]
        raw_results = self.client.search(
            collection_name=self.collection_name,
            data=[query_vector],
            anns_field="dense_vector",
            limit=max(limit * 3 if filters else limit, limit),
            output_fields=["content", "metadata"],
        )
        hits = raw_results[0] if raw_results else []
        results: List[Dict[str, Any]] = []
        for hit in hits:
            entity = hit.get("entity", {}) if isinstance(hit, dict) else getattr(hit, "entity", {})
            metadata_raw = entity.get("metadata", "{}") if isinstance(entity, dict) else "{}"
            metadata = json.loads(metadata_raw) if isinstance(metadata_raw, str) else metadata_raw
            if not self._metadata_matches(metadata, filters):
                continue
            results.append(
                {
                    "id": hit.get("id") if isinstance(hit, dict) else getattr(hit, "id", None),
                    "content": entity.get("content") if isinstance(entity, dict) else None,
                    "metadata": metadata,
                    "score": hit.get("distance") if isinstance(hit, dict) else getattr(hit, "distance", None),
                    "search_type": "dense",
                }
            )
            if len(results) >= limit:
                break
        return results

    def hybrid_search(self, query: str, limit: int = 10, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run hybrid/BM25 search when the installed Milvus client exposes it.

        The default collection created by this adapter is dense-vector-first for
        broad Milvus compatibility. If a deployment upgrades the collection with
        sparse/BM25 fields, expose that capability here; otherwise fall back to
        dense search and report the fallback explicitly.
        """
        supports_hybrid = hasattr(self.client, "hybrid_search")
        if not supports_hybrid:
            return {
                "mode": "dense_fallback",
                "hybrid_supported": False,
                "results": self.dense_search(query=query, limit=limit, filters=filters),
            }

        # The high-level client has version-specific hybrid signatures. Avoid
        # guessing schema-specific sparse fields unless the user configured them.
        sparse_field = os.getenv("OMEGA_MILVUS_SPARSE_FIELD")
        if not sparse_field:
            return {
                "mode": "dense_fallback",
                "hybrid_supported": True,
                "reason": "Set OMEGA_MILVUS_SPARSE_FIELD for BM25/sparse hybrid search.",
                "results": self.dense_search(query=query, limit=limit, filters=filters),
            }

        return {
            "mode": "dense_fallback",
            "hybrid_supported": True,
            "reason": "Sparse/BM25 field is configured, but query-time sparse embedding is deployment-specific.",
            "results": self.dense_search(query=query, limit=limit, filters=filters),
        }

    def health(self) -> Dict[str, Any]:
        return {
            "available": True,
            "uri": config.milvus_uri,
            "collection": self.collection_name,
            "collection_exists": self.client.has_collection(self.collection_name),
            "hybrid_supported": hasattr(self.client, "hybrid_search"),
        }
