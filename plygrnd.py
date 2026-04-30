import streamlit as st
import sqlite3
import pandas as pd
import os

# Konfigurasi Halaman
st.set_page_config(page_title="SQL Playground", page_icon="💻", layout="wide")

st.title("💻 Streamlit SQL Playground")
st.write("Jalankan query SQL langsung pada database yang sudah tersedia.")

# --- KONFIGURASI DATABASE ---
# Ganti "SQLite.db" dengan nama file database Anda yang ada di GitHub.
# Jika nama filenya hanya "SQLite" tanpa ekstensi, tulis "SQLite".
db_path = "SQLite.db" 

# Mengecek apakah file database ada di dalam repository/folder
if os.path.exists(db_path):
    try:
        # Koneksi langsung ke database SQLite lokal
        conn = sqlite3.connect(db_path)

        st.success("✅ Database berhasil terhubung!")

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
                    # Menangkap error SQL
                    st.error(f"Terjadi kesalahan pada query: {e}")
            else:
                st.warning("Silakan tulis query SQL terlebih dahulu.")

        # Menutup koneksi
        conn.close()

    except Exception as e:
        st.error(f"Gagal membaca database: {e}")
else:
    st.error(f"⚠️ File database '{db_path}' tidak ditemukan.")
    st.info("Pastikan nama file di variabel `db_path` sudah sama persis (termasuk huruf besar/kecil dan ekstensinya) dengan yang ada di GitHub Anda.")
