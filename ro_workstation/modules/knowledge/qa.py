from .search import hybrid_search
from ..llm.client import LLMClient

def answer_question(query: str, dept_filter: str = None) -> dict:
    chunks = hybrid_search(query, n_results=5, dept_filter=dept_filter)
    
    if not chunks:
        llm = LLMClient()
        filter_note = f" for department {dept_filter}" if dept_filter and dept_filter != "ALL" else ""
        ans = llm.generate(
            f"Question: {query}",
            f"You are an AI Research Assistant. No specific documents are available in the database yet{filter_note}."
        )
        return {"answer": ans, "sources": []}
        
    context_str = "\n\n".join([f"Source [{i+1}]: {c['content']}" for i, c in enumerate(chunks)])
    
    llm = LLMClient()
    prompt = f"Context:\n{context_str}\n\nQuestion: {query}\n\nAnswer using only the context provided. Cite sources using [1], [2], etc."
    system_prompt = "You are a helpful AI Research Assistant. Always cite your sources."
    answer = llm.generate(prompt, system_prompt)
    
    return {
        "answer": answer,
        "sources": [c['metadata'] for c in chunks]
    }
