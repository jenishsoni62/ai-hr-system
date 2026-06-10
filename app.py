import streamlit as st
import pymupdf
from groq import Groq
import os
from dotenv import load_dotenv
import pandas as pd
import json
import plotly.express as px

load_dotenv()

st.set_page_config(page_title="AI HR System", page_icon="👥", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif; }

p, h1, h2, h3, h4, h5, label, .stMarkdown { color: #ffffff !important; }
[data-testid="stMetricLabel"] { color: #a78bfa !important; }
[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 2rem !important; }
[data-testid="stMetricDelta"] { color: #34d399 !important; }

.stApp { background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); }

div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 20px;
    backdrop-filter: blur(10px);
}

.stButton>button {
    background: linear-gradient(90deg, #7c3aed 0%, #a78bfa 100%);
    color: white;
    font-weight: 700;
    border: none;
    border-radius: 12px;
    padding: 12px 30px;
    width: 100%;
    font-size: 1.1rem;
    letter-spacing: 0.5px;
    transition: all 0.3s ease;
}

.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(124, 58, 237, 0.5);
}

.stTextArea textarea {
    background: #1e2536 !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 12px !important;
    color: #ffffff !important;
    font-size: 1rem !important;
}

.stTextArea label {
    color: #ffffff !important;
}

textarea::placeholder {
    color: rgba(255,255,255,0.4) !important;
}
.stFileUploader {
    background: rgba(255,255,255,0.05);
    border: 2px dashed rgba(167, 139, 250, 0.5);
    border-radius: 12px;
    padding: 20px;
}

.hero-title {
    font-size: 3.5rem;
    font-weight: 800;
    background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 0.5rem;
}

.hero-subtitle {
    text-align: center;
    color: rgba(255,255,255,0.6) !important;
    font-size: 1.1rem;
    margin-bottom: 2rem;
}

.candidate-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 24px;
    margin: 16px 0;
    backdrop-filter: blur(10px);
    word-wrap: break-word;
    overflow-wrap: break-word;
}

.top-candidate { border-left: 5px solid #34d399; }
.good-candidate { border-left: 5px solid #60a5fa; }
.average-candidate { border-left: 5px solid #fbbf24; }
.low-candidate { border-left: 5px solid #f87171; }

.score-badge {
    display: inline-block;
    padding: 4px 16px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 1rem;
}

.section-header {
    font-size: 1.5rem;
    font-weight: 700;
    color: #a78bfa !important;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid rgba(167, 139, 250, 0.3);
}

.info-box {
    background: rgba(167, 139, 250, 0.1);
    border: 1px solid rgba(167, 139, 250, 0.3);
    border-radius: 12px;
    padding: 16px;
    margin: 8px 0;
}

.tag {
    display: inline-block;
    background: rgba(96, 165, 250, 0.2);
    border: 1px solid rgba(96, 165, 250, 0.4);
    color: #60a5fa !important;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.85rem;
    margin: 2px;
}

.missing-tag {
    display: inline-block;
    background: rgba(248, 113, 113, 0.2);
    border: 1px solid rgba(248, 113, 113, 0.4);
    color: #f87171 !important;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.85rem;
    margin: 2px;
}

.divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.1);
    margin: 2rem 0;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="hero-title">👥 AI Powered HR System</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Upload resumes and instantly find your perfect candidates using AI</p>', unsafe_allow_html=True)
st.markdown('<hr class="divider">', unsafe_allow_html=True)

def extract_text_from_pdf(pdf_file):
    doc = pymupdf.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def analyze_candidate(resume_text, job_description):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "You are an expert HR analyst. Analyze this resume against the job description and respond ONLY with a JSON object, no other text.\n\nJob Description:\n" + job_description + "\n\nResume:\n" + resume_text[:3000] + "\n\nRespond with exactly this JSON format:\n{\"name\": \"candidate name or Unknown\", \"score\": 85, \"experience\": \"3 years\", \"skills_match\": [\"Python\", \"SQL\"], \"missing_skills\": [\"Java\"], \"strengths\": \"strong analytical skills\", \"weaknesses\": \"lacks leadership experience\", \"recommendation\": \"Shortlist\"}"
            }
        ],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown('<p class="section-header">📋 Job Description</p>', unsafe_allow_html=True)
    job_description = st.text_area(
        "Describe the role and requirements...",
        height=220,
        placeholder="Example: We are looking for a Data Analyst with 2+ years experience in Python, SQL, and data visualization. Must have strong analytical skills and experience with Power BI or Tableau..."
    )

with col2:
    st.markdown('<p class="section-header">📁 Upload Resumes</p>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "Drop PDF resumes here or browse",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload multiple PDF resumes at once"
    )
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} resume(s) uploaded successfully!")

st.markdown('<hr class="divider">', unsafe_allow_html=True)

if st.button("🚀 Analyze All Candidates"):
    if not job_description:
        st.warning("⚠️ Please enter a job description!")
    elif not uploaded_files:
        st.warning("⚠️ Please upload at least one resume!")
    else:
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, pdf_file in enumerate(uploaded_files):
            status_text.markdown(f"🔍 Analyzing **{pdf_file.name}**... ({i+1}/{len(uploaded_files)})")
            progress_bar.progress((i + 1) / len(uploaded_files))

            try:
                resume_text = extract_text_from_pdf(pdf_file)
                result_text = analyze_candidate(resume_text, job_description)
                result_text = result_text.strip()
                if result_text.startswith("```"):
                    result_text = result_text.split("```")[1]
                    if result_text.startswith("json"):
                        result_text = result_text[4:]
                result = json.loads(result_text)
                result["filename"] = pdf_file.name
                results.append(result)
            except Exception as e:
                st.error(f"❌ Error analyzing {pdf_file.name}: {str(e)}")

        progress_bar.empty()
        status_text.empty()

        if results:
            results.sort(key=lambda x: x.get("score", 0), reverse=True)

            st.markdown('<p class="section-header">📊 Overview</p>', unsafe_allow_html=True)

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Candidates", len(results))
            with col2:
                shortlisted = len([r for r in results if r.get("recommendation") == "Shortlist"])
                st.metric("Shortlisted", shortlisted)
            with col3:
                avg_score = sum(r.get("score", 0) for r in results) / len(results)
                st.metric("Average Score", f"{avg_score:.0f}/100")
            with col4:
                top_score = max(r.get("score", 0) for r in results)
                st.metric("Top Score", f"{top_score}/100")

            st.markdown('<hr class="divider">', unsafe_allow_html=True)

            col_chart, col_rank = st.columns([1, 1], gap="large")

            with col_chart:
                st.markdown('<p class="section-header">📈 Score Comparison</p>', unsafe_allow_html=True)
                df = pd.DataFrame([
                    {
                        "Candidate": r.get("name", "Unknown"),
                        "Score": r.get("score", 0)
                    } for r in results
                ])
                fig = px.bar(
                    df, x="Candidate", y="Score",
                    color="Score",
                    color_continuous_scale=["#f87171", "#fbbf24", "#34d399"],
                    template="plotly_dark",
                    title="Candidate Score Comparison"
                )
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)

            with col_rank:
                st.markdown('<p class="section-header">🏆 Quick Rankings</p>', unsafe_allow_html=True)
                for i, r in enumerate(results):
                    score = r.get("score", 0)
                    if score >= 80:
                        emoji = "🥇"
                        color = "#34d399"
                    elif score >= 60:
                        emoji = "🥈"
                        color = "#60a5fa"
                    elif score >= 40:
                        emoji = "🥉"
                        color = "#fbbf24"
                    else:
                        emoji = "❌"
                        color = "#f87171"

                    st.markdown(f"""
                    <div class="info-box">
                        <span style="font-size:1.2rem">{emoji}</span>
                        <span style="color:#ffffff; font-weight:600"> #{i+1} {r.get("name", "Unknown")}</span>
                        <span style="float:right; color:{color}; font-weight:700">{score}/100</span>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown('<hr class="divider">', unsafe_allow_html=True)
            st.markdown('<p class="section-header">👤 Detailed Candidate Profiles</p>', unsafe_allow_html=True)

            for i, candidate in enumerate(results):
                score = candidate.get("score", 0)
                if score >= 80:
                    card_class = "candidate-card top-candidate"
                    emoji = "🥇"
                    rec_color = "#34d399"
                elif score >= 60:
                    card_class = "candidate-card good-candidate"
                    emoji = "🥈"
                    rec_color = "#60a5fa"
                elif score >= 40:
                    card_class = "candidate-card average-candidate"
                    emoji = "🥉"
                    rec_color = "#fbbf24"
                else:
                    card_class = "candidate-card low-candidate"
                    emoji = "❌"
                    rec_color = "#f87171"

                skills_html = "".join([f'<span class="tag">{s}</span>' for s in candidate.get("skills_match", [])])
                missing_html = "".join([f'<span class="missing-tag">{s}</span>' for s in candidate.get("missing_skills", [])])

                st.markdown(f"""
                <div class="{card_class}">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
                        <h3 style="margin:0; font-size:1.4rem;">{emoji} {candidate.get("name", "Unknown")}</h3>
                        <span style="background:rgba(255,255,255,0.1); padding:6px 20px; border-radius:20px; font-weight:700; color:{rec_color}; font-size:1.1rem;">{score}/100</span>
                    </div>
                    <p style="color:rgba(255,255,255,0.5); margin-bottom:16px;">📄 {candidate.get("filename", "")}</p>
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-bottom:16px;">
                        <div>
                            <p style="color:#a78bfa; font-weight:600; margin-bottom:8px;">✅ Matching Skills</p>
                            <div>{skills_html if skills_html else "<span style='color:rgba(255,255,255,0.4)'>None found</span>"}</div>
                        </div>
                        <div>
                            <p style="color:#f87171; font-weight:600; margin-bottom:8px;">❌ Missing Skills</p>
                            <div>{missing_html if missing_html else "<span style='color:rgba(255,255,255,0.4)'>None missing</span>"}</div>
                        </div>
                    </div>
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-bottom:16px;">
                        <div style="background:rgba(52,211,153,0.1); border-radius:8px; padding:12px;">
                            <p style="color:#34d399; font-weight:600; margin-bottom:4px;">💪 Strengths</p>
                            <p style="margin:0;">{candidate.get("strengths", "N/A")}</p>
                        </div>
                        <div style="background:rgba(248,113,113,0.1); border-radius:8px; padding:12px;">
                            <p style="color:#f87171; font-weight:600; margin-bottom:4px;">⚠️ Weaknesses</p>
                            <p style="margin:0;">{candidate.get("weaknesses", "N/A")}</p>
                        </div>
                    </div>
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span>🕐 Experience: <b>{candidate.get("experience", "N/A")}</b></span>
                        <span style="background:rgba(255,255,255,0.1); padding:4px 16px; border-radius:20px; color:{rec_color}; font-weight:700;">
                            {candidate.get("recommendation", "N/A")}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div style="text-align:center; padding:40px;">
        <p style="font-size:4rem; margin-bottom:1rem;">🎯</p>
        <p style="font-size:1.3rem; color:rgba(255,255,255,0.6);">Enter a job description and upload resumes to get started!</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="candidate-card" style="text-align:center;">
            <p style="font-size:2.5rem;">📄</p>
            <p style="font-weight:700; font-size:1.1rem;">Resume Parsing</p>
            <p style="color:rgba(255,255,255,0.6);">Extracts text from PDF resumes automatically</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="candidate-card" style="text-align:center;">
            <p style="font-size:2.5rem;">🤖</p>
            <p style="font-weight:700; font-size:1.1rem;">AI Scoring</p>
            <p style="color:rgba(255,255,255,0.6);">Scores each candidate out of 100 using AI</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="candidate-card" style="text-align:center;">
            <p style="font-size:2.5rem;">🏆</p>
            <p style="font-weight:700; font-size:1.1rem;">Smart Ranking</p>
            <p style="color:rgba(255,255,255,0.6);">Ranks and shortlists best candidates instantly</p>
        </div>
        """, unsafe_allow_html=True)