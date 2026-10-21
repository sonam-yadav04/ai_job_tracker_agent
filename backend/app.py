import json
import streamlit as st
from scrapper import scrape_job_url
from extractor import extract_job_details
from agent import run_agent
from job_tools import jobs , get_application_count


st.set_page_config(
    page_title="AI Job Tracker",
    page_icon="💼",
    layout="wide"
)

st.title("💼 AI Job Tracker")
st.caption("Scrape job postings, extract details, and track opportunities.")

st.sidebar.info(
    "Jobs are stored in memory and will be lost "
    "when the application process restarts."
)


# ---------------------------
# Session state
# ---------------------------

if "extracted_job" not in st.session_state:
    st.session_state.extracted_job = None

if "scraped_text" not in st.session_state:
    st.session_state.scraped_text = ""

if "agent_result" not in st.session_state:
    st.session_state.agent_result = ""

if "agent_answer" not in st.session_state:
    st.session_state.agent_answer = ""


# ---------------------------
# Helpers
# ---------------------------

def format_requirements(requirements):
    if isinstance(requirements, list):
        return ", ".join(str(item) for item in requirements)

    if requirements:
        return str(requirements)

    return "Not specified"


def show_job_details(details):
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Company**")
        st.write(details.get("company") or "Not identified")

        st.write("**Role**")
        st.write(details.get("role") or "Not identified")

    with col2:
        st.write("**Salary**")
        st.write(details.get("salary") or "Not disclosed")

        st.write("**Requirements**")
        st.write(format_requirements(details.get("requirements")))


# ---------------------------
# Tabs
# ---------------------------

add_tab, tracker_tab, assistant_tab = st.tabs(
    ["➕ Add a Job", "📋 My Jobs", "💬 Ask the Agent"]
)


# =========================================================
# TAB 1: Scrape and track a job
# =========================================================

with add_tab:
    st.subheader("Add a job from a public webpage")

    url = st.text_input(
        "Job posting URL",
        placeholder="https://company.com/careers/job-posting"
    )

    if st.button("Scrape & Extract", type="primary"):
        if not url.strip().startswith(("https://", "http://")):
            st.error("Please enter a valid HTTP or HTTPS URL.")

        else:
            try:
                with st.spinner("Scraping the webpage..."):
                    raw_text = scrape_job_url(url.strip())

                if not raw_text or not raw_text.strip():
                    st.error("The scraper did not find readable page content.")

                else:
                    st.session_state.scraped_text = raw_text

                    with st.spinner("Extracting job details with Groq..."):
                        details = extract_job_details(raw_text)

                    if not isinstance(details, dict):
                        st.error("The extractor did not return a valid dictionary.")

                    else:
                        st.session_state.extracted_job = details
                        st.session_state.agent_result = ""
                        st.success("Job details extracted. Review them below.")

            except Exception as error:
                st.error(f"Could not process this webpage: {error}")

    details = st.session_state.extracted_job

    if details:
        st.divider()
        st.subheader("Review extracted details")
        show_job_details(details)

        with st.expander("View scraped text"):
            st.text(st.session_state.scraped_text[:5000])

        st.warning(
            "Review the extracted information before tracking the job. "
            "LLM extraction can be inaccurate."
        )

        if st.button("Confirm & Track Job", type="primary"):
            if not details.get("company") or not details.get("role"):
                st.error("A company and role are required to track this job.")

            else:
                user_message = (
                    "Please track this job. First check whether the company "
                    "and role already exist. If it is a duplicate, do not save it. "
                    "Otherwise, save it with status 'saved'. Do not claim success "
                    "unless the tool confirms that the job was saved.\n\n"
                    "Extracted job details:\n"
                    f"{json.dumps(details, ensure_ascii=False)}"
                )

                try:
                    with st.spinner("Checking for duplicates and tracking the job..."):
                        result = run_agent(user_message)

                    st.session_state.agent_result = result

                except Exception as error:
                    st.session_state.agent_result = ""
                    st.error(f"The agent could not process the job: {error}")

        if st.session_state.agent_result:
            st.markdown("#### Agent response")
            st.write(st.session_state.agent_result)

        if st.button("Clear extracted job"):
            st.session_state.extracted_job = None
            st.session_state.scraped_text = ""
            st.session_state.agent_result = ""
            st.rerun()


# =========================================================
# TAB 2: View tracked jobs
# =========================================================

with tracker_tab:
    st.subheader("Your job tracker")

    total_jobs = get_application_count("all")
    saved_jobs = get_application_count("saved")
    applied_jobs = get_application_count("applied")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total jobs", total_jobs)
    col2.metric("Saved", saved_jobs)
    col3.metric("Applied", applied_jobs)

    st.divider()

    if not jobs:
        st.info("No jobs tracked yet. Add a job from the first tab.")
    else:
        rows = []

        for job in jobs:
            rows.append({
                "Company": job.get("company", ""),
                "Role": job.get("role", ""),
                "Salary": job.get("salary") or "Not disclosed",
                "Requirements": format_requirements(
                    job.get("requirements")
                ),
                "Status": job.get("status", "saved"),
            })

        st.dataframe(
            rows,
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# TAB 3: Ask the agent
# =========================================================

with assistant_tab:
    st.subheader("Ask your job-tracking agent")

    st.write(
        "Ask questions about your tracked jobs. "
        "The agent can use its registered tools when appropriate."
    )

    question = st.text_area(
        "Your question",
        placeholder=(
            "Examples:\n"
            "- How many jobs are in my tracker?\n"
            "- How many jobs have I applied to?"
        ),
        height=110
    )

    if st.button("Ask Agent", type="primary"):
        if not question.strip():
            st.warning("Please enter a question.")

        else:
            try:
                with st.spinner("The agent is thinking..."):
                    answer = run_agent(question.strip())

                st.session_state.agent_answer = answer

            except Exception as error:
                st.error(f"The agent encountered an error: {error}")

    if st.session_state.agent_answer:
        st.markdown("#### Agent response")
        st.write(st.session_state.agent_answer)



            