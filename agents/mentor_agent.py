from agents.base_agent import BaseAgent
from config.prompts import Prompts


class MentorAgent(BaseAgent):
    def run(self, query: str, context: str = "", topic: str = "", **kwargs) -> str:
        topic_line = f"\nTOPIC: {topic}" if topic and topic.lower() not in query.lower() else ""

        if context and context.strip() and context.strip() != "No relevant documents found.":
            prompt = f"""You are a course mentor at Lovely Professional University (LPU).

CRITICAL INSTRUCTION: You MUST base your answer PRIMARILY on the course material provided below.
If the documents contain relevant information, use it as the foundation of your answer.
You may add brief supplementary explanations, but the core content MUST come from the documents.

===== COURSE MATERIAL FROM UPLOADED DOCUMENTS =====
{context}
===== END COURSE MATERIAL =====
{topic_line}
STUDENT QUESTION: {query}

Now provide a clear, detailed explanation. When you reference concepts, point to the specific document sections above. Use examples from the course material where available."""
        else:
            prompt = f"""You are a course mentor at Lovely Professional University (LPU).
No course documents are currently available for this topic.
Provide a general educational explanation based on your knowledge.
{topic_line}
STUDENT QUESTION: {query}

Provide a clear, educational explanation with examples."""

        response = self.llm.generate(
            prompt=prompt,
            system_prompt=Prompts.MENTOR_AGENT,
            temperature=0.3,
        )
        return response
