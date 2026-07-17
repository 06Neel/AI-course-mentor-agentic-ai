from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class Message:
    role: str
    content: str
    agent: str = ""
    sources: list = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


class ConversationManager:
    def __init__(self, session_state):
        self.state = session_state
        if "messages" not in self.state:
            self.state["messages"] = []
        if "conversation_history" not in self.state:
            self.state["conversation_history"] = []

    def add_user_message(self, content: str):
        msg = Message(role="user", content=content)
        self.state["messages"].append(msg)
        self.state["conversation_history"].append({"role": "user", "content": content})

    def add_assistant_message(self, content: str, agent: str = "", sources: list = None):
        msg = Message(role="assistant", content=content, agent=agent, sources=sources or [])
        self.state["messages"].append(msg)
        self.state["conversation_history"].append({"role": "assistant", "content": content})

    def get_messages(self) -> list[Message]:
        return self.state.get("messages", [])

    def get_history_for_llm(self) -> list[dict]:
        return self.state.get("conversation_history", [])

    def clear_history(self):
        self.state["messages"] = []
        self.state["conversation_history"] = []

    def get_last_n(self, n: int = 10) -> list[dict]:
        return self.state.get("conversation_history", [])[-n:]
