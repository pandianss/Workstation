from __future__ import annotations

from functools import lru_cache

from src.core.paths import project_path


class DummyEmbedder:
    def encode(self, texts):
        return [[0.0] * 384 for _ in texts]


@lru_cache(maxsize=1)
def get_embedder():
    try:
        from sentence_transformers import SentenceTransformer

        model_path = str(project_path("src", "assets", "models", "all-MiniLM-L6-v2"))
        return SentenceTransformer(model_path)
    except Exception:
        return DummyEmbedder()
