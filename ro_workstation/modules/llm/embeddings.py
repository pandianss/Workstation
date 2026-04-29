import streamlit as st
from ..utils.paths import project_path

class DummyEmbedder:
    def encode(self, texts):
        return [[0.0]*384 for _ in texts]

@st.cache_resource
def get_embedder():
    try:
        from sentence_transformers import SentenceTransformer
        MODEL_PATH = str(project_path("assets", "models", "all-MiniLM-L6-v2"))
        return SentenceTransformer(MODEL_PATH)
    except Exception as e:
        # Provide a dummy embedder if the model isn't downloaded yet or module is missing
        return DummyEmbedder()
