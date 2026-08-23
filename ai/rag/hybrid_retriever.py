"""
2. Hybrid Search & Embeddings
Dense Search (Векторный поиск по эмбеддингам) + Sparse Search (BM25 по ключевым терминам SMM).
Объединение выдачи через Reciprocal Rank Fusion (RRF).
"""

import math
import re
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
from rag.models import Chunk, RetrievalResult

class LocalDenseStore:
    """
    Локальное векторное хранилище с вычислением косинусного сходства.
    Поддерживает подключение SentenceTransformers / BGE моделей с быстрым in-memory fallback.
    """
    def __init__(self, embedding_dim: int = 384):
        self.embedding_dim = embedding_dim
        self.chunks: List[Chunk] = []
        self.embeddings: List[List[float]] = []
        self.model = None
        
        # Попытка инициализации локальной sentence-transformers модели
        try:
            from sentence_transformers import SentenceTransformer
            # Используем легкую мультиязычную модель или bge
            self.model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
            print("[LocalDenseStore] 🟢 SentenceTransformer успешно загружен.")
        except Exception as e:
            print(f"[LocalDenseStore] ℹ️ SentenceTransformer не загружен ({e}). Используется локальный TF-IDF / Hashing Vectorizer.")

    def _encode_text(self, text: str) -> List[float]:
        """Генерирует вектор для текста."""
        if self.model is not None:
            try:
                emb = self.model.encode(text, normalize_embeddings=True)
                return emb.tolist()
            except Exception:
                pass
                
        # Детерминированный fallback хеш-векторизатор (L2-нормализованный)
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
        """Добавляет чанки в векторный индекс."""
        for chunk in chunks:
            self.chunks.append(chunk)
            emb = self._encode_text(chunk.text)
            self.embeddings.append(emb)

    def search(self, query: str, top_k: int = 10) -> List[Tuple[Chunk, float]]:
        """Dense-поиск по косинусному сходству."""
        if not self.chunks:
            return []
            
        q_emb = self._encode_text(query)
        scored: List[Tuple[Chunk, float]] = []
        
        for chunk, emb in zip(self.chunks, self.embeddings):
            # Скалярное произведение для L2-нормализованных векторов = cosine similarity
            sim = sum(q * e for q, e in zip(q_emb, emb))
            scored.append((chunk, float(sim)))
            
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]


class BM25SparseRetriever:
    """
    Лексический поиск BM25 для точного нахождения редких SMM-терминов,
    названий компаний (@user), цен, адресов и промокодов.
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
        """Индексирует чанки для BM25."""
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

    def search(self, query: str, top_k: int = 10) -> List[Tuple[Chunk, float]]:
        """BM25 поиск по запросу."""
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
                
            # IDF формулировка Робертсона-Спарка Джонса
            idf = math.log(1.0 + (self.corpus_size - df + 0.5) / (df + 0.5))
            
            for i, term_counts in enumerate(self.doc_term_counts):
                tf = term_counts.get(token, 0)
                if tf == 0:
                    continue
                doc_len = self.doc_lengths[i]
                numerator = tf * (self.k1 + 1.0)
                denominator = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / (self.avg_doc_length or 1.0)))
                scores[i] += idf * (numerator / denominator)
                
        # Нормализация скоров в диапазон [0, 1]
        max_score = max(scores) if scores and max(scores) > 0 else 1.0
        results = [(self.chunks[i], scores[i] / max_score) for i in range(self.corpus_size) if scores[i] > 0]
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]


class HybridRetriever:
    """
    Гибридный поисковый движок:
    Объединяет Dense (Векторный) и Sparse (BM25) результаты через Reciprocal Rank Fusion (RRF).
    """
    def __init__(self, rrf_k: int = 60, dense_weight: float = 0.6, sparse_weight: float = 0.4):
        self.dense_store = LocalDenseStore()
        self.sparse_retriever = BM25SparseRetriever()
        self.rrf_k = rrf_k
        self.dense_weight = dense_weight
        self.sparse_weight = sparse_weight

    def index_chunks(self, chunks: List[Chunk]):
        """Одновременная индексация чанков в оба хранилища."""
        self.dense_store.add_chunks(chunks)
        self.sparse_retriever.add_chunks(chunks)

    def hybrid_search(self, query: str, top_k: int = 5) -> List[RetrievalResult]:
        """
        Выполняет параллельный поиск в Dense и Sparse, объединяя скоры через RRF.
        """
        dense_results = self.dense_store.search(query, top_k=top_k * 2)
        sparse_results = self.sparse_retriever.search(query, top_k=top_k * 2)
        
        # Словарь для агрегации результатов
        chunk_map: Dict[str, Chunk] = {}
        dense_scores: Dict[str, float] = {}
        sparse_scores: Dict[str, float] = {}
        rrf_scores: Dict[str, float] = {}
        
        # Обработка Dense результатов
        for rank, (chunk, score) in enumerate(dense_results):
            cid = chunk.chunk_id
            chunk_map[cid] = chunk
            dense_scores[cid] = score
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + self.dense_weight * (1.0 / (self.rrf_k + rank + 1))
            
        # Обработка Sparse результатов
        for rank, (chunk, score) in enumerate(sparse_results):
            cid = chunk.chunk_id
            chunk_map[cid] = chunk
            sparse_scores[cid] = score
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + self.sparse_weight * (1.0 / (self.rrf_k + rank + 1))
            
        # Формирование RetrievalResult
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
            
        # Сортировка по гибридному RRF скору
        combined.sort(key=lambda x: x.hybrid_score, reverse=True)
        return combined[:top_k]
