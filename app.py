import streamlit as st
import fitz  # PyMuPDF
import os

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Sains Data Library", layout="wide", page_icon="📚")

# --- 2. CSS "GRID TOKOPEDIA" (FIXED) ---
st.markdown("""
<style>
    /* Reset warna teks biar jelas */
    .stApp { background-color: #0e1117; color: white; }
    
    /* Judul Gradient tetap ada biar manis */
    h1 {
        background: -webkit-linear-gradient(45deg, #00C9FF, #92FE9D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }

    /* KARTU BUKU */
    div[data-testid="column"] {
        background-color: #262730;
        border: 1px solid #41444d;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        /* Biar tinggi kartu seragam */
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    /* Gambar Cover */
    img { border-radius: 4px; margin-bottom: 8px; width: 100%; object-fit: cover; }

    /* Tombol */
    div.stButton > button {
        width: 100%;
        border-radius: 15px;
        font-weight: bold;
        border: 1px solid #555;
    }

    /* --- HACK TAMPILAN HP (WAJIB ADA) --- */
    @media (max-width: 640px) {
        /* Paksa wadah kolom biar mau berjejer ke samping */
        div[data-testid="stHorizontalBlock"] {
            flex-direction: row !important;
            flex-wrap: wrap !important;
        }
        
        /* Paksa setiap kolom jadi 50% (setengah layar) */
        div[data-testid="column"] {
            width: 50% !important;
            flex: 0 0 50% !important;
            max-width: 50% !important;
            padding: 5px !important;
        }

        /* Kecilin font di HP biar muat */
        div[data-testid="column"] p {
            font-size: 11px !important;
            margin-bottom: 5px !important;
            line-height: 1.2;
        }
        
        /* Tombol lebih kecil di HP */
        div.stButton > button {
            font-size: 10px !important;
            padding: 2px 0px !important;
            min-height: 0px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- 3. STATE MANAGEMENT ---
if 'buku_terpilih' not in st.session_state: st.session_state.buku_terpilih = None
if 'halaman' not in st.session_state: st.session_state.halaman = 0
if 'sedang_dibaca' not in st.session_state: st.session_state.sedang_dibaca = set()

# --- 4. FUNGSI ---
def rapikan_judul(nama_file):
    nama = nama_file.replace('.pdf', '')
    nama = nama.split('(')[0]
    return nama.strip().title()

def get_list_buku(folder_path):
    if not os.path.exists(folder_path): os.makedirs(folder_path)
    return [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]

@st.cache_data
def get_cover(path_buku):
    try:
        doc = fitz.open(path_buku)
        pix = doc.load_page(0).get_pixmap(matrix=fitz.Matrix(0.4, 0.4))
        return pix.tobytes("png")
    except: return None

def get_page_image(path_buku, nomor_halaman, zoom=1.5):
    try:
        doc = fitz.open(path_buku)
        pix = doc.load_page(nomor_halaman).get_pixmap(matrix=fitz.Matrix(zoom, zoom))
        return pix.tobytes("png")
    except: return None

# --- 5. MAIN APP ---
folder_buku = "buku_pdf"
semua_buku = get_list_buku(folder_buku)

# SIDEBAR
with st.sidebar:
    st.header("🎧 Teman Belajar")
    st.video("https://www.youtube.com/watch?v=jfKfPfyJRdk")
    st.divider()
    if st.session_state.buku_terpilih:
        if st.button("⬅️ KEMBALI KE RAK", type="primary"):
            st.session_state.buku_terpilih = None
            st.session_state.halaman = 0
            st.rerun()

# AREA UTAMA
if st.session_state.buku_terpilih is None:
    st.title("📚 Pustaka Sains Data")
    
    cari = st.text_input("🔍 Cari Judul...", placeholder="Ketik judul...")
    buku_filtered = [b for b in semua_buku if cari.lower() in b.lower()]
    
    if not buku_filtered:
        st.warning("Buku tidak ditemukan.")
    else:
        # --- LOGIKA GRID BARU (PENTING BUAT HP) ---
        # Kita bagi buku jadi kelompok 4 (untuk laptop).
        # CSS di atas akan otomatis maksa jadi 2 kolom kalau di HP.
        
        kolom_per_baris = 4
        # Loop dengan loncat setiap 4 angka
        for i in range(0, len(buku_filtered), kolom_per_baris):
            # Ambil potongan 4 buku
            batch_buku = buku_filtered[i : i + kolom_per_baris]
            
            # Bikin wadah kolom (Row)
            cols = st.columns(kolom_per_baris)
            
            # Masukkan buku ke kolom yang tersedia
            for j, buku in enumerate(batch_buku):
                path = os.path.join(folder_buku, buku)
                with cols[j]:
                    cover = get_cover(path)
                    if cover: st.image(cover, use_container_width=True)
                    
                    judul_rapi = rapikan_judul(buku)
                    # Judul dipotong dikit biar gak ngerusak kotak
                    if len(judul_rapi) > 35: judul_rapi = judul_rapi[:32] + "..."
                    st.caption(f"**{judul_rapi}**")
                    
                    if st.button("📖 Baca", key=f"btn_{buku}"):
                        st.session_state.buku_terpilih = buku
                        st.session_state.halaman = 0
                        st.session_state.sedang_dibaca.add(buku)
                        st.rerun()

# MODE BACA
else:
    buku_aktif = st.session_state.buku_terpilih
    path_lengkap = os.path.join(folder_buku, buku_aktif)
    judul_rapi = rapikan_judul(buku_aktif)
    
    c1, c2 = st.columns([3, 1])
    with c1: st.subheader(f"📖 {judul_rapi}")
    with c2: zoom = st.slider("🔍 Zoom", 0.5, 2.0, 1.0, 0.1)

    try:
        doc = fitz.open(path_lengkap)
        total_hal = doc.page_count
        gambar = get_page_image(path_lengkap, st.session_state.halaman, zoom)
        
        # Layout tengah
        kiri, tengah, kanan = st.columns([1, 10, 1])
        with tengah:
            st.image(gambar, use_container_width=True)
            
            col_prev, col_info, col_next = st.columns([1, 2, 1])
            with col_prev:
                if st.session_state.halaman > 0:
                    if st.button("⬅️ Prev", use_container_width=True):
                        st.session_state.halaman -= 1
                        st.rerun()
            with col_info:
                st.markdown(f"<div style='text-align:center; margin-top:5px'>{st.session_state.halaman + 1} / {total_hal}</div>", unsafe_allow_html=True)
            with col_next:
                if st.session_state.halaman < total_hal - 1:
                    if st.button("Next ➡️", use_container_width=True):
                        st.session_state.halaman += 1
                        st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")
