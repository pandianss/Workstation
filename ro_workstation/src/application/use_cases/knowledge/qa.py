from __future__ import annotations

from src.infrastructure.llm.client import LLMClient

from .search import KnowledgeSearchService


class KnowledgeQaService:
    def __init__(self) -> None:
        self.search_service = KnowledgeSearchService()
        self.llm = LLMClient()

    def answer_question(self, query: str, dept_filter: str | None = None) -> dict:
        chunks = self.search_service.search(query, n_results=5, dept_filter=dept_filter)
        if not chunks:
            filter_note = f" for department {dept_filter}" if dept_filter and dept_filter != "ALL" else ""
            answer = self.llm.generate(
                f"Question: {query}",
                f"You are an AI Research Assistant. No specific documents are available in the database yet{filter_note}.",
            )
            return {"answer": answer, "sources": []}

        context = "\n\n".join([f"Source [{idx + 1}]: {chunk['content']}" for idx, chunk in enumerate(chunks)])
        prompt = (
            f"Context:\n{context}\n\nQuestion: {query}\n\n"
            "Answer using only the context provided. Cite sources using [1], [2], etc."
        )
        answer = self.llm.generate(prompt, "You are a helpful AI Research Assistant. Always cite your sources.")
        return {"answer": answer, "sources": [chunk["metadata"] for chunk in chunks]}
