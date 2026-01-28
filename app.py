import streamlit as st
import fitz  # PyMuPDF
import os
import random
import matplotlib.pyplot as plt
import base64
import json 

# =====================
# 1. KONFIGURASI HALAMAN
# =====================
st.set_page_config(page_title="Liaaaa-Library Mini", page_icon="😻", layout="wide")

# =====================
# 2. SISTEM PENYIMPANAN DATA (DATABASE JSON) 💾
# =====================
FILE_DATABASE = "data_perpus.json"

def load_data():
    """Mengambil data dari file"""
    if not os.path.exists(FILE_DATABASE):
        # FIX ERROR: Defaultnya harus set() bukan []
        return {"sedang": set(), "selesai": set(), "progress": {}, "catatan": {}}
    
    try:
        with open(FILE_DATABASE, "r") as f:
            data = json.load(f)
            # FIX ERROR: Paksa ubah list dari JSON menjadi set kembali
            return {
                "sedang": set(data.get("sedang", [])),
                "selesai": set(data.get("selesai", [])),
                "progress": data.get("progress", {}),
                "catatan": data.get("catatan", {})
            }
    except:
        # Kalau file rusak, reset ulang
        return {"sedang": set(), "selesai": set(), "progress": {}, "catatan": {}}

def save_data():
    """Menyimpan data ke file"""
    data_simpan = {
        "sedang": list(st.session_state.sedang), # Ubah set ke list biar bisa masuk JSON
        "selesai": list(st.session_state.selesai),
        "progress": st.session_state.progress,
        "catatan": st.session_state.catatan
    }
    try:
        with open(FILE_DATABASE, "w") as f:
            json.dump(data_simpan, f)
    except Exception as e:
        st.error(f"Gagal menyimpan data: {e}")

# =====================
# 3. SISTEM LOGIN 🔐
# =====================
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("🔒 Masukkan Password Akses:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("🔒 Masukkan Password Akses:", type="password", on_change=password_entered, key="password")
        st.error("🚫 Password salah, coba lagi ya!")
        return False
    else:
        return True

if not check_password():
    st.stop()

# =====================
# 4. INIT STATE (LOAD DARI FILE)
# =====================
data_awal = load_data()

if 'buku' not in st.session_state: st.session_state.buku = None
if 'halaman' not in st.session_state: st.session_state.halaman = 0
# Pastikan ini ngambil dari data_awal yang sudah dikonversi jadi set
if 'sedang' not in st.session_state: st.session_state.sedang = data_awal["sedang"]
if 'selesai' not in st.session_state: st.session_state.selesai = data_awal["selesai"]
if 'progress' not in st.session_state: st.session_state.progress = data_awal["progress"]
if 'catatan' not in st.session_state: st.session_state.catatan = data_awal["catatan"]

# =====================
# 5. ASSETS & CSS
# =====================
firefly_html = ""
for i in range(50):
    left = random.randint(1, 99)
    delay = random.uniform(0, 20)
    duration = random.uniform(10, 20)
    size = random.randint(2, 5)
    firefly_html += f"""<div class="firefly" style="left: {left}%; animation-delay: {delay}s; animation-duration: {duration}s; width: {size}px; height: {size}px;"></div>"""

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
.stApp { background: radial-gradient(circle at center, #1b2735 0%, #090a0f 100%); color: #eaeaea; font-family: 'Poppins', sans-serif; overflow-x: hidden; }
header[data-testid="stHeader"] { background-color: transparent !important; z-index: 1; }
div[data-testid="stDecoration"] { visibility: hidden; }
button[title="View fullscreen"], [data-testid="StyledFullScreenButton"] { display: none !important; }
.firefly { position: fixed; bottom: -10px; background: rgba(255, 255, 255, 0.5); box-shadow: 0 0 15px 2px rgba(0, 201, 255, 0.6); border-radius: 50%; pointer-events: none; z-index: 999; animation: floatUp linear infinite; }
@keyframes floatUp { 0% { bottom: -10px; opacity: 0; transform: translateX(0); } 10% { opacity: 1; } 90% { opacity: 1; } 100% { bottom: 100vh; opacity: 0; transform: translateX(20px); } }
section[data-testid="stSidebar"] { background-color: rgba(17, 20, 29, 0.95); border-right: 1px solid #2d323e; z-index: 1000; }
section[data-testid="stSidebar"] * { color: #ffffff !important; }
.stCaption { color: #cccccc !important; }
.stTextArea textarea { background-color: #262a36 !important; color: white !important; }
button[kind="secondary"] { background: transparent !important; border: 1px solid #555 !important; color: white !important; font-size: 10px !important; }
.stButton button { background: #262a36 !important; color: #ffffff !important; border: 1px solid #3a3f4b; border-radius: 12px; transition: all 0.3s ease; width: 100%; }
[data-testid="column"] .stButton button { background: linear-gradient(45deg, #00C9FF, #0078ff) !important; border: none !important; box-shadow: 0 4px 15px rgba(0, 201, 255, 0.3); }
[data-testid="column"] .stButton button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0, 201, 255, 0.6); }
.book-card { background: rgba(28, 31, 38, 0.8); backdrop-filter: blur(5px); border: 1px solid #2d323e; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3); border-radius: 16px; padding: 15px; transition: all 0.3s ease; margin-bottom: 20px; height: 100%; display: flex; flex-direction: column; justify-content: space-between; }
.book-card:hover { transform: translateY(-5px); border-color: #00C9FF; }
.cover-img { width: 100%; height: 280px; object-fit: cover; border-radius: 8px; margin-bottom: 12px; }
.book-title { text-align: center; font-size: 14px; font-weight: 600; color: #fff; margin-bottom: 15px; height: 42px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
</style>
""", unsafe_allow_html=True)
st.markdown(firefly_html, unsafe_allow_html=True)

# =====================
# 6. FUNGSI UTAMA
# =====================
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

# =====================
# 7. SIDEBAR
# =====================
with st.sidebar:
    st.header("👤 Rak Lia")
    
    st.subheader("📊 Statistik")
    jml_sedang = len(st.session_state.sedang)
    jml_selesai = len(st.session_state.selesai)
    
    if jml_sedang > 0 or jml_selesai > 0:
        fig, ax = plt.subplots(figsize=(4, 2.5)) 
        fig.patch.set_alpha(0) 
        ax.set_facecolor("none")
        kategori = ['Sedang', 'Selesai']
        jumlah = [jml_sedang, jml_selesai]
        warna = ['#00C9FF', '#92FE9D'] 
        bars = ax.bar(kategori, jumlah, color=warna)
        ax.tick_params(colors='white', which='both')
        for spine in ax.spines.values():
            spine.set_edgecolor('white')
        st.pyplot(fig, use_container_width=True)
    else:
        st.caption("Grafik akan muncul jika ada aktivitas.")

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
                if st.button("↺", key=f"undo_{b}"):
                    st.session_state.selesai.discard(b)
                    st.session_state.sedang.add(b)
                    save_data() # SIMPAN DATA!
                    st.rerun()
    else:
        st.caption("- Belum ada -")
        
    if st.session_state.buku:
        st.divider()
        st.subheader("📝 Catatan Halaman Ini")
        buku_sekarang = st.session_state.buku
        hal_sekarang = st.session_state.halaman
        id_catatan = f"{buku_sekarang}_hal_{hal_sekarang}"
        isi_lama = st.session_state.catatan.get(id_catatan, "")
        
        catatan_baru = st.text_area("Tulis sesuatu...", value=isi_lama, height=150, placeholder="Contoh: Rumus penting...", key="input_catatan")
        
        if st.button("💾 Simpan Catatan"):
            if catatan_baru:
                st.session_state.catatan[id_catatan] = catatan_baru
            elif id_catatan in st.session_state.catatan:
                del st.session_state.catatan[id_catatan]
            save_data() # SIMPAN DATA!
            st.toast("Catatan tersimpan!")

    st.divider()
    st.header("🎧 Mood")
    video_id = "g9yQoMe8VDA"
    youtube_html = f"""<iframe width="100%" height="200" src="https://www.youtube.com/embed/{video_id}?playsinline=1" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>"""
    st.markdown(youtube_html, unsafe_allow_html=True)
    
    if st.session_state.buku:
        st.divider()
        zoom = st.slider("🔍 Ukuran Baca", 0.3, 2.0, 0.6, 0.1)
    else:
        zoom = 0.6

# =====================
# 8. MAIN APP
# =====================
books = list_buku()

if st.session_state.buku is None:
    st.markdown("<h1>✨ Galeri Buku</h1>", unsafe_allow_html=True)
    
    cari = st.text_input("🔍 Cari buku...", placeholder="Ketik judul buku...").lower()
    if cari: books = [b for b in books if cari in b.lower()]

    if not books: st.info("Belum ada buku. Upload di GitHub ya! 📂")
    
    cols = st.columns(4)
    for i, b in enumerate(books):
        with cols[i % 4]:
            path = f"buku_pdf/{b}"
            img_bytes = cover(path)
            if img_bytes:
                b64_img = base64.b64encode(img_bytes).decode('utf-8')
                img_html = f'<img src="data:image/png;base64,{b64_img}" class="cover-img">'
            else:
                img_html = '<div style="height:280px; background:#333; border-radius:8px;"></div>'

            judul = b.replace(".pdf", "").replace("_", " ")

            st.markdown(f"""<div class="book-card">{img_html}<div class="book-title" title="{judul}">{judul}</div></div>""", unsafe_allow_html=True)
            
            label_tombol = "📖 BACA"
            if b in st.session_state.selesai: label_tombol = "♻️ ULANG"
            
            if st.button(label_tombol, key=f"btn_{b}"):
                st.session_state.buku = b
                st.session_state.halaman = st.session_state.progress.get(b, 0)
                st.session_state.sedang.add(b)
                st.session_state.selesai.discard(b)
                save_data() # SIMPAN DATA!
                st.rerun()

else:
    b = st.session_state.buku
    path = f"buku_pdf/{b}"
    
    try:
        doc = fitz.open(path)
        total_hal = doc.page_count
        
        c1, c2, c3 = st.columns([1, 6, 1])
        with c1:
            if st.button("⬅️ Kembali"):
                st.session_state.buku = None
                save_data()
                st.rerun()
        with c2:
            st.markdown(f"<h3 style='text-align:center; margin:0'>{b.replace('.pdf','')}</h3>", unsafe_allow_html=True)
        with c3:
            if st.button("✅ Selesai"):
                st.session_state.selesai.add(b)
                st.session_state.sedang.discard(b)
                st.session_state.buku = None
                st.toast("Buku selesai! 🎉")
                save_data() # SIMPAN DATA!
                st.rerun()

        st.divider()

        st.markdown(f"<div style='text-align:center; margin-bottom: 10px;'><b>Halaman {st.session_state.halaman + 1} / {total_hal}</b></div>", unsafe_allow_html=True)
        id_catatan_cek = f"{b}_hal_{st.session_state.halaman}"
        if id_catatan_cek in st.session_state.catatan:
            st.info(f"📝 Catatan: {st.session_state.catatan[id_catatan_cek]}")

        st.markdown("<div style='text-align:center; background:rgba(22, 24, 29, 0.9); padding:10px; border-radius:15px; border:1px solid #333'>", unsafe_allow_html=True)
        gambar = render_page(doc, st.session_state.halaman, zoom)
        if gambar: st.image(gambar, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.write("") 

        n1, n2 = st.columns([1, 1])
        with n1:
            if st.session_state.halaman > 0:
                if st.button("⬅️ Sebelumnya", use_container_width=True):
                    st.session_state.halaman -= 1
                    st.session_state.progress[b] = st.session_state.halaman 
                    save_data() # SIMPAN DATA!
                    st.rerun()
            else:
                st.markdown("") 

        with n2:
            if st.session_state.halaman < total_hal - 1:
                if st.button("Berikutnya
