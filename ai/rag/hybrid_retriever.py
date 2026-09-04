"""
2. Hybrid Search & Embeddings with Multi-Tenant Partitioning
Dense Search (Векторный поиск по эмбеддингам) + Sparse Search (BM25 по ключевым терминам SMM).
Объединение выдачи через Reciprocal Rank Fusion (RRF) с жесткой изоляцией по tenant_id.
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import math
import re
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
from rag.models import Chunk, RetrievalResult

class LocalDenseStore:
    """
    Локальное векторное хранилище с вычислением косинусного сходства
    и мульти-тенантной фильтрацией по tenant_id.
    """
    def __init__(self, embedding_dim: int = 384):
        self.embedding_dim = embedding_dim
        self.chunks: List[Chunk] = []
        self.embeddings: List[List[float]] = []
        self.model = None
        
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2", local_files_only=True)
        except Exception:
            self.model = None

    def _encode_text(self, text: str) -> List[float]:
        if self.model is not None:
            try:
                emb = self.model.encode(text, normalize_embeddings=True)
                return emb.tolist()
            except Exception:
                pass
                
        vec = [0.0] * self.embedding_dim
        tokens = re.findall(r'\w+', text.lower())
        if not tokens:
            return vec
            
        for token in tokens:
            idx = abs(hash(token)) % self.embedding_dim
            vec[idx] += 1.0
            
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec

    def add_chunks(self, chunks: List[Chunk]):
        for chunk in chunks:
            self.chunks.append(chunk)
            emb = self._encode_text(chunk.text)
            self.embeddings.append(emb)

    def search(self, query: str, top_k: int = 10, tenant_id: Optional[str] = None) -> List[Tuple[Chunk, float]]:
        if not self.chunks:
            return []
            
        q_emb = self._encode_text(query)
        scored: List[Tuple[Chunk, float]] = []
        
        for chunk, emb in zip(self.chunks, self.embeddings):
            if tenant_id:
                c_tenant = chunk.metadata.get("tenant_id") or chunk.metadata.get("company_name", "").lower().replace(" ", "_")
                if c_tenant and c_tenant.strip().lower() != tenant_id.strip().lower():
                    continue
            sim = sum(q * e for q, e in zip(q_emb, emb))
            scored.append((chunk, float(sim)))
            
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]


class BM25SparseRetriever:
    """
    Лексический поиск BM25 для точного нахождения редких SMM-терминов
    с поддержкой фильтрации по tenant_id.
    """
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.chunks: List[Chunk] = []
        self.doc_lengths: List[int] = []
        self.avg_doc_length: float = 0.0
        self.doc_freqs: Dict[str, int] = Counter()
        self.corpus_size: int = 0
        self.doc_term_counts: List[Dict[str, int]] = []

    def _tokenize(self, text: str) -> List[str]:
        return [t for t in re.findall(r'[a-zA-Zа-яА-Я0-9_@]+', text.lower()) if len(t) > 1]

    def add_chunks(self, chunks: List[Chunk]):
        for chunk in chunks:
            self.chunks.append(chunk)
            tokens = self._tokenize(chunk.text)
            term_count = Counter(tokens)
            self.doc_term_counts.append(term_count)
            self.doc_lengths.append(len(tokens))
            
            for term in term_count.keys():
                self.doc_freqs[term] += 1
                
        self.corpus_size = len(self.chunks)
        self.avg_doc_length = sum(self.doc_lengths) / self.corpus_size if self.corpus_size > 0 else 0.0

    def search(self, query: str, top_k: int = 10, tenant_id: Optional[str] = None) -> List[Tuple[Chunk, float]]:
        if not self.chunks:
            return []
            
        q_tokens = self._tokenize(query)
        if not q_tokens:
            return []
            
        scores: List[float] = [0.0] * self.corpus_size
        
        for token in q_tokens:
            df = self.doc_freqs.get(token, 0)
            if df == 0:
                continue
                
            idf = math.log(1.0 + (self.corpus_size - df + 0.5) / (df + 0.5))
            
            for i, term_counts in enumerate(self.doc_term_counts):
                chunk = self.chunks[i]
                if tenant_id:
                    c_tenant = chunk.metadata.get("tenant_id") or chunk.metadata.get("company_name", "").lower().replace(" ", "_")
                    if c_tenant and c_tenant.strip().lower() != tenant_id.strip().lower():
                        continue
                        
                tf = term_counts.get(token, 0)
                if tf == 0:
                    continue
                doc_len = self.doc_lengths[i]
                numerator = tf * (self.k1 + 1.0)
                denominator = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / (self.avg_doc_length or 1.0)))
                scores[i] += idf * (numerator / denominator)
                
        max_score = max(scores) if scores and max(scores) > 0 else 1.0
        results = [(self.chunks[i], scores[i] / max_score) for i in range(self.corpus_size) if scores[i] > 0]
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]


class HybridRetriever:
    """
    Гибридный поисковый движок с поддержкой Multi-Tenant изоляции:
    Объединяет Dense (Векторный) и Sparse (BM25) результаты через Reciprocal Rank Fusion (RRF).
    """
    def __init__(self, rrf_k: int = 60, dense_weight: float = 0.6, sparse_weight: float = 0.4):
        self.dense_store = LocalDenseStore()
        self.sparse_retriever = BM25SparseRetriever()
        self.rrf_k = rrf_k
        self.dense_weight = dense_weight
        self.sparse_weight = sparse_weight

    def index_chunks(self, chunks: List[Chunk]):
        self.dense_store.add_chunks(chunks)
        self.sparse_retriever.add_chunks(chunks)

    def hybrid_search(self, query: str, top_k: int = 5, tenant_id: Optional[str] = None) -> List[RetrievalResult]:
        dense_results = self.dense_store.search(query, top_k=top_k * 2, tenant_id=tenant_id)
        sparse_results = self.sparse_retriever.search(query, top_k=top_k * 2, tenant_id=tenant_id)
        
        chunk_map: Dict[str, Chunk] = {}
        dense_scores: Dict[str, float] = {}
        sparse_scores: Dict[str, float] = {}
        rrf_scores: Dict[str, float] = {}
        
        for rank, (chunk, score) in enumerate(dense_results):
            cid = chunk.chunk_id
            chunk_map[cid] = chunk
            dense_scores[cid] = score
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + self.dense_weight * (1.0 / (self.rrf_k + rank + 1))
            
        for rank, (chunk, score) in enumerate(sparse_results):
            cid = chunk.chunk_id
            chunk_map[cid] = chunk
            sparse_scores[cid] = score
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + self.sparse_weight * (1.0 / (self.rrf_k + rank + 1))
            
        combined: List[RetrievalResult] = []
        for cid, chunk in chunk_map.items():
            combined.append(
                RetrievalResult(
                    chunk=chunk,
                    dense_score=dense_scores.get(cid, 0.0),
                    sparse_score=sparse_scores.get(cid, 0.0),
                    hybrid_score=rrf_scores.get(cid, 0.0)
                )
            )
            
        combined.sort(key=lambda x: x.hybrid_score, reverse=True)
        return combined[:top_k]
