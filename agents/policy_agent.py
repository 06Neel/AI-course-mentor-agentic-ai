from agents.base_agent import BaseAgent
from config.prompts import Prompts
from rag.retriever import Retriever


class PolicyAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.retriever = Retriever()

    def run(self, query: str, context: str = "", **kwargs) -> str:
        if not self.retriever.is_available:
            return (
                "No university policy documents have been uploaded yet. "
                "Please upload LPU policy documents (PDF) to get accurate policy information. "
                "I can only answer policy questions based on official uploaded documents."
            )

        document_context = self.retriever.get_context(query, top_k=8)

        prompt = f"""Answer this policy question based ONLY on the provided university documents.

POLICY QUESTION: {query}

UNIVERSITY DOCUMENT CONTEXT:
{document_context}

STRICT RULES:
1. ONLY use information from the provided context
2. NEVER make up or guess policy information
3. ALWAYS cite the source document and page number using [Source: X, Page Y] format
4. If the information is not in the context, respond with: "I cannot find this specific policy in the uploaded documents. Please contact the LPU administration for accurate information."
5. Be precise and factual
6. Include any relevant deadlines or thresholds mentioned"""

        response = self.llm.generate(
            prompt=prompt,
            system_prompt=Prompts.POLICY_AGENT,
        )
        return response
