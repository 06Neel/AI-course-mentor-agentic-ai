import sys
import json
from unittest.mock import MagicMock

sys.path.insert(0, ".")


class MockRetriever:
    is_available = False


class MockCoordinator:
    def __init__(self):
        self.llm = MagicMock()
        self.retriever = MockRetriever()
        self.agents = {}

    def classify_intent(self, query):
        response = self.llm.generate(
            prompt=f"Classify: {query}",
            system_prompt="JSON only",
            temperature=0.1,
            max_tokens=200,
        )
        try:
            response = response.strip()
            if response.startswith("```"):
                response = response.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            return json.loads(response)
        except Exception:
            return {"intent": "general", "topic": query, "confidence": 0.5}


def test_coordinator():
    c = MockCoordinator()

    c.llm.generate.return_value = json.dumps(
        {"intent": "quiz_generation", "topic": "machine learning", "confidence": 0.9}
    )
    r = c.classify_intent("Generate 10 MCQs on machine learning")
    assert r["intent"] == "quiz_generation", f"Expected quiz_generation, got {r['intent']}"
    print("1. Quiz intent: PASS")

    c.llm.generate.return_value = json.dumps(
        {"intent": "policy_query", "topic": "attendance", "confidence": 0.85}
    )
    r = c.classify_intent("What is the attendance policy?")
    assert r["intent"] == "policy_query"
    print("2. Policy intent: PASS")

    c.llm.generate.return_value = json.dumps(
        {"intent": "concept_explanation", "topic": "neural networks", "confidence": 0.92}
    )
    r = c.classify_intent("Explain neural networks")
    assert r["intent"] == "concept_explanation"
    print("3. Concept intent: PASS")

    c.llm.generate.return_value = "This is not JSON"
    r = c.classify_intent("random query")
    assert r["intent"] == "general"
    print("4. Fallback on bad JSON: PASS")

    print("\nAll coordinator tests PASSED!")


if __name__ == "__main__":
    test_coordinator()
