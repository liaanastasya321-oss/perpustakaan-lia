import streamlit as st
import fitz  # PyMuPDF
import os
import random # Kita butuh ini buat acak posisi kunang-kunang

# =====================
# CONFIG
# =====================
st.set_page_config(page_title="Z-Library Mini", page_icon="📚", layout="wide")

# =====================
# MAGIC KUNANG-KUNANG ✨
# =====================
# Kita bikin 50 kunang-kunang dengan posisi acak biar natural
firefly_html = ""
for i in range(50):
    left = random.randint(1, 99)   # Posisi kiri-kanan acak
    delay = random.uniform(0, 20)  # Munculnya gantian
    duration = random.uniform(10, 20) # Kecepatannya beda-beda
    size = random.randint(2, 5)    # Ukurannya beda-beda
    
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
/* Import Font */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

/* --- DASAR HALAMAN --- */
.stApp {{
    /* Background Gelap Pekat biar Kunang-kunang kelihatan */
    background: radial-gradient(circle at center, #1b2735 0%, #090a0f 100%);
    color: #eaeaea;
    font-family: 'Poppins', sans-serif;
    overflow-x: hidden; /* Biar gak ada scroll samping */
}}

/* --- KUNANG-KUNANG (FIREFLIES) --- */
.firefly {{
    position: fixed;
    bottom: -10px;
    background: rgba(255, 255, 255, 0.5); /* Warna putih transparan */
    box-shadow: 0 0 15px 2px rgba(0, 201, 255, 0.6); /* Efek Glowing Biru */
    border-radius: 50%;
    pointer-events: none; /* PENTING: Biar bisa klik tembus */
    z-index: 0; /* Di belakang konten utama tapi di depan background */
    animation: floatUp linear infinite;
}}

/* Animasi Gerak ke Atas */
@keyframes floatUp {{
    0% {{
        bottom: -10px;
        opacity: 0;
        transform: translateX(0);
    }}
    10% {{
        opacity: 1; /* Mulai muncul */
    }}
    90% {{
        opacity: 1; 
    }}
    100% {{
        bottom: 100vh; /* Terbang sampai atas layar */
        opacity: 0;
        transform: translateX(20px); /* Geser dikit ke kanan */
    }}
}}

/* --- CONTAINER KONTEN (Biar gak ketutup bintang) --- */
.block-container {{
    position: relative;
    z-index: 1; /* Konten harus di atas bintang */
}}

/* --- SIDEBAR --- */
section[data-testid="stSidebar"] {{
    background-color: rgba(17, 20, 29, 0.95); /* Agak transparan dikit */
    border-right: 1px solid #2d323e;
    z-index: 2;
}}

/* Paksa Tulisan Sidebar Jadi Putih */
section[data-testid="stSidebar"] * {{
    color: #ffffff !important;
}}
.stCaption {{ color: #cccccc !important; }}

/* Tombol Undo (Kecil) */
button[kind="secondary"] {{
    background: transparent !important;
    border: 1px solid #555 !important;
    color: white !important;
    font-size: 10px !important;
}}
button[kind="secondary"]:hover {{
    border-color: #00C9FF !important;
    color: #00C9FF !important;
}}

/* --- KARTU BUKU & TOMBOL --- */
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
    background: rgba(28, 31, 38, 0.8); /* Semi transparan biar background kelihatan dikit */
    backdrop-filter: blur(5px); /* Efek kaca buram */
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

@st.cache_data
def cover(path):
    try:
        d = fitz.open(path)
        return d.load_page(0).get_pixmap(matrix=fitz.Matrix(0.4, 0.4)).tobytes("png")
    except: return None

def render_page(doc, page_num, zoom):
    try:
        return doc.load_page(page_num).get_pixmap(matrix=fitz.Matrix(zoom, zoom)).tobytes("png")
    except: return None

# =====================
# SIDEBAR
# =====================
with st.sidebar:
    st.header("👤 Rak Lia")
    
    st.subheader("📖 Sedang Dibaca")
    if st.session_state.sedang:
        for b in list(st.session_state.sedang):
            st.caption(f"• {b.replace('.pdf', '')}")
    else:
        st.caption("- Kosong -")

    st.divider()

    st.subheader("✅ Selesai")
    if st.session_state.selesai:
        for b in list(st.session_state.selesai):
            c1, c2 = st.columns([4, 1])
            with c1: st.caption(f"✔ {b.replace('.pdf', '')}")
            with c2:
                if st.button("↺", key=f"undo_{b}", help="Batal Selesai"):
                    st.session_state.selesai.discard(b)
                    st.session_state.sedang.add(b)
                    st.rerun()
    else:
        st.caption("- Belum ada -")

    st.divider()
    st.header("🎧 Mood")
    st.video("https://youtu.be/g9yQoMe8VDA")
    
    if st.session_state.buku:
        st.divider()
        zoom = st.slider("🔍 Ukuran Baca", 0.8, 2.5, 1.4, 0.1)
    else:
        zoom = 1.4

# =====================
# MAIN APP
# =====================
books = list_buku()

# --- MODE GALERI ---
if st.session_state.buku is None:
    st.markdown("<h1>✨ Galeri Buku</h1>", unsafe_allow_html=True)
    
    cari = st.text_input("🔍 Cari buku...", placeholder="Ketik judul buku...").lower()
    if cari: books = [b for b in books if cari in b.lower()]

    if not books: st.info("Belum ada buku. Upload di GitHub ya! 📂")
    
    cols = st.columns(4)
    for i, b in enumerate(books):
        with cols[i % 4]:
            path = f"buku_pdf/{b}"
            st.markdown("<div class='book-card'>", unsafe_allow_html=True)
            
            img_cover = cover(path)
            if img_cover: st.image(img_cover
