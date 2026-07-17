from agents.base_agent import BaseAgent
from config.prompts import Prompts
from rag.retriever import Retriever


class RAGAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.retriever = Retriever()

    def run(self, query: str, context: str = "", **kwargs) -> str:
        has_coordinator_context = context and context.strip() and context.strip() != "No relevant documents found."

        if has_coordinator_context:
            document_context = context
            citations = self.retriever.get_citations(query) if self.retriever.is_available else []
        else:
            if not self.retriever.is_available:
                return "No documents have been uploaded yet. Please upload PDF, DOCX, or PPTX files first."

            results = self.retriever.search(query)
            if not results:
                return "No relevant information found in the uploaded documents for your query."

            context_parts = []
            for i, r in enumerate(results, 1):
                context_parts.append(
                    f"Excerpt {i} (Relevance: {r.score:.2f}):\n{r.text}\n{r.citation}"
                )
            document_context = "\n\n".join(context_parts)
            citations = [r.citation for r in results]

        prompt = f"""Based on the following document excerpts, answer the user's question.

DOCUMENT EXCERPTS:
{document_context}

USER QUESTION: {query}

Instructions:
1. Provide a clear, direct answer
2. Cite specific sources using [Source: filename, Page X] format
3. If the documents don't contain enough information, say so
4. Be concise but thorough"""

        response = self.llm.generate(
            prompt=prompt,
            system_prompt=Prompts.RAG_AGENT,
        )

        if citations:
            return response + "\n\n**Citations:**\n" + "\n".join(set(citations))
        return response
