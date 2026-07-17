from agents.base_agent import BaseAgent
from config.prompts import Prompts
from utils.ppt_generator import PPTGenerator, PPTContent, SlideContent


PPT_JSON_PROMPT = """Generate a PowerPoint presentation on the following topic.
Return ONLY a valid JSON object (no markdown, no extra text) with this exact structure:

{{
    "title": "Presentation Title",
    "subtitle": "Subtitle or presenter info",
    "slides": [
        {{
            "title": "Slide Title",
            "bullets": ["Point 1", "Point 2", "Point 3"],
            "notes": "Optional speaker notes"
        }}
    ]
}}

Guidelines:
- Create 8-15 slides depending on topic depth
- First slide after title should be an Overview/Agenda
- Last slide should be a Summary/Key Takeaways
- Each slide should have 3-5 concise bullet points
- Use clear, professional academic language
- Bullets should be informative but brief (one line each)
- Make content suitable for a university lecture

Topic: {topic}
{context}"""


class FacultyAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ppt_generator = PPTGenerator()

    def run(self, query: str, context: str = "", topic: str = "", **kwargs) -> str:
        task_type = kwargs.get("task_type", "lesson_plan")
        effective_topic = topic if topic and topic.lower() not in query.lower() else query

        if task_type == "ppt":
            return self._generate_ppt(query, effective_topic, context)

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

    def _generate_ppt(self, query: str, topic: str, context: str = "") -> str:
        context_block = ""
        if context and context.strip() and context.strip() != "No relevant documents found.":
            context_block = f"\nUse the following course material as reference:\n{context}"

        prompt = PPT_JSON_PROMPT.format(topic=topic, context=context_block)

        llm_response = self.llm.generate(
            prompt=prompt,
            system_prompt=Prompts.FACULTY_AGENT,
            temperature=0.4,
            max_tokens=4096,
        )

        ppt_content = PPTGenerator.parse_llm_output(llm_response)

        if ppt_content is None:
            ppt_content = self._build_fallback_content(topic, llm_response)

        filepath = self.ppt_generator.generate(ppt_content)

        return (
            f"**Presentation generated successfully!**\n\n"
            f"**Title:** {ppt_content.title}\n"
            f"**Slides:** {len(ppt_content.slides)}\n\n"
            f"Click the download button below to save your PowerPoint file.\n\n"
            f"---\n"
            f"**PPT_FILE_PATH:** `{filepath}`"
        )

    def _build_fallback_content(self, topic: str, raw_text: str) -> PPTContent:
        """Build PPT content from unstructured LLM output as fallback."""
        lines = [l.strip() for l in raw_text.strip().split("\n") if l.strip()]
        slides = []
        current_title = topic
        current_bullets = []

        for line in lines:
            stripped = line.lstrip("#>-* ")
            if line.startswith("#") or (len(stripped) < 60 and line.endswith(":")):
                if current_bullets:
                    slides.append(SlideContent(title=current_title, bullets=current_bullets))
                current_title = stripped.rstrip(":")
                current_bullets = []
            else:
                current_bullets.append(stripped)

        if current_bullets:
            slides.append(SlideContent(title=current_title, bullets=current_bullets))

        if not slides:
            slides = [SlideContent(title=topic, bullets=[raw_text[:500]])]

        return PPTContent(
            title=topic,
            subtitle="Generated by AI Course Mentor",
            slides=slides,
        )
