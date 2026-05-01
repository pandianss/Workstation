from __future__ import annotations

from src.infrastructure.llm.client import LLMClient

from .search import KnowledgeSearchService


SYSTEM_PROMPT = (
    "You are an AI Research Assistant for an Indian Public Sector Bank "
    "Regional Office. You answer questions strictly using the document context "
    "provided. Follow these rules exactly:\n"
    "1. Respond in formal Indian banking English.\n"
    "2. Cite every factual claim inline with its source number: [1], [2], etc.\n"
    "3. If the context does not contain enough information, respond exactly:\n"
    "   'The indexed documents do not contain sufficient information on this "
    "topic. Please refer to the relevant HO circular or RBI Master Direction.'\n"
    "4. Never speculate, infer, or add information beyond what the sources state.\n"
    "5. Structure your response as:\n"
    "   ANSWER: <response with inline citations>\n"
    "   SOURCES USED: <comma-separated list of source numbers cited>\n"
    "6. Keep answers under 300 words unless the question explicitly requests "
    "a detailed note or summary."
)

class KnowledgeQaService:
    def __init__(self) -> None:
        self.search_service = KnowledgeSearchService()
        self.llm = LLMClient()

    def answer_question(self, query: str, dept_filter: str | None = None) -> dict:
        chunks = self.search_service.search(query, n_results=5, dept_filter=dept_filter)
        if not chunks:
            filter_note = (
                f" for department '{dept_filter}'" if dept_filter and dept_filter != "ALL" else ""
            )
            fallback_system = (
                f"You are an AI Research Assistant. No indexed documents are available{filter_note}. "
                "Politely state this and suggest the user upload and index relevant documents."
            )
            answer = self.llm.generate(f"Question: {query}", fallback_system)
            return {"answer": answer, "sources": []}

        context = "\n\n".join(
            [f"[{idx + 1}] {chunk['content']}" for idx, chunk in enumerate(chunks)]
        )
        prompt = (
            f"Document Context:\n{context}\n\n"
            f"Question: {query}\n\n"
            "Provide a precise, well-cited answer following all rules above."
        )
        answer = self.llm.generate(prompt, SYSTEM_PROMPT)
        return {"answer": answer, "sources": [chunk["metadata"] for chunk in chunks]}
