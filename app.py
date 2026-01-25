import streamlit as st
import fitz
import os

# =====================
# CONFIG
# =====================
st.set_page_config("Z-Library Mini", "📚", layout="wide")

# =====================
# CSS
# =====================
st.markdown("""
<style>
.stApp {
    background-color: #0e1117;
    color: #eaeaea;
}

/* BUTTON FIX */
.stButton button {
    background: #1c1f26 !important;
    color: #ffffff !important;
    border-radius: 25px;
    font-weight: 600;
}

/* BOOK CARD */
.book-card {
    background: #1c1f26;
    border-radius: 16px;
    padding: 12px;
    transition: 0.2s;
}
.book-card:hover {
    transform: translateY(-4px);
}
.book-title {
    text-align: center;
    font-size: 14px;
    font-weight: 600;
    margin-top: 6px;
}

/* READER */
.reader-wrap {
    max-width: 900px;
    margin: auto;
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
    st.video("https://www.youtube.com/watch?v=jfKfPfyJRdk")

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
    st.title("📚 Galeri Buku")

    q = st.text_input("🔍 Cari buku").lower()
    books = [b for b in books if q in b.lower()]

    cols = st.columns(4)
    for i, b in enumerate(books):
        with cols[i % 4]:
            path = f"buku_pdf/{b}"
            c = cover(path)
            title = b.replace(".pdf","").replace("_"," ")

            st.markdown("<div class='book-card'>", unsafe_allow_html=True)
            if c: st.image(c, use_container_width=True)
            st.markdown(f"<div class='book-title'>{title}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            if st.button("📖 Baca", key=b, use_container_width=True):
                st.session_state.buku = b
                st.session_state.halaman = st.session_state.progress.get(b, 0)
                st.session_state.sedang.add(b)
                st.rerun()

# =====================
# READER
# =====================
else:
    b = st.session_state.buku
    doc = fitz.open(f"buku_pdf/{b}")
    total = doc.page_count

    top1, top2, top3 = st.columns([1,6,1])
    with top1:
        if st.button("⬅️"):
            st.session_state.buku = None
            st.rerun()
    with top2:
        st.markdown(f"<h3 style='text-align:center'>{b.replace('.pdf','')}</h3>", unsafe_allow_html=True)
    with top3:
        if st.button("✅"):
            st.session_state.selesai.add(b)
            st.session_state.sedang.discard(b)
            st.session_state.buku = None
            st.toast("Buku selesai 🎉")
            st.rerun()

    nav1, nav2, nav3 = st.columns([1,2,1])
    with nav1:
        if st.session_state.halaman > 0:
            if st.button("⬅️ Sebelumnya"):
                st.session_state.halaman -= 1
                st.rerun()
    with nav2:
        st.markdown(f"<center>{st.session_state.halaman+1} / {total}</center>", unsafe_allow_html=True)
    with nav3:
        if st.session_state.halaman < total-1:
            if st.button("Berikutnya ➡️"):
                st.session_state.halaman += 1
                st.rerun()

    st.markdown("<div class='reader-wrap'>", unsafe_allow_html=True)
    img = render(doc, st.session_state.halaman, zoom)
    st.image(img, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.session_state.progress[b] = st.session_state.halaman
    doc.close()
