import requests
import json
import streamlit as st
import io
import base64
import time
import json
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
from pypdf import PdfReader
from docx import Document

from langchain_text_splitters import RecursiveCharacterTextSplitter
from groq import Groq

from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(
    page_title="Mindflix — PDF Chatbot",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* Import modern typography */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

    /* Global font */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif !important;
    }

    /* Hide default Streamlit header/footer */
    #MainMenu, footer, header { visibility: hidden; }

    /* Remove top and bottom padding */
    .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    .stApp > div:first-child {
        padding-top: 0 !important;
    }
    section[data-testid="stSidebar"] { padding-top: 0 !important; }
    div[data-testid="stAppViewContainer"] > section > div {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }

    /* Animated Aurora Background */
    @keyframes aurora {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .stApp {
        background: linear-gradient(-45deg, #0b0f19, #1a1025, #0a192f, #112240);
        background-size: 400% 400%;
        animation: aurora 15s ease infinite;
        min-height: 100vh;
    }

    /* Hero banner */
    .hero {
        text-align: center;
        padding: 3rem 1rem 2rem;
        animation: fadeInDown 1s ease-out;
    }
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .hero h1 {
        font-size: 3.2rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #00f2fe, #4facfe, #00f2fe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -1px;
        margin-bottom: 0.5rem;
        text-shadow: 0px 4px 15px rgba(0, 242, 254, 0.3);
    }
    .hero p {
        color: #94a3b8;
        font-size: 1.15rem;
        font-weight: 300;
        margin-top: 0;
        letter-spacing: 0.5px;
    }

    /* Card containers / Glassmorphism */
    .card {
        background: rgba(17, 25, 40, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(0, 242, 254, 0.15);
    }

    /* Section headings */
    .section-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #e2e8f0;
        letter-spacing: 1px;
        margin-bottom: 1.2rem;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .section-title::before {
        content: '';
        display: inline-block;
        width: 8px;
        height: 24px;
        background: linear-gradient(180deg, #00f2fe, #4facfe);
        border-radius: 4px;
    }


    /* Hero Redesign CSS */
    .tools-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin-top: 30px;
    }
    
    .animated-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
        cursor: default;
    }
    
    .animated-card:hover {
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.06);
        border-color: rgba(0, 242, 254, 0.4);
        box-shadow: 0 10px 20px -10px rgba(0, 242, 254, 0.3);
    }
    
    .animated-card .emoji {
        font-size: 2.5rem;
        margin-bottom: 10px;
        display: block;
        transition: transform 0.3s ease;
    }
    
    .animated-card:hover .emoji {
        transform: scale(1.1);
    }
    
    .animated-card .title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #e2e8f0;
    }
    

    .animated-card .subtitle {
        display: block;
        font-size: 0.85rem;
        color: #94a3b8;
        margin-top: 6px;
        line-height: 1.3;
    }

    .hero p.tagline {
        color: #00f2fe;
        font-weight: 500;
        font-size: 1.2rem;
        margin-top: -10px;
    }


    /* KPI Redesign CSS */
    .kpi-grid {
        display: flex;
        justify-content: center;
        gap: 30px;
        margin-bottom: 40px;
        flex-wrap: wrap;
    }
    .kpi-card {
        background: rgba(0, 242, 254, 0.05);
        border: 1px solid rgba(0, 242, 254, 0.2);
        border-radius: 8px;
        padding: 15px 25px;
        color: #00f2fe;
        font-weight: bold;
        font-size: 1.2rem;
        box-shadow: 0 4px 15px rgba(0, 242, 254, 0.1);
        text-align: center;
        min-width: 140px;
        letter-spacing: 0.5px;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        background: transparent;
        border-bottom: 2px solid rgba(255,255,255,0.05);
        padding-bottom: 8px;
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 0;
        color: #64748b;
        font-weight: 600;
        font-size: 1.05rem;
        padding: 0.5rem 0.5rem;
        border: none;
        transition: color 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        background: transparent !important;
        color: #00f2fe !important;
        border-bottom: 3px solid #00f2fe !important;
        box-shadow: 0 4px 15px -10px #00f2fe;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        color: #ffffff;
        border: none;
        border-radius: 12px;
        padding: 0.7rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        letter-spacing: 0.5px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        width: 100%;
        box-shadow: 0 4px 15px rgba(0, 242, 254, 0.3);
    }
    .stButton > button:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 8px 25px rgba(0, 242, 254, 0.5);
        color: white;
    }
    .stButton > button:active {
        transform: translateY(1px);
    }

    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input {
        background: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        border-radius: 12px !important;
        color: #f8fafc !important;
        caret-color: #00f2fe !important;
        padding: 0.8rem 1.2rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
    }
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: #64748b !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #00f2fe !important;
        box-shadow: 0 0 0 3px rgba(0, 242, 254, 0.2), inset 0 2px 4px rgba(0,0,0,0.1) !important;
        background: rgba(15, 23, 42, 0.8) !important;
    }

    /* File uploader */
    .stFileUploader > div {
        background: rgba(15, 23, 42, 0.4) !important;
        border: 2px dashed rgba(0, 242, 254, 0.3) !important;
        border-radius: 16px !important;
        padding: 2rem 1.5rem !important;
        transition: all 0.3s ease;
    }
    .stFileUploader > div:hover {
        border-color: #00f2fe !important;
        background: rgba(0, 242, 254, 0.05) !important;
    }
    .stFileUploader label, .stFileUploader span, .stFileUploader p {
        color: #94a3b8 !important;
    }

    /* Labels */
    label, .stTextInput label, .stTextArea label, .stNumberInput label,
    .stFileUploader label, p, span {
        color: #cbd5e1 !important;
        font-weight: 500 !important;
    }

    /* General text */
    .stMarkdown, .stMarkdown p, .stMarkdown li, div[data-testid="stMarkdownContainer"] p {
        color: #e2e8f0 !important;
    }

    /* Answer box */
    .answer-box {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(0, 242, 254, 0.2);
        border-left: 5px solid #00f2fe;
        border-radius: 12px;
        padding: 1.5rem;
        color: #f8fafc;
        line-height: 1.8;
        margin-top: 1.5rem;
        box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5);
        animation: fadeIn 0.5s ease-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Alerts */
    .stSuccess, .stInfo, .stWarning, .stError {
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        backdrop-filter: blur(10px);
    }
    .stSuccess { background: rgba(16, 185, 129, 0.1) !important; border-color: rgba(16, 185, 129, 0.3) !important; color: #34d399 !important; }
    .stWarning { background: rgba(245, 158, 11, 0.1) !important; border-color: rgba(245, 158, 11, 0.3) !important; color: #fbbf24 !important; }
    .stError { background: rgba(239, 68, 68, 0.1) !important; border-color: rgba(239, 68, 68, 0.3) !important; color: #f87171 !important; }

    /* Divider */
    hr {
        border-color: rgba(255,255,255,0.05);
        margin: 2rem 0;
    }

    /* Navbar */
    .navbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1rem 2.5rem;
        background: rgba(15, 23, 42, 0.5);
        border-bottom: 1px solid rgba(255,255,255,0.05);
        margin-bottom: 1rem;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        position: sticky;
        top: 0;
        z-index: 999;
    }
    .navbar-brand {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    .navbar-logo {
        height: 48px;
        width: auto;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .navbar-name {
        font-size: 1.4rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.5px;
        line-height: 1.2;
    }
    .navbar-tagline {
        font-size: 0.8rem;
        color: #94a3b8;
        font-weight: 400;
        letter-spacing: 0.5px;
    }
    .navbar-badge {
        background: rgba(0, 242, 254, 0.1);
        border: 1px solid rgba(0, 242, 254, 0.3);
        color: #00f2fe;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 0.4rem 1.2rem;
        border-radius: 30px;
        letter-spacing: 0.5px;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.1);
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: rgba(15, 23, 42, 0.5); }
    ::-webkit-scrollbar-thumb { background: rgba(0, 242, 254, 0.5); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(0, 242, 254, 0.8); }
</style>
""", unsafe_allow_html=True)


def extract_text_from_uploaded(uploaded):
    if not uploaded:
        return ""
    try:
        reader = PdfReader(io.BytesIO(uploaded.read()))
        txt = ""
        for p in reader.pages:
            t = p.extract_text() or ""
            txt += t + "\n"
        return txt
    except Exception as e:
        st.error(f"Failed to read PDF: {e}")
        return ""


def extract_text_from_docx(uploaded):
    try:
        doc = Document(io.BytesIO(uploaded.read()))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception as e:
        st.error(f"Failed to read Word file: {e}")
        return ""

def extract_text_from_json(uploaded):
    try:
        data = json.load(uploaded)
        return json.dumps(data, indent=2)
    except Exception as e:
        st.error(f"Failed to read JSON file: {e}")
        return ""

def extract_text_from_file(uploaded):
    name = uploaded.name.lower()
    if name.endswith(".pdf"):
        return extract_text_from_uploaded(uploaded)
    elif name.endswith(".docx"):
        return extract_text_from_docx(uploaded)
    elif name.endswith(".json"):
        return extract_text_from_json(uploaded)
    else:
        st.error(f"Unsupported file type: {name}")
        return ""

def get_chunks(text, chunk_size=1000, chunk_overlap=200):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_text(text)


# Navbar
st.markdown("""
<div class="navbar">
    <div class="navbar-brand">
        <img class="navbar-logo"
             src="https://ui-avatars.com/api/?name=Mindflix&background=0b0f19&color=00f2fe&size=128"
             onerror="this.style.display='none'"
             alt="Mindflix Logo">
        <div>
            <div class="navbar-name">Mindflix</div>
            <div class="navbar-tagline">One AI workspace for QA engineers, marketers, and teams.</div>
        </div>
    </div>
    <div class="navbar-badge">AI Tools</div>
</div>
""", unsafe_allow_html=True)

# Hero
st.markdown("""
<div class="hero">
    <h1>📄 Mindflix AI</h1>
    <p class="tagline">AI Workspace for Modern Teams</p>
    <div class="tools-grid">
        <div class="animated-card">
            <span class="emoji">📄</span>
            <span class="title">Docs Intelligence</span>
            <span class="subtitle">Ask anything from documents</span>
        </div>
        <div class="animated-card">
            <span class="emoji">🧪</span>
            <span class="title">QA Copilot</span>
            <span class="subtitle">Generate test cases instantly</span>
        </div>
        <div class="animated-card">
            <span class="emoji">🎨</span>
            <span class="title">Social Studio</span>
            <span class="subtitle">Create branded social content</span>
        </div>
        <div class="animated-card">
            <span class="emoji">🧬</span>
            <span class="title">Brand Intelligence</span>
            <span class="subtitle">Extract and scale your brand identity</span>
        </div>
    </div>
</div>
<div class="kpi-grid">
    <div class="kpi-card">150+ Docs</div>
    <div class="kpi-card">2000+ Tests</div>
    <div class="kpi-card">500+ Posts</div>
    <div class="kpi-card">50+ Brands</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["📄 Documents", "🧪 QA Copilot", "🎨 Social Studio", "🧬 Brand Intelligence"])

with tab1:
    col1, col2 = st.columns([1, 1.6], gap="large")

    with col1:
        st.markdown('<div class="section-title">📂 Upload File (PDF, DOCX, JSON)</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("", type=["pdf", "docx", "json"], key="qa_upload", label_visibility="collapsed")

        if uploaded_file:
            file_id = uploaded_file.file_id
            if st.session_state.get("qa_file_id") != file_id:
                with st.spinner(f"Reading and indexing {uploaded_file.name}..."):
                    text = extract_text_from_file(uploaded_file)
                if not text.strip():
                    st.error(f"No text extracted from {uploaded_file.name}.")
                else:
                    chunks = get_chunks(text)
                    if not chunks:
                        st.error("Text splitting produced no chunks.")
                    else:
                        chunk_token_sets = [set(c.lower().split()) for c in chunks]
                        st.session_state["vector_store"] = {"chunks": chunks, "token_sets": chunk_token_sets}
                        st.session_state["qa_file_id"] = file_id
                        st.success(f"Ready! {len(chunks)} chunks indexed.")
            else:
                st.success(f"Already indexed — {len(st.session_state['vector_store']['chunks'])} chunks.")
        else:
            st.session_state.pop("vector_store", None)
            st.session_state.pop("qa_file_id", None)
            st.markdown("""
            <div style="color:#6b7280; font-size:0.9rem; margin-top:0.5rem;">
                Supports PDF, Word (.docx), and JSON files up to 200MB.
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-title">💬 Ask a Question</div>', unsafe_allow_html=True)
        vector_store = st.session_state.get("vector_store")
        question = st.text_input("", placeholder="e.g. What is the main topic of this document?", key="qa_question", label_visibility="collapsed")
        st.button("Get Answer", key="qa_button")

        if st.session_state.get("qa_button"):
            if not question:
                st.warning("Please enter a question.")
            elif not vector_store:
                st.warning("Please upload a PDF first.")
            else:
                with st.spinner("Thinking..."):
                    k = 3
                    q_tokens = set(question.lower().split())
                    scores = [(i, len(q_tokens & toks)) for i, toks in enumerate(vector_store["token_sets"])]
                    scores.sort(key=lambda x: x[1], reverse=True)
                    top_idxs = [i for i, s in scores[:k]]
                    context = "\n\n---\n\n".join([vector_store["chunks"][i] for i in top_idxs])
                    groq_key = os.getenv("GROQ_API_KEY")
                    if not groq_key:
                        st.error("Missing GROQ_API_KEY in environment.")
                    else:
                        try:
                            client = Groq(api_key=groq_key)
                            messages = [
                                {"role": "system", "content": "You are a helpful assistant. Use the provided context to answer the user's question."},
                                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
                            ]
                            resp = client.chat.completions.create(
                                model="qwen/qwen3-32b",
                                messages=messages,
                                temperature=0.0,
                                max_completion_tokens=1024,
                                top_p=0.95,
                                stream=False
                            )
                            try:
                                answer = resp.choices[0].message.content
                            except Exception:
                                answer = str(resp)
                            st.markdown(f'<div class="answer-box">{answer}</div>', unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"Groq request failed: {e}")


with tab2:
    st.markdown('<div class="section-title">🧪 QA Copilot</div>', unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns([1, 1, 1], gap="large")

    with col_a:
        st.markdown("**Context & Data**")
        tc_file = st.file_uploader("Upload File (PDF, DOCX, JSON)", type=["pdf", "docx", "json"], key="tc_upload")
        tc_text_input = st.text_area("Paste Requirements", placeholder="Paste your requirements, feature description, or any text here...", height=200, key="tc_text_input")

    with col_b:
        st.markdown("**Testing Scope**")
        tc_count = st.number_input("Number of test cases", min_value=1, max_value=50, value=5, step=1, key="tc_count")
        
        st.markdown("**Generate:**")
        tc_manual = st.checkbox("✓ Manual Test Cases", value=True)
        tc_api = st.checkbox("✓ API Test Cases")
        tc_sec = st.checkbox("✓ Security Tests")
        tc_perf = st.checkbox("✓ Performance Tests")
        tc_edge = st.checkbox("✓ Edge Cases")
        tc_neg = st.checkbox("✓ Negative Scenarios")

    with col_c:
        st.markdown("**Automation Engine**")
        auto_fw = st.selectbox("Automation Framework", ["None", "Cypress", "Playwright", "Selenium Java", "Postman Collection"])
        tc_prompt = st.text_area("Custom Instructions", placeholder="e.g. focus on login flow...", height=80)
        btn_generate_qa = st.button("✨ Generate QA Suite", type="primary", use_container_width=True)

    if btn_generate_qa:
        pdf_text = ""
        manual_text = tc_text_input.strip()

        if tc_file:
            with st.spinner(f"Reading {tc_file.name}..."):
                from utils import extract_text_from_file # Ensure it's imported or available
                pdf_text = extract_text_from_file(tc_file).strip()
            if not pdf_text:
                st.warning(f"No text extracted from {tc_file.name} — falling back to pasted text only.")

        # Build combined context
        if pdf_text and manual_text:
            context = f"[From PDF]\n{pdf_text[:40000]}\n\n[Additional Text]\n{manual_text[:10000]}"
            source_label = "PDF + pasted text"
        elif pdf_text:
            context = pdf_text[:50000]
            source_label = "PDF"
        elif manual_text:
            context = manual_text[:50000]
            source_label = "pasted text"
        else:
            st.warning("Please upload a file or paste some text to generate the QA Suite.")
            context = None
            source_label = ""

        if context:
            groq_key = os.getenv("GROQ_API_KEY")
            if not groq_key:
                st.error("Missing GROQ_API_KEY in environment.")
            else:
                st.markdown("---")
                with st.spinner(f"Generating comprehensive QA Suite..."):
                    try:
                        client = Groq(api_key=groq_key)
                        
                        # Build Prompt Scope
                        scope_list = []
                        if tc_manual: scope_list.append("Manual Test Cases (title, steps, expected result)")
                        if tc_api: scope_list.append("API Test Cases (endpoint, payload, assertions)")
                        if tc_sec: scope_list.append("Security Tests (XSS, SQLi, Auth bypass etc.)")
                        if tc_perf: scope_list.append("Performance Tests (load, stress, latency)")
                        if tc_edge: scope_list.append("Edge Cases (boundary values, extreme states)")
                        if tc_neg: scope_list.append("Negative Scenarios (invalid inputs, error handling)")
                        
                        user_msg = f"Act as a Principal QA Automation Engineer. Based on the following context, generate a massive, highly professional testing suite.\n\n"
                        user_msg += f"**CONTEXT:**\n{context}\n\n"
                        user_msg += f"Please generate exactly {tc_count} total test cases, distributing them logically across the following requested categories:\n"
                        user_msg += "\n".join([f"- {s}" for s in scope_list])
                        
                        if auto_fw != "None":
                            user_msg += f"\n\n**AUTOMATION INSTRUCTIONS:**\n"
                            user_msg += f"After the test cases, write a production-ready automation script using {auto_fw} that covers the most critical happy-path scenarios. Ensure the code is wrapped in standard markdown code blocks (e.g. ```javascript or ```java or ```json)."
                            
                        if tc_prompt.strip():
                            user_msg += f"\n\n**ADDITIONAL INSTRUCTIONS:**\n{tc_prompt.strip()}"
                            
                        user_msg += "\n\nFormat the entire output beautifully with Markdown headers (###)."

                        messages = [
                            {"role": "system", "content": "You are an elite Software Development Engineer in Test (SDET). You write crystal clear test cases and perfect automation code."},
                            {"role": "user", "content": user_msg}
                        ]
                        
                        resp = client.chat.completions.create(
                            model="qwen/qwen3-32b",
                            messages=messages,
                            temperature=0.2,
                            max_completion_tokens=4000,
                            top_p=0.95,
                            stream=False
                        )
                        out = resp.choices[0].message.content
                        
                        st.markdown(f"### 🏆 Comprehensive QA Suite")
                        st.markdown(f"*Source: {source_label}*")
                        st.markdown(out)
                        
                    except Exception as e:
                        st.error(f"Groq request failed: {e}")


with tab3:
    st.markdown('<div class="section-title">🎨 AI Creative Studio</div>', unsafe_allow_html=True)
    
    col_left, col_center, col_right = st.columns([1, 1.5, 1], gap="medium")
    
    with col_left:
        st.markdown("**🎨 Creative Controls**")
        bg_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"], key="bg_upload_v2")
        brand_name = st.text_input("Brand Name", value="Mindflix", key="brand_name_v2")
        logo_file = st.file_uploader("Logo Upload (Optional)", type=["png"], key="logo_upload_v2")
        
        platform = st.radio("Platform", ["LinkedIn", "Instagram", "Facebook", "X"], horizontal=True)
        style = st.selectbox("Style", ["Corporate", "Futuristic", "Luxury", "Minimal", "Startup"])
        
    with col_center:
        st.markdown("**🖼️ Image Preview**")
        center_placeholder = st.empty()
        
        if not bg_file:
            center_placeholder.info("Upload an image on the left to see the preview here.")
        else:
            try:
                import io
                from PIL import Image
                if 'bg_file_id' not in st.session_state or st.session_state['bg_file_id'] != bg_file.file_id:
                    original_img = Image.open(io.BytesIO(bg_file.read())).convert("RGBA")
                    st.session_state['bg_original'] = original_img
                    st.session_state['bg_file_id'] = bg_file.file_id
                # Quick preview of current state
                center_placeholder.image(st.session_state['bg_original'], use_container_width=True)
            except Exception as e:
                center_placeholder.error(f"Error loading image: {e}")
                
    with col_right:
        st.markdown("**🤖 AI Enhancement**")
        st.markdown("- ✓ Add Brand Logo\n- ✓ Add AI Generated Quote\n- ✓ Create Marketing Headline\n- ✓ Generate CTA\n- ✓ Add Trending Hashtags\n- ✓ Create Multiple Variants")
        
        st.markdown("**Templates**")
        template = st.selectbox("", ["🚀 Product Launch", "📢 Announcement", "💡 Tip Of The Day", "🎯 Hiring", "📈 Growth Stats", "🤖 AI Quote", "📰 News Update"], label_visibility="collapsed")
        
        st.markdown("**AI Actions**")
        btn_generate = st.button("✨ Generate Campaign Assets", type="primary", use_container_width=True)
        btn_bg = st.button("✨ Remove Background", use_container_width=True)
        btn_enhance = st.button("✨ Enhance Image", use_container_width=True)
        btn_resize = st.button("✨ Resize for LinkedIn", use_container_width=True)
        
        if btn_bg and 'bg_original' in st.session_state:
            with st.spinner("Simulating smart background removal..."):
                img = st.session_state['bg_original'].convert("RGBA")
                datas = img.getdata()
                newData = []
                bg_color = datas[0] # assume top-left is background
                for item in datas:
                    if abs(item[0]-bg_color[0]) < 35 and abs(item[1]-bg_color[1]) < 35 and abs(item[2]-bg_color[2]) < 35:
                        newData.append((255, 255, 255, 0))
                    else:
                        newData.append(item)
                img.putdata(newData)
                st.session_state['bg_original'] = img
                center_placeholder.image(img, use_container_width=True)
                
        if btn_enhance and 'bg_original' in st.session_state:
            from PIL import ImageEnhance
            img = st.session_state['bg_original'].convert("RGB")
            img = ImageEnhance.Color(img).enhance(1.3)
            img = ImageEnhance.Contrast(img).enhance(1.15)
            img = ImageEnhance.Sharpness(img).enhance(1.4)
            img = img.convert("RGBA")
            st.session_state['bg_original'] = img
            center_placeholder.image(img, use_container_width=True)
            
        if btn_resize and 'bg_original' in st.session_state:
            img = st.session_state['bg_original']
            width, height = img.size
            new_size = min(width, height)
            left = (width - new_size)/2
            top = (height - new_size)/2
            right = (width + new_size)/2
            bottom = (height + new_size)/2
            img = img.crop((left, top, right, bottom))
            from PIL import Image
            img = img.resize((1200, 1200), Image.Resampling.LANCZOS)
            st.session_state['bg_original'] = img
            center_placeholder.image(img, use_container_width=True)
        
    # Generate Output Grid below if clicked
    if btn_generate and st.session_state.get('bg_original'):
        st.markdown("---")
        st.markdown("### 🏆 AI Generated Variants")
        
        with st.spinner("Generating marketing copy and rendering variants..."):
            try:
                # 1. Groq LLM Generation
                import os
                from groq import Groq
                groq_key = os.getenv("GROQ_API_KEY")
                quotes = [
                    "The Future of Automation Starts Here",
                    "Transform Ideas Into Reality",
                    "Powered by AI Excellence"
                ]
                
                if groq_key:
                    client = Groq(api_key=groq_key)
                    prompt = f"Generate 3 very short (3-6 words) punchy marketing headlines for a brand named '{brand_name}' targeting '{platform}' in a '{style}' tone for a '{template}' post. Output ONLY the 3 headlines on separate lines, no numbers, no quotes."
                    resp = client.chat.completions.create(
                        model="qwen/qwen3-32b",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7,
                        max_completion_tokens=150
                    )
                    out_lines = [line.strip().strip('"').strip("'") for line in resp.choices[0].message.content.strip().split('\n') if line.strip()]
                    if len(out_lines) >= 3:
                        quotes = out_lines[:3]
                
                # 2. Setup Font Download
                import urllib.request
                import os
                from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
                font_path = "Roboto-Bold.ttf"
                if not os.path.exists(font_path):
                    urllib.request.urlretrieve("https://raw.githubusercontent.com/googlefonts/roboto/main/src/hinted/Roboto-Bold.ttf", font_path)
                
                # 3. Render Variants
                base_img = st.session_state['bg_original'].copy()
                w, h = base_img.size
                
                # Dynamic font sizing
                title_font_size = int(h * 0.08)
                brand_font_size = int(h * 0.04)
                try:
                    title_font = ImageFont.truetype(font_path, title_font_size)
                    brand_font = ImageFont.truetype(font_path, brand_font_size)
                except Exception:
                    title_font = ImageFont.load_default()
                    brand_font = ImageFont.load_default()
                
                def render_variant(img, quote, filter_type):
                    v_img = img.copy()
                    # Apply filter
                    if filter_type == "Corporate":
                        tint = Image.new("RGBA", v_img.size, (0, 50, 100, 50))
                        v_img = Image.alpha_composite(v_img, tint)
                    elif filter_type == "Startup":
                        enhancer = ImageEnhance.Color(v_img)
                        v_img = enhancer.enhance(1.4)
                    elif filter_type == "Futuristic":
                        tint = Image.new("RGBA", v_img.size, (200, 0, 255, 40))
                        v_img = Image.alpha_composite(v_img, tint)
                        enhancer = ImageEnhance.Contrast(v_img)
                        v_img = enhancer.enhance(1.2)
                    
                    # Draw Text
                    draw = ImageDraw.Draw(v_img)
                    # Overlay dark gradient at bottom for text readability
                    grad = Image.new('RGBA', (w, int(h*0.4)), color=(0,0,0,0))
                    g_draw = ImageDraw.Draw(grad)
                    for i in range(int(h*0.4)):
                        alpha = int(255 * (i / (h*0.4)))
                        g_draw.line([(0, i), (w, i)], fill=(0, 0, 0, alpha))
                    v_img.paste(grad, (0, int(h*0.6)), grad)
                    
                    # Wrap text
                    import textwrap
                    wrapped_quote = textwrap.fill(quote, width=25)
                    
                    # Need bbox for height
                    try:
                        bbox = draw.multiline_textbbox((0,0), wrapped_quote, font=title_font)
                        text_h = bbox[3] - bbox[1]
                    except Exception:
                        text_h = title_font_size * 2
                    
                    draw.multiline_text((int(w*0.05), int(h*0.85) - text_h), wrapped_quote, fill="white", font=title_font)
                    draw.text((int(w*0.05), int(h*0.92)), f"Powered by {brand_name}", fill="#00f2fe", font=brand_font)
                    
                    # Convert to RGB for Streamlit/Download
                    return v_img.convert("RGB")
                
                v1 = render_variant(base_img, quotes[0] if len(quotes) > 0 else "Corporate Update", "Corporate")
                v2 = render_variant(base_img, quotes[1] if len(quotes) > 1 else "Startup Mode", "Startup")
                v3 = render_variant(base_img, quotes[2] if len(quotes) > 2 else "Futuristic Vision", "Futuristic")
                
                col_o1, col_o2, col_o3, col_o4 = st.columns(4)
                with col_o1:
                    st.markdown("**Original**")
                    st.image(base_img.convert("RGB"), use_container_width=True)
                with col_o2:
                    st.markdown("**Corporate**")
                    st.image(v1, use_container_width=True)
                with col_o3:
                    st.markdown("**Startup**")
                    st.image(v2, use_container_width=True)
                with col_o4:
                    st.markdown("**Futuristic**")
                    st.image(v3, use_container_width=True)
                
            except Exception as e:
                import traceback
                st.error(f"Error during generation: {e}\n{traceback.format_exc()}")

with tab4:
    st.markdown('<div class="section-title">🧬 Brand Intelligence & AI Visuals Generator</div>', unsafe_allow_html=True)
    st.markdown("Extract your Brand Intelligence and generate brand-compliant marketing images using AI.")
    
    col_dna1, col_dna2 = st.columns([1, 1], gap="large")
    
    with col_dna1:
        st.markdown("**Paste Brand Guidelines / Aesthetic Rules**")
        dna_guidelines = st.text_area("", height=150, placeholder="e.g. Minimalist, neon cyan and dark blue, energetic tone, targeting young professionals...", key="dna_guidelines")
        
        st.markdown("**Campaign Goal**")
        dna_goal = st.text_input("", placeholder="e.g. Instagram post for summer sale", key="dna_goal")
        
        generate_btn = st.button("Extract Intelligence & Generate Image", key="dna_btn")
        
    with col_dna2:
        if generate_btn:
            if not dna_guidelines or not dna_goal:
                st.warning("Please provide both guidelines and a campaign goal.")
            else:
                with st.spinner("🧠 Extracting Brand Intelligence..."):
                    # 1. Extract Intelligence using Groq
                    try:
                        import os
                        from groq import Groq
                        
                        groq_key = os.getenv("GROQ_API_KEY")
                        if not groq_key:
                            st.error("Missing GROQ_API_KEY in environment.")
                            st.stop()
                            
                        client = Groq(api_key=groq_key)
                        prompt = f"""
                        You are an expert Brand Designer. 
                        Read these guidelines: "{dna_guidelines}"
                        And this campaign goal: "{dna_goal}"
                        
                        Write a highly detailed, 1-paragraph Image Generation Prompt (for DALL-E/Stable Diffusion) that incorporates the exact visual style, colors, and tone from the guidelines to accomplish the campaign goal.
                        Output ONLY the prompt text, no intro, no extra text.
                        """
                        
                        messages = [{"role": "user", "content": prompt}]
                        resp = client.chat.completions.create(
                            model="qwen/qwen3-32b",
                            messages=messages,
                            temperature=0.7,
                            max_completion_tokens=512
                        )
                        optimized_prompt = resp.choices[0].message.content.strip()
                        
                        st.success("Intelligence Extracted & Prompt Engineered!")
                        with st.expander("View Optimized Image Prompt"):
                            st.write(optimized_prompt)
                            
                        # 2. Call SubNP Free API
                        st.markdown("### 🎨 Generating Final Asset...")
                        status_text = st.empty()
                        img_container = st.empty()
                        
                        status_text.info("Initiating Image Generation... (this takes ~10-15s)")
                        
                        # Use requests directly
                        try:
                            response = requests.post(
                                "https://subnp.com/api/free/generate",
                                json={"prompt": optimized_prompt, "model": "magic"},
                                stream=True,
                                timeout=60
                            )
                            
                            final_img_url = None
                            api_error = None
                            for line in response.iter_lines():
                                if line:
                                    decoded_line = line.decode('utf-8')
                                    if decoded_line.startswith('data: '):
                                        data_str = decoded_line[6:]
                                        try:
                                            data = json.loads(data_str)
                                            if data.get('status') == 'processing':
                                                status_text.info(f"Progress: {data.get('message', 'Generating...')}")
                                            elif data.get('status') == 'complete':
                                                final_img_url = data.get('imageUrl')
                                                break
                                            elif data.get('status') == 'error':
                                                api_error = data.get('message', data.get('error', 'Unknown API Error'))
                                                break
                                        except json.JSONDecodeError:
                                            pass
                                            
                            if final_img_url:
                                status_text.success("✨ Asset generated successfully!")
                                img_container.image(final_img_url, use_container_width=True)
                            elif api_error:
                                status_text.error(f"API Error: {api_error}")
                            else:
                                status_text.error("Failed to retrieve image URL from API (No error provided).")
                        except Exception as req_e:
                            status_text.error(f"API Request Failed: {req_e}")
                            
                    except Exception as e:
                        import traceback
                        st.error(f"Error extracting Intelligence: {e}\n{traceback.format_exc()}")
