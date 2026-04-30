import streamlit as st
import sqlite3
import pandas as pd
import os

# Konfigurasi Halaman
st.set_page_config(page_title="Data Analyst SQL Assessment", page_icon="📝", layout="wide")

# Inisialisasi Session State untuk melacak nomor soal
if 'current_q' not in st.session_state:
    st.session_state.current_q = 0

# --- DAFTAR SOAL & KUNCI JAWABAN ---
# SILAKAN SESUAIKAN DENGAN TABEL DAN SOAL ANDA DI SINI
questions = [
    {
        "task": "Tampilkan 5 baris pertama dari seluruh kolom yang ada di tabel `nama_tabel_anda`.",
        "solution_query": "SELECT * FROM nama_tabel_anda LIMIT 5;"
    },
    {
        "task": "Hitung total pendapatan (misal kolom `revenue`) dikelompokkan berdasarkan `kategori`.",
        "solution_query": "SELECT kategori, SUM(revenue) as total_pendapatan FROM nama_tabel_anda GROUP BY kategori;"
    },
    {
        "task": "Tampilkan nama pelanggan yang melakukan transaksi di atas nilai 1.000.000, urutkan dari yang terbesar.",
        "solution_query": "SELECT nama_pelanggan, total_transaksi FROM nama_tabel_anda WHERE total_transaksi > 1000000 ORDER BY total_transaksi DESC;"
    }
]

st.title("📝 SQL Assessment - Data Analyst")
st.write("Selesaikan instruksi query di bawah ini. Jika hasil query Anda benar, Anda dapat melanjutkan ke soal berikutnya.")

# --- KONFIGURASI DATABASE ---
db_path = "SQLite.db" 

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)

    # Menampilkan Skema Database di dalam Expander agar tidak memakan tempat
    with st.expander("🔍 Klik untuk melihat Skema Database & Tabel", expanded=False):
        tables_query = "SELECT name FROM sqlite_master WHERE type='table';"
        try:
            tables_df = pd.read_sql_query(tables_query, conn)
            if not tables_df.empty:
                for table_name in tables_df['name']:
                    st.markdown(f"**Tabel: `{table_name}`**")
                    pragma_query = f"PRAGMA table_info('{table_name}');"
                    pragma_df = pd.read_sql_query(pragma_query, conn)
                    st.dataframe(pragma_df[['name', 'type']], hide_index=True)
            else:
                st.warning("Database kosong.")
        except Exception as e:
            st.error(f"Gagal memuat skema: {e}")

    st.divider()

    # --- LOGIKA TES / SOAL ---
    # Cek apakah kandidat sudah menyelesaikan semua soal
    if st.session_state.current_q < len(questions):
        q_index = st.session_state.current_q
        current_question = questions[q_index]

        st.subheader(f"Soal {q_index + 1} dari {len(questions)}")
        st.info(f"**Instruksi:** {current_question['task']}")

        # Area untuk kandidat menulis Query SQL
        user_query = st.text_area(
            "Tulis Query SQL Anda di sini:", 
            height=150,
            key=f"query_input_{q_index}" # Key unik agar text area reset setiap ganti soal
        )

        # Tombol eksekusi
        if st.button("Jalankan & Periksa Jawaban", type="primary"):
            if user_query.strip():
                try:
                    # 1. Eksekusi query kandidat
                    user_df = pd.read_sql_query(user_query, conn)
                    
                    # 2. Eksekusi query kunci jawaban secara rahasia
                    solution_df = pd.read_sql_query(current_question['solution_query'], conn)
                    
                    st.write("**Hasil Query Anda:**")
                    st.dataframe(user_df, use_container_width=True, hide_index=True)

                    # 3. Validasi (Membandingkan hasil DataFrame)
                    # Kita reset index agar perbedaan urutan index pandas tidak membuat hasil dianggap salah
                    if user_df.reset_index(drop=True).equals(solution_df.reset_index(drop=True)):
                        st.success("✨ Jawaban Anda Benar!")
                        
                        # Tombol untuk lanjut ke soal berikutnya
                        if st.button("Lanjut ke Soal Berikutnya"):
                            st.session_state.current_q += 1
                            st.rerun() # Refresh halaman untuk memuat soal baru
                    else:
                        st.error("❌ Jawaban masih kurang tepat atau hasil tabel tidak sesuai ekspektasi. Perhatikan nama kolom dan urutannya. Coba lagi!")
                        
                except Exception as e:
                    st.error(f"Terjadi kesalahan pada query Anda: {e}")
            else:
                st.warning("Silakan tulis query SQL terlebih dahulu.")

    else:
        # Jika semua soal selesai
        st.balloons()
        st.success("🎉 Selamat! Anda telah menyelesaikan semua soal Assessment SQL.")
        if st.button("Ulangi Tes"):
            st.session_state.current_q = 0
            st.rerun()

    conn.close()

else:
    st.error(f"⚠️ File database '{db_path}' tidak ditemukan di sistem.")
