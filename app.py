import requests
import json
import streamlit as st
import requests
from bs4 import BeautifulSoup
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
    initial_sidebar_state="expanded"
)

# Handle query parameter routing from dashboard cards
if "nav" in st.query_params:
    nav_val = st.query_params["nav"]
    nav_map = {
        "docs": "📄 Docs AI",
        "qa": "🧪 QA Copilot",
        "social": "🎨 Social Studio",
        "brand": "🧬 Brand Intelligence",
        "billing": "💰 Billing",
        "latex": "📝 LaTeX Studio"
    }
    if nav_val in nav_map:
        st.session_state.current_page = nav_map[nav_val]
    # Clear the parameter so it doesn't get stuck in the URL
    del st.query_params["nav"]


# Project State Initialization
if 'active_project' not in st.session_state:
    st.session_state.active_project = "Mindflix Website"
if 'projects' not in st.session_state:
    st.session_state.projects = {
        "Mindflix Website": {
            "files": ["BRD_v2.pdf", "API_Spec.docx"],
            "generated": ["Test Cases", "Cypress Scripts", "Social Posts", "Brand Analysis"]
        },
        "Login Automation": {
            "files": ["Login_Flow.pdf"],
            "generated": ["Playwright Scripts"]
        }
    }



# Global Sidebar
if "current_page" not in st.session_state:
    st.session_state.current_page = "🏠 Dashboard"

current_page = st.session_state.current_page

st.markdown('''<style>[data-testid="collapsedControl"] { display: none; }</style>''', unsafe_allow_html=True)

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
        margin-bottom: 2rem;
    }
    .recent-projects-section {
        margin: 4rem auto;
        max-width: 800px;
        text-align: left;
    }
    .recent-projects-section h3 {
        color: #ffffff;
        font-size: 1.3rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    .projects-grid {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    .project-card {
        background: rgba(255, 255, 255, 0.02);
        border: none;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        color: #cbd5e1;
        cursor: pointer;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        gap: 15px;
        font-weight: 400;
    }
    .project-card:hover {
        background: rgba(255, 255, 255, 0.06);
        color: #ffffff;
    }
    .project-card span {
        font-size: 1.2rem;
    }
    

    .quick-actions-section {
        margin: 2rem auto 4rem;
        max-width: 1000px;
        text-align: center;
    }
    .quick-actions-grid {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 15px;
    }
    .quick-action-btn {
        background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 0.7rem 1.5rem;
        border-radius: 30px;
        color: #e2e8f0;
        font-weight: 500;
        font-size: 0.95rem;
        cursor: pointer;
        transition: all 0.3s ease;
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }
    .quick-action-btn:hover {
        background: rgba(0, 242, 254, 0.1);
        border-color: #00f2fe;
        transform: translateY(-2px);
        color: #ffffff;
        box-shadow: 0 5px 15px rgba(0, 242, 254, 0.2);
    }
    .hero-ctas {
        display: flex;
        justify-content: center;
        gap: 15px;
        margin-bottom: 3rem;
    }
    .cta-primary, .cta-secondary {
        padding: 0.8rem 1.8rem;
        font-size: 1rem;
        font-weight: 600;
        border-radius: 30px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .cta-primary {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        color: white;
        border: none;
        box-shadow: 0 4px 15px rgba(0, 242, 254, 0.4);
    }
    .cta-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 242, 254, 0.6);
    }
    .cta-secondary {
        background: transparent;
        color: #00f2fe;
        border: 2px solid #00f2fe;
    }
    .cta-secondary:hover {
        background: rgba(0, 242, 254, 0.1);
        transform: translateY(-2px);
    }
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
        transform: translateY(-8px);
        background: rgba(255, 255, 255, 0.06);
        border-color: rgba(0, 242, 254, 0.4);
        box-shadow: 0 0 30px rgba(0, 255, 255, 0.25);
    }
    .animated-card .card-action {
        display: block;
        margin-top: 15px;
        font-size: 0.85rem;
        font-weight: 600;
        color: #00f2fe;
        opacity: 0;
        transform: translateY(10px);
        transition: all 0.3s ease;
    }
    .animated-card:hover .card-action {
        opacity: 1;
        transform: translateY(0);
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
        justify-content: space-around;
        gap: 20px;
        margin: 4rem auto;
        max-width: 1000px;
        text-align: center;
    }
    .kpi-card {
        background: transparent;
        border: none;
        padding: 0;
        border-radius: 0;
        box-shadow: none;
    }
    .kpi-card .kpi-num {
        display: block;
        font-size: 2.5rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #00f2fe, #4facfe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }
    .kpi-card .kpi-label {
        font-size: 0.8rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
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
    .navbar-right {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    .user-menu-wrapper {
        position: relative;
        display: inline-block;
    }
    .user-menu-btn {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #e2e8f0;
        padding: 6px 15px;
        border-radius: 20px;
        cursor: pointer;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s;
    }
    .user-menu-btn:hover {
        background: rgba(255, 255, 255, 0.1);
        color: #ffffff;
    }
    .user-menu-dropdown {
        display: none;
        position: absolute;
        right: 0;
        top: calc(100% + 10px);
        background: rgba(15, 23, 42, 0.95);
        min-width: 150px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.5);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        z-index: 10000;
        backdrop-filter: blur(10px);
        overflow: hidden;
    }
    .user-menu-wrapper:hover .user-menu-dropdown {
        display: flex;
        flex-direction: column;
    }
    .user-menu-dropdown a {
        color: #e2e8f0;
        padding: 10px 15px;
        text-decoration: none;
        font-size: 0.9rem;
        transition: background 0.2s;
    }
    .user-menu-dropdown a:hover {
        background: rgba(0, 242, 254, 0.1);
        color: #00f2fe;
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
    .testimonial-section {
        margin: 5rem auto;
        max-width: 1200px;
        text-align: center;
    }
    .testimonial-section h3 {
        color: #ffffff;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 3rem;
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .testimonial-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
        padding: 1rem;
    }
    .testimonial-card {
        background: rgba(15, 23, 42, 0.6);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(0, 242, 254, 0.15);
        padding: 2.5rem 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
    }
    .testimonial-card::before {
        content: '"';
        position: absolute;
        top: -20px;
        left: 20px;
        font-size: 8rem;
        color: rgba(0, 242, 254, 0.05);
        font-family: serif;
        z-index: 0;
    }
    .testimonial-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 20px 50px rgba(0, 242, 254, 0.2);
        border-color: rgba(0, 242, 254, 0.5);
    }
    .testimonial-text {
        color: #e2e8f0;
        font-size: 1.1rem;
        font-style: italic;
        margin-bottom: 2rem;
        line-height: 1.7;
        position: relative;
        z-index: 1;
    }
    .testimonial-author {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        gap: 15px;
        border-top: 1px solid rgba(255,255,255,0.05);
        padding-top: 1.5rem;
        position: relative;
        z-index: 1;
    }
    .testimonial-author img {
        width: 55px;
        height: 55px;
        border-radius: 50%;
        border: 2px solid transparent;
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%) border-box;
        -webkit-mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: destination-out;
        mask-composite: exclude;
        padding: 2px;
        box-shadow: 0 0 15px rgba(0,242,254,0.3);
    }
    .testimonial-author div {
        text-align: left;
    }
    .testimonial-author strong {
        display: block;
        color: #ffffff;
        font-size: 1.15rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .testimonial-author span {
        color: #00f2fe;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    .avatar-initials {
        width: 55px;
        height: 55px;
        min-width: 55px;
        border-radius: 50%;
        background: linear-gradient(135deg, rgba(0, 242, 254, 0.1) 0%, rgba(79, 172, 254, 0.2) 100%);
        border: 2px solid #00f2fe;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #ffffff;
        font-weight: 800;
        font-size: 1.2rem;
        letter-spacing: 1px;
        box-shadow: 0 0 15px rgba(0,242,254,0.3);
    }
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
<div class="navbar-right">
<div class="navbar-badge">AI Tools</div>
</div>
</div>
""", unsafe_allow_html=True)


if current_page != "🏠 Dashboard" and current_page not in ["📧 Inquiry"]:
    active_docs = "active" if current_page == "📄 Docs AI" else ""
    active_qa = "active" if current_page == "🧪 QA Copilot" else ""
    active_social = "active" if current_page == "🎨 Social Studio" else ""
    active_brand = "active" if current_page == "🧬 Brand Intelligence" else ""
    active_billing = "active" if current_page == "💰 Billing" else ""
    active_latex = "active" if current_page == "📝 LaTeX Studio" else ""
    
    st.markdown(f"""
    <style>
    .global-nav-tabs {{
        display: flex;
        gap: 8px;
        margin-top: 10px;
        margin-bottom: 30px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 0px;
    }}
    .global-tab {{
        background-color: rgba(30, 41, 59, 0.2);
        padding: 10px 20px;
        color: #94a3b8;
        text-decoration: none !important;
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-bottom: none;
        border-radius: 8px 8px 0 0;
        font-weight: 500;
        transition: all 0.3s;
    }}
    .global-tab:hover {{
        color: #e2e8f0;
        background-color: rgba(255,255,255,0.05);
    }}
    .global-tab.active {{
        color: #00f2fe !important;
        background-color: rgba(0, 242, 254, 0.1) !important;
        border-color: rgba(0, 242, 254, 0.3) !important;
    }}
    </style>
    <div class="global-nav-tabs">
        <a href="?nav=home" target="_self" class="global-tab">🏠 Home</a>
        <a href="?nav=docs" target="_self" class="global-tab {active_docs}">📄 Documents</a>
        <a href="?nav=qa" target="_self" class="global-tab {active_qa}">🧪 QA Copilot</a>
        <a href="?nav=social" target="_self" class="global-tab {active_social}">🎨 Social Studio</a>
        <a href="?nav=brand" target="_self" class="global-tab {active_brand}">🧬 Brand Intelligence</a>
        <a href="?nav=billing" target="_self" class="global-tab {active_billing}">🧾 Billing Studio</a>
        <a href="?nav=latex" target="_self" class="global-tab {active_latex}">📝 LaTeX Studio</a>
    </div>
    """, unsafe_allow_html=True)




def render_docs_ai():
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



def render_qa_copilot():
        st.markdown('<div class="section-title">🧪 QA Copilot</div>', unsafe_allow_html=True)

        col_a, col_b, col_c = st.columns([1, 1, 1], gap="large")

        with col_a:
            st.markdown("**Context & Data**")
            tc_url_input = st.text_input("Scan Web URL", placeholder="https://example.com", key="tc_url_input")
            tc_file = st.file_uploader("Upload File (PDF, DOCX, JSON)", type=["pdf", "docx", "json"], key="tc_upload")
            tc_text_input = st.text_area("Paste Requirements", placeholder="Paste your requirements, feature description, or any text here...", height=130, key="tc_text_input")

        with col_b:
            st.markdown("**Testing Scope**")
            tc_count = st.number_input("Number of test cases", min_value=1, max_value=50, value=5, step=1, key="tc_count")
        
            st.markdown("**Generate:**")
            tc_manual = st.checkbox("✓ Manual Test Cases", value=True)
            tc_a11y = st.checkbox("✓ Accessibility (a11y) Scan", value=True)
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
                            if tc_a11y: scope_list.append("Accessibility (a11y) Tests (WCAG compliance, ARIA roles, missing alt tags, semantic HTML)")
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



def render_social_studio():
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


def render_brand_intelligence():
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



def render_billing_studio():
        st.markdown('<div class="section-title">🧾 Billing Studio</div>', unsafe_allow_html=True)
    
        col_l, col_preview, col_r = st.columns([1, 1.8, 1], gap="medium")
    
        with col_l:
            st.markdown("**Company Details**")
            comp_name = st.text_input("Your Company Name", value="Mindflix AI")
            comp_addr = st.text_input("Your Address", value="123 AI Boulevard, Tech City")
        
            st.markdown("**Client Details**")
            client_name = st.text_input("Billed To", value="Acme Corp")
            client_addr = st.text_input("Client Address", value="456 Enterprise Way")
        
            st.markdown("**Invoice Details**")
            inv_num = st.text_input("Invoice #", value="INV-2026-001")
            inv_date = st.text_input("Date", value="Jun 12, 2026")
        
            st.markdown("**Line Items (Item | Qty | Price)**")
            default_items = "Enterprise API License | 1 | 5000\nCustom Integration Support | 10 | 150"
            items_raw = st.text_area("", value=default_items, height=120, label_visibility="collapsed")
        
            tax_pct = st.number_input("Tax Rate (%)", min_value=0.0, max_value=50.0, value=10.0, step=1.0)
        
        with col_r:
            st.markdown("**Invoice Styling**")
            template_var = st.selectbox("Select Template", ["Modern Tech", "Classic Corporate", "Minimalist Startup", "Vibrant Creative"])
        
            st.markdown("**AI Assistant**")
            ai_inv_text = st.text_area("Paste Contract/Email to Auto-fill", height=100)
            if st.button("✨ AI Auto-Fill Invoice", use_container_width=True):
                st.info("AI Auto-fill simulated: Parsed client and items successfully!")
            
            st.markdown("---")
            st.markdown("### Export")
            st.caption("To export this invoice as a high-quality PDF, right-click the preview area and select **Print -> Save as PDF**.")

        with col_preview:
            # Parse items
            parsed_items = []
            subtotal = 0
            for line in items_raw.split("\n"):
                if "|" in line:
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) >= 3:
                        try:
                            qty = float(parts[1])
                            price = float(parts[2])
                            total = qty * price
                            subtotal += total
                            parsed_items.append({"name": parts[0], "qty": qty, "price": price, "total": total})
                        except:
                            pass
        
            tax_amt = subtotal * (tax_pct / 100.0)
            grand_total = subtotal + tax_amt
        
            # Build HTML Rows
            rows_html = ""
            for i, item in enumerate(parsed_items):
                rows_html += f"<tr><td>{item['name']}</td><td>{item['qty']}</td><td>${item['price']:,.2f}</td><td>${item['total']:,.2f}</td></tr>"

            # Theme definitions
            themes = {
                "Modern Tech": {"bg": "#ffffff", "text": "#1e293b", "accent": "#00f2fe", "font": "sans-serif", "border_radius": "12px", "header_bg": "#f8fafc"},
                "Classic Corporate": {"bg": "#ffffff", "text": "#333333", "accent": "#2563eb", "font": "Georgia, serif", "border_radius": "0px", "header_bg": "#f1f5f9"},
                "Minimalist Startup": {"bg": "#ffffff", "text": "#0f172a", "accent": "#000000", "font": "system-ui", "border_radius": "4px", "header_bg": "#ffffff"},
                "Vibrant Creative": {"bg": "#ffffff", "text": "#171717", "accent": "#ec4899", "font": "'Courier New', Courier, monospace", "border_radius": "20px", "header_bg": "#fdf2f8"}
            }
            theme = themes[template_var]

            # Generate HTML
            invoice_html = f"""
    <div style="background-color: {theme['bg']}; color: {theme['text']}; font-family: {theme['font']}; padding: 40px; border-radius: {theme['border_radius']}; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06); max-width: 800px; margin: 0 auto; border-top: 8px solid {theme['accent']};">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 40px;">
    <div>
    <h1 style="margin: 0; color: {theme['accent']}; font-size: 32px;">{comp_name}</h1>
    <p style="margin: 5px 0 0 0; color: #64748b;">{comp_addr}</p>
    </div>
    <div style="text-align: right;">
    <h2 style="margin: 0; font-size: 24px; color: #94a3b8; text-transform: uppercase; letter-spacing: 2px;">Invoice</h2>
    <p style="margin: 5px 0 0 0; font-weight: bold;">#{inv_num}</p>
    <p style="margin: 2px 0 0 0; color: #64748b;">Date: {inv_date}</p>
    </div>
    </div>
            
    <div style="background-color: {theme['header_bg']}; padding: 20px; border-radius: {theme['border_radius']}; margin-bottom: 40px;">
    <p style="margin: 0; font-size: 14px; color: #64748b; text-transform: uppercase;">Billed To</p>
    <h3 style="margin: 5px 0 0 0; font-size: 18px;">{client_name}</h3>
    <p style="margin: 5px 0 0 0; color: #64748b;">{client_addr}</p>
    </div>
            
    <table style="width: 100%; border-collapse: collapse; margin-bottom: 40px;">
    <thead>
    <tr style="border-bottom: 2px solid {theme['accent']}; text-align: left;">
    <th style="padding: 10px; font-weight: bold;">Item Description</th>
    <th style="padding: 10px; font-weight: bold;">Qty</th>
    <th style="padding: 10px; font-weight: bold;">Price</th>
    <th style="padding: 10px; font-weight: bold;">Total</th>
    </tr>
    </thead>
    <tbody>
                        {rows_html}
    </tbody>
    </table>
            
    <div style="display: flex; justify-content: flex-end;">
    <div style="width: 300px;">
    <div style="display: flex; justify-content: space-between; margin-bottom: 10px; padding-bottom: 10px; border-bottom: 1px solid #e2e8f0;">
    <span>Subtotal:</span>
    <span>${subtotal:,.2f}</span>
    </div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 10px; padding-bottom: 10px; border-bottom: 1px solid #e2e8f0;">
    <span>Tax ({tax_pct}%):</span>
    <span>${tax_amt:,.2f}</span>
    </div>
    <div style="display: flex; justify-content: space-between; font-size: 20px; font-weight: bold; color: {theme['accent']};">
    <span>Total Due:</span>
    <span>${grand_total:,.2f}</span>
    </div>
    </div>
    </div>
            
    <div style="margin-top: 60px; text-align: center; color: #94a3b8; font-size: 12px; border-top: 1px solid #e2e8f0; padding-top: 20px;">
    <p>Thank you for your business. Please remit payment within 30 days.</p>
    <p>Powered by Mindflix Billing Studio</p>
    </div>
    </div>
            """
        
            st.components.v1.html(invoice_html, height=800, scrolling=True)







def render_latex_studio():
    st.markdown('<div class="section-title">📝 LaTeX to PDF Studio</div>', unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8; font-size: 1.1rem; margin-bottom: 2rem;'>Edit and compile LaTeX documents instantly.</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        if "latex_code" not in st.session_state:
            st.session_state.latex_code = "\\documentclass{article}\n\\begin{document}\nHello World!\n\\end{document}"
            
        st.markdown("### 📝 Code Editor")
        # Use a unique key and on_change to ensure state stays in sync
        def update_latex():
            st.session_state.latex_code = st.session_state.latex_editor_val
            
        st.text_area("LaTeX Source Code", value=st.session_state.latex_code, height=500, key="latex_editor_val", on_change=update_latex)
        
    with col2:
        st.markdown("### 📄 Live Preview")
        if st.button("🔄 Compile to PDF", type="primary", use_container_width=True):
            with st.spinner("Compiling PDF on remote server..."):
                import requests
                try:
                    url = "https://latexonline.cc/compile"
                    res = requests.get(url, params={"text": st.session_state.latex_code}, timeout=30)
                    if res.status_code == 200:
                        st.session_state.compiled_pdf = res.content
                        st.success("Successfully compiled!")
                    else:
                        st.error("Compilation Error:")
                        st.code(res.text, language="text")
                except Exception as e:
                    st.error(f"Failed to reach compilation server: {e}")
                    
        if "compiled_pdf" in st.session_state:
            import base64
            b64_pdf = base64.b64encode(st.session_state.compiled_pdf).decode('utf-8')
            pdf_display = f'<embed src="data:application/pdf;base64,{b64_pdf}" width="100%" height="600" type="application/pdf" style="border: 1px solid rgba(255,255,255,0.1); border-radius: 8px;">'
            st.markdown(pdf_display, unsafe_allow_html=True)
            
            st.download_button(
                label="⬇️ Download PDF",
                data=st.session_state.compiled_pdf,
                file_name="document.pdf",
                mime="application/pdf",
                use_container_width=True
            )

if current_page == "📝 LaTeX Studio":
    render_latex_studio()

if current_page == "🏠 Dashboard":
    # Hero
    st.markdown("""
<div class="hero">
<h1>Build. Test. Brand. Scale.</h1>
<p class="tagline">The AI Workspace for QA Engineers, Marketers, and Growing Teams.</p>
</div>
""", unsafe_allow_html=True)


    st.markdown("""
<div class="tools-grid">
<a href="?nav=docs" target="_self" style="text-decoration: none; color: inherit;">
<div class="animated-card">
<span class="emoji">📄</span>
<span class="title">Docs Intelligence</span>
<span class="subtitle">Ask anything from documents</span>
</div>
</a>
<a href="?nav=qa" target="_self" style="text-decoration: none; color: inherit;">
<div class="animated-card">
<span class="emoji">🧪</span>
<span class="title">QA Copilot</span>
<span class="subtitle">Generate test cases instantly</span>
</div>
</a>
<a href="?nav=social" target="_self" style="text-decoration: none; color: inherit;">
<div class="animated-card">
<span class="emoji">🎨</span>
<span class="title">Social Studio</span>
<span class="subtitle">Create branded social content</span>
</div>
</a>
<a href="?nav=brand" target="_self" style="text-decoration: none; color: inherit;">
<div class="animated-card">
<span class="emoji">🧬</span>
<span class="title">Brand Intelligence</span>
<span class="subtitle">Extract and scale your brand identity</span>
</div>
</a>
<a href="?nav=billing" target="_self" style="text-decoration: none; color: inherit;">
<div class="animated-card">
<span class="emoji">🧾</span>
<span class="title">Billing Studio</span>
<span class="subtitle">Create beautiful invoices instantly</span>
</div>
</a>
<a href="?nav=latex" target="_self" style="text-decoration: none; color: inherit;">
<div class="animated-card">
<span class="emoji">📝</span>
<span class="title">LaTeX Studio</span>
<span class="subtitle">Generate & Compile PDF Documents</span>
</div>
</a>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
</div>

<div class="quick-actions-section">
<h3>⚡ Quick Actions</h3>
<div class="quick-actions-grid">
<button class="quick-action-btn" data-tab-target="1">📄 Upload Document</button>
<button class="quick-action-btn" data-tab-target="2">🧪 Generate Test Cases</button>
<button class="quick-action-btn" data-tab-target="2">🛡️ Security Scan</button>
<button class="quick-action-btn" data-tab-target="3">🎨 Create Social Post</button>
<button class="quick-action-btn" data-tab-target="4">🧬 Analyze Brand</button>
</div>
</div>

<div class="kpi-grid">
<div class="kpi-card"><span class="kpi-num">12</span><span class="kpi-label">Documents Analyzed</span></div>
<div class="kpi-card"><span class="kpi-num">45</span><span class="kpi-label">Test Cases Generated</span></div>
<div class="kpi-card"><span class="kpi-num">8</span><span class="kpi-label">Social Posts Created</span></div>
<div class="kpi-card"><span class="kpi-num">3</span><span class="kpi-label">Brands Analyzed</span></div>
<div class="kpi-card"><span class="kpi-num">5</span><span class="kpi-label">Invoices Created</span></div>
</div>

<a href="https://mindflix.in" target="_blank" style="text-decoration: none; display: block; margin: 4rem auto; max-width: 900px; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.5); transition: transform 0.2s ease;" onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1)'">
<div style="display: flex; background: linear-gradient(135deg, #0f172a, #1e1b4b); height: 250px; position: relative;">
<div style="position: absolute; top: 10px; right: 10px; background: rgba(255,255,255,0.2); color: #fff; font-size: 0.7rem; padding: 2px 6px; border-radius: 4px; font-family: sans-serif; letter-spacing: 1px;">ADVERTISEMENT</div>
<div style="flex: 1; padding: 2.5rem; display: flex; flex-direction: column; justify-content: center; text-align: left;">
<h2 style="color: #fff; margin: 0; font-size: 2rem; font-weight: 800; line-height: 1.2;">Supercharge your workflow.</h2>
<p style="color: #cbd5e1; margin: 10px 0 20px 0; font-size: 1.1rem;">Join 10,000+ teams using Mindflix to automate testing and scale content.</p>
<span style="color: #4da8da; font-weight: bold; font-size: 1rem;">Visit Mindflix.in &rarr;</span>
</div>
<div style="flex: 1; background: url('https://images.unsplash.com/photo-1460925895917-afdab827c52f?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80') center right/cover; clip-path: polygon(15% 0, 100% 0, 100% 100%, 0 100%);"></div>
</div>
</a>

<div class="testimonial-section">
<h3>Loved by Innovators</h3>
<div class="testimonial-grid">
<div class="testimonial-card">
<p class="testimonial-text">"Mindflix has completely transformed how our engineering and marketing teams collaborate. The AI test generation capabilities are simply unmatched and have saved us countless hours of manual work."</p>
<div class="testimonial-author">
<div class="avatar-initials">AP</div>
<div>
<strong>Arjun Patel</strong>
<span>Lead QA Engineer</span>
</div>
</div>
</div>
    
<div class="testimonial-card">
<p class="testimonial-text">"The Brand Intelligence feature is a game-changer. We can now ensure every single piece of content aligns perfectly with our brand DNA before it ever goes live."</p>
<div class="testimonial-author">
<div class="avatar-initials" style="border-color: #b14bf4; color: #ffffff; background: linear-gradient(135deg, rgba(177, 75, 244, 0.1) 0%, rgba(177, 75, 244, 0.2) 100%); box-shadow: 0 0 15px rgba(177,75,244,0.3);">PS</div>
<div>
<strong>Priya Sharma</strong>
<span>Marketing Director</span>
</div>
</div>
</div>
    
<div class="testimonial-card">
<p class="testimonial-text">"Having our documents, tests, and social media tools all living inside one unified AI workspace is incredible. It's the SaaS product we didn't know we needed."</p>
<div class="testimonial-author">
<div class="avatar-initials" style="border-color: #10b981; color: #ffffff; background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.2) 100%); box-shadow: 0 0 15px rgba(16,185,129,0.3);">RG</div>
<div>
<strong>Rohan Gupta</strong>
<span>Product Manager</span>
</div>
</div>
</div>
</div>
</div>


    """, unsafe_allow_html=True)

    # Magic JS to link the Dashboard Cards to the Streamlit Tabs
    st.components.v1.html("""
<!-- Removed JS tab routing since we use sidebar navigation now -->
    """, height=0, width=0)


if current_page == "📄 Docs AI":
    render_docs_ai()

if current_page == "🧪 QA Copilot":
    render_qa_copilot()

if current_page == "🎨 Social Studio":
    render_social_studio()

if current_page == "🧬 Brand Intelligence":
    render_brand_intelligence()

if current_page == "💰 Billing":
    render_billing_studio()

if current_page == "🛡️ Security Auditor":
    st.markdown("<h2 style='color: #00f2fe; margin-bottom: 0;'>🛡️ Security Auditor</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8; font-size: 1.1rem; margin-bottom: 2rem;'>Penetration testing and security compliance checks powered by AI.</p>", unsafe_allow_html=True)
    
    st.markdown("<div style='background: rgba(255,255,255,0.03); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(0,242,254,0.2); margin-bottom: 2rem;'>", unsafe_allow_html=True)
    col1, col2 = st.columns([4, 1])
    with col1:
        st.text_input("Target URL / IP Address", placeholder="https://api.example.com", label_visibility="collapsed")
    with col2:
        if st.button("Scan Now", use_container_width=True, type="primary"):
            st.session_state.scan_started = True
    st.markdown("</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### 📊 Vulnerability Dashboard")
        st.markdown("""
        <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 2rem;'>
            <div style='background: rgba(239, 68, 68, 0.1); border-left: 4px solid #ef4444; padding: 1rem; border-radius: 8px;'>
                <h4 style='margin:0; color: #ef4444;'>Critical</h4>
                <p style='margin:0; font-size: 2rem; font-weight: 800; color: #fff;'>0</p>
            </div>
            <div style='background: rgba(249, 115, 22, 0.1); border-left: 4px solid #f97316; padding: 1rem; border-radius: 8px;'>
                <h4 style='margin:0; color: #f97316;'>High</h4>
                <p style='margin:0; font-size: 2rem; font-weight: 800; color: #fff;'>2</p>
            </div>
            <div style='background: rgba(234, 179, 8, 0.1); border-left: 4px solid #eab308; padding: 1rem; border-radius: 8px;'>
                <h4 style='margin:0; color: #eab308;'>Medium</h4>
                <p style='margin:0; font-size: 2rem; font-weight: 800; color: #fff;'>5</p>
            </div>
            <div style='background: rgba(34, 197, 94, 0.1); border-left: 4px solid #22c55e; padding: 1rem; border-radius: 8px;'>
                <h4 style='margin:0; color: #22c55e;'>Low</h4>
                <p style='margin:0; font-size: 2rem; font-weight: 800; color: #fff;'>14</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📋 Compliance Reports")
        st.button("📄 Generate SOC2 Report", use_container_width=True)
        st.button("📄 Generate HIPAA Report", use_container_width=True)
        
    with col2:
        st.markdown("### 💻 Live Scan Terminal")
        st.markdown("""
        <div style='background: #0b0f19; padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); font-family: monospace; font-size: 0.9rem; height: 350px; overflow-y: auto;'>
            <div style='color: #22c55e;'>$ Initializing Security Auditor Agent...</div>
            <div style='color: #94a3b8;'>[INFO] Target: https://api.example.com</div>
            <div style='color: #94a3b8;'>[INFO] Running Nmap stealth scan (SYN)...</div>
            <div style='color: #22c55e;'>[OK] Ports 80, 443 open.</div>
            <div style='color: #94a3b8;'>[INFO] Checking OWASP Top 10 vulnerabilities...</div>
            <div style='color: #94a3b8;'>[INFO] Testing for SQL Injection (SQLi)...</div>
            <div style='color: #22c55e;'>[OK] No SQLi detected.</div>
            <div style='color: #94a3b8;'>[INFO] Testing for Cross-Site Scripting (XSS)...</div>
            <div style='color: #eab308;'>[WARN] Potential Reflected XSS on /search endpoint.</div>
            <div style='color: #94a3b8;'>[INFO] Analyzing TLS configuration...</div>
            <div style='color: #f97316;'>[HIGH] TLS 1.0 is enabled. Recommend disabling.</div>
            <div style='color: #94a3b8; margin-top: 1rem;' class='blink'>_</div>
        </div>
        <style>
            .blink { animation: blinker 1s linear infinite; }
            @keyframes blinker { 50% { opacity: 0; } }
        </style>
        """, unsafe_allow_html=True)


if current_page == "📈 Automation Engineer":
    st.markdown("<h2 style='color: #b14bf4; margin-bottom: 0;'>📈 Automation Engineer</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8; font-size: 1.1rem; margin-bottom: 2rem;'>Generate complex end-to-end automation scripts in seconds.</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        framework = st.selectbox("Select Target Framework", ["Selenium (Python)", "Playwright (TypeScript)", "Cypress (JavaScript)", "Appium (Java)"])
        scenario = st.text_area("Describe Test Scenario", height=150, placeholder="Example: Navigate to the login page, enter invalid credentials, and assert that the 'Invalid Username or Password' error message is visible.")
        st.button("⚙️ Generate Script", type="primary", use_container_width=True)
        
        st.markdown("### 📌 Recent Scripts")
        st.markdown("""
        <div style='background: rgba(255,255,255,0.03); padding: 1rem; border-radius: 8px; border-left: 3px solid #b14bf4; margin-bottom: 10px; cursor: pointer;'>
            <strong>Login Validations</strong> <span style='color: #94a3b8; font-size: 0.8rem; float: right;'>Cypress</span>
        </div>
        <div style='background: rgba(255,255,255,0.03); padding: 1rem; border-radius: 8px; border-left: 3px solid #00f2fe; margin-bottom: 10px; cursor: pointer;'>
            <strong>Checkout Flow</strong> <span style='color: #94a3b8; font-size: 0.8rem; float: right;'>Playwright</span>
        </div>
        <div style='background: rgba(255,255,255,0.03); padding: 1rem; border-radius: 8px; border-left: 3px solid #10b981; margin-bottom: 10px; cursor: pointer;'>
            <strong>API Data Sync</strong> <span style='color: #94a3b8; font-size: 0.8rem; float: right;'>Selenium</span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("### 📝 Generated Code")
        sample_code = """import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestLoginScenario:
    def setup_method(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 10)

    def teardown_method(self):
        self.driver.quit()

    def test_invalid_login_credentials(self):
        # Navigate to login page
        self.driver.get("https://demo.mindflix.ai/login")
        
        # Enter invalid credentials
        username_field = self.wait.until(EC.presence_of_element_located((By.ID, "username")))
        username_field.send_keys("invalid_user")
        
        password_field = self.driver.find_element(By.ID, "password")
        password_field.send_keys("wrong_password123")
        
        # Click login button
        login_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_btn.click()
        
        # Assert error message is visible
        error_msg = self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "error-alert")))
        assert error_msg.text == "Invalid Username or Password"
"""
        st.code(sample_code, language="python")
        st.button("📋 Copy to Clipboard", use_container_width=True)



elif current_page == "📧 Inquiry":
    st.markdown("<h1 style='text-align: center; color: #ffffff;'>📧 Start Building with Mindflix</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #a0aec0; font-size: 1.2rem; margin-bottom: 3rem;'>Fill out the form below to inquire about our services. Our team will get back to you shortly.</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <style>
    [data-testid="stForm"] {
        background: rgba(30, 41, 59, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        padding: 30px !important;
        max-width: 600px !important;
        margin: 0 auto !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.form("inquiry_form", border=False):
        name = st.text_input("Name", placeholder="John Doe")
        email = st.text_input("Email Address", placeholder="john@example.com")
        company = st.text_input("Company", placeholder="Acme Corp")
        message = st.text_area("How can we help you build?", placeholder="I'm interested in...")
        
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Send Inquiry", use_container_width=True)
        
        if submitted:
            if not name or not email:
                st.error("⚠️ Please fill in your name and email address.")
            else:
                st.success(f"✅ Thank you, {name}! An inquiry email has been triggered for {email}. Our team will contact you soon.")
                st.balloons()

    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #ffffff;'>🌍 Global Offices</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #a0aec0; font-size: 1.1rem; margin-bottom: 2rem;'>Find us across the globe.</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <style>
    .office-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 25px;
        text-align: left;
        transition: transform 0.3s ease, border-color 0.3s ease;
        height: 100%;
    }
    .office-card:hover {
        transform: translateY(-5px);
        border-color: rgba(0, 242, 254, 0.5);
    }
    .office-city {
        font-size: 1.5rem;
        font-weight: 700;
        color: white;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .office-address {
        color: #94a3b8;
        line-height: 1.6;
        font-size: 1rem;
    }
    .office-contact {
        margin-top: 15px;
        color: #38bdf8;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="office-card">
            <div class="office-city">🇮🇳 Mumbai</div>
            <div class="office-address">
                Mindflix Innovation Hub<br>
                Bandra Kurla Complex (BKC)<br>
                Mumbai, Maharashtra 400051<br>
                India
            </div>
            <div class="office-contact">
                📞 +91 22 1234 5678<br>
                ✉️ mumbai@mindflix.ai
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="office-card">
            <div class="office-city">🇸🇬 Singapore</div>
            <div class="office-address">
                Mindflix APAC Headquarters<br>
                Marina Bay Financial Centre<br>
                8 Marina Blvd, Tower 1<br>
                Singapore 018981
            </div>
            <div class="office-contact">
                📞 +65 6789 0123<br>
                ✉️ apac@mindflix.ai
            </div>
        </div>
        """, unsafe_allow_html=True)


# ==========================================
# GLOBAL FOOTER & CONTACT SECTION
# ==========================================

# Determine dynamic footer data based on current page
footer_data = {
    "email": "rahulryadarx@gmail.com",
    "location": "Singapore",
    "response_time": "Within 24 hours",
    "heading": "Something Great",
    "subheading": "Have a project in mind? We'd love to hear about it. Drop us a message and we'll get back to you within 24 hours."
}

if current_page == "📄 Docs AI":
    footer_data["email"] = "docs.support@mindflix.ai"
    footer_data["heading"] = "Document Intelligence"
    footer_data["subheading"] = "Need custom extraction rules? Our document AI team can help you build custom pipelines."
elif current_page == "🧪 QA Copilot":
    footer_data["email"] = "qa.automation@mindflix.ai"
    footer_data["heading"] = "Testing Automation"
    footer_data["subheading"] = "Need to integrate with your CI/CD? Reach out to our QA engineering experts."
elif current_page == "🎨 Social Studio":
    footer_data["email"] = "creators@mindflix.ai"
    footer_data["heading"] = "Viral Campaigns"
    footer_data["subheading"] = "Want to scale your social media presence? Our creative agency can manage your brand."
elif current_page == "🧬 Brand Intelligence":
    footer_data["email"] = "strategy@mindflix.ai"
    footer_data["heading"] = "Brand Strategy"
    footer_data["subheading"] = "Looking for deep market analytics? Talk to our brand intelligence consultants."
elif current_page == "📈 Automation Engineer":
    footer_data["email"] = "engineering@mindflix.ai"
    footer_data["heading"] = "Custom Automation"
    footer_data["subheading"] = "Have a complex workflow that needs automating? Our engineers are ready."
elif current_page == "🛡️ Security Auditor":
    footer_data["email"] = "security@mindflix.ai"
    footer_data["heading"] = "Secure Systems"
    footer_data["subheading"] = "Need a comprehensive penetration test? Talk to our certified ethical hackers."
    footer_data["response_time"] = "Within 4 hours (Priority)"

st.markdown(f"""
<style>
.global-footer-section {{
    margin-top: 2rem;
    padding-top: 3rem;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
    background: transparent;
}}

.footer-contact-container {{
max-width: 1200px;
margin: 0 auto;
display: flex;
flex-wrap: wrap;
gap: 4rem;
padding: 0 2rem;
}}

.footer-left {{
flex: 1;
min-width: 300px;
}}

.footer-right {{
flex: 1;
min-width: 400px;
}}

.footer-heading {{
font-size: 3.5rem;
font-weight: 900;
line-height: 1.1;
margin-bottom: 1.5rem;
color: white;
}}

.footer-heading .gradient-text {{
background: linear-gradient(135deg, #a855f7 0%, #3b82f6 100%);
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
display: block;
}}

.footer-subheading {{
color: #94a3b8;
font-size: 1.1rem;
line-height: 1.6;
margin-bottom: 3rem;
max-width: 90%;
}}

.footer-info-block {{
display: flex;
align-items: center;
gap: 1rem;
margin-bottom: 2rem;
}}

.footer-icon-box {{
width: 50px;
height: 50px;
border-radius: 12px;
background: linear-gradient(135deg, rgba(168, 85, 247, 0.2) 0%, rgba(59, 130, 246, 0.2) 100%);
display: flex;
align-items: center;
justify-content: center;
font-size: 1.5rem;
border: 1px solid rgba(168, 85, 247, 0.3);
}}

.footer-info-content .info-label {{
font-size: 0.75rem;
text-transform: uppercase;
letter-spacing: 1px;
color: #64748b;
margin-bottom: 0.2rem;
font-weight: 600;
}}

.footer-info-content .info-value {{
color: white;
font-size: 1.1rem;
font-weight: 500;
}}

.footer-form-container {{
background: rgba(30, 41, 59, 0.3);
border: 1px solid rgba(255, 255, 255, 0.05);
border-radius: 16px;
padding: 2.5rem;
}}

.footer-form-row {{
display: flex;
gap: 1.5rem;
margin-bottom: 1.5rem;
}}

.footer-form-group {{
flex: 1;
display: flex;
flex-direction: column;
gap: 0.5rem;
}}

.footer-form-group label {{
font-size: 0.9rem;
color: #cbd5e1;
}}

.footer-form-group input, .footer-form-group textarea {{
    width: 100%;
    box-sizing: border-box;
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    color: white;
    font-family: inherit;
    font-size: 1rem;
    transition: all 0.3s ease;
}}

.footer-form-group input:focus, .footer-form-group textarea:focus {{
outline: none;
border-color: #a855f7;
background: rgba(15, 23, 42, 0.9);
}}

.footer-submit-btn {{
width: 100%;
background: linear-gradient(135deg, #a855f7 0%, #3b82f6 100%);
color: white;
border: none;
padding: 1rem;
border-radius: 8px;
font-size: 1.1rem;
font-weight: 600;
cursor: pointer;
margin-top: 1rem;
transition: all 0.3s ease;
}}

.footer-submit-btn:hover {{
opacity: 0.9;
transform: translateY(-2px);
}}

.footer-bottom-bar {{
max-width: 1200px;
margin: 4rem auto 0;
padding: 2rem 2rem;
border-top: 1px solid rgba(255, 255, 255, 0.05);
display: flex;
justify-content: space-between;
align-items: center;
flex-wrap: wrap;
gap: 2rem;
}}

.footer-brand .brand-name {{
font-size: 1.5rem;
font-weight: 800;
background: linear-gradient(135deg, #a855f7 0%, #3b82f6 100%);
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
}}

.footer-brand .brand-tag {{
color: #64748b;
font-size: 0.9rem;
margin-top: 0.2rem;
}}

.footer-links {{
display: flex;
gap: 1.5rem;
}}

.footer-links a {{
color: #94a3b8;
text-decoration: none;
font-size: 0.95rem;
transition: color 0.3s ease;
}}

.footer-links a:hover {{
color: white;
}}

.footer-copyright {{
color: #64748b;
font-size: 0.9rem;
}}

@media (max-width: 768px) {{
.footer-form-row {{
flex-direction: column;
}}
.footer-bottom-bar {{
flex-direction: column;
text-align: center;
}}
}}
</style>

<div class="global-footer-section">
<div class="footer-contact-container">
<div class="footer-left">
<h2 class="footer-heading">Let's Build <span class="gradient-text">{footer_data["heading"]}</span></h2>
<p class="footer-subheading">{footer_data["subheading"]}</p>

<div class="footer-info-block">
<div class="footer-icon-box">✉️</div>
<div class="footer-info-content">
<div class="info-label">EMAIL</div>
<div class="info-value">{footer_data["email"]}</div>
</div>
</div>

<div class="footer-info-block">
<div class="footer-icon-box">🌍</div>
<div class="footer-info-content">
<div class="info-label">LOCATION</div>
<div class="info-value">{footer_data["location"]}</div>
</div>
</div>

<div class="footer-info-block">
<div class="footer-icon-box">⏰</div>
<div class="footer-info-content">
<div class="info-label">RESPONSE TIME</div>
<div class="info-value">{footer_data["response_time"]}</div>
</div>
</div>
</div>

<div class="footer-right">
<div class="footer-form-container">
<div class="footer-form-row">
<div class="footer-form-group">
<label>Name *</label>
<input type="text" placeholder="Your name">
</div>
<div class="footer-form-group">
<label>Email *</label>
<input type="email" placeholder="you@company.com">
</div>
</div>
<div class="footer-form-group" style="margin-bottom: 1.5rem;">
<label>Company</label>
<input type="text" placeholder="Your company name">
</div>
<div class="footer-form-group">
<label>Message *</label>
<textarea rows="4" placeholder="Tell us about your project..."></textarea>
</div>
<button class="footer-submit-btn">Send Message</button>
</div>
</div>
</div>

<div class="footer-bottom-bar">
<div class="footer-brand">
<div class="brand-name">Mindflix</div>
<div class="brand-tag">Technologies Ltd</div>
</div>
<div class="footer-copyright">
© 2026 Mindflix Technologies. All rights reserved.
</div>
</div>
</div>
""", unsafe_allow_html=True)
