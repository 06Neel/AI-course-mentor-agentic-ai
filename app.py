import streamlit as st
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config.settings import Settings
from utils.document_processor import DocumentProcessor
from utils.security import SecurityManager
from utils.formatters import ResponseFormatter
from utils.conversation_manager import ConversationManager
from rag.vector_store import VectorStore
from agents.coordinator import CoordinatorAgent
from agents.rag_agent import RAGAgent
from agents.mentor_agent import MentorAgent
from agents.quiz_agent import QuizAgent
from agents.assignment_agent import AssignmentAgent
from agents.summary_agent import SummaryAgent
from agents.policy_agent import PolicyAgent
from agents.faculty_agent import FacultyAgent

Settings.ensure_dirs()

st.set_page_config(
    page_title=Settings.APP_TITLE,
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .agent-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .source-citation {
        background: #f0f2f6;
        padding: 8px 12px;
        border-left: 3px solid #0f3460;
        border-radius: 4px;
        margin: 8px 0;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)


def init_session():
    defaults = {
        "messages": [],
        "conversation_history": [],
        "selected_agent": "auto",
        "coordinator": None,
        "api_key_valid": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def get_conversation_manager() -> ConversationManager:
    return ConversationManager(st.session_state)


def get_coordinator(api_key: str):
    if not api_key:
        return None
    if st.session_state["coordinator"] is not None and st.session_state.get("api_key_valid"):
        return st.session_state["coordinator"]

    try:
        coord = CoordinatorAgent(api_key=api_key)
        coord.register_agent("rag", RAGAgent(api_key=api_key))
        coord.register_agent("mentor", MentorAgent(api_key=api_key))
        coord.register_agent("quiz", QuizAgent(api_key=api_key))
        coord.register_agent("assignment", AssignmentAgent(api_key=api_key))
        coord.register_agent("summary", SummaryAgent(api_key=api_key))
        coord.register_agent("policy", PolicyAgent(api_key=api_key))
        coord.register_agent("faculty", FacultyAgent(api_key=api_key))
        st.session_state["coordinator"] = coord
        st.session_state["api_key_valid"] = True
        return coord
    except Exception as e:
        st.error(f"Failed to initialize: {e}")
        return None


def process_files(uploaded_files):
    processor = DocumentProcessor()

    valid, msg = processor.validate_batch(uploaded_files)
    if not valid:
        st.warning(msg)
        return

    for file in uploaded_files:
        with st.spinner(f"Processing {file.name}..."):
            success, message, chunks = processor.process_uploaded_file(file)
            if success:
                st.success(f"✅ {file.name}: {chunks} chunks indexed")
            else:
                st.error(f"❌ {file.name}: {message}")


def display_message(role, content, agent="", sources=None):
    with st.chat_message(role):
        if agent and role == "assistant":
            colors = {
                "mentor": "#4CAF50", "quiz": "#FF9800", "assignment": "#2196F3",
                "summary": "#9C27B0", "policy": "#F44336", "faculty": "#00BCD4",
                "rag": "#795548", "coordinator": "#607D8B",
            }
            color = colors.get(agent, "#607D8B")
            label = Settings.AGENT_NAMES.get(agent, agent)
            st.markdown(
                f'<span class="agent-badge" style="background:{color}20;color:{color};border:1px solid {color}">{label}</span>',
                unsafe_allow_html=True,
            )
        formatted = ResponseFormatter.format_response(content, agent)
        st.markdown(formatted)
        if sources:
            with st.expander("📚 Sources", expanded=False):
                for src in set(sources):
                    st.markdown(f'<div class="source-citation">{src}</div>', unsafe_allow_html=True)


def handle_query(query, api_key):
    conv = get_conversation_manager()
    conv.add_user_message(query)
    display_message("user", query)

    with st.chat_message("assistant"):
        spinner = st.spinner("Thinking...")
        with spinner:
            try:
                coordinator = get_coordinator(api_key)
                if coordinator is None:
                    st.error("Please enter a valid Groq API key.")
                    return

                selected = st.session_state["selected_agent"]
                response = coordinator.run(query, selected_agent=selected)

                conv.add_assistant_message(response, agent=selected)

                if selected and selected != "auto":
                    colors = {
                        "mentor": "#4CAF50", "quiz": "#FF9800", "assignment": "#2196F3",
                        "summary": "#9C27B0", "policy": "#F44336", "faculty": "#00BCD4",
                        "rag": "#795548", "coordinator": "#607D8B",
                    }
                    color = colors.get(selected, "#607D8B")
                    label = Settings.AGENT_NAMES.get(selected, selected)
                    st.markdown(
                        f'<span class="agent-badge" style="background:{color}20;color:{color};border:1px solid {color}">{label}</span>',
                        unsafe_allow_html=True,
                    )

                formatted = ResponseFormatter.format_response(response, selected)
                st.markdown(formatted)

            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.error(error_msg)
                conv.add_assistant_message(error_msg, agent="coordinator")


def render_sidebar():
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/graduation-cap.png", width=60)
        st.title("AI Course Mentor")
        st.caption("Lovely Professional University")

        st.divider()

        st.subheader("Upload Documents")
        uploaded_files = st.file_uploader(
            "Upload course materials",
            type=["pdf", "docx", "pptx"],
            accept_multiple_files=True,
            help=f"Max {Settings.MAX_UPLOAD_SIZE_MB}MB per file, {Settings.MAX_FILES_PER_UPLOAD} files per upload",
        )
        if uploaded_files:
            process_files(uploaded_files)

        st.divider()

        st.subheader("Select Agent")
        st.session_state["selected_agent"] = st.selectbox(
            "Agent",
            options=list(Settings.AGENT_NAMES.keys()),
            format_func=lambda x: Settings.AGENT_NAMES[x],
            index=0,
            label_visibility="collapsed",
        )

        st.divider()

        st.subheader("Document Stats")
        vs = VectorStore()
        col1, col2 = st.columns(2)
        col1.metric("Files", vs.file_count)
        col2.metric("Chunks", vs.total_chunks)

        if vs.is_loaded:
            st.caption(f"Index: {vs.total_chunks} vectors")

        if vs.is_loaded:
            if st.button("Delete All Documents", use_container_width=True, type="secondary"):
                vs.reset()
                for f in Settings.DATA_DIR.iterdir():
                    if f.suffix.lower() in [".pdf", ".docx", ".pptx"]:
                        f.unlink()
                st.success("All documents deleted")
                st.rerun()

        st.divider()

        conv = get_conversation_manager()
        if st.button("Clear Chat History", use_container_width=True):
            conv.clear_history()
            st.rerun()

        st.divider()
        st.caption("Powered by Llama 3.3 70B via Groq")


def main():
    init_session()

    render_sidebar()

    st.markdown("""
    <div class="main-header">
        <h1>AI Course Mentor</h1>
        <p>Intelligent Academic Assistant for LPU Faculty & Students</p>
    </div>
    """, unsafe_allow_html=True)

    api_key = os.getenv("GROQ_API_KEY", "")

    conv = get_conversation_manager()
    for msg in conv.get_messages():
        display_message(msg.role, msg.content, msg.agent, msg.sources if msg.sources else None)

    if "sample_query" in st.session_state:
        q = st.session_state.pop("sample_query")
        handle_query(q, api_key)

    if prompt := st.chat_input("Ask me anything about your courses..."):
        sanitized = SecurityManager.sanitize(prompt)
        valid, msg = SecurityManager.validate_input(sanitized)
        if not valid:
            st.warning(msg)
        else:
            sensitive, s_msg = SecurityManager.check_sensitive(sanitized)
            if sensitive:
                st.warning(f"{s_msg}. Please remove sensitive information before sending.")
            else:
                handle_query(sanitized, api_key)


if __name__ == "__main__":
    main()
