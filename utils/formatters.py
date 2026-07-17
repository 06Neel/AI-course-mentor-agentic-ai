import re


class ResponseFormatter:
    @staticmethod
    def format_citations(text: str) -> str:
        pattern = r"\[Source:\s*([^,]+),\s*Page\s*(\d+)\]"
        return re.sub(
            pattern,
            r"**[\1, Page \2]**",
            text,
        )

    @staticmethod
    def format_quiz(text: str) -> str:
        text = re.sub(r"(\d+)\.\s*", r"**\1.** ", text)
        text = re.sub(r"\*\*Answer:?\*\*\s*", "\n> **Answer:** ", text)
        return text

    @staticmethod
    def format_assignment(text: str) -> str:
        text = re.sub(r"(Question|Q)\s*(\d+)", r"**\1 \2**", text, flags=re.IGNORECASE)
        text = re.sub(r"Marks?:?\s*(\d+)", r"*[Marks: \1]*", text, flags=re.IGNORECASE)
        return text

    @staticmethod
    def format_summary(text: str) -> str:
        text = re.sub(r"^#+\s+(.+)$", r"### \1", text, flags=re.MULTILINE)
        return text

    @staticmethod
    def format_response(text: str, agent_type: str = "general") -> str:
        formatters = {
            "quiz": ResponseFormatter.format_quiz,
            "assignment": ResponseFormatter.format_assignment,
            "summary": ResponseFormatter.format_summary,
        }
        formatter = formatters.get(agent_type, lambda x: x)
        text = formatter(text)
        text = ResponseFormatter.format_citations(text)
        return text

    @staticmethod
    def to_markdown(text: str) -> str:
        return text

    @staticmethod
    def to_plain_text(text: str) -> str:
        text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
        text = re.sub(r"\*(.+?)\*", r"\1", text)
        text = re.sub(r"#{1,6}\s+", "", text)
        return text
