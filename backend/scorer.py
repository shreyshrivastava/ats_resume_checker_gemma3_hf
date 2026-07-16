import math
import re
from collections import Counter


STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "best", "but", "by", "can",
    "for", "from", "has", "have", "in", "into", "is", "it", "its", "may",
    "more", "must", "of", "on", "or", "our", "such", "that", "the", "their",
    "them", "then", "this", "to", "we", "with", "within", "will", "you",
    "your", "work", "working", "role", "team", "teams", "ability", "skills",
    "experience", "including", "required", "requirements", "responsibilities",
    "include", "looking",
}

SECTION_NAMES = [
    "summary",
    "objective",
    "experience",
    "employment",
    "education",
    "skills",
    "projects",
    "certifications",
    "licenses",
    "publications",
    "volunteer",
]


def tokenize(text):
    raw_tokens = re.findall(r"[a-zA-Z][a-zA-Z+#/\-]{1,}", text.lower())
    return [canonical_token(token) for token in raw_tokens]


def canonical_token(token):
    token = token.strip(".,:;()[]{}")
    if len(token) > 3 and token.endswith("ies"):
        return token[:-3] + "y"
    if len(token) > 3 and token.endswith("s") and not token.endswith(("ss", "sis")):
        return token[:-1]
    return token


def normalize_phrase(phrase):
    return re.sub(r"\s+", " ", phrase.strip().lower())


def candidate_terms(text, max_terms=30):
    tokens = [token for token in tokenize(text) if token not in STOPWORDS and len(token) > 2]
    counts = Counter(tokens)

    phrases = []
    for size in (2,):
        for i in range(len(tokens) - size + 1):
            phrase = " ".join(tokens[i:i + size])
            if any(part in STOPWORDS for part in phrase.split()):
                continue
            phrases.append(phrase)

    phrase_counts = Counter(phrases)
    scored = {}
    for term, count in counts.items():
        scored[term] = count
    for phrase, count in phrase_counts.items():
        scored[phrase] = count * 2.2

    return [
        term for term, _ in sorted(
            scored.items(),
            key=lambda item: (item[1], len(item[0])),
            reverse=True,
        )[:max_terms]
    ]


def term_in_text(term, text):
    normalized_text = " ".join(tokenize(text))
    normalized_term = " ".join(tokenize(term))
    pattern = r"(?<![a-z0-9])" + re.escape(normalized_term) + r"(?![a-z0-9])"
    if normalized_term and re.search(pattern, normalized_text):
        return True
    parts = [part for part in tokenize(term) if part not in STOPWORDS]
    return len(parts) > 1 and all(term_in_text(part, normalized_text) for part in parts)


def extract_job_title(job_description):
    patterns = [
        r"looking for (?:a|an)\s+([^.\n]+)",
        r"job title[:\s]+([^.\n]+)",
        r"position[:\s]+([^.\n]+)",
        r"role[:\s]+([^.\n]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, job_description, re.IGNORECASE)
        if match:
            return match.group(1).strip()[:90]
    first_line = next((line.strip() for line in job_description.splitlines() if line.strip()), "")
    return first_line[:90] or "Target role"


def section_score(resume_text):
    lower_resume = resume_text.lower()
    found = [name for name in SECTION_NAMES if re.search(rf"\b{name}\b", lower_resume)]
    score = min(100, round(len(found) / 5 * 100))
    return score, found


def role_similarity(job_title, resume_text):
    title_terms = [term for term in tokenize(job_title) if term not in STOPWORDS]
    if not title_terms:
        return 50
    matched = sum(1 for term in title_terms if term_in_text(term, resume_text))
    return round((matched / len(title_terms)) * 100)


def analyze_resume(resume_text, job_description):
    resume_text = resume_text or ""
    job_description = job_description or ""
    job_title = extract_job_title(job_description)
    job_terms = candidate_terms(job_description, max_terms=28)
    resume_terms = candidate_terms(resume_text)

    matched_terms = [term for term in job_terms if term_in_text(term, resume_text)]
    missing_terms = [term for term in job_terms if term not in matched_terms]

    keyword_score = round((len(matched_terms) / max(1, len(job_terms))) * 100)
    sections, found_sections = section_score(resume_text)
    title_score = role_similarity(job_title, resume_text)
    length_score = 100 if len(resume_text.split()) >= 250 else max(35, round(len(resume_text.split()) / 250 * 100))

    score = round(
        keyword_score * 0.55
        + title_score * 0.15
        + sections * 0.15
        + length_score * 0.15
    )
    score = max(0, min(100, score))

    verdict = "Strong match" if score >= 75 else "Moderate match" if score >= 55 else "Needs improvement"
    if score >= 75:
        summary = "The resume shows good alignment with the job description, with a few keyword or evidence gaps to tighten."
    elif score >= 55:
        summary = "The resume has some relevant alignment, but important job-specific evidence or keywords are missing."
    else:
        summary = "The resume does not yet mirror enough of the job description for a strong ATS match."

    role_gaps = []
    if missing_terms:
        role_gaps.append(
            "The resume does not clearly show several job-specific terms from the target role: "
            + ", ".join(missing_terms[:6])
            + "."
        )
    if title_score < 60:
        role_gaps.append(
            f"The resume does not strongly mirror the target role title ({job_title}), so the role fit may look weaker to ATS filters."
        )
    if sections < 60:
        role_gaps.append(
            "The resume structure may be harder for an ATS to parse because common section headings are limited or unclear."
        )
    if length_score < 70:
        role_gaps.append(
            "The resume appears light on detailed evidence; add more role-specific achievements, responsibilities, tools, or measurable results."
        )
    if not role_gaps:
        role_gaps.append(
            "No major role-level gaps were detected. Focus on tightening wording and adding evidence for the most important requirements."
        )

    resume_changes = [
        "Rewrite the resume summary so it names the target role and includes the strongest matching keywords.",
        "Add the most important missing terms only if they reflect real experience.",
        "Move the strongest role-relevant skills into a clearly labeled Skills or Core Competencies section.",
        "Update experience bullets to show evidence for the target role using outcomes, tools, responsibilities, or metrics.",
    ]
    if missing_terms:
        resume_changes.insert(
            1,
            "Add evidence for these job-specific terms where accurate: "
            + ", ".join(missing_terms[:5])
            + ".",
        )
    if title_score < 60:
        resume_changes.append(
            f"Use wording closer to the target role title ({job_title}) in the summary or relevant project/experience headings."
        )

    return {
        "score": score,
        "score_10": round(score / 10, 1),
        "verdict": verdict,
        "summary": summary,
        "job_title": job_title,
        "matched_terms": matched_terms[:12],
        "missing_terms": missing_terms[:12],
        "resume_terms": resume_terms[:12],
        "keyword_score": keyword_score,
        "title_score": title_score,
        "section_score": sections,
        "length_score": length_score,
        "found_sections": found_sections,
        "role_gaps": role_gaps[:4],
        "resume_changes": resume_changes[:6],
    }


def format_ats_report(analysis):
    matched = analysis["matched_terms"] or ["No strong keyword matches found."]
    missing = analysis["missing_terms"] or ["No major missing terms found."]
    sections = analysis["found_sections"] or ["Add clear resume section headings."]

    return f"""ATS Match Score: {analysis["score"]}/100

Verdict: {analysis["verdict"]}

Target Role: {analysis["job_title"]}

Matched Keywords:
{", ".join(matched)}

Missing / Weak Keywords:
{", ".join(missing)}

Role Gaps:
{chr(10).join("- " + gap for gap in analysis["role_gaps"])}

Resume Changes For This Job:
{chr(10).join("- " + change for change in analysis["resume_changes"])}

Resume Structure:
Detected sections: {", ".join(sections)}

Score Breakdown:
- Keyword match: {analysis["keyword_score"]}/100
- Role/title alignment: {analysis["title_score"]}/100
- Resume structure: {analysis["section_score"]}/100
- Resume content depth: {analysis["length_score"]}/100

What this means:
{analysis["summary"]}

Recommended Fixes:
- Add the missing keywords only where they are accurate and supported by real experience.
- Mirror the job description's terminology in your skills, summary, and experience bullets.
- Use clear section headings such as Summary, Experience, Skills, Education, Projects, Certifications, or Licenses.
- Add measurable evidence for the most important requirements in the job description.

Fit: {analysis["score_10"]}/10"""
