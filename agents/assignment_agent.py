from agents.base_agent import BaseAgent
from config.prompts import Prompts


class AssignmentAgent(BaseAgent):
    def run(self, query: str, context: str = "", topic: str = "", **kwargs) -> str:
        assignment_type = kwargs.get("assignment_type", "theory")
        num_questions = kwargs.get("num_questions", 5)
        effective_topic = topic if topic and topic.lower() not in query.lower() else query

        if context and context.strip() and context.strip() != "No relevant documents found.":
            prompt = f"""You are an assignment generator for Lovely Professional University (LPU).

CRITICAL INSTRUCTION: You MUST create assignments based on the course material provided below.
Questions should test understanding of concepts covered in the documents.
Reference specific topics and content from the material.

===== COURSE MATERIAL FROM UPLOADED DOCUMENTS =====
{context}
===== END COURSE MATERIAL =====

Create an assignment based on the ABOVE course material.

Assignment Requirements:
- Topic: {effective_topic}
- Type: {assignment_type}
- Number of Questions: {num_questions}

Generate with:
1. Questions testing concepts from the course material
2. Clear instructions
3. Marks allocation
4. Evaluation criteria/rubric at the end
5. Reference to which part of the material each question covers

Types:
- theory: Research/essay questions
- lab: Lab exercises with coding
- coding: Coding problems with test cases
- viva: Viva voce questions
- project: Mini project
- mixed: Mix of all types"""
        else:
            prompt = f"""You are an assignment generator for LPU.
No course documents available. Generate general assignments for: {effective_topic}"""
        response = self.llm.generate(
            prompt=prompt,
            system_prompt=Prompts.ASSIGNMENT_AGENT,
            temperature=0.4,
        )
        return response
