from agents.base_agent import BaseAgent
from config.prompts import Prompts


class FacultyAgent(BaseAgent):
    def run(self, query: str, context: str = "", topic: str = "", **kwargs) -> str:
        task_type = kwargs.get("task_type", "lesson_plan")
        effective_topic = topic if topic and topic.lower() not in query.lower() else query

        if context and context.strip() and context.strip() != "No relevant documents found.":
            prompt = f"""You are a faculty assistant for Lovely Professional University (LPU).

CRITICAL INSTRUCTION: You MUST base the generated material on the course content provided below.
Align all outputs with the topics, concepts, and learning outcomes found in the documents.

===== COURSE MATERIAL FROM UPLOADED DOCUMENTS =====
{context}
===== END COURSE MATERIAL =====

Help a faculty member with the following task based on the ABOVE course material:

Task Type: {task_type}
Request: {effective_topic}

Generate with:
1. Content aligned with the course material above
2. Professional academic formatting
3. Clear structure and sections
4. Learning outcomes based on document content
5. Assessment criteria tied to course topics

Types:
- lesson_plan: Detailed lesson plan with timeline
- question_paper: Exam paper with marks distribution
- mcq_set: MCQ paper with answer key
- lab_manual: Lab manual with experiments
- co_mapping: Course Outcome to Bloom's Taxonomy mapping
- feedback_form: Student feedback form
- email: Professional email draft
- rubric: Evaluation rubric"""
        else:
            prompt = f"""You are a faculty assistant for LPU.
No course documents available. Generate general academic material for: {effective_topic}"""
        response = self.llm.generate(
            prompt=prompt,
            system_prompt=Prompts.FACULTY_AGENT,
            temperature=0.4,
        )
        return response
