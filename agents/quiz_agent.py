from agents.base_agent import BaseAgent
from config.prompts import Prompts


class QuizAgent(BaseAgent):
    def run(self, query: str, context: str = "", topic: str = "", **kwargs) -> str:
        quiz_type = kwargs.get("quiz_type", "mcq")
        count = kwargs.get("count", 10)
        difficulty = kwargs.get("difficulty", "medium")
        effective_topic = topic if topic and topic.lower() not in query.lower() else query

        if context and context.strip() and context.strip() != "No relevant documents found.":
            prompt = f"""You are a quiz generator for Lovely Professional University (LPU).

CRITICAL INSTRUCTION: You MUST generate quiz questions PRIMARILY from the course material provided below.
Every question should test understanding of concepts found in the documents.
Do NOT generate questions from topics not covered in the material.

===== COURSE MATERIAL FROM UPLOADED DOCUMENTS =====
{context}
===== END COURSE MATERIAL =====

Generate a quiz based on the ABOVE course material.

Quiz Requirements:
- Topic: {effective_topic}
- Type: {quiz_type}
- Number of Questions: {count}
- Difficulty: {difficulty}

Generate the quiz with:
1. Questions directly testing concepts from the course material above
2. Clear numbering
3. All answers with brief explanations
4. References to which part of the material each question covers

Quiz Types:
- mcq: Multiple Choice (4 options A-D)
- true_false: True/False
- fill_blank: Fill in the blanks
- scenario: Scenario-based
- blooms: Bloom's Taxonomy (specify level)
- co_based: Course Outcome-based
- mixed: Mix of all types"""
        else:
            prompt = f"""You are a quiz generator for LPU courses.
No course documents available. Generate general quiz questions.

Quiz Requirements:
- Topic: {effective_topic}
- Type: {quiz_type}
- Count: {count}
- Difficulty: {difficulty}"""
        response = self.llm.generate(
            prompt=prompt,
            system_prompt=Prompts.QUIZ_AGENT,
            temperature=0.4,
        )
        return response
