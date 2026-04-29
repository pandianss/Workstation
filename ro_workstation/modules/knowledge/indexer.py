import os
import hashlib
import chromadb
from ..utils.paths import project_path

MODEL_PATH = str(project_path("assets", "models", "all-MiniLM-L6-v2"))

def get_chroma_client():
    chroma_path = project_path("data", "chroma_db")
    chroma_path.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(chroma_path))

def index_document(file_path: str, text_chunks: list[str], metadata: dict):
    client = get_chroma_client()
    collection = client.get_or_create_collection(name="bank_knowledge")
    
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(MODEL_PATH)
        embeddings = model.encode(text_chunks).tolist()
    except Exception:
        # Fallback for dummy embedder if model not downloaded
        from ..llm.embeddings import get_embedder
        model = get_embedder()
        embeddings = model.encode(text_chunks)
        if hasattr(embeddings, 'tolist'):
            embeddings = embeddings.tolist()
            
    source_name = os.path.basename(file_path)
    ids = [
        hashlib.md5(f"{source_name}:{i}:{chunk}".encode("utf-8")).hexdigest()
        for i, chunk in enumerate(text_chunks)
    ]
    metadatas = [
        {
            **metadata,
            "source_file": source_name,
            "chunk_index": i,
        }
        for i in range(len(text_chunks))
    ]

    if hasattr(collection, "upsert"):
        collection.upsert(
            embeddings=embeddings,
            documents=text_chunks,
            metadatas=metadatas,
            ids=ids
        )
    else:
        collection.add(
            embeddings=embeddings,
            documents=text_chunks,
            metadatas=metadatas,
            ids=ids
        )
