import streamlit as st
import sqlite3
import pandas as pd
import tempfile
import os

# Konfigurasi Halaman
st.set_page_config(page_title="SQL Playground", page_icon="💻", layout="wide")

st.title("💻 Streamlit SQL Playground")
st.write("Upload file database SQLite Anda (.db atau .sqlite) dan mulai jalankan query SQL langsung dari browser.")

# Uploader untuk file database
uploaded_file = st.file_uploader("Pilih file Database SQLite", type=["db", "sqlite"])

if uploaded_file is not None:
    # Streamlit membaca file ke memori, tapi SQLite butuh path file fisik.
    # Jadi, kita simpan file upload ke temporary file.
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        db_path = tmp_file.name

    try:
        # Koneksi ke database SQLite
        conn = sqlite3.connect(db_path)

        st.success("Database berhasil diunggah dan terkoneksi!")

        # Menampilkan daftar tabel yang ada di dalam database
        st.subheader("Tabel yang Tersedia di Database")
        tables_query = "SELECT name FROM sqlite_master WHERE type='table';"
        tables_df = pd.read_sql_query(tables_query, conn)
        
        if not tables_df.empty:
            st.write("Tabel: **" + ", ".join(tables_df['name'].tolist()) + "**")
        else:
            st.warning("Tidak ada tabel yang ditemukan dalam database ini.")

        st.divider()

        # Area untuk menulis Query SQL
        st.subheader("📝 Tulis Query SQL Anda")
        query = st.text_area(
            "Masukkan query di bawah ini:", 
            value="SELECT * FROM sqlite_master LIMIT 5;", 
            height=150
        )

        # Tombol eksekusi
        if st.button("Jalankan Query", type="primary"):
            if query.strip():
                try:
                    # Menjalankan query dan mengubahnya menjadi DataFrame
                    result_df = pd.read_sql_query(query, conn)
                    
                    st.write(f"**Hasil Query:** ({result_df.shape[0]} baris, {result_df.shape[1]} kolom)")
                    st.dataframe(result_df, use_container_width=True)
                except Exception as e:
                    # Menangkap error SQL (misal typo nama kolom/tabel)
                    st.error(f"Terjadi kesalahan pada query: {e}")
            else:
                st.warning("Silakan tulis query SQL terlebih dahulu.")

        # Menutup koneksi
        conn.close()

    except Exception as e:
        st.error(f"Gagal membaca database: {e}")
    
    finally:
        # Membersihkan / menghapus file temporary setelah selesai digunakan
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
            except:
                pass
else:
    st.info("Silakan unggah database Anda untuk memulai.")
