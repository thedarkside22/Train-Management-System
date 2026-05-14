"""
vector_store.py - Hybrid Search with NVIDIA NIM Models (Ziyad)
================================================================
Stores policy documents and retrieves them using a 3-stage pipeline:

  Stage 1: Keyword Search (BM25-style TF-IDF)
           Fast, catches exact term matches. Runs locally, no API needed.

  Stage 2: Semantic Search (NVIDIA nv-embedqa-e5-v5)
           Converts text to embeddings via NVIDIA NIM API.
           Understands meaning — "I want my money back" matches "refund policy".
           Stored in ChromaDB for fast cosine similarity search.

  Stage 3: Reranking (NVIDIA llama-3.2-nv-rerankqa-1b-v2)
           Cross-encoder reranker via NVIDIA NIM API.
           Scores each (query, document) pair for true relevance.
           Only used when many candidates come back from stages 1+2.

All NVIDIA models run on NVIDIA's servers — no local GPU needed.
Uses same NVIDIA_API_KEY from .env file.

Install:
    pip install chromadb python-dotenv requests
"""

import os
import re
import math
import time
import logging
import requests
import numpy as np
from collections import Counter
from typing import Optional

import chromadb

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from knowledge_base import DOCUMENTS

logger = logging.getLogger(__name__)

# ============================================
# CONFIG
# ============================================
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
EMBEDDING_MODEL = "nvidia/nv-embedqa-e5-v5"
EMBEDDING_URL = "https://integrate.api.nvidia.com/v1/embeddings"
RERANKER_MODEL = "nvidia/llama-3.2-nv-rerankqa-1b-v2"
RERANKER_URL = "https://ai.api.nvidia.com/v1/retrieval/nvidia/llama-3_2-nv-rerankqa-1b-v2/reranking"


# ============================================
# NVIDIA NIM API HELPERS
# ============================================

def _nvidia_embed(texts: list[str], input_type: str = "passage") -> list[list[float]]:
    """
    Call NVIDIA nv-embedqa-e5-v5 to generate embeddings.
    
    Args:
        texts: List of strings to embed
        input_type: "passage" for documents, "query" for search queries
    
    Returns:
        List of embedding vectors (each is a list of floats)
    """
    if not NVIDIA_API_KEY:
        raise ValueError("NVIDIA_API_KEY not set in .env")

    all_embeddings = []

    # NVIDIA API has a batch limit, so process in chunks of 50
    batch_size = 50
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]

        resp = requests.post(
            EMBEDDING_URL,
            headers={
                "Authorization": f"Bearer {NVIDIA_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "input": batch,
                "model": EMBEDDING_MODEL,
                "input_type": input_type,
                "encoding_format": "float",
                "truncate": "END",
            },
            timeout=30,
        )

        if resp.status_code != 200:
            error = resp.json().get("detail", resp.text)[:200]
            raise RuntimeError(f"NVIDIA Embedding API error ({resp.status_code}): {error}")

        data = resp.json()
        # Sort by index to maintain order
        sorted_data = sorted(data["data"], key=lambda x: x["index"])
        batch_embeddings = [item["embedding"] for item in sorted_data]
        all_embeddings.extend(batch_embeddings)

    return all_embeddings


def _nvidia_rerank(query: str, documents: list[dict], top_k: int = 3) -> list[dict]:
    """
    Call NVIDIA llama-3.2-nv-rerankqa-1b-v2 to rerank documents.
    
    Args:
        query: The search query
        documents: List of dicts with "content" field
        top_k: How many top results to return
    
    Returns:
        Reranked list of document dicts with "rerank_score" added
    """
    if not NVIDIA_API_KEY:
        logger.warning("No API key for reranker, skipping reranking")
        return documents[:top_k]

    # Build passages list for the API
    passages = [{"text": doc["content"][:2000]} for doc in documents]

    try:
        resp = requests.post(
            RERANKER_URL,
            headers={
                "Authorization": f"Bearer {NVIDIA_API_KEY}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            json={
                "model": RERANKER_MODEL,
                "query": {"text": query},
                "passages": passages,
            },
            timeout=30,
        )

        if resp.status_code != 200:
            error = resp.json().get("detail", resp.text)[:200]
            logger.error(f"NVIDIA Reranker API error ({resp.status_code}): {error}")
            return documents[:top_k]

        data = resp.json()
        rankings = data.get("rankings", [])

        # Attach rerank scores to documents
        for ranking in rankings:
            idx = ranking["index"]
            if idx < len(documents):
                documents[idx]["rerank_score"] = round(ranking["logit"], 4)

        # Sort by rerank score descending
        reranked = sorted(
            [d for d in documents if "rerank_score" in d],
            key=lambda x: x["rerank_score"],
            reverse=True,
        )

        logger.info(
            f"Reranked {len(documents)} candidates → top {top_k} "
            f"(best: {reranked[0]['rerank_score']:.3f}, "
            f"worst kept: {reranked[min(top_k-1, len(reranked)-1)]['rerank_score']:.3f})"
        )

        return reranked[:top_k]

    except Exception as e:
        logger.error(f"Reranker failed: {e}, returning unranked results")
        return documents[:top_k]


# ============================================
# STAGE 1: KEYWORD SEARCH (BM25-style TF-IDF)
# ============================================

class KeywordSearcher:
    """
    BM25-style keyword search. Pure Python, no API calls.
    Catches exact term matches that semantic search might miss.
    """

    def __init__(self):
        self.documents = []
        self.doc_term_freqs = []
        self.idf = {}
        self.avg_doc_len = 0

    def _tokenize(self, text: str) -> list[str]:
        text = text.lower()
        text = re.sub(r"[^\w\s]", " ", text)
        tokens = text.split()
        stop_words = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "can", "shall",
            "to", "of", "in", "for", "on", "with", "at", "by", "from",
            "as", "into", "through", "during", "before", "after", "and",
            "but", "or", "not", "no", "nor", "so", "yet", "both", "each",
            "this", "that", "these", "those", "it", "its", "i", "you",
            "he", "she", "we", "they", "me", "him", "her", "us", "them",
            "my", "your", "his", "our", "their", "what", "which", "who",
        }
        return [t for t in tokens if t not in stop_words and len(t) > 1]

    def index(self, documents: list[dict]):
        self.documents = documents
        self.doc_term_freqs = []

        for doc in documents:
            text = f"{doc['title']} {doc['content']}"
            tokens = self._tokenize(text)
            self.doc_term_freqs.append(Counter(tokens))

        n = len(documents)
        all_terms = set()
        for tf in self.doc_term_freqs:
            all_terms.update(tf.keys())

        self.idf = {}
        for term in all_terms:
            doc_count = sum(1 for tf in self.doc_term_freqs if term in tf)
            self.idf[term] = math.log((n - doc_count + 0.5) / (doc_count + 0.5) + 1)

        doc_lengths = [sum(tf.values()) for tf in self.doc_term_freqs]
        self.avg_doc_len = sum(doc_lengths) / len(doc_lengths) if doc_lengths else 1
        logger.info(f"Keyword index: {n} docs, {len(all_terms)} terms")

    def search(self, query: str, top_k: int = 10) -> list[dict]:
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        k1, b = 1.5, 0.75
        scores = []

        for i, doc in enumerate(self.documents):
            tf = self.doc_term_freqs[i]
            doc_len = sum(tf.values())
            score = 0.0

            for term in query_tokens:
                if term not in tf:
                    continue
                freq = tf[term]
                idf = self.idf.get(term, 0)
                score += idf * (freq * (k1 + 1)) / (freq + k1 * (1 - b + b * (doc_len / self.avg_doc_len)))

            if score > 0:
                scores.append({
                    "id": doc["id"], "title": doc["title"],
                    "content": doc["content"], "category": doc.get("category", ""),
                    "score": round(score, 4), "source": "keyword",
                })

        scores.sort(key=lambda x: x["score"], reverse=True)
        return scores[:top_k]


# ============================================
# STAGE 2: SEMANTIC SEARCH (NVIDIA Embeddings + ChromaDB)
# ============================================

class SemanticSearcher:
    """
    Semantic search using NVIDIA nv-embedqa-e5-v5 embeddings
    stored in ChromaDB for fast retrieval.
    """

    def __init__(self):
        self.client = chromadb.Client()
        self.collection = None
        self.documents = []

    def index(self, documents: list[dict]):
        self.documents = documents

        try:
            self.client.delete_collection("train_policies")
        except Exception:
            pass

        # Get embeddings from NVIDIA API
        logger.info(f"Generating embeddings for {len(documents)} documents via NVIDIA NIM...")
        texts = [doc["content"] for doc in documents]
        embeddings = _nvidia_embed(texts, input_type="passage")
        logger.info(f"Received {len(embeddings)} embeddings (dim={len(embeddings[0])})")

        # Store in ChromaDB
        self.collection = self.client.create_collection(
            name="train_policies",
            metadata={"hnsw:space": "cosine"},
        )

        self.collection.add(
            ids=[doc["id"] for doc in documents],
            embeddings=embeddings,
            documents=texts,
            metadatas=[{"title": doc["title"], "category": doc.get("category", "")} for doc in documents],
        )

        logger.info(f"Semantic index: {len(documents)} docs stored in ChromaDB")

    def search(self, query: str, top_k: int = 10) -> list[dict]:
        if not self.collection:
            return []

        # Embed query using NVIDIA API (note: input_type="query" for search)
        query_embedding = _nvidia_embed([query], input_type="query")

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=min(top_k, len(self.documents)),
            include=["documents", "metadatas", "distances"],
        )

        output = []
        for i in range(len(results["ids"][0])):
            distance = results["distances"][0][i]
            similarity = 1 - distance

            output.append({
                "id": results["ids"][0][i],
                "title": results["metadatas"][0][i]["title"],
                "content": results["documents"][0][i],
                "category": results["metadatas"][0][i].get("category", ""),
                "score": round(similarity, 4),
                "source": "semantic",
            })

        return output


# ============================================
# MAIN PIPELINE: PolicyStore
# ============================================

class PolicyStore:
    """
    Complete hybrid retrieval pipeline:
      1. Keyword search (BM25) → exact term matches
      2. Semantic search (NVIDIA embeddings) → meaning-based matches
      3. Merge & deduplicate → combine results
      4. Rerank (NVIDIA reranker) → pick best when many candidates

    Usage:
        store = PolicyStore()
        results = store.search("How do I cancel a ticket?")
        context = store.build_context(results)
    """

    def __init__(self, rerank_threshold: int = 5):
        self.keyword_searcher = KeywordSearcher()
        self.semantic_searcher = SemanticSearcher()
        self.rerank_threshold = rerank_threshold
        self.is_indexed = False
        self._index_all()

    def _index_all(self):
        logger.info(f"Indexing {len(DOCUMENTS)} policy documents...")

        # Keyword index always works (no API needed)
        self.keyword_searcher.index(DOCUMENTS)

        # Semantic index needs NVIDIA API
        if NVIDIA_API_KEY:
            try:
                self.semantic_searcher.index(DOCUMENTS)
            except Exception as e:
                logger.error(f"Semantic indexing failed: {e}. Will use keyword-only search.")
        else:
            logger.warning("NVIDIA_API_KEY not set. Semantic search disabled, using keyword-only.")

        self.is_indexed = True
        logger.info("Indexing complete")

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        if not self.is_indexed:
            self._index_all()

        # Stage 1: Keyword search (always works)
        keyword_results = self.keyword_searcher.search(query, top_k=5)

        # Stage 2: Semantic search (if API available)
        semantic_results = []
        if self.semantic_searcher.collection:
            try:
                semantic_results = self.semantic_searcher.search(query, top_k=5)
            except Exception as e:
                logger.error(f"Semantic search failed: {e}")

        # Stage 3: Merge and deduplicate
        seen_ids = set()
        merged = []

        for r in keyword_results:
            if r["id"] not in seen_ids:
                seen_ids.add(r["id"])
                merged.append(r)

        for r in semantic_results:
            if r["id"] not in seen_ids:
                seen_ids.add(r["id"])
                merged.append(r)

        logger.info(
            f"Search '{query[:50]}' → "
            f"keyword: {len(keyword_results)}, semantic: {len(semantic_results)}, "
            f"merged: {len(merged)}"
        )

        # Stage 4: Rerank with NVIDIA API (if many candidates)
        if len(merged) > self.rerank_threshold and NVIDIA_API_KEY:
            logger.info(f"Reranking {len(merged)} candidates with NVIDIA NIM...")
            merged = _nvidia_rerank(query, merged, top_k=top_k)
        else:
            merged = merged[:top_k]

        return merged

    def build_context(self, results: list[dict], max_chars: int = 3000) -> str:
        if not results:
            return ""

        context_parts = []
        total_chars = 0

        for r in results:
            entry = f"[{r['title']}]:\n{r['content']}"
            if total_chars + len(entry) > max_chars:
                remaining = max_chars - total_chars
                if remaining > 100:
                    entry = entry[:remaining] + "..."
                    context_parts.append(entry)
                break
            context_parts.append(entry)
            total_chars += len(entry)

        return "\n\n".join(context_parts)

    def get_stats(self) -> dict:
        return {
            "total_documents": len(DOCUMENTS),
            "keyword_terms": len(self.keyword_searcher.idf),
            "semantic_enabled": self.semantic_searcher.collection is not None,
            "reranker_enabled": bool(NVIDIA_API_KEY),
            "embedding_model": EMBEDDING_MODEL,
            "reranker_model": RERANKER_MODEL,
            "is_indexed": self.is_indexed,
            "rerank_threshold": self.rerank_threshold,
        }


# ============================================
# GLOBAL INSTANCE
# ============================================

policy_store = PolicyStore()