import json

from agents.base_agent import BaseAgent
from config.prompts import Prompts
from rag.retriever import Retriever


class CoordinatorAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.retriever = Retriever()
        self.agents = {}

    def register_agent(self, name: str, agent):
        self.agents[name] = agent

    def classify_intent(self, query: str) -> dict:
        classification_prompt = f"""Classify the following user query into one of these categories:
- concept_explanation: User wants to understand a topic or concept
- quiz_generation: User wants quizzes or practice questions
- assignment: User wants assignments, lab exercises, or coding problems
- summary: User wants content summarized or revised
- policy_query: User asks about university rules, attendance, grading, exams
- faculty_task: Faculty member needs help preparing materials
- document_search: User wants to find information from uploaded documents
- general: General academic question

Query: {query}

Respond in JSON format only:
{{"intent": "<category>", "topic": "<extracted topic>", "confidence": <0.0-1.0>}}"""

        response = self.llm.generate(
            prompt=classification_prompt,
            system_prompt="You are an intent classifier. Respond only in valid JSON.",
            temperature=0.1,
            max_tokens=200,
        )

        try:
            response = response.strip()
            if response.startswith("```"):
                response = response.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            return json.loads(response)
        except (json.JSONDecodeError, IndexError):
            return {"intent": "general", "topic": query, "confidence": 0.5}

    def run(self, query: str, context: str = "", selected_agent: str = "auto", **kwargs) -> str:
        document_context = ""
        if self.retriever.is_available:
            document_context = self.retriever.get_context(query)

        full_context = f"{context}\n\n{document_context}".strip() if context else document_context

        agent_name = selected_agent

        if agent_name == "auto" or agent_name not in self.agents:
            classification = self.classify_intent(query)
            intent = classification.get("intent", "general")
            topic = classification.get("topic", query)
            kwargs["topic"] = topic

            agent_map = {
                "concept_explanation": "mentor",
                "quiz_generation": "quiz",
                "assignment": "assignment",
                "summary": "summary",
                "policy_query": "policy",
                "faculty_task": "faculty",
                "document_search": "rag",
                "general": "mentor",
            }
            agent_name = agent_map.get(intent, "mentor")

        if agent_name in self.agents:
            response = self.agents[agent_name].run(
                query, context=full_context, **kwargs
            )
        else:
            response = self.llm.generate(
                prompt=query,
                system_prompt=Prompts.COORDINATOR,
            )

        citations = self.retriever.get_citations(query) if self.retriever.is_available else []
        result = response
        if citations:
            result += "\n\n---\n**References:**\n" + "\n".join(citations)

        return result
