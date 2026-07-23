from frontend.ui import extract_block, extract_breakdown, extract_score, extract_value, split_items

REPORT = """ATS Match Score: 72/100

Verdict: Moderate match

Target Role: Applied AI Engineer

Matched Keywords:
python, fastapi, evaluation

Missing / Weak Keywords:
docker, monitoring

Score Breakdown:
- Keyword match: 80/100
- Role/title alignment: 50/100

Fit: 7.2/10"""


def test_extract_score_prefers_ats_score():
    assert extract_score(REPORT) == 72


def test_extract_score_can_parse_fit_score():
    assert extract_score("Fit: 8.5/10") == 85


def test_extract_value_reads_single_line_fields():
    assert extract_value(REPORT, "Verdict") == "Moderate match"
    assert extract_value(REPORT, "Target Role") == "Applied AI Engineer"


def test_extract_block_and_split_items():
    block = extract_block(REPORT, "Matched Keywords")

    assert split_items(block) == ["python", "fastapi", "evaluation"]


def test_extract_breakdown_reads_progress_rows():
    assert extract_breakdown(REPORT) == [
        ("Keyword match", 80),
        ("Role/title alignment", 50),
    ]
