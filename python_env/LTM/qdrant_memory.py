# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
import sys
import json
import logging
import numpy as np
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from sentence_transformers import SentenceTransformer, CrossEncoder

# Ensure project root and python_env are in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from configs.config import config
from utils.logger import logger

class QdrantMemorySystem:
    def __init__(self):
        self.client = QdrantClient(path=str(config.qdrant_path))
        self.collection_name = "omega_memories"
        self.embedding_model_name = config.ltm_embedding
        self.reranker_model_name = config.reranker_model
        
        logger.info(f"Initializing Qdrant Memory System with {self.embedding_model_name}")
        self.embedding_model = SentenceTransformer(self.embedding_model_name, trust_remote_code=True)
        self.embedding_dim = 1024 # Based on our check
        
        logger.info(f"Loading Reranker: {self.reranker_model_name}")
        # Note: CrossEncoder might need trust_remote_code for Qwen3 if it's dynamic
        self.reranker = CrossEncoder(self.reranker_model_name, trust_remote_code=True)
        
        self._ensure_collection()

    def _ensure_collection(self):
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)
        
        if not exists:
            logger.info(f"Creating Qdrant collection: {self.collection_name}")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=rest.VectorParams(
                    size=self.embedding_dim,
                    distance=rest.Distance.COSINE
                )
            )

    def add_memory(self, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Embeds and stores a memory in Qdrant."""
        try:
            vector = self.embedding_model.encode([content], task="retrieval")[0].tolist()
            
            # Generate a point ID (can be incremental or UUID)
            # For simplicity, we'll let Qdrant handle IDs if possible or use a hash
            import uuid
            point_id = str(uuid.uuid4())
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    rest.PointStruct(
                        id=point_id,
                        vector=vector,
                        payload={
                            "content": content,
                            "metadata": metadata or {},
                            "created_at": str(np.datetime64('now'))
                        }
                    )
                ]
            )
            logger.info(f"✅ Memory stored in Qdrant: {content[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Error storing memory in Qdrant: {e}")
            return False

    def search(self, query: str, limit: int = 10, rerank: bool = True) -> List[Dict[str, Any]]:
        """Searches memories and optionally reranks them."""
        try:
            query_vector = self.embedding_model.encode([query], task="retrieval")[0].tolist()
            
            search_result = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=limit * 2 if rerank else limit,
                with_payload=True
            ).points
            
            results = [
                {
                    "content": hit.payload["content"],
                    "metadata": hit.payload["metadata"],
                    "score": hit.score
                }
                for hit in search_result
            ]
            
            if rerank and results:
                logger.info(f"Reranking {len(results)} results with {self.reranker_model_name}")
                pairs = [[query, r["content"]] for r in results]
                rerank_scores = self.reranker.predict(pairs)
                
                for i, score in enumerate(rerank_scores):
                    results[i]["rerank_score"] = float(score)
                
                # Sort by rerank score
                results.sort(key=lambda x: x["rerank_score"], reverse=True)
                results = results[:limit]
                
            return results
        except Exception as e:
            logger.error(f"Error searching memories in Qdrant: {e}")
            return []

if __name__ == "__main__":
    qms = QdrantMemorySystem()
    qms.add_memory("The fusion reactor core is stable at 150M degrees.", {"branch": "tokamak"})
    qms.add_memory("Market analysis suggests a 5% growth in GPU demand.", {"branch": "business"})
    
    print("Searching for 'fusion'...")
    res = qms.search("fusion")
    for r in res:
        print(f"Score: {r.get('rerank_score', r['score']):.4f} | Content: {r['content']}")
