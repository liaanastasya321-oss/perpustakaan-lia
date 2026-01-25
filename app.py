import streamlit as st
import fitz  # PyMuPDF
import os

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(page_title="Lia's Library", layout="wide", page_icon="📚")

# ==========================================
# 2. CSS (DESAIN TAMPILAN HP & LAPTOP)
# ==========================================
st.markdown("""
<style>
    /* --- DASAR --- */
    .stApp { background-color: #0e1117; color: #eaeaea; }
    
    /* Judul Gradient */
    h1 {
        background: linear-gradient(45deg, #00C9FF, #92FE9D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        margin-bottom: 10px;
    }

    /* --- KARTU BUKU (DESAIN KOTAK) --- */
    div[data-testid="column"] {
        background-color: #1c1f26;
        border: 1px solid #2d3035;
        border-radius: 12px;
        padding: 10px;
        text-align: center;
        transition: 0.3s;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        
        /* Biar isinya rapi vertikal */
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
    }
    
    div[data-testid="column"]:hover {
        border-color: #00C9FF;
        transform: translateY(-5px);
    }
    
    /* Gambar Sampul */
    img { border-radius: 6px; margin-bottom: 8px; }

    /* Tombol Baca */
    div.stButton > button {
        background-color: #2b2f38 !important;
        color: white !important;
        border-radius: 20px;
        border: 1px solid #3e424b;
        font-size: 14px;
        width: 100%;
        margin-top: auto;
    }
    div.stButton > button:hover {
        border-color: #00C9FF;
        color: #00C9FF !important;
    }

    /* --- KHUSUS TAMPILAN HP (MOBILE) --- */
    /* Ini Hack biar jadi 2 kolom di HP */
    @media (max-width: 576px) {
        div[data-testid="column"] {
            width: 48% !important;
            flex: 0 0 48% !important;
            max-width: 48% !important;
            min-width: 48% !important;
            margin-bottom: 8px !important;
            padding: 8px !important;
        }
        
        /* Font Judul di HP dikecilin dikit */
        div[data-testid="column"] p {
            font-size: 12px !important;
            line-height: 1.3 !important;
            margin-bottom: 8px !important;
            font-weight: bold;
        }
        
        /* Tombol di HP */
        div.stButton > button {
            font-size: 11px !important;
            padding: 4px 0px !important;
            min-height: 0px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. STATE (MEMORI APLIKASI)
# ==========================================
if 'buku_terpilih' not in st.session_state: st.session_state.buku_terpilih = None
if 'halaman' not in st.session_state: st.session_state.halaman = 0
if 'riwayat_baca' not in st.session_state: st.session_state.riwayat_baca = {} 

# ==========================================
# 4. FUNGSI PINTAR
# ==========================================
def rapikan_judul(nama_file):
    # Buang .pdf
    clean = nama_file.replace('.pdf', '')
    # Buang tulisan dalam kurung kayak (Z-Library)
    clean = clean.split('(')[0]
    return clean.strip().title()

def get_list_buku():
    folder = "buku_pdf"
    if not os.path.exists(folder): os.makedirs(folder)
    return [f for f in os.listdir(folder) if f.lower().endswith('.pdf')]

@st.cache_data
def get_cover(path_buku):
    try:
        doc = fitz.open(path_buku)
        pix = doc.load_page(0).get_pixmap(matrix=fitz.Matrix(0.5, 0.5))
        return pix.tobytes("png")
    except: return None

def get_page_image(path_buku, nomor_halaman, zoom=1.5):
    try:
        doc = fitz.open(path_buku)
        pix = doc.load_page(nomor_halaman).get_pixmap(matrix=fitz.Matrix(zoom, zoom))
        return pix.tobytes("png")
    except: return None

# ==========================================
# 5. HALAMAN UTAMA
# ==========================================
folder_buku = "buku_pdf"
semua_buku = get_list_buku()

# --- SIDEBAR (MENU KIRI) ---
with st.sidebar:
    st.header("👤 Rak Lia")
    
    # Riwayat Baca (Bookmark)
    st.subheader("🔖 Terakhir Dibaca")
    if st.session_state.riwayat_baca:
        for buku, hal in st.session_state.riwayat_baca.items():
            judul_pendek = rapikan_judul(buku)
            if len(judul_pendek) > 18: judul_pendek = judul_pendek[:18] + "..."
            
            # Tombol Lanjut Baca
            if st.button(f"📄 {judul_pendek} (Hal {hal+1})", key=f"hist_{buku}"):
                st.session_state.buku_terpilih = buku
                st.session_state.halaman = hal
                st.rerun()
    else:
        st.caption("Belum ada riwayat.")

    st.divider()
    st.header("🎧 Musik Fokus")
    st.video("https://www.youtube.com/watch?v=jfKfPfyJRdk")
    
    if st.session_state.buku_terpilih:
        st.divider()
        zoom_level = st.slider("🔍 Zoom Tulisan", 0.8, 2.5, 1.2, 0.1)

# --- AREA KONTEN ---

# MODE 1: GALERI (RAK BUKU)
if st.session_state.buku_terpilih is None:
    st.title("📚 Pustaka Sains Data")
    
    # Pencarian
    cari = st.text_input("🔍 Cari buku...", placeholder="Ketik judul buku...").lower()
    
    # Filter Buku
    buku_filtered = [b for b in semua_buku if cari in b.lower()]
    
    if not buku_filtered:
        st.info("Buku tidak ditemukan atau folder kosong.")
    else:
        # GRID LAYOUT (4 Kolom Laptop / 2 Kolom HP - Diatur CSS di atas)
        cols = st.columns(4)
        for i, buku in enumerate(buku_filtered):
            path = os.path.join(folder_buku, buku)
            col = cols[i % 4]
            
            with col:
                # Cover
                cover = get_cover(path)
                if cover: st.image(cover, use_container_width=True)
                
                # Judul Bersih
                judul_rapi = rapikan_judul(buku)
                st.markdown(f"**{judul_rapi}**")
                
                # Tombol Baca
                if st.button("📖 Baca", key=f"btn_{i}"):
                    st.session_state.buku_terpilih = buku
                    # Cek kalau pernah baca, lanjut halaman terakhir
                    st.session_state.halaman = st.session_state.riwayat_baca.get(buku, 0)
                    st.rerun()

# MODE 2: BACA BUKU (READER)
else:
    buku_aktif = st.session_state.buku_terpilih
    path_lengkap = os.path.join(folder_buku, buku_aktif)
    
    try:
        doc = fitz.open(path_lengkap)
        total_hal = doc.page_count
        judul_rapi = rapikan_judul(buku_aktif)

        # Header Navigasi Atas
        c1, c2, c3 = st.columns([1, 4, 1])
        with c1:
            if st.button("⬅️ Kembali"):
                st.session_state.buku_terpilih = None
                st.rerun()
        with c2:
            st.markdown(f"<h3 style='text-align:center; margin:0'>{judul_rapi}</h3>", unsafe_allow_html=True)
        with c3:
            # Tombol refresh/bookmark otomatis
            pass 

        # Tampilkan Halaman
        # Gunakan zoom dari sidebar (default 1.2)
        zoom = zoom_level if 'zoom_level' in locals() else 1.2
        gambar = get_page_image(path_lengkap, st.session_state.halaman, zoom)
        
        # Container Gambar (Biar rapi di tengah)
        st.image(gambar, use_container_width=True)
        
        # Simpan Progress Baca Otomatis
        st.session_state.riwayat_baca[buku_aktif] = st.session_state.halaman

        # Tombol Navigasi Bawah
        col_prev, col_hal, col_next = st.columns([1, 2, 1])
        
        with col_prev:
            if st.session_state.halaman > 0:
                if st.button("⬅️ Mundur", use_container_width=True):
                    st.session_state.halaman -= 1
                    st.rerun()
        
        with col_hal:
            st.markdown(f"<p style='text-align:center; padding-top:10px'>Hal <b>{st.session_state.halaman + 1}</b> / {total_hal}</p>", unsafe_allow_html=True)
            
        with col_next:
            if st.session_state.halaman < total_hal - 1:
                if st.button("Lanjut ➡️", use_container_width=True):
                    st.session_state.halaman += 1
                    st.rerun()

    except Exception as e:
        st.error(f"Error membuka buku: {e}")
        if st.button("Kembali ke Rak"):
            st.session_state.buku_terpilih = None
            st.rerun()
