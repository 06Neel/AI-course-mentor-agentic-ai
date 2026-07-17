import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Settings:
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / "data"
    VECTOR_DB_DIR = BASE_DIR / "vector_db"
    PROMPTS_DIR = BASE_DIR / "prompts"

    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    APP_TITLE: str = os.getenv("APP_TITLE", "AI Course Mentor - LPU")
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))
    DEFAULT_TEMPERATURE: float = float(os.getenv("DEFAULT_TEMPERATURE", "0.3"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "4096"))

    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K_RESULTS: int = 5

    SUPPORTED_FILE_TYPES: list = ["pdf", "docx", "pptx"]
    MAX_FILES_PER_UPLOAD: int = 10

    AGENT_NAMES: dict = {
        "auto": "Auto (Coordinator)",
        "mentor": "Course Mentor",
        "quiz": "Quiz Generator",
        "assignment": "Assignment Generator",
        "summary": "Lecture Summarizer",
        "policy": "Academic Policy",
        "faculty": "Faculty Assistant",
        "rag": "Document Search",
    }

    @classmethod
    def ensure_dirs(cls):
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.VECTOR_DB_DIR.mkdir(exist_ok=True)
