import streamlit as st
import fitz  # PyMuPDF
import os

# =====================
# CONFIG
# =====================
st.set_page_config(page_title="Z-Library Mini", page_icon="📚", layout="wide")

# =====================
# CSS (DESAIN TAMPILAN)
# =====================
st.markdown("""
<style>
/* Import Font Keren: Poppins */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

/* --- DASAR HALAMAN --- */
.stApp {
    background: linear-gradient(to bottom right, #0e1117, #161b24);
    color: #eaeaea;
    font-family: 'Poppins', sans-serif;
}

/* --- SIDEBAR (Menu Kiri) --- */
section[data-testid="stSidebar"] {
    background-color: #11141d;
    border-right: 1px solid #2d323e;
}

/* Paksa semua tulisan di Sidebar jadi Putih Terang */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div,
section[data-testid="stSidebar"] label {
    color: #ffffff !important;
}

/* Fix Icon Panah & Tombol di Sidebar */
button[kind="header"] svg, 
section[data-testid="stSidebar"] svg {
    fill: white !important;
    color: white !important;
}

/* Fix Text Caption (Daftar buku) */
.stCaption {
    color: #cccccc !important;
}

/* --- JUDUL GRADIENT --- */
h1, h2, h3 {
    font-weight: 700 !important;
    background: -webkit-linear-gradient(45deg, #00C9FF, #92FE9D);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
/* Reset gradient khusus di sidebar biar tetap putih */
section[data-testid="stSidebar"] h1, 
section[data-testid="stSidebar"] h2 {
    background: none !important;
    -webkit-text-fill-color: white !important;
}

/* --- TOMBOL --- */
.stButton button {
    background: #262a36 !important;
    color: #ffffff !important;
    border: 1px solid #3a3f4b;
    border-radius: 12px;
    transition: all 0.3s ease;
}
.stButton button:hover {
    border-color: #00C9FF;
    box-shadow: 0 0 10px rgba(0, 201, 255, 0.3);
}

/* Tombol BACA (Gradient Biru) */
[data-testid="column"] .stButton button {
    background: linear-gradient(45deg, #00C9FF, #0078ff) !important;
    border: none !important;
    box-shadow: 0 4px 15px rgba(0, 201, 255, 0.4);
}

/* --- KARTU BUKU --- */
.book-card {
    background: #1c1f26;
    border: 1px solid #2d323e;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    border-radius: 16px;
    padding: 15px;
    transition: all 0.3s ease;
    margin-bottom: 20px;
}
.book-card:hover {
    transform: translateY(-5px);
    border-color: #00C9FF;
    box-shadow: 0 10px 30px rgba(0, 201, 255, 0.2);
}
.book-title {
    text-align: center;
    font-size: 14px;
    font-weight: 600;
    margin-top: 10px;
    color: #fff;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* --- READER AREA --- */
.reader-wrap {
    max-width: 900px;
    margin: 0 auto;
    padding: 10px;
    background: #16181d;
    border-radius: 15px;
    text-align: center;
}
</style>
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
# FUNGSI-FUNGSI
# =====================
def list_buku():
    if not os.path.exists("buku_pdf"):
        os.makedirs("buku_pdf")
    return [b for b in os.listdir("buku_pdf") if b.endswith(".pdf")]

@st.cache_data
def cover(path):
    try:
        d = fitz.open(path)
        p = d.load_page(0)
        pix = p.get_pixmap(matrix=fitz.Matrix(0.4, 0.4))
        return pix.tobytes("png")
    except:
        return None

def render_page(doc, page_num, zoom):
    try:
        page = doc.load_page(page_num)
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
        return pix.tobytes("png")
    except Exception as e:
        return None

# =====================
# SIDEBAR
# =====================
with st.sidebar:
    st.header("👤 Rak Lia")
    
    st.subheader("📖 Sedang Dibaca")
    if st.session_state.sedang:
        for b in st.session_state.sedang:
            st.caption(f"• {b.replace('.pdf', '')}")
    else:
        st.caption("-")

    st.subheader("✅ Selesai")
    if st.session_state.selesai:
        for b in st.session_state.selesai:
            st.caption(f"✔ {b.replace('.pdf', '')}")
    else:
        st.caption("-")

    st.divider()
    st.header("🎧 Mood")
    st.video("https://youtu.be/g9yQoMe8VDA")
    st.divider()
    
    # Slider Zoom hanya muncul pas baca
    if st.session_state.buku is not None:
        zoom = st.slider("🔍 Ukuran Baca", 0.8, 2.5, 1.4, 0.1)
    else:
        zoom = 1.4

# =====================
# HALAMAN UTAMA
# =====================
books = list_buku()

# --- MODE GALERI ---
if st.session_state.buku is None:
    st.markdown("<h1>📚 Galeri Buku</h1>", unsafe_allow_html=True)
    
    cari = st.text_input("🔍 Cari buku...", placeholder="Ketik judul buku...").lower()
    if cari:
        books = [b for b in books if cari in b.lower()]

    if not books:
        st.info("Buku tidak ditemukan. Upload dulu di GitHub ya! 📂")
    
    # Grid Layout
    cols = st.columns(4)
    for i, b in enumerate(books):
        with cols[i % 4]:
            path = f"buku_pdf/{b}"
            
            # Tampilan Kartu
            st.markdown("<div class='book-card'>", unsafe_allow_html=True)
            
            img_cover = cover(path)
            if img_cover:
                st.image(img_cover, use_container_width=True)
            else:
                st.markdown("📄 *Cover tidak tersedia*")
                
            judul = b.replace(".pdf", "").replace("_", " ")
            st.markdown(f"<div class='book-title' title='{judul}'>{judul}</div>", unsafe_allow_html=True)
            
            # Tombol Baca
            if st.button("📖 BACA", key=f"read_{b}", use_container_width=True):
                st.session_state.buku = b
                st.session_state.halaman = st.session_state.progress.get(b, 0)
                st.session_state.sedang.add(b)
                st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)

# --- MODE BACA ---
else:
    b = st.session_state.buku
    path = f"buku_pdf/{b}"
    
    try:
        doc = fitz.open(path)
        total_hal = doc.page_count
        
        # Header Baca
        c1, c2, c3 = st.columns([1, 6, 1])
        with c1:
            if st.button("⬅️ Kembali"):
                st.session_state.buku = None
                st.rerun()
        with c2:
            st.markdown(f"<h3 style='text-align:center; margin:0'>{b.replace('.pdf','')}</h3>", unsafe_allow_html=True)
        with c3:
            if st.button("✅ Selesai"):
                st.session_state.selesai.add(b)
                st.session_state.sedang.discard(b)
                st.session_state.buku = None
                st.toast("Buku selesai! Selamat 🎉")
                st.rerun()

        st.divider()

        # Navigasi Halaman
        n1, n2, n3 = st.columns([1, 2, 1])
        with n1:
            if st.session_state.halaman > 0:
                if st.button("⬅️ Sebelumnya", use_container_width=True):
                    st.session_state.halaman -= 1
                    st.rerun()
        with n2:
            st.markdown(f"<div style='text-align:center; padding-top:10px; font-weight:bold'>Halaman {st.session_state.halaman + 1} / {total_hal}</div>", unsafe_allow_html=True)
        with n3:
            if st.session_state.halaman < total_hal - 1:
                if st.button("Berikutnya ➡️", use_container_width=True):
                    st.session_state.halaman += 1
                    st.rerun()

        # Render Halaman PDF
        st.markdown("<div class='reader-wrap'>", unsafe_allow_html=True)
        gambar_halaman = render_page(doc, st.session_state.halaman, zoom)
        
        if gambar_halaman:
            st.image(gambar_halaman, use_container_width=True)
        else:
            st.error("Gagal memuat halaman ini. Coba refresh atau pindah halaman.")
            
        st.markdown("</div>", unsafe_allow_html=True)

        # Simpan Progress
        st.session_state.progress[b] = st.session_state.halaman
        doc.close()

    except Exception as e:
        st.error(f"Terjadi kesalahan saat membuka buku: {e}")
        if st.button("Kembali ke Rak"):
            st.session_state.buku = None
            st.rerun()
