import streamlit as st
import io
import json
from pypdf import PdfReader
from docx import Document

from langchain_text_splitters import RecursiveCharacterTextSplitter
from groq import Groq

from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(
    page_title="Mind Setters Academy — PDF Chatbot",
    page_icon="https://mindsetters.sg/favicon.ico",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* Global font */
    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
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

    /* Page background */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        min-height: 100vh;
    }

    /* Hero banner */
    .hero {
        text-align: center;
        padding: 2.5rem 1rem 1.5rem;
    }
    .hero h1 {
        font-size: 2.8rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.5px;
        margin-bottom: 0.3rem;
    }
    .hero p {
        color: #a78bfa;
        font-size: 1.05rem;
        margin-top: 0;
    }

    /* Card containers */
    .card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.8rem 2rem;
        margin-bottom: 1.2rem;
        backdrop-filter: blur(10px);
    }

    /* Section headings */
    .section-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #c4b5fd;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.8rem;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: transparent;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        padding-bottom: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,0.05);
        border-radius: 10px 10px 0 0;
        color: #a78bfa;
        font-weight: 600;
        padding: 0.5rem 1.4rem;
        border: 1px solid rgba(255,255,255,0.08);
        border-bottom: none;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
        color: white !important;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #7c3aed, #4f46e5);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.55rem 2rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: opacity 0.2s;
        width: 100%;
    }
    .stButton > button:hover {
        opacity: 0.85;
        color: white;
    }

    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input {
        background: rgba(255,255,255,0.07) !important;
        border: 1px solid rgba(167,139,250,0.4) !important;
        border-radius: 10px !important;
        color: #f3f4f6 !important;
        caret-color: #f3f4f6 !important;
        padding: 0.6rem 1rem !important;
    }
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: #9ca3af !important;
        opacity: 1 !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #7c3aed !important;
        box-shadow: 0 0 0 2px rgba(124,58,237,0.3) !important;
    }

    /* File uploader */
    .stFileUploader > div {
        background: rgba(255,255,255,0.04) !important;
        border: 2px dashed rgba(167,139,250,0.5) !important;
        border-radius: 12px !important;
        padding: 1.2rem !important;
        color: #d8b4fe !important;
    }
    .stFileUploader label, .stFileUploader span, .stFileUploader p {
        color: #d8b4fe !important;
    }

    /* Labels */
    label, .stTextInput label, .stTextArea label, .stNumberInput label,
    .stFileUploader label, p, span {
        color: #d8b4fe !important;
        font-weight: 500 !important;
    }

    /* General text */
    .stMarkdown, .stMarkdown p, .stMarkdown li, div[data-testid="stMarkdownContainer"] p {
        color: #f3f4f6 !important;
    }

    /* Answer box */
    .answer-box {
        background: rgba(124, 58, 237, 0.12);
        border-left: 4px solid #7c3aed;
        border-radius: 0 12px 12px 0;
        padding: 1.2rem 1.5rem;
        color: #f3f4f6;
        line-height: 1.7;
        margin-top: 1rem;
    }

    /* Alerts */
    .stSuccess, .stInfo, .stWarning, .stError {
        border-radius: 10px !important;
    }

    /* Divider */
    hr {
        border-color: rgba(255,255,255,0.08);
    }

    /* Navbar */
    .navbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.8rem 2rem;
        background: rgba(255,255,255,0.04);
        border-bottom: 1px solid rgba(167,139,250,0.2);
        margin-bottom: 0.5rem;
        backdrop-filter: blur(10px);
    }
    .navbar-brand {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .navbar-logo {
        height: 42px;
        width: auto;
        border-radius: 8px;
    }
    .navbar-name {
        font-size: 1.25rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.3px;
        line-height: 1.2;
    }
    .navbar-tagline {
        font-size: 0.72rem;
        color: #a78bfa;
        font-weight: 400;
        letter-spacing: 0.5px;
    }
    .navbar-badge {
        background: linear-gradient(135deg, #7c3aed, #4f46e5);
        color: white;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.3rem 0.9rem;
        border-radius: 20px;
        letter-spacing: 0.5px;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #7c3aed; border-radius: 3px; }
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
             src="https://mindsetters.sg/favicon.ico"
             onerror="this.style.display='none'"
             alt="Mind Setters Academy Logo">
        <div>
            <div class="navbar-name">Mind Setters Academy</div>
            <div class="navbar-tagline">mindsetters.sg &nbsp;·&nbsp; Empowering Every Learner</div>
        </div>
    </div>
    <div class="navbar-badge">AI Tools</div>
</div>
""", unsafe_allow_html=True)

# Hero
st.markdown("""
<div class="hero">
    <h1>📄 PDF Chatbot</h1>
    <p>Powered by Mind Setters Academy &nbsp;·&nbsp; Ask questions or generate test cases from PDF, DOCX, or JSON</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["💬  Upload & QA", "🧪  Test Case Generator"])

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
    st.markdown('<div class="section-title">🧪 Generate Test Cases</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns([1, 1.6], gap="large")

    with col_a:
        st.markdown("**Upload File** *(PDF, DOCX, JSON — optional)*")
        tc_file = st.file_uploader("", type=["pdf", "docx", "json"], key="tc_upload", label_visibility="collapsed")
        st.markdown("**Number of test cases**")
        tc_count = st.number_input("", min_value=1, max_value=50, value=5, step=1, key="tc_count", label_visibility="collapsed")

    with col_b:
        st.markdown("**Paste text / requirements** *(optional if PDF uploaded)*")
        tc_text_input = st.text_area("", placeholder="Paste your requirements, feature description, or any text here...", height=140, key="tc_text_input", label_visibility="collapsed")
        st.markdown("**Additional instructions** *(optional)*")
        tc_prompt = st.text_area("", placeholder="e.g. focus on edge cases, generate unit tests, include invalid inputs", height=80, label_visibility="collapsed")
        st.button("Generate Test Cases", key="tc_button")

    if st.session_state.get("tc_button"):
        pdf_text = ""
        manual_text = tc_text_input.strip()

        if tc_file:
            with st.spinner(f"Reading {tc_file.name}..."):
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
            st.warning("Please upload a PDF or paste some text to generate test cases.")
            context = None
            source_label = ""

        if context:
            groq_key = os.getenv("GROQ_API_KEY")
            if not groq_key:
                st.error("Missing GROQ_API_KEY in environment.")
            else:
                with st.spinner(f"Generating test cases from {source_label}..."):
                    try:
                        client = Groq(api_key=groq_key)
                        user_msg = f"Generate {tc_count} concise, actionable test cases (title + short description + example input/output where applicable) based on the following context:\n\n{context}"
                        if tc_prompt.strip():
                            user_msg += f"\n\nAdditional instructions: {tc_prompt.strip()}"
                        messages = [
                            {"role": "system", "content": "You are an assistant that generates clear test cases for software components."},
                            {"role": "user", "content": user_msg}
                        ]
                        resp = client.chat.completions.create(
                            model="qwen/qwen3-32b",
                            messages=messages,
                            temperature=0.0,
                            max_completion_tokens=2048,
                            top_p=0.95,
                            stream=False
                        )
                        try:
                            out = resp.choices[0].message.content
                        except Exception:
                            out = str(resp)
                        st.markdown(f'<div class="section-title" style="margin-top:1.5rem;">Generated Test Cases <span style="font-size:0.75rem;opacity:0.6;">· source: {source_label}</span></div>', unsafe_allow_html=True)
                        st.code(out, language="markdown")
                    except Exception as e:
                        st.error(f"Groq request failed: {e}")
