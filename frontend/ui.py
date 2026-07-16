import re

import streamlit as st


def inject_css():
    st.markdown("""
    <style>
    @keyframes fadeUp { from { opacity:0; transform:translateY(8px);} to { opacity:1; transform:translateY(0);} }
    .stApp { background:#101116; }
    .block-container { padding-top:2rem; max-width:820px; }

    .header-row { display:flex; align-items:center; gap:10px; margin-bottom:16px; animation: fadeUp 0.5s ease both; }
    .header-bar { width:10px; height:34px; background:#a78bfa; border-radius:3px; }
    .header-title { font-size:20px; font-weight:600; color:#f5f5f2; }
    .header-subtitle { color:#a0a0a8; font-size:13px; margin:-8px 0 18px 20px; animation: fadeUp 0.5s ease both; animation-delay:0.1s; }

    .section-label { font-size:12px; font-weight:600; color:#a0a0a8; letter-spacing:0.03em; text-transform:uppercase; margin:16px 0 8px; }

    div[data-testid="stFileUploaderDropzone"] {
        border-radius:14px; background:#18191f; border:1px solid #3c3d47;
        transition: border-color 0.2s, background 0.2s;
    }
    div[data-testid="stFileUploaderDropzone"]:hover { border-color:#a78bfa; background:#1c1830; }

    .stTextArea textarea { border-radius:14px; background:#18191f; border:1px solid #2c2d34; color:#f5f5f2; }

    div.stButton > button {
        width:100%; height:48px; border-radius:24px;
        background:#ff8060; color:#1e0c06; border:none;
        font-size:14px; font-weight:600;
        transition: background 0.2s, transform 0.15s;
    }
    div.stButton > button:hover { background:#ff9068; }
    div.stButton > button:active { transform:scale(0.97); }

    .result-card { border-radius:14px; padding:16px 18px; margin-bottom:12px; animation: fadeUp 0.5s ease both; background:#181920; }
    .result-label { font-size:12px; font-weight:700; letter-spacing:0.04em; text-transform:uppercase; margin:0 0 8px; color:#a0a0a8; }
    .result-body { font-size:13px; color:#f5f5f2; margin:0; line-height:1.55; }
    .score-card { display:flex; align-items:center; gap:18px; background:linear-gradient(135deg,#181920,#15161d); box-shadow:0 18px 40px rgba(0,0,0,0.22); }
    .score-title { font-size:16px; font-weight:700; color:#f5f5f2; margin:0 0 4px; }
    .score-subtitle { font-size:13px; color:#a0a0a8; margin:0; line-height:1.5; }
    .verdict-pill { display:inline-flex; align-items:center; border-radius:999px; padding:5px 10px; font-size:12px; font-weight:700; margin-bottom:8px; }
    .verdict-strong { background:#14413a; color:#2dd4ab; }
    .verdict-moderate { background:#3f3516; color:#fac775; }
    .verdict-weak { background:#4b281c; color:#ff8060; }
    .insight-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:12px; }
    .insight-card { border-radius:14px; padding:16px; animation: fadeUp 0.5s ease both; }
    .insight-card.match { background:#123b35; animation-delay:0.15s; }
    .insight-card.missing { background:#403315; animation-delay:0.2s; }
    .insight-card.structure { background:#211c35; animation-delay:0.25s; }
    .insight-card.action { background:#271b18; animation-delay:0.3s; }
    .chip-list { display:flex; flex-wrap:wrap; gap:7px; }
    .chip { border-radius:999px; padding:6px 9px; font-size:12px; line-height:1; color:#f5f5f2; background:rgba(255,255,255,0.08); }
    .match .chip { background:rgba(45,212,171,0.16); color:#9df2df; }
    .missing .chip { background:rgba(250,199,117,0.16); color:#ffe0a1; }
    .breakdown-row { margin:9px 0; }
    .breakdown-head { display:flex; justify-content:space-between; gap:10px; font-size:12px; color:#d9d9df; margin-bottom:5px; }
    .bar-track { height:7px; border-radius:99px; background:#262832; overflow:hidden; }
    .bar-fill { height:100%; border-radius:99px; background:linear-gradient(90deg,#a78bfa,#2dd4ab); }
    .detail-card { background:#181920; border-radius:14px; padding:18px; animation: fadeUp 0.5s ease both; animation-delay:0.35s; }
    .detail-title { font-size:14px; color:#f5f5f2; font-weight:700; margin:0 0 10px; }
    .detail-text { white-space:pre-wrap; font-size:13px; line-height:1.6; color:#d8d8df; margin:0; }
    @media (max-width: 680px) {
        .score-card { align-items:flex-start; flex-direction:column; }
        .insight-grid { grid-template-columns:1fr; }
    }
    </style>
    """, unsafe_allow_html=True)


def render_header():
    st.markdown("""
    <div class="header-row">
        <div class="header-bar"></div>
        <span class="header-title">ATS resume checker</span>
    </div>
    <p class="header-subtitle">Field-agnostic resume scoring with plain-English feedback.</p>
    """, unsafe_allow_html=True)


def render_ui():
    inject_css()
    render_header()

    st.markdown('<p class="section-label">Resume</p>', unsafe_allow_html=True)
    resume_file = st.file_uploader(" ", type="pdf", label_visibility="collapsed")

    st.markdown('<p class="section-label">Job description</p>', unsafe_allow_html=True)
    job_description = st.text_area(" ", height=100, placeholder="Paste job description", label_visibility="collapsed")

    submit = st.button("Get ATS feedback")

    return resume_file, job_description, submit


def extract_score(feedback_text):
    match = re.search(r"ATS Match Score:\s*([0-9]{1,3})\s*/\s*100", feedback_text, re.IGNORECASE)
    if match:
        return max(0, min(100, int(match.group(1))))
    fit = re.search(r"Fit:\s*([0-9]+(?:\.[0-9]+)?)\s*/\s*10", feedback_text, re.IGNORECASE)
    if fit:
        return max(0, min(100, round(float(fit.group(1)) * 10)))
    return 0


def extract_value(feedback_text, label):
    match = re.search(rf"^{re.escape(label)}:\s*(.+)$", feedback_text, re.IGNORECASE | re.MULTILINE)
    return match.group(1).strip() if match else ""


def extract_block(feedback_text, heading):
    pattern = rf"^{re.escape(heading)}:\s*\n(.*?)(?=\n\n[A-Z][A-Za-z /]+:|\n\nFit:|\Z)"
    match = re.search(pattern, feedback_text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else ""


def split_items(text):
    if not text:
        return []
    cleaned = []
    for line in text.splitlines():
        line = line.strip().lstrip("- ").strip()
        if not line:
            continue
        cleaned.extend(part.strip() for part in line.split(",") if part.strip())
    return cleaned[:12]


def extract_breakdown(feedback_text):
    block = extract_block(feedback_text, "Score Breakdown")
    rows = []
    for line in block.splitlines():
        match = re.search(r"-?\s*(.+?):\s*([0-9]{1,3})\s*/\s*100", line)
        if match:
            rows.append((match.group(1).strip(), max(0, min(100, int(match.group(2))))))
    return rows


def render_chips(items):
    if not items:
        st.caption("No data found")
        return
    for item in items:
        st.markdown(f"- `{item}`")


def render_score_ring(score):
    circumference = 226
    offset = circumference - (circumference * score / 100)
    st.markdown(f"""
    <div class="result-card score-card" style="animation-delay:0.1s;">
        <svg width="88" height="88" viewBox="0 0 88 88">
            <circle cx="44" cy="44" r="36" fill="none" stroke="#14413a" stroke-width="8"/>
            <circle cx="44" cy="44" r="36" fill="none" stroke="#2dd4ab" stroke-width="8"
                stroke-linecap="round" stroke-dasharray="{circumference}"
                stroke-dashoffset="{offset}" transform="rotate(-90 44 44)"/>
            <text x="44" y="50" text-anchor="middle" font-size="20" font-weight="600" fill="#f5f5f2">{score}</text>
        </svg>
        <div>
            <p class="score-title">ATS match score</p>
            <p class="score-subtitle">Based on keyword overlap, role alignment, resume structure, and content depth.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_feedback(feedback_text):
    score = extract_score(feedback_text)
    verdict = extract_value(feedback_text, "Verdict") or "Review needed"
    role = extract_value(feedback_text, "Target Role") or "Target role"
    matched = split_items(extract_block(feedback_text, "Matched Keywords"))
    missing = split_items(extract_block(feedback_text, "Missing / Weak Keywords"))
    role_gaps = extract_block(feedback_text, "Role Gaps")
    resume_changes = extract_block(feedback_text, "Resume Changes For This Job")
    structure = extract_block(feedback_text, "Resume Structure")
    meaning = extract_block(feedback_text, "What this means")
    fixes = extract_block(feedback_text, "Recommended Fixes")
    breakdown = extract_breakdown(feedback_text)

    render_score_ring(score)

    st.markdown(f"### {verdict}")
    st.caption(role)
    st.write(meaning or "Review the sections below to improve ATS alignment.")

    left, right = st.columns(2)
    with left:
        st.markdown("#### Matched keywords")
        render_chips(matched)
    with right:
        st.markdown("#### Missing / weak keywords")
        render_chips(missing)

    st.markdown("#### Resume structure")
    st.info(structure or "No structure details found.")

    st.markdown("#### Role gaps")
    st.warning(role_gaps or "No major role-level gaps found.")

    st.markdown("#### Resume changes for this job")
    st.success(resume_changes or "No targeted resume changes found.")

    st.markdown("#### Score breakdown")
    if breakdown:
        for label, value in breakdown:
            st.write(f"{label}: {value}/100")
            st.progress(value / 100)
    else:
        st.caption("No breakdown found.")

    st.markdown("#### Detailed feedback")
    st.success(fixes or feedback_text)
