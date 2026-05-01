from __future__ import annotations

from src.core.paths import project_path
from src.infrastructure.llm.embeddings import get_embedder


class KnowledgeSearchService:
    def __init__(self) -> None:
        self.client = self._create_client()

    @staticmethod
    def _create_client():
        try:
            import chromadb

            return chromadb.PersistentClient(path=str(project_path("data", "chroma_db")))
        except Exception:
            class _FallbackClient:
                def get_collection(self, name):
                    raise RuntimeError("Knowledge store unavailable")

            return _FallbackClient()

    def search(self, query: str, n_results: int = 5, dept_filter: str | None = None) -> list[dict]:
        try:
            collection = self.client.get_collection(name="bank_knowledge")
        except Exception:
            return []

        embedder = get_embedder()
        embeddings = embedder.encode([query])
        if hasattr(embeddings, "tolist"):
            embeddings = embeddings.tolist()

        kwargs = {"query_embeddings": embeddings, "n_results": n_results}
        if dept_filter and dept_filter != "ALL":
            kwargs["where"] = {"department": dept_filter}
        results = collection.query(**kwargs)

        payload = []
        documents = results.get("documents", [[]])[0] if results else []
        metadatas = results.get("metadatas", [[]])[0] if results else []
        for document, metadata in zip(documents, metadatas):
            payload.append({"content": document, "metadata": metadata})
        return payload
