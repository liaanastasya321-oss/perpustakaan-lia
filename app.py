import streamlit as st
import fitz  # PyMuPDF
import os
import random

# =====================
# CONFIG
# =====================
st.set_page_config(page_title="Z-Library Mini", page_icon="📚", layout="wide")

# =====================
# MAGIC KUNANG-KUNANG ✨
# =====================
firefly_html = ""
for i in range(50):
    left = random.randint(1, 99)
    delay = random.uniform(0, 20)
    duration = random.uniform(10, 20)
    size = random.randint(2, 5)
    
    firefly_html += f"""
    <div class="firefly" style="
        left: {left}%; 
        animation-delay: {delay}s; 
        animation-duration: {duration}s;
        width: {size}px;
        height: {size}px;
    "></div>
    """

# =====================
# CSS (DESAIN + ANIMASI)
# =====================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

.stApp {{
    background: radial-gradient(circle at center, #1b2735 0%, #090a0f 100%);
    color: #eaeaea;
    font-family: 'Poppins', sans-serif;
    overflow-x: hidden;
}}

.firefly {{
    position: fixed;
    bottom: -10px;
    background: rgba(255, 255, 255, 0.5);
    box-shadow: 0 0 15px 2px rgba(0, 201, 255, 0.6);
    border-radius: 50%;
    pointer-events: none;
    z-index: 0;
    animation: floatUp linear infinite;
}}

@keyframes floatUp {{
    0% {{ bottom: -10px; opacity: 0; transform: translateX(0); }}
    10% {{ opacity: 1; }}
    90% {{ opacity: 1; }}
    100% {{ bottom: 100vh; opacity: 0; transform: translateX(20px); }}
}}

.block-container {{ position: relative; z-index: 1; }}

section[data-testid="stSidebar"] {{
    background-color: rgba(17, 20, 29, 0.95);
    border-right: 1px solid #2d323e;
    z-index: 2;
}}

section[data-testid="stSidebar"] * {{ color: #ffffff !important; }}
.stCaption {{ color: #cccccc !important; }}

button[kind="secondary"] {{
    background: transparent !important;
    border: 1px solid #555 !important;
    color: white !important;
    font-size: 10px !important;
}}

.stButton button {{
    background: #262a36 !important;
    color: #ffffff !important;
    border: 1px solid #3a3f4b;
    border-radius: 12px;
    transition: all 0.3s ease;
}}
[data-testid="column"] .stButton button {{
    background: linear-gradient(45deg, #00C9FF, #0078ff) !important;
    border: none !important;
    box-shadow: 0 4px 15px rgba(0, 201, 255, 0.3);
}}
[data-testid="column"] .stButton button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 201, 255, 0.6);
}}

.book-card {{
    background: rgba(28, 31, 38, 0.8);
    backdrop-filter: blur(5px);
    border: 1px solid #2d323e;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    border-radius: 16px;
    padding: 15px;
    transition: all 0.3s ease;
    margin-bottom: 20px;
}}
.book-card:hover {{
    transform: translateY(-5px);
    border-color: #00C9FF;
}}
.book-title {{
    text-align: center;
    font-size: 14px;
    font-weight: 600;
    margin-top: 10px;
    color: #fff;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}
</style>
{firefly_html}
""", unsafe_allow_html=True)

# =====================
# STATE MANAGEMENT
# =====================
if 'buku' not in st.session_state: st.session_state.buku = None
if 'halaman' not in st.session_state: st.session_state.halaman = 0
if 'sedang' not in st.session_state: st.session_state.sedang = set()
if 'selesai' not in st.session_state: st.session_state.selesai = set()
if 'progress' not in st.session_state: st.session_state.progress = {}

# =====================
# FUNGSI
# =====================
def list_buku():
    if not os.path.exists("buku_pdf"): os.makedirs("buku_pdf")
    return [b for b in os.listdir("buku_pdf") if b.endswith(".pdf")]

@st
