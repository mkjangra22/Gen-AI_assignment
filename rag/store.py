from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer
from .config import settings

class VectorStore:
    def __init__(self):
        Path(settings.chroma_path).mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=settings.chroma_path)
        self.model = SentenceTransformer(settings.embedding_model)
        self.collection = self.client.get_or_create_collection(
            name=settings.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    @property
    def dimension(self) -> int:
        return self.model.get_sentence_embedding_dimension()

    def upsert(self, chunks):
        if not chunks:
            return
        embeddings = self.model.encode(
            [c.text for c in chunks],
            normalize_embeddings=True,
            show_progress_bar=False,
        ).tolist()

        self.collection.upsert(
            ids=[c.id for c in chunks],
            documents=[c.text for c in chunks],
            embeddings=embeddings,
            metadatas=[c.metadata for c in chunks],
        )

    def search(self, query: str, k: int = 5, source: str | None = None):
        q = self.model.encode([query], normalize_embeddings=True).tolist()[0]

        kwargs = {
            "query_embeddings": [q],
            "n_results": k,
        }
        if source:
            kwargs["where"] = {"source": source}

        return self.collection.query(**kwargs)

    def count(self):
        return self.collection.count()
