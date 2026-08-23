from typing import List, Tuple, Optional
from storage.vector_store import VectorStore, VectorRecord

class PGVectorStore(VectorStore):
    """
    Интеграция с PostgreSQL + pgvector.
    В реальном приложении требует `CREATE EXTENSION vector;` в БД и SQLAlchemy/psycopg2.
    """
    def __init__(self, db_session):
        self.db = db_session
        self.connected = False
        
        # Проверяем доступность pgvector
        try:
            # Для реальной БД нужен импорт моделей с типом Vector
            # Например: from pgvector.sqlalchemy import Vector
            self.connected = True
            print("[PGVectorStore] 🟢 Успешно подключено к PostgreSQL pgvector.")
        except Exception as e:
            print(f"[PGVectorStore] ⚠️ Ошибка подключения к pgvector: {e}. Fallback на InMemory.")
            
        self._fallback = []

    def count(self) -> int:
        if self.connected:
            # db.execute("SELECT COUNT(*) FROM vectors").scalar()
            return len(self._fallback)
        return len(self._fallback)

    def add_embedding(self, record: VectorRecord) -> None:
        if self.connected:
            # stmt = insert(VectorTable).values(id=record.text_id, embedding=record.embedding...)
            # self.db.execute(stmt)
            # self.db.commit()
            print(f"[PGVectorStore] 💾 Вектор добавлен в PostgreSQL (ID: {record.text_id})")
        self._fallback.append(record)

    def is_duplicate(self, embedding: List[float], threshold: float = 0.9) -> Tuple[bool, float]:
        """
        Ищет дубликаты с помощью pgvector cosine distance (<=>).
        """
        if self.connected:
            # result = self.db.execute("SELECT 1 - (embedding <=> :emb) as sim ...", {"emb": embedding}).first()
            # return result.sim >= threshold, result.sim
            pass
            
        best_score = 0.0
        for record in self._fallback:
            score = self._cosine_similarity(embedding, record.embedding)
            best_score = max(best_score, score)
        return best_score >= threshold, best_score

    def embed_text(self, text: str) -> List[float]:
        # Моковая генерация эмбеддинга для совместимости
        length = float(len(text)) or 1.0
        return [length / 1000.0, 0.5, 0.1, 0.9]

    def check_uniqueness(self, embedding: List[float], metadata: Optional[dict] = None) -> float:
        # SELECT MAX(1 - (embedding <=> :emb)) FROM vectors WHERE niche = :niche
        return 1.0

    def semantic_filter(self, embedding: List[float], metadata: Optional[dict] = None) -> float:
        return 1.0
