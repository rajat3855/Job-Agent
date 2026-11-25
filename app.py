"""
app.py — Streamlit UI for the Job Application Agent
Run with: streamlit run app.py
"""

import os
import json
import streamlit as st
from dotenv import load_dotenv
import pypdf
import io

load_dotenv()

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="JobAgent AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }

    .stApp { background-color: #0f0f13; color: #e2e8f0; }

    .main-header {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0;
    }

    .sub-header {
        color: #64748b;
        font-size: 1rem;
        margin-top: 0;
        margin-bottom: 2rem;
    }

    .metric-card {
        background: #1e1e2e;
        border: 1px solid #2d2d3d;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #6366f1;
    }

    .metric-label {
        font-size: 0.85rem;
        color: #64748b;
        margin-top: 4px;
    }

    .chat-message-user {
        background: #1e1e2e;
        border-left: 3px solid #6366f1;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }

    .chat-message-agent {
        background: #141420;
        border-left: 3px solid #06b6d4;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }

    .status-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }

    div[data-testid="stSidebar"] {
        background-color: #13131a;
        border-right: 1px solid #2d2d3d;
    }

    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4);
    }

    .stTextArea textarea, .stTextInput input {
        background-color: #1e1e2e !important;
        border: 1px solid #2d2d3d !important;
        color: #e2e8f0 !important;
        border-radius: 8px !important;
    }

    .resume-preview {
        background: #1e1e2e;
        border: 1px solid #2d2d3d;
        border-radius: 10px;
        padding: 1rem;
        font-size: 0.85rem;
        max-height: 300px;
        overflow-y: auto;
        color: #a0aec0;
        white-space: pre-wrap;
    }

    hr { border-color: #2d2d3d; }
</style>
""", unsafe_allow_html=True)


# ── Session State ─────────────────────────────────────────────────────────────
if "agent_executor" not in st.session_state:
    st.session_state.agent_executor = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "messages" not in st.session_state:
    st.session_state.messages = []
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "agent_ready" not in st.session_state:
    st.session_state.agent_ready = False


# ── Helper: Extract text from PDF ────────────────────────────────────────────
def extract_pdf_text(uploaded_file) -> str:
    reader = pypdf.PdfReader(io.BytesIO(uploaded_file.read()))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


# ── Helper: Initialize Agent ─────────────────────────────────────────────────
def initialize_agent():
    try:
        from agent.job_agent import build_agent
        st.session_state.agent_executor = build_agent()
        st.session_state.agent_ready = True
        return True
    except Exception as e:
        st.error(f"Failed to initialize agent: {e}")
        return False


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎯 JobAgent AI")
    st.markdown("---")

    # API Keys
    st.markdown("#### 🔑 API Keys")
    anthropic_key = st.text_input(
    "Groq API Key",
        value=os.getenv("ANTHROPIC_API_KEY", ""),
        type="password",
        placeholder="sk-ant-...",
    )
    tavily_key = st.text_input(
        "Tavily API Key",
        value=os.getenv("TAVILY_API_KEY", ""),
        type="password",
        placeholder="tvly-...",
    )

    if anthropic_key:
        os.environ["GROQ_API_KEY"] = anthropic_key
    if tavily_key:
        os.environ["TAVILY_API_KEY"] = tavily_key

    st.markdown("---")

    # Resume Upload
    st.markdown("#### 📄 Your Resume")
    resume_file = st.file_uploader(
        "Upload Resume (PDF or TXT)",
        type=["pdf", "txt"],
        help="Your resume will be used for all tailoring and matching",
    )

    if resume_file:
        if resume_file.type == "application/pdf":
            st.session_state.resume_text = extract_pdf_text(resume_file)
        else:
            st.session_state.resume_text = resume_file.read().decode("utf-8")
        st.success(f"✅ Resume loaded ({len(st.session_state.resume_text)} chars)")

    # Or paste resume
    if not st.session_state.resume_text:
        pasted = st.text_area(
            "Or paste your resume text here",
            height=150,
            placeholder="Paste your resume content...",
        )
        if pasted:
            st.session_state.resume_text = pasted

    if st.session_state.resume_text:
        with st.expander("Preview resume"):
            st.markdown(
                f'<div class="resume-preview">{st.session_state.resume_text[:1000]}...</div>',
                unsafe_allow_html=True
            )

    st.markdown("---")

    # Initialize Agent button
    if not st.session_state.agent_ready:
        if st.button("🚀 Initialize Agent", use_container_width=True):
            if not anthropic_key or not tavily_key:
                st.error("Please enter both API keys first.")
            elif not st.session_state.resume_text:
                st.error("Please upload or paste your resume first.")
            else:
                with st.spinner("Initializing agent..."):
                    if initialize_agent():
                        st.success("Agent ready!")
                        st.rerun()
    else:
        st.success("✅ Agent is active")
        if st.button("🔄 Reset Session", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.messages = []
            st.session_state.agent_ready = False
            st.session_state.agent_executor = None
            st.rerun()

    st.markdown("---")
    st.caption("Built with LangChain + Claude + Tavily")


# ── Main Content ──────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["💬 Agent Chat", "📊 Application Tracker"])

# ── Tab 1: Chat ───────────────────────────────────────────────────────────────
with tab1:
    st.markdown('<p class="main-header">JobAgent AI</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Find jobs → Tailor resume → Write cover letters — all in one conversation</p>',
        unsafe_allow_html=True,
    )

    if not st.session_state.agent_ready:
        st.info("👈 Set your API keys, upload your resume, and click **Initialize Agent** to get started.")

        st.markdown("#### ✨ What this agent does:")
        cols = st.columns(3)
        with cols[0]:
            st.markdown("**🔍 Job Search**\nFinds relevant listings matching your target role")
        with cols[1]:
            st.markdown("**📝 Resume Tailor**\nRewrite bullets to match job requirements")
        with cols[2]:
            st.markdown("**✉️ Cover Letters**\nPersonalized letters for each application")
    else:
        # Show chat history
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(
                    f'<div class="chat-message-user">🧑 <strong>You:</strong><br>{msg["content"]}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="chat-message-agent">🤖 <strong>JobAgent:</strong><br>{msg["content"]}</div>',
                    unsafe_allow_html=True,
                )

        # Quick action buttons
        st.markdown("#### Quick Actions")
        qcols = st.columns(3)
        quick_msg = None
        with qcols[0]:
            if st.button("🔍 Find ML Engineer jobs"):
                quick_msg = "Find Machine Learning Engineer job listings. Use my resume to tailor one top result and write a cover letter."
        with qcols[1]:
            if st.button("📊 Find Data Scientist jobs"):
                quick_msg = "Search for Data Scientist openings. Analyze the best match against my resume and suggest improvements."
        with qcols[2]:
            if st.button("🤖 Find AI Engineer jobs"):
                quick_msg = "Search for AI Engineer or LLM Engineer jobs. Find top listings and tailor my resume for the best fit."

        # Chat input
        user_input = st.chat_input("Type your request... e.g. 'Find SDE roles at startups in Bangalore'")

        # Handle input
        final_input = quick_msg or user_input

        if final_input:
            # Prepend resume context on first message
            if not st.session_state.messages:
                full_input = (
                    f"Here is my resume:\n\n{st.session_state.resume_text}\n\n"
                    f"---\n\nNow, {final_input}"
                )
            else:
                full_input = final_input

            st.session_state.messages.append({"role": "user", "content": final_input})

            with st.spinner("🤖 Agent is working... (searching jobs, analyzing fit...)"):
                try:
                    from agent.job_agent import run_agent
                    response, st.session_state.chat_history = run_agent(
                        st.session_state.agent_executor,
                        full_input,
                        st.session_state.chat_history,
                    )
                    st.session_state.messages.append({"role": "agent", "content": response})
                except Exception as e:
                    error_msg = f"Agent error: {str(e)}"
                    st.session_state.messages.append({"role": "agent", "content": error_msg})

            st.rerun()


# ── Tab 2: Tracker ────────────────────────────────────────────────────────────
with tab2:
    st.markdown("### 📊 Application Tracker")
    st.caption("All job applications saved by the agent appear here.")

    try:
        from utils.tracker import to_dataframe, update_status, delete_application, STATUS_COLORS, load_applications

        apps = load_applications()

        if not apps:
            st.info("No applications tracked yet. Ask the agent to search and save jobs!")
        else:
            # Summary metrics
            df = to_dataframe()
            m_cols = st.columns(5)
            statuses = ["To Apply", "Applied", "Interview", "Offer", "Rejected"]
            for i, status in enumerate(statuses):
                count = len(df[df["status"] == status]) if "status" in df.columns else 0
                with m_cols[i]:
                    st.markdown(
                        f'<div class="metric-card">'
                        f'<div class="metric-value">{count}</div>'
                        f'<div class="metric-label">{status}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

            st.markdown("---")
            st.dataframe(
                df[["company", "role", "match_score", "status", "saved_at"]],
                use_container_width=True,
                hide_index=True,
            )

            # Update status
            st.markdown("#### Update Application Status")
            uc1, uc2, uc3 = st.columns([2, 2, 1])
            with uc1:
                app_labels = [f"{a['role']} @ {a['company']}" for a in apps]
                selected = st.selectbox("Select application", app_labels)
            with uc2:
                new_status = st.selectbox("New status", statuses)
            with uc3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Update"):
                    idx = app_labels.index(selected)
                    update_status(idx, new_status)
                    st.success("Updated!")
                    st.rerun()

    except Exception as e:
        st.error(f"Tracker error: {e}")
