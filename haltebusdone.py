"""
SISTEM HALTE BUS - INTERAKTIF (enqueue & dequeue)
====================================================
Versi Streamlit. Semua data (halte, rute, jadwal, penumpang) diisi sendiri
oleh pengguna lewat form di sidebar/menu, tidak ada data contoh bawaan.
"""

import streamlit as st
from collections import deque

st.set_page_config(page_title="Sistem Halte Bus - Deque", page_icon="🚌", layout="wide")

# ===== PENYIMPANAN DATA (awalnya kosong, diisi lewat menu) =====
# Disimpan di session_state agar tidak hilang setiap interaksi/rerun
if "antrian_halte" not in st.session_state:
    st.session_state.antrian_halte = {}   # nama_halte -> deque(penumpang)
if "rute_bus" not in st.session_state:
    st.session_state.rute_bus = {}        # nama_rute  -> [list nama halte]
if "jadwal_rute" not in st.session_state:
    st.session_state.jadwal_rute = {}     # nama_rute  -> deque(jam keberangkatan)
if "pesan" not in st.session_state:
    st.session_state.pesan = []           # log pesan output, pengganti print()

antrian_halte = st.session_state.antrian_halte
rute_bus = st.session_state.rute_bus
jadwal_rute = st.session_state.jadwal_rute


# ===== FUNGSI DASAR ENQUEUE / DEQUEUE (tidak diubah) =====

def enqueue(antrian, data):
    """Memasukkan data ke belakang antrian."""
    antrian.append(data)


def dequeue(antrian):
    """Mengeluarkan data dari depan antrian. Mengembalikan None jika kosong."""
    if antrian:
        return antrian.popleft()
    return None


def log(pesan, tipe="info"):
    """Pengganti print() versi CLI -> ditampilkan sebagai pesan di Streamlit."""
    st.session_state.pesan.insert(0, (tipe, pesan))
    st.session_state.pesan = st.session_state.pesan[:8]  # simpan 8 pesan terbaru


def tampilkan_log():
    for tipe, pesan in st.session_state.pesan:
        if tipe == "success":
            st.success(pesan)
        elif tipe == "warning":
            st.warning(pesan)
        elif tipe == "error":
            st.error(pesan)
        else:
            st.info(pesan)


# ===== FUNGSI HALTE =====

def tambah_halte(nama):
    nama = nama.strip()
    if not nama:
        log("Nama halte tidak boleh kosong.", "warning")
        return
    if nama in antrian_halte:
        log(f"Halte '{nama}' sudah ada.", "warning")
        return
    antrian_halte[nama] = deque()
    log(f"Halte '{nama}' berhasil ditambahkan.", "success")


def tambah_penumpang(nama_halte, nama_penumpang):
    if not antrian_halte:
        log("Belum ada halte. Tambahkan halte dulu.", "warning")
        return
    if nama_halte not in antrian_halte:
        log(f"Halte '{nama_halte}' tidak ditemukan.", "error")
        return
    nama_penumpang = nama_penumpang.strip()
    if not nama_penumpang:
        log("Nama penumpang tidak boleh kosong.", "warning")
        return
    enqueue(antrian_halte[nama_halte], nama_penumpang)
    log(f"{nama_penumpang} mengantri di {nama_halte}.", "success")


def bus_datang(nama_halte, kapasitas):
    if nama_halte not in antrian_halte:
        log(f"Halte '{nama_halte}' tidak ditemukan.", "error")
        return

    naik = []
    for _ in range(kapasitas):
        penumpang = dequeue(antrian_halte[nama_halte])
        if penumpang is None:
            break
        naik.append(penumpang)

    if naik:
        log(f"Bus di {nama_halte} menaikkan: {', '.join(naik)}", "success")
    else:
        log(f"Tidak ada penumpang di {nama_halte}.", "warning")


# ===== FUNGSI RUTE & JADWAL =====

def tambah_rute(nama_rute, daftar_halte, daftar_jadwal):
    nama_rute = nama_rute.strip()
    if not nama_rute:
        log("Nama rute tidak boleh kosong.", "warning")
        return
    if nama_rute in rute_bus:
        log(f"Rute '{nama_rute}' sudah ada.", "warning")
        return

    if not daftar_halte:
        log("Urutan halte tidak boleh kosong.", "warning")
        return

    for h in daftar_halte:
        if h not in antrian_halte:
            log(f"Halte '{h}' belum terdaftar. Tambahkan halte itu dulu.", "error")
            return

    rute_bus[nama_rute] = daftar_halte
    jadwal_rute[nama_rute] = deque(daftar_jadwal)
    log(f"Rute '{nama_rute}' berhasil ditambahkan.", "success")


def bus_berangkat(nama_rute):
    if nama_rute not in jadwal_rute:
        log(f"Rute '{nama_rute}' tidak ditemukan.", "error")
        return
    jam = dequeue(jadwal_rute[nama_rute])
    if jam:
        log(f"Bus {nama_rute} berangkat pukul {jam}.", "success")
    else:
        log(f"Tidak ada lagi bus untuk {nama_rute} hari ini.", "warning")


# ===== UI STREAMLIT =====

st.title("🚌 Sistem Halte Bus")
st.caption("Implementasi struktur data **deque** untuk operasi `enqueue` (append) dan `dequeue` (popleft)")

menu = st.sidebar.radio(
    "Pilih Menu",
    [
        " Tambah Halte",
        " Tampilkan Daftar Halte",
        " Tambah Penumpang ke Halte",
        " Bus Datang (naikkan penumpang)",
        " Tampilkan Antrian di Halte",
        " Tambah Rute + Jadwal",
        " Tampilkan Satu Rute",
        " Tampilkan Semua Rute",
    ]
)

st.divider()

# ---------- 1. Tambah Halte ----------
if menu.startswith("Tambah halte"):
    st.subheader("➕ Tambah Halte")
    with st.form("form_tambah_halte", clear_on_submit=True):
        nama = st.text_input("Nama halte baru")
        submit = st.form_submit_button("Tambahkan")
    if submit:
        tambah_halte(nama)

# ---------- 2. Tampilkan Daftar Halte ----------
elif menu.startswith("2"):
    st.subheader("📋 Daftar Halte")
    if not antrian_halte:
        st.info("Belum ada halte.")
    else:
        st.write("Daftar halte:", ", ".join(antrian_halte.keys()))
        for nama_halte, antrian in antrian_halte.items():
            st.write(f"- **{nama_halte}** — {len(antrian)} penumpang mengantri")

# ---------- 3. Tambah Penumpang ke Halte ----------
    st.subheader("🧍 Tambah Penumpang ke Halte")
    if not antrian_halte:
        st.warning("Belum ada halte. Tambahkan halte dulu.")
    else:
        with st.form("form_tambah_penumpang", clear_on_submit=True):
            nama_halte = st.selectbox("Nama halte", list(antrian_halte.keys()))
            nama_penumpang = st.text_input("Nama penumpang")
            submit = st.form_submit_button("Masuk Antrian")
        if submit:
            tambah_penumpang(nama_halte, nama_penumpang)

# ---------- 4. Bus Datang ----------
elif menu.startswith("4"):
    st.subheader("🚍 Bus Datang (Naikkan Penumpang)")
    if not antrian_halte:
        st.warning("Belum ada halte.")
    else:
        with st.form("form_bus_datang"):
            nama_halte = st.selectbox("Nama halte", list(antrian_halte.keys()))
            kapasitas = st.number_input("Kapasitas penumpang", min_value=1, step=1, value=1)
            submit = st.form_submit_button("Bus Datang")
        if submit:
            bus_datang(nama_halte, int(kapasitas))

# ---------- 5. Tampilkan Antrian di Halte ----------
elif menu.startswith("5"):
    st.subheader("📍 Antrian di Halte")
    if not antrian_halte:
        st.warning("Belum ada halte.")
    else:
        nama_halte = st.selectbox("Nama halte", list(antrian_halte.keys()))
        antrian = antrian_halte[nama_halte]
        if antrian:
            st.write(f"Antrian **{nama_halte}** (depan ➝ belakang):")
            for i, p in enumerate(antrian, start=1):
                tanda = " ⬅️ depan (naik selanjutnya)" if i == 1 else ""
                st.write(f"{i}. {p}{tanda}")
        else:
            st.info(f"Antrian {nama_halte}: kosong")

# ---------- 6. Tambah Rute + Jadwal ----------
elif menu.startswith("6"):
    st.subheader("🛣️ Tambah Rute + Jadwal")
    if not antrian_halte:
        st.warning("Belum ada halte. Tambahkan halte dulu sebelum membuat rute.")
    else:
        with st.form("form_tambah_rute", clear_on_submit=True):
            nama_rute = st.text_input("Nama rute baru")
            urutan = st.multiselect(
                "Urutan halte yang dilewati (pilih sesuai urutan klik)",
                list(antrian_halte.keys())
            )
            jadwal_input = st.text_input(
                "Jadwal keberangkatan (pisahkan koma, contoh: 06:00,07:00)"
            )
            submit = st.form_submit_button("Tambah Rute")
        if submit:
            daftar_jadwal = [j.strip() for j in jadwal_input.split(",") if j.strip()]
            tambah_rute(nama_rute, urutan, daftar_jadwal)

# ---------- 7. Tampilkan Satu Rute ----------
elif menu.startswith("7"):
    st.subheader("🔎 Tampilkan Satu Rute")
    if not rute_bus:
        st.info("Belum ada rute.")
    else:
        nama_rute = st.selectbox("Nama rute", list(rute_bus.keys()))
        st.write(f"**{nama_rute}**: {' ➝ '.join(rute_bus[nama_rute])}")

# ---------- 8. Tampilkan Semua Rute ----------
elif menu.startswith("8"):
    st.subheader("🗺️ Semua Rute")
    if not rute_bus:
        st.info("Belum ada rute.")
    else:
        for nama_rute, daftar_halte in rute_bus.items():
            st.write(f"**{nama_rute}**: {' ➝ '.join(daftar_halte)}")

# ===== LOG / OUTPUT (pengganti print di CLI) =====
st.subheader("📝 Riwayat Pesan")
if not st.session_state.pesan:
    st.caption("Belum ada aktivitas.")
else:
    tampilkan_log()

# ===== RESET =====
with st.sidebar:
    st.divider()
    st.caption(f"Total halte: {len(antrian_halte)} | Total rute: {len(rute_bus)}")
    if st.button("🔄 Reset Semua Data"):
        st.session_state.antrian_halte = {}
        st.session_state.rute_bus = {}
        st.session_state.jadwal_rute = {}
        st.session_state.pesan = []
        st.rerun()
