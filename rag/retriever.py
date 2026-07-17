from dataclasses import dataclass

from rag.vector_store import VectorStore
from config.settings import Settings


@dataclass
class RetrievalResult:
    text: str
    source: str
    page: int
    score: float
    citation: str


class Retriever:
    def __init__(self):
        self.vector_store = VectorStore()

    def search(self, query: str, top_k: int = None) -> list[RetrievalResult]:
        top_k = top_k or Settings.TOP_K_RESULTS
        raw_results = self.vector_store.search(query, top_k)
        results = []
        for chunk, distance in raw_results:
            score = 1.0 / (1.0 + distance)
            citation = f"[Source: {chunk.source}, Page {chunk.page}]"
            results.append(
                RetrievalResult(
                    text=chunk.text,
                    source=chunk.source,
                    page=chunk.page,
                    score=score,
                    citation=citation,
                )
            )
        return results

    def get_context(self, query: str, top_k: int = None) -> str:
        results = self.search(query, top_k)
        if not results:
            return "No relevant documents found."
        context_parts = []
        for i, r in enumerate(results, 1):
            context_parts.append(
                f"--- Document Excerpt {i} (Score: {r.score:.2f}, Source: {r.source}, Page {r.page}) ---\n"
                f"{r.text}\n"
            )
        return "\n".join(context_parts)

    def get_citations(self, query: str, top_k: int = None) -> list[str]:
        results = self.search(query, top_k)
        return list(set(r.citation for r in results))

    @property
    def is_available(self) -> bool:
        return self.vector_store.is_loaded
