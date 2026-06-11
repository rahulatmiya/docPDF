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
            <div class="navbar-tagline">Mindflix &nbsp;·&nbsp; Empowering Every Learner</div>
        </div>
    </div>
    <div class="navbar-badge">AI Tools</div>
</div>
""", unsafe_allow_html=True)

# Hero
st.markdown("""
<div class="hero">
    <h1>📄 PDF Chatbot</h1>
    <p>Powered by Mindflix &nbsp;·&nbsp; Ask questions or generate test cases from PDF, DOCX, or JSON</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["💬  Upload & QA", "🧪  Test Case Generator", "🖼️ BrandGen", "🧬 Brand DNA"])

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


with tab3:
    st.markdown('<div class="section-title">🖼️ BrandGen: Image Watermarking & Filters</div>', unsafe_allow_html=True)
    
    st.markdown("**Upload Image** *(PNG, JPG, JPEG)*")
    bg_file = st.file_uploader("", type=["png", "jpg", "jpeg"], key="bg_upload", label_visibility="collapsed")
    
    col_c, col_d = st.columns([1, 1], gap="large")
    with col_c:
        st.markdown("**Filter Style**")
        bg_filter = st.selectbox("", ["Mindflix Signature", "Vibrant", "Cinematic", "Vintage", "None"], key="bg_filter", label_visibility="collapsed")
    with col_d:
        st.markdown("**Brand Text**")
        bg_text = st.text_input("", value="Mindflix", key="bg_text", label_visibility="collapsed")
        
    st.button("Apply Branding", key="bg_button")
        
    if st.session_state.get("bg_button") and bg_file:
        try:
            start_time = time.time()
            
            # Open image
            original_image = Image.open(io.BytesIO(bg_file.read())).convert("RGBA")
            image = original_image.copy()
            
            # --- APPLY FILTERS ---
            if bg_filter != "None":
                img_rgb = image.convert("RGB")
                
                if bg_filter in ["Mindflix Signature", "Vibrant"]:
                    enhancer = ImageEnhance.Color(img_rgb)
                    img_rgb = enhancer.enhance(1.3)
                    enhancer = ImageEnhance.Contrast(img_rgb)
                    img_rgb = enhancer.enhance(1.1)
                    enhancer = ImageEnhance.Sharpness(img_rgb)
                    img_rgb = enhancer.enhance(1.2)
                    
                if bg_filter in ["Cinematic", "Mindflix Signature"]:
                    tint = Image.new("RGB", img_rgb.size, (0, 100, 150))
                    img_rgb = Image.blend(img_rgb, tint, alpha=0.1)
                    enhancer = ImageEnhance.Brightness(img_rgb)
                    img_rgb = enhancer.enhance(0.9)
                    
                if bg_filter == "Vintage":
                    tint = Image.new("RGB", img_rgb.size, (255, 150, 0))
                    img_rgb = Image.blend(img_rgb, tint, alpha=0.15)
                    enhancer = ImageEnhance.Contrast(img_rgb)
                    img_rgb = enhancer.enhance(0.8)
                    
                if bg_filter in ["Mindflix Signature", "Cinematic", "Vintage"]:
                    import math
                    w, h = img_rgb.size
                    from PIL import ImageFilter
                    vignette = Image.new("L", (w, h), 0)
                    d = ImageDraw.Draw(vignette)
                    for i in range(min(w, h) // 2, min(w, h), 5):
                        d.ellipse((w/2 - i, h/2 - i, w/2 + i, h/2 + i), outline=int(255 * (i / min(w, h))), width=5)
                    vignette = vignette.filter(ImageFilter.GaussianBlur(min(w, h) * 0.1))
                    dark = Image.new("RGB", img_rgb.size, (0, 0, 0))
                    img_rgb = Image.composite(dark, img_rgb, vignette)
                
                image = img_rgb.convert("RGBA")
            
            # --- APPLY WATERMARK ---
            txt_img = Image.new("RGBA", image.size, (255, 255, 255, 0))
            d = ImageDraw.Draw(txt_img)
            font_size = int(image.width * 0.05)
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            bbox = d.textbbox((0, 0), bg_text, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            
            margin = int(image.width * 0.02)
            x = image.width - text_w - margin
            y = image.height - text_h - margin
            
            outline_color = (0, 0, 0, 150)
            text_color = (0, 242, 254, 230)
            for adj in range(-2, 3):
                d.text((x+adj, y), bg_text, font=font, fill=outline_color)
                d.text((x, y+adj), bg_text, font=font, fill=outline_color)
            d.text((x, y), bg_text, font=font, fill=text_color)
            
            out = Image.alpha_composite(image, txt_img).convert("RGB")
            orig_rgb = original_image.convert("RGB")
            
            st.markdown('<div class="section-title">✨ Final Result</div>', unsafe_allow_html=True)
            st.image(out, use_container_width=True)
            
            # Download button
            buf_out = io.BytesIO()
            out.save(buf_out, format="JPEG", quality=95)
            
            st.download_button(
                label="Download Branded Image",
                data=buf_out.getvalue(),
                file_name="brandgen_result.jpg",
                mime="image/jpeg"
            )
            
        except Exception as e:
            import traceback
            st.error(f"Error processing image: {e}\\n{traceback.format_exc()}")
    elif st.session_state.get("bg_button"):
        st.warning("Please upload an image first.")

with tab4:
    st.markdown('<div class="section-title">🧬 Brand DNA & AI Visuals Generator</div>', unsafe_allow_html=True)
    st.markdown("Extract your Brand DNA and generate brand-compliant marketing images using AI.")
    
    col_dna1, col_dna2 = st.columns([1, 1], gap="large")
    
    with col_dna1:
        st.markdown("**Paste Brand Guidelines / Aesthetic Rules**")
        dna_guidelines = st.text_area("", height=150, placeholder="e.g. Minimalist, neon cyan and dark blue, energetic tone, targeting young professionals...", key="dna_guidelines")
        
        st.markdown("**Campaign Goal**")
        dna_goal = st.text_input("", placeholder="e.g. Instagram post for summer sale", key="dna_goal")
        
        generate_btn = st.button("Extract DNA & Generate Image", key="dna_btn")
        
    with col_dna2:
        if generate_btn:
            if not dna_guidelines or not dna_goal:
                st.warning("Please provide both guidelines and a campaign goal.")
            else:
                with st.spinner("🧠 Extracting Brand DNA..."):
                    # 1. Extract DNA using Groq
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
                        
                        st.success("DNA Extracted & Prompt Engineered!")
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
                        st.error(f"Error extracting DNA: {e}\n{traceback.format_exc()}")
