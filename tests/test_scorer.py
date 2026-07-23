from backend.scorer import analyze_resume, candidate_terms, format_ats_report, term_in_text

JOB_DESCRIPTION = """
Role: Applied AI Engineer
We need Python, FastAPI, LLM systems, retrieval augmented generation, evaluation,
pytest, CI, Docker, deployment, monitoring, and prompt engineering.
"""

STRONG_RESUME = """
Summary Applied AI Engineer.
Experience building Python FastAPI services for LLM systems, retrieval augmented
generation, prompt engineering, evaluation, pytest test suites, CI, Docker
deployment, monitoring dashboards, and production APIs.
Skills Python FastAPI LLM RAG evaluation pytest CI Docker deployment monitoring.
Projects built resume matcher and AI assistants.
"""

MODERATE_RESUME = """
Summary Python developer.
Experience with Python APIs, documentation, tests, data analysis, and deployment support.
Skills Python REST APIs pytest documentation.
Education Computer Science.
"""

WEAK_RESUME = """
Summary retail supervisor with customer service, scheduling, inventory, sales,
cashier training, and store operations.
Education business administration.
"""


def test_token_candidate_terms_are_deterministic():
    first = candidate_terms(JOB_DESCRIPTION)
    second = candidate_terms(JOB_DESCRIPTION)

    assert first == second
    assert "python" in first


def test_term_matching_handles_phrases_and_inflection():
    assert term_in_text("deployment monitoring", STRONG_RESUME)
    assert term_in_text("APIs", MODERATE_RESUME)
    assert not term_in_text("kubernetes", MODERATE_RESUME)


def test_scoring_is_reproducible_for_same_input():
    first = analyze_resume(STRONG_RESUME, JOB_DESCRIPTION)
    second = analyze_resume(STRONG_RESUME, JOB_DESCRIPTION)

    assert first == second


def test_strong_moderate_weak_ranking_order():
    strong = analyze_resume(STRONG_RESUME, JOB_DESCRIPTION)["score"]
    moderate = analyze_resume(MODERATE_RESUME, JOB_DESCRIPTION)["score"]
    weak = analyze_resume(WEAK_RESUME, JOB_DESCRIPTION)["score"]

    assert strong > moderate > weak
    assert strong >= 75
    assert weak < 55


def test_empty_inputs_return_bounded_score_and_report():
    analysis = analyze_resume("", "")
    report = format_ats_report(analysis)

    assert 0 <= analysis["score"] <= 100
    assert "ATS Match Score:" in report
    assert "Fit:" in report


def test_report_contains_score_evidence_sections():
    report = format_ats_report(analyze_resume(STRONG_RESUME, JOB_DESCRIPTION))

    assert "Matched Keywords:" in report
    assert "Missing / Weak Keywords:" in report
    assert "Score Breakdown:" in report
    assert "Fit:" in report
