import streamlit as st
import fitz
import os

# =====================
# CONFIG
# =====================
st.set_page_config("Z-Library Mini", "📚", layout="wide")

# =====================
# CSS (BAGIAN PERMAK TAMPILAN ✨)
# =====================
st.markdown("""
<style>
/* Import Font Keren: Poppins */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

/* --- DASAR HALAMAN --- */
.stApp {
    /* Background gelap dengan gradasi halus biar berdimensi */
    background: linear-gradient(to bottom right, #0e1117, #161b24);
    color: #eaeaea;
    font-family: 'Poppins', sans-serif; /* Pakai font baru */
}

/* --- JUDUL GRADIENT --- */
h1, h2, h3 {
    font-weight: 700 !important;
    background: -webkit-linear-gradient(45deg, #00C9FF, #92FE9D);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* --- TOMBOL UMUM (Navigasi dll) --- */
.stButton button {
    background: #262a36 !important;
    color: #ffffff !important;
    border: 1px solid #3a3f4b;
    border-radius: 12px; /* Lebih rounded */
    font-weight: 600;
    transition: all 0.3s ease;
}
.stButton button:hover {
    background: #3a3f4b !important;
    border-color: #00C9FF;
    box-shadow: 0 0 10px rgba(0, 201, 255, 0.3); /* Efek glow pas hover */
}

/* --- TOMBOL KHUSUS "BACA" (Biar menonjol) --- */
/* Kita targetkan tombol di dalam kolom galeri */
[data-testid="column"] .stButton button {
    background: linear-gradient(45deg, #00C9FF, #0078ff) !important;
    border: none !important;
    box-shadow: 0 4px 15px rgba(0, 201, 255, 0.4);
}
[data-testid="column"] .stButton button:hover {
    box-shadow: 0 6px 20px rgba(0, 201, 255, 0.6);
    transform: translateY(-2px);
}

/* --- KARTU BUKU --- */
.book-card {
    background: #1c1f26;
    /* Tambah border tipis dan shadow biar 'pop up' */
    border: 1px solid #2d323e;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    border-radius: 16px;
    padding: 15px;
    transition: all 0.3s ease;
}

/* EFEK HOVER KARTU (GLOWING!) ✨ */
.book-card:hover {
    transform: translateY(-7px) scale(1.02);
    border-color: #00C9FF;
    /* Efek sinar biru di sekeliling kartu */
    box-shadow: 0 10px 30px rgba(0, 201, 255, 0.2);
}

.book-title {
    text-align: center;
    font-size: 15px;
    font-weight: 600;
    margin-top: 12px;
    margin-bottom: 10px;
    color: #fff;
    /* Biar judul panjang gak ngerusak tampilan */
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* Gambar Cover */
.book-card img {
    border-radius: 8px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.5);
}

/* --- READER AREA --- */
.reader-wrap {
    max-width: 900px;
    margin: 20px auto;
    padding: 20px;
    background: #16181d;
    border-radius: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}

/* --- SIDEBAR --- */
section[data-testid="stSidebar"] {
    background-color: #11141d;
    border-right: 1px solid #2d323e;
}
</style>
""", unsafe_allow_html=True)

# =====================
# STATE
# =====================
for k, v in {
    "buku": None,
    "halaman": 0,
    "sedang": set(),
    "selesai": set(),
    "progress": {}
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# =====================
# FUNGSI
# =====================
def list_buku():
    os.makedirs("buku_pdf", exist_ok=True)
    return [b for b in os.listdir("buku_pdf") if b.endswith(".pdf")]

@st.cache_data
def cover(path):
    try:
        d = fitz.open(path)
        p = d.load_page(0)
        pix = p.get_pixmap(matrix=fitz.Matrix(0.4,0.4))
        return pix.tobytes("png")
    except:
        return None

def render(doc, page, zoom):
    p = doc.load_page(page)
    pix = p.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
    return pix.tobytes("png")

# =====================
# SIDEBAR
# =====================
with st.sidebar:
    st.header("👤 Rak Lia")

    st.subheader("📖 Sedang Dibaca")
    if st.session_state.sedang:
        for b in st.session_state.sedang:
            st.caption("• " + b.replace(".pdf",""))
    else:
        st.caption("-")

    st.subheader("✅ Selesai")
    if st.session_state.selesai:
        for b in st.session_state.selesai:
            st.caption("✔ " + b.replace(".pdf",""))
    else:
        st.caption("-")

    st.divider()

    st.header("🎧 Mood")
    # Musik sesuai permintaan terakhir
    st.video("https://youtu.be/g9yQoMe8VDA")

    st.divider()
    zoom = st.slider("🔍 Ukuran Baca", 0.8, 2.5, 1.4, 0.1)

# =====================
# DATA
# =====================
books = list_buku()

# =====================
# GALERI
# =====================
if st.session_state.buku is None:
    # Pakai H1 biar kena efek gradient
    st.markdown("<h1>📚 Galeri Buku</h1>", unsafe_allow_html=True)

    q = st.text_input("🔍 Cari buku", placeholder="Ketik judul buku...").lower()
    books = [b for b in books if q in b.lower()]

    if not books:
        st.info("Belum ada buku yang cocok. Coba cari yang lain atau upload dulu ya! 😊")

    cols = st.columns(4)
    for i, b in enumerate(books):
        with cols[i % 4]:
            path = f"buku_pdf/{b}"
            c = cover(path)
            title = b.replace(".pdf","").replace("_"," ")

            # Kartu Buku dengan HTML Wrapper
            st.markdown("<div class='book-card'>", unsafe_allow_html=True)
            if c: st.image(c, use_container_width=True)
            # Judul dibungkus div biar rapi
            st.markdown(f"<div class='book-title' title='{title}'>{title}</div>", unsafe_allow_html=True)
            
            # Tombol Baca (Style-nya sudah diatur di CSS di atas)
            if st.button("📖 BACA SEKARANG", key=b, use_container_width=True):
                st.session_state.buku = b
                st.session_state.halaman = st.session_state.progress.get(b, 0)
                st.session_state.sedang.add(b)
                st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True) # Tutup div book-card

# =====================
# READER
# =====================
else:
    b = st.session_state.buku
    doc = fitz.open(f"buku_pdf/{b}")
    total = doc.page_count

    top1, top2, top3 = st.columns([1,6,1])
    with top1:
        if st.button("⬅️ Kembali"):
            st.session_state.buku = None
            st.rerun()
    with top2:
        # Judul H2 biar kena gradient
        st.markdown(f"<h2 style='text-align:center; margin:0'>{b.replace('.pdf','')}</h2>", unsafe_allow_html=True)
    with top3:
        if st.button("✅ Selesai"):
            st.session_state.selesai.add(b)
            st.session_state.sedang.discard(b)
            st.session_state.buku = None
            st.toast("Yey! Buku selesai dibaca! 🎉")
            st.rerun()

    st.divider()

    nav1, nav2, nav3 = st.columns([1,2,1])
    with nav1:
        if st.session_state.halaman > 0:
            if st.button("⬅️ Sebelumnya", use_container_width=True):
                st.session_state.halaman -= 1
                st.rerun()
    with nav2:
        st.markdown(f"<div style='text-align:center; font-weight:bold; padding-top:10px'>Halaman {st.session_state.halaman+1} / {total}</div>", unsafe_allow_html=True)
    with nav3:
        if st.session_state.halaman < total-1:
            if st.button("Berikutnya ➡️", use_container_width=True):
                st.session_state.halaman += 1
                st.rerun()

    # Area baca dikasih bingkai di CSS
    st.markdown("<div class='reader-wrap'>", unsafe_allow_html=True)
    img = render(doc, st.session_state.halaman, zoom)
    st.image(img, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.session_state.progress[b] = st.session_state.halaman
    doc.close()
