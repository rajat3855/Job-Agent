"""
tools.py — Custom LangChain tools for the Job Application Agent
"""

import os
import json
from langchain.tools import tool
from tavily import TavilyClient


# ── 1. Search Jobs ──────────────────────────────────────────────────────────
@tool
def search_jobs(query: str) -> str:
    """
    Search the web for job listings matching the given query.
    Use queries like 'Machine Learning Engineer jobs at Google 2024' or
    'Data Scientist remote jobs Python'.
    Returns a list of job postings with titles, URLs, and snippets.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "Error: TAVILY_API_KEY not set in environment."

    client = TavilyClient(api_key=api_key)
    results = client.search(query, max_results=5, search_depth="advanced")

    output_lines = []
    for i, r in enumerate(results.get("results", []), 1):
        output_lines.append(
            f"[{i}] {r.get('title', 'No Title')}\n"
            f"    URL: {r.get('url', '')}\n"
            f"    {r.get('content', '')[:400]}\n"
        )

    return "\n".join(output_lines) if output_lines else "No results found."


# ── 2. Fetch Full Job Description ───────────────────────────────────────────
@tool
def fetch_job_description(url: str) -> str:
    """
    Fetch and extract the full job description from a given job listing URL.
    Use this after search_jobs to get complete requirements, responsibilities,
    and qualifications for a specific role.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "Error: TAVILY_API_KEY not set in environment."

    client = TavilyClient(api_key=api_key)
    result = client.extract(urls=[url])

    if result and result.get("results"):
        content = result["results"][0].get("raw_content", "")
        return content[:3000] if content else "Could not extract content from this URL."
    return "Could not fetch job description."


# ── 3. Tailor Resume ─────────────────────────────────────────────────────────
@tool
def tailor_resume(job_description: str, resume_text: str) -> str:
    """
    Analyze the job description against the user's resume and return:
    1. Match score (0–100)
    2. Missing keywords/skills the resume should mention
    3. Rewritten bullet points that better align with the job
    4. Sections to emphasize or de-emphasize

    Input job_description and resume_text as plain strings.
    """
    # The agent (LLM) will interpret this tool call and do the analysis itself.
    # This tool acts as a structured prompt trigger.
    return (
        f"TAILORING TASK:\n\n"
        f"JOB DESCRIPTION:\n{job_description[:2000]}\n\n"
        f"RESUME:\n{resume_text[:2000]}\n\n"
        f"Please provide:\n"
        f"1. Match Score (0-100) with brief reason\n"
        f"2. Top 5 missing keywords/skills to add\n"
        f"3. 3-5 rewritten resume bullet points optimized for this role\n"
        f"4. Which resume sections to highlight or downplay\n"
    )


# ── 4. Generate Cover Letter ─────────────────────────────────────────────────
@tool
def generate_cover_letter(role: str, company: str, job_description: str, resume_text: str) -> str:
    """
    Generate a professional, personalized cover letter for the given role and company.
    Tailors the letter to match both the job description requirements and the
    candidate's actual experience from their resume. Keep it under 350 words.
    """
    return (
        f"COVER LETTER TASK:\n\n"
        f"Role: {role}\nCompany: {company}\n\n"
        f"JOB DESCRIPTION (key points):\n{job_description[:1500]}\n\n"
        f"CANDIDATE RESUME:\n{resume_text[:1500]}\n\n"
        f"Write a compelling cover letter (under 350 words) that:\n"
        f"- Opens with a strong, specific hook (not 'I am writing to apply')\n"
        f"- Highlights 2-3 specific achievements from the resume relevant to this role\n"
        f"- Shows genuine knowledge of the company\n"
        f"- Closes with a confident call to action\n"
    )


# ── 5. Save Application to Tracker ──────────────────────────────────────────
@tool
def save_application(data_json: str) -> str:
    """
    Save a job application to the local tracker file (applications.json).
    Input must be a JSON string with keys:
      - company (str)
      - role (str)
      - url (str)
      - match_score (int)
      - status (str): one of 'To Apply', 'Applied', 'Interview', 'Rejected', 'Offer'
      - notes (str)
    """
    tracker_path = "applications.json"

    try:
        data = json.loads(data_json)
    except json.JSONDecodeError:
        return "Error: Invalid JSON provided. Could not save application."

    # Load existing tracker
    if os.path.exists(tracker_path):
        with open(tracker_path, "r") as f:
            tracker = json.load(f)
    else:
        tracker = []

    from datetime import datetime
    data["saved_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    tracker.append(data)

    with open(tracker_path, "w") as f:
        json.dump(tracker, f, indent=2)

    return f"✅ Saved application for {data.get('role')} at {data.get('company')} to tracker."
