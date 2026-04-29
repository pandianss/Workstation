from .indexer import get_chroma_client

def hybrid_search(query: str, n_results: int = 5, dept_filter: str | None = None):
    client = get_chroma_client()
    try:
        collection = client.get_collection(name="bank_knowledge")
    except Exception:
        return [] # Collection does not exist
        
    try:
        from sentence_transformers import SentenceTransformer
        from ..utils.paths import project_path
        MODEL_PATH = str(project_path("assets", "models", "all-MiniLM-L6-v2"))
        model = SentenceTransformer(MODEL_PATH)
        query_embedding = model.encode([query]).tolist()
    except Exception:
        from ..llm.embeddings import get_embedder
        model = get_embedder()
        query_embedding = model.encode([query])
        if hasattr(query_embedding, 'tolist'):
            query_embedding = query_embedding.tolist()

    query_kwargs = {
        "query_embeddings": query_embedding,
        "n_results": n_results,
    }
    if dept_filter and dept_filter != "ALL":
        query_kwargs["where"] = {"department": dept_filter}

    results = collection.query(**query_kwargs)
    
    formatted_results = []
    if results and 'documents' in results and len(results['documents']) > 0:
        docs = results['documents'][0]
        metas = results['metadatas'][0]
        for doc, meta in zip(docs, metas):
            formatted_results.append({
                "content": doc,
                "metadata": meta
            })
    return formatted_results
