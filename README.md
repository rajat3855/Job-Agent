# 🎯 JobAgent AI

An AI-powered job application agent that searches for jobs, tailors your resume, and writes cover letters — all from a single chat interface.

## ✨ Features

- **Job Search** — Finds real job listings via Tavily web search
- **Resume Analysis** — Scores your fit (0–100) against any job description
- **Resume Tailoring** — Rewrites your bullet points to match job requirements
- **Cover Letters** — Generates personalized, compelling cover letters
- **Application Tracker** — Tracks all your applications with status updates

## 🏗️ Tech Stack

| Layer | Tech |
|-------|------|
| LLM | Claude (Anthropic) |
| Agent Framework | LangChain + Tool Calling |
| Web Search | Tavily API |
| UI | Streamlit |
| Resume Parsing | pypdf |

## 🚀 Getting Started

### 1. Clone & Install

```bash
git clone <your-repo>
cd job-agent
pip install -r requirements.txt
```

### 2. Set Up API Keys

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

Get your keys from:
- **Anthropic**: https://console.anthropic.com
- **Tavily**: https://tavily.com (free tier available)

### 3. Run the App

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

## 🧑‍💻 How to Use

1. Enter your API keys in the sidebar
2. Upload your resume (PDF or TXT) or paste it
3. Click **Initialize Agent**
4. Ask the agent anything, e.g.:
   - *"Find Machine Learning Engineer jobs at startups in Bangalore"*
   - *"Search for remote Data Scientist roles and tailor my resume for the best match"*
   - *"Find AI Engineer jobs and write me a cover letter for the top result"*
5. Track your applications in the **Application Tracker** tab

## 📁 Project Structure

```
job-agent/
├── app.py                  # Streamlit UI
├── agent/
│   ├── __init__.py
│   ├── job_agent.py        # LangChain agent + Claude
│   └── tools.py            # Custom tools (search, tailor, cover letter, tracker)
├── utils/
│   ├── __init__.py
│   └── tracker.py          # Application tracker CRUD
├── applications.json       # Auto-created by agent (tracker data)
├── requirements.txt
└── .env.example
```

## 🔧 Customizing the Agent

**Change the LLM model** in `agent/job_agent.py`:
```python
llm = ChatAnthropic(model="claude-opus-4-5")  # or claude-haiku-4-5 for speed
```

**Add more tools** in `agent/tools.py` — any function decorated with `@tool` is automatically available to the agent.

**Modify the agent's behavior** by editing `SYSTEM_PROMPT` in `agent/job_agent.py`.

## 📸 Screenshots

The app has two tabs:
- **Agent Chat** — conversational interface with quick-action buttons
- **Application Tracker** — dashboard with status metrics and update controls

## 🎤 What to Say in Interviews

> *"I built a multi-tool LangChain agent using Claude that automates the entire job application workflow. It uses Tavily for real-time job search, performs resume-to-JD matching with gap analysis, rewrites resume bullet points using keyword optimization, and generates personalized cover letters. The system maintains a persistent application tracker with status management."*

---

Built as an AI/ML Engineering portfolio project.
