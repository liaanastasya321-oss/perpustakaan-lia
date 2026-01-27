import streamlit as st
import fitz  # PyMuPDF
import os
import random
import pandas as pd  # Kita butuh ini buat bikin Grafik Data Science 📊

# =====================
# 1. KONFIGURASI HALAMAN
# =====================
st.set_page_config(page_title="Z-Library Mini", page_icon="📚", layout="wide")

# =====================
# 2. LOGIKA KUNANG-KUNANG
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
# 3. INJECT DESAIN (CSS)
# =====================
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

/* --- KARTU BUKU --- */
.book-card {
    background: rgba(28, 31, 38, 0.8);
    backdrop-filter: blur(5px);
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
</style>
""", unsafe_allow_html=True)

# =====================
# 4. INJECT KUNANG-KUNANG
# =====================
st.markdown(firefly_html, unsafe_allow_html=True)

# =====================
# 5. STATE MANAGEMENT
# =====================
if 'buku' not in st.session_state: st.session_state.buku = None
if 'halaman' not in st.session_state: st.session_state.halaman = 0
if 'sedang' not in st.session_state: st.session_state.sedang = set()
if 'selesai' not in st.session_state: st.session_state.selesai = set()
if 'progress' not in st.session_state: st.session_state.progress = {}
if 'catatan' not in st.session_state: st.session_state.catatan = {} 

# =====================
# 6. FUNGSI
# =====================
def list_buku():
    if not os.path.exists("buku_pdf"): os.makedirs("buku_pdf")
    return [b for b in os.listdir("buku_pdf") if b.endswith(".pdf")]

# --- FUNGSI DETEKSI KATEGORI ---
def get_kategori(judul_file):
    # Cek apakah ada kurung siku [...] di nama file
    if "[" in judul_file and "]" in judul_file:
        start = judul_file.find("[") + 1
        end = judul_file.find("]")
        return judul_file[start:end] # Ambil teks di dalam kurung
    return "Lainnya"

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
# 7. SIDEBAR (DENGAN STATISTIK)
# =====================
with st.sidebar:
    st.header("👤 Rak Lia")
    
    # --- FITUR 1: STATISTIK BACAAN (DATA SCIENCE STYLE) 📊 ---
    st.subheader("📊 Statistik")
    
    # Hitung Data
    jml_sedang = len(st.session_state.sedang)
    jml_selesai = len(st.session_state.selesai)
    
    # Tampilkan Angka Cepat
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1: st.metric("Sedang", f"{jml_sedang}")
    with col_stat2: st.metric("Selesai", f"{jml_selesai}")
    
    # Tampilkan Grafik Batang (Kalau ada datanya)
    if jml_sedang > 0 or jml_selesai > 0:
        data_statistik = pd.DataFrame({
            'Status': ['Sedang', 'Selesai'],
            'Jumlah': [jml_sedang, jml_selesai]
        })
        st.bar_chart(data_statistik.set_index('Status'), color=["#00C9FF"]) # Warna Biru Neon

    st.divider()

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
        
    # --- FITUR CATATAN ---
    if st.session_state.buku:
        st.divider()
        st.subheader("📝 Catatan Halaman Ini")
        
        buku_sekarang = st.session_state.buku
        hal_sekarang = st.session_state.halaman
        id_catatan = f"{buku_sekarang}_hal_{hal_sekarang}"
        isi_lama = st.session_state.catatan.get(id_catatan, "")
        
        catatan_baru = st.text_area("Tulis sesuatu...", value=isi_lama, height=150, placeholder="Contoh: Rumus penting...")
        
        if catatan_baru:
            st.session_state.catatan[id_catatan] = catatan_baru
        elif id_catatan in st.session_state.catatan:
            del st.session_state.catatan[id_catatan]

    st.divider()
    st.header("🎧 Mood")
    
    video_id = "g9yQoMe8VDA"
    youtube_html = f"""
    <iframe width="100%" height="200" 
    src="https://www.youtube.com/embed/{video_id}?playsinline=1" 
    frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
    allowfullscreen></iframe>
    """
    st.markdown(youtube_html, unsafe_allow_html=True)
    
    # ZOOM
    if st.session_state.buku:
        st.divider()
        zoom = st.slider("🔍 Ukuran Baca", 0.3, 2.0, 0.6, 0.1)
    else:
        zoom = 0.6

# =====================
# 8. MAIN APP
# =====================
books = list_buku()

# --- MODE GALERI ---
if st.session_state.buku is None:
    st.markdown("<h1>✨ Galeri Buku</h1>", unsafe_allow_html=True)
    
    # --- FITUR 2: FILTER KATEGORI 📂 ---
    # 1. Ambil semua kategori unik dari nama file
    semua_kategori = set()
    for b in books:
        kategori = get_kategori(b)
        semua_kategori.add(kategori)
    
    # Urutkan dan tambahkan opsi "Semua"
    list_opsi = ["Semua"] + sorted(list(semua_kategori))
    
    # Tampilkan Dropdown Filter
    col_filter1, col_filter2 = st.columns([1, 3])
    with col_filter1:
        pilih_kategori = st.selectbox("📂 Pilih Rak:", list_opsi)
    
    # Filter list buku berdasarkan pilihan
    buku_tampil = []
    if pilih_kategori == "Semua":
        buku_tampil = books
    else:
        for b in books:
            if get_kategori(b) == pilih_kategori:
                buku_tampil.append(b)

    # Search Bar (Tetap ada)
    cari = st.text_input("🔍 Cari buku...", placeholder="Ketik judul buku...").lower()
    if cari: buku_tampil = [b for b in buku_tampil if cari in b.lower()]

    if not buku_tampil: 
        st.info("Belum ada buku di rak ini. Upload di GitHub ya! 📂")
    
    # Tampilkan Grid Buku
    cols = st.columns(4)
    for i, b in enumerate(buku_tampil):
        with cols[i % 4]:
            path = f"buku_pdf/{b}"
            st.markdown("<div class='book-card'>", unsafe_allow_html=True)
            
            img_cover = cover(path)
            if img_cover: st.image(img_cover, use_container_width=True)
            
            # Bersihkan nama file dari [Kategori] biar judulnya rapi
            judul_bersih = b.replace(".pdf", "").replace("_", " ")
            if "[" in judul_bersih and "]" in judul_bersih:
                judul_bersih = judul_bersih.split("]")[1].strip() # Ambil setelah kurung siku

            st.markdown(f"<div class='book-title' title='{judul_bersih}'>{judul_bersih}</div>", unsafe_allow_html=True)
            
            label_tombol = "📖 BACA"
            if b in st.session_state.selesai:
                label_tombol = "♻️ BACA ULANG"
            
            if st.button(label_tombol, key=f"btn_{b}", use_container_width=True):
                st.session_state.buku = b
                st.session_state.halaman = st.session_state.progress.get(b, 0)
                st.session_state.sedang.add(b)
                st.session_state.selesai.discard(b)
                st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)

# --- MODE BACA ---
else:
    b = st.session_state.buku
    path = f"buku_pdf/{b}"
    
    try:
        doc = fitz.open(path)
        total_hal = doc.page_count
        
        # === HEADER (JUDUL & TOMBOL KELUAR) ===
        c1, c2, c3 = st.columns([1, 6, 1])
        with c1:
            if st.button("⬅️ Kembali"):
                st.session_state.buku = None
                st.rerun()
        with c2:
            # Judul bersih di mode baca juga
            judul_bersih = b.replace('.pdf','').replace("_", " ")
            if "[" in judul_bersih and "]" in judul_bersih:
                judul_bersih = judul_bersih.split("]")[1].strip()
            st.markdown(f"<h3 style='text-align:center; margin:0'>{judul_bersih}</h3>", unsafe_allow_html=True)
        with c3:
            if st.button("✅ Selesai"):
                st.session_state.selesai.add(b)
                st.session_state.sedang.discard(b)
                st.session_state.buku = None
                st.toast("Buku selesai! 🎉")
                st.rerun()

        st.divider()

        # === 1. INFO HALAMAN ===
        st.markdown(f"<div style='text-align:center; margin-bottom: 10px;'><b>Halaman {st.session_state.halaman + 1} / {total_hal}</b></div>", unsafe_allow_html=True)
        
        # Indikator Catatan
        id_catatan_cek = f"{b}_hal_{st.session_state.halaman}"
        if id_catatan_cek in st.session_state.catatan:
            st.info(f"📝 Catatan: {st.session_state.catatan[id_catatan_cek]}")

        # === 2. GAMBAR BUKU ===
        st.markdown("<div style='text-align:center; background:rgba(22, 24, 29, 0.9); padding:10px; border-radius:15px; border:1px solid #333'>", unsafe_allow_html=True)
        gambar = render_page(doc, st.session_state.halaman, zoom)
        if gambar: st.image(gambar, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.write("") 

        # === 3. NAVIGASI ===
        n1, n2 = st.columns([1, 1])
        with n1:
            if st.session_state.halaman > 0:
                if st.button("⬅️ Sebelumnya", use_container_width=True):
                    st.session_state.halaman -= 1
                    st.rerun()
            else:
                st.markdown("") 

        with n2:
            if st.session_state.halaman < total_hal - 1:
                if st.button("Berikutnya ➡️", use_container_width=True):
                    st.session_state.halaman += 1
                    st.rerun()

        st.session_state.progress[b] = st.session_state.halaman
        doc.close()

    except Exception as e:
        st.error(f"Error: {e}")
        if st.button("Kembali ke Rak"):
            st.session_state.buku = None
            st.rerun()
