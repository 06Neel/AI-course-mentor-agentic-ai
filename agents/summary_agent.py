from agents.base_agent import BaseAgent
from config.prompts import Prompts


class SummaryAgent(BaseAgent):
    def run(self, query: str, context: str = "", topic: str = "", **kwargs) -> str:
        summary_type = kwargs.get("summary_type", "chapter")
        effective_topic = topic if topic and topic.lower() not in query.lower() else query

        if context and context.strip() and context.strip() != "No relevant documents found.":
            prompt = f"""You are a lecture summarizer for Lovely Professional University (LPU).

CRITICAL INSTRUCTION: You MUST summarize the EXACT content provided below.
Do NOT add information that is not in the source material.
Your summary must faithfully represent what is in the documents.

===== CONTENT TO SUMMARIZE =====
{context}
===== END CONTENT =====

Generate a {summary_type} summary of the ABOVE content for the topic: {effective_topic}

Summary format requirements:
1. Clear structure with headings matching the source material
2. Key points extracted directly from the content
3. Important terms and definitions as they appear in the material
4. Study-friendly format

Summary Types:
- chapter: Comprehensive chapter summary
- revision: Bullet-point revision notes
- flashcards: Q&A format flashcards
- key_points: Numbered list of essential points
- one_page: One-page compact notes"""
        else:
            prompt = f"""You are a lecture summarizer for LPU.
No source material available. Generate a general {summary_type} summary for: {effective_topic}"""
        response = self.llm.generate(
            prompt=prompt,
            system_prompt=Prompts.SUMMARY_AGENT,
            temperature=0.3,
        )
        return response
