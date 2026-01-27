import streamlit as st
import fitz  # PyMuPDF
import os
import random
import matplotlib.pyplot as plt
import base64

# =====================
# 1. KONFIGURASI HALAMAN
# =====================
st.set_page_config(page_title="Liaaaa-Library Mini", page_icon="😻", layout="wide")

# =====================
# 2. SISTEM LOGIN (GERBANG RAHASIA) 🔐
# =====================
def check_password():
    """Fungsi mengecek password"""
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Hapus password dari memori biar aman
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # Awal buka, belum login
        st.text_input(
            "🔒 Masukkan Password Akses:", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password salah
        st.text_input(
            "🔒 Masukkan Password Akses:", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        st.error("🚫 Password salah, coba lagi ya!")
        return False
    else:
        # Password benar
        return True

# --- CEK LOGIN DULU SEBELUM LANJUT ---
if not check_password():
    st.stop()  # <--- INI KUNCINYA! Kalau belum login, stop di sini.

# =====================
# 3. KODE APLIKASI UTAMA (HANYA JALAN KALAU SUDAH LOGIN)
# =====================

# --- LOGIKA KUNANG-KUNANG ---
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

# --- INJECT DESAIN (CSS) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

/* --- DASAR HALAMAN --- */
.stApp {
    background: radial-gradient(circle at center, #1b2735 0%, #090a0f 100%);
    color: #eaeaea;
    font-family: 'Poppins', sans-serif;
    overflow-x: hidden;
}

/* --- HEADER TRANSPARAN --- */
header[data-testid="stHeader"] {
    background-color: transparent !important;
    z-index: 1;
}
div[data-testid="stDecoration"] {
    visibility: hidden;
}

/* --- HILANGKAN TOMBOL FULLSCREEN GAMBAR --- */
button[title="View fullscreen"] {
    display: none !important;
}
[data-testid="StyledFullScreenButton"] {
    display: none !important;
}

/* --- KUNANG-KUNANG --- */
.firefly {
    position: fixed;
    bottom: -10px;
    background: rgba(255, 255, 255, 0.5);
    box-shadow: 0 0 15px 2px rgba(0, 201, 255, 0.6);
    border-radius: 50%;
    pointer-events: none;
    z-index: 999;
    animation: floatUp linear infinite;
}

@keyframes floatUp {
    0% { bottom: -10px; opacity: 0; transform: translateX(0); }
    10% { opacity: 1; }
    90% { opacity: 1; }
    100% { bottom: 100vh; opacity: 0; transform: translateX(20px); }
}

/* --- SIDEBAR --- */
section[data-testid="stSidebar"] {
    background-color: rgba(17, 20, 29, 0.95);
    border-right: 1px solid #2d323e;
    z-index: 1000;
}
section[data-testid="stSidebar"] * { color: #ffffff !important; }
.stCaption { color: #cccccc !important; }
.stTextArea textarea { background-color: #262a36 !important; color: white !important; }

/* --- TOMBOL --- */
button[kind="secondary"] {
    background: transparent !important;
    border: 1px solid #555 !important;
    color: white !important;
    font-size: 10px !important;
}

.stButton button {
    background: #262a36 !important;
    color: #ffffff !important;
    border: 1px solid #3a3f4b;
    border-radius: 12px;
    transition: all 0.3s ease;
    width: 100%;
}
[data-testid="column"] .stButton button {
    background: linear-gradient(45deg, #00C9FF, #0078ff) !important;
    border: none !important;
    box-shadow: 0 4px 15px rgba(0, 201, 255, 0.3);
}
[data-testid="column"] .stButton button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 201, 255, 0.6);
}

/* --- KARTU BUKU (GRID RAPIH) --- */
.book-card {
    background: rgba(28, 31, 38, 0.8);
    backdrop-filter: blur(5px);
    border: 1px solid #2d323e;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    border-radius: 16px;
    padding: 15px;
    transition: all 0.3s ease;
    margin-bottom: 20px;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.book-card:hover {
    transform: translateY(-5px);
    border-color: #00C9FF;
}

/* --- GAMBAR COVER (UKURAN TETAP) --- */
.cover-img {
    width: 100%;
    height: 280px;
    object-fit: cover;
    border-radius: 8px;
    margin-bottom: 12px;
}

/* --- JUDUL BUKU (BATAS BARIS) --- */
.book-title {
    text-align: center;
    font-size: 14px;
    font-weight: 600;
    color: #fff;
    margin-bottom: 15px;
    height: 42px;
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
}
</style>
""", unsafe_allow_html=True)

# --- INJECT KUNANG-KUNANG ---
st.markdown(firefly_html, unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
if 'buku' not in st.session_state: st.session_state.buku = None
if 'halaman' not in st.session_state: st.session_state.halaman = 0
if 'sedang' not in st.session_state: st.session_state.sedang = set()
if 'selesai' not in st.session_state: st.session_state.selesai = set()
if 'progress' not in st.session_state: st.session_state.progress = {}
if 'catatan' not in st.session_state: st.session_state.catatan = {} 

# --- FUNGSI ---
def list_buku():
    if not os.path.exists("buku_pdf"): os.makedirs("buku_pdf")
    return [b for b in os.listdir("buku_pdf") if b.endswith(".pdf")]

@st.cache_data
def cover(path):
    try:
        d = fitz.open(path)
        return d.load_page(0).get_pixmap(matrix=fitz.Matrix(0.8, 0.8)).tobytes("png")
    except: return None

def render_page(doc, page_num, zoom):
    try:
        return doc.load_page(page_num).get_pixmap(matrix=fitz.Matrix(zoom, zoom)).tobytes("png")
    except: return None

# --- SIDEBAR ---
with st.sidebar:
    st.header("👤 Rak Lia")
    
    st.subheader("📊 Statistik")
    jml_sedang = len(
