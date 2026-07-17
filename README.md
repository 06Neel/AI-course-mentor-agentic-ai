# AI Course Mentor - LPU

An Agentic AI-powered Course Mentor system for Lovely Professional University (LPU) that uses multi-agent orchestration to provide accurate, context-aware, and document-grounded responses for faculty and students.

## Features

- **8 Specialized Agents**: Coordinator, RAG, Course Mentor, Quiz, Assignment, Summary, Academic Policy, Faculty Assistant
- **RAG Pipeline**: FAISS vector store with Sentence Transformers embeddings for document-grounded responses
- **Multi-Agent Orchestration**: Coordinator agent classifies intent and delegates to specialized agents
- **Document Support**: PDF, DOCX, PPTX upload and processing
- **Groq API + Llama 3.3 70B**: Fast inference via Groq cloud
- **Streamlit Dashboard**: Interactive chat UI with dark mode support
- **Conversation Memory**: Multi-turn conversation with history
- **Document Citations**: Source references for all document-grounded answers
- **Security**: Prompt injection protection, input validation

## Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | Llama 3.3 70B Versatile (via Groq API) |
| Agent Framework | Custom AntiGravity-inspired orchestration |
| RAG | FAISS + Sentence Transformers |
| Frontend | Streamlit |
| Embeddings | all-MiniLM-L6-v2 |
| Document Processing | PyPDF2, python-docx, python-pptx |

## Project Structure

```
AI_Course_Mentor/
├── app.py                  # Streamlit application entry point
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker build file
├── docker-compose.yml     # Docker Compose config
├── .env.example           # Environment variables template
├── config/
│   ├── settings.py        # App configuration
│   └── prompts.py         # Agent prompt templates
├── agents/
│   ├── base_agent.py      # Base agent class
│   ├── coordinator.py     # Coordinator agent
│   ├── rag_agent.py       # RAG search agent
│   ├── mentor_agent.py    # Course mentor agent
│   ├── quiz_agent.py      # Quiz generator agent
│   ├── assignment_agent.py # Assignment generator agent
│   ├── summary_agent.py   # Lecture summarizer agent
│   ├── policy_agent.py    # Academic policy agent
│   └── faculty_agent.py   # Faculty assistant agent
├── rag/
│   ├── loader.py          # Document loader (PDF/DOCX/PPTX)
│   ├── embeddings.py      # Embedding engine
│   ├── vector_store.py    # FAISS vector store
│   └── retriever.py       # Semantic retriever
├── llm/
│   ├── provider.py        # LLM provider interface
│   └── groq_provider.py   # Groq API implementation
├── utils/
│   ├── document_processor.py  # File validation & processing
│   ├── conversation_manager.py # Chat history management
│   ├── security.py         # Prompt injection protection
│   └── formatters.py       # Response formatting
├── prompts/                # Agent prompt templates
├── data/                   # Uploaded documents
├── vector_db/              # FAISS index storage
└── tests/                  # Test suite
```

## Quick Start

### Prerequisites

1. Python 3.10+
2. Groq API key (free at [console.groq.com](https://console.groq.com))

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/AI_Course_Mentor.git
cd AI_Course_Mentor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### Run the Application

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or with Docker
docker build -t course-mentor .
docker run -p 8501:8501 --env-file .env course-mentor
```

## Usage Guide

### 1. Upload Documents
- Click "Upload Documents" in the sidebar
- Upload PDF, DOCX, or PPTX files
- Documents are automatically chunked and indexed

### 2. Select Agent
- **Auto**: Coordinator automatically routes your query
- **Course Mentor**: Concept explanations with examples
- **Quiz Generator**: MCQs, True/False, Fill-in-blanks, Bloom's questions
- **Assignment Generator**: Theory, lab, coding, rubrics
- **Lecture Summarizer**: Chapter summaries, flashcards, revision notes
- **Academic Policy**: University rules (from uploaded documents only)
- **Faculty Assistant**: Lesson plans, question papers, CO mapping
- **Document Search**: Direct semantic search through documents

### 3. Sample Queries

| Query | Agent |
|-------|-------|
| Explain Decision Trees with examples | Course Mentor |
| Generate 20 MCQs on Machine Learning | Quiz Generator |
| Summarize Unit 4 | Lecture Summarizer |
| Create an assignment on Data Preprocessing | Assignment Generator |
| What is the attendance policy? | Academic Policy |
| Generate Bloom's Level 3 questions | Quiz Generator |
| Create viva questions for Linear Regression | Quiz Generator |
| Prepare a lesson plan for DBMS Unit 1 | Faculty Assistant |

## Testing

```bash
python tests/test_rag.py
python tests/test_agents.py
python tests/test_coordinator.py
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | - | Your Groq API key |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | LLM model name |
| `MAX_UPLOAD_SIZE_MB` | `50` | Max file upload size |
| `DEFAULT_TEMPERATURE` | `0.3` | LLM temperature |
| `MAX_TOKENS` | `4096` | Max tokens per response |

## Architecture

```
User Query → Streamlit UI → Coordinator Agent
                                │
                    ┌───────────┼───────────┐
                    │           │           │
                    ▼           ▼           ▼
              RAG Agent    Quiz Agent  Mentor Agent  ...
                    │           │           │
                    ▼           ▼           ▼
              FAISS Search  LLM Generate  LLM Generate
                    │           │           │
                    └───────────┼───────────┘
                                │
                                ▼
                        Response + Citations
                                │
                                ▼
                        Streamlit Display
```

## License

MIT License

## Acknowledgments

- Groq for fast LLM inference
- Meta for Llama 3.3 model
- Streamlit for the web framework
- FAISS for vector similarity search
- Sentence Transformers for embeddings
