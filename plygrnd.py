import streamlit as st
import sqlite3
import pandas as pd
import os

# Konfigurasi Halaman
st.set_page_config(page_title="SQL Playground", page_icon="💻", layout="wide")

st.title("💻 Streamlit SQL Playground")
st.write("Jalankan query SQL langsung pada database yang sudah tersedia.")

# --- KONFIGURASI DATABASE ---
# Pastikan nama file sesuai dengan yang Anda upload di GitHub
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
            st.write("Klik pada nama tabel untuk melihat struktur kolom dan pratinjau data.")
            
            # Looping untuk membuat drop-down (expander) untuk setiap tabel
            for table_name in tables_df['name']:
                with st.expander(f"📁 Tabel: **{table_name}**"):
                    
                    # 1. Menampilkan struktur kolom menggunakan PRAGMA
                    pragma_query = f"PRAGMA table_info('{table_name}');"
                    pragma_df = pd.read_sql_query(pragma_query, conn)
                    
                    st.markdown("**Struktur Kolom:**")
                    # Hanya menampilkan kolom 'name' (nama kolom) dan 'type' (tipe data)
                    st.dataframe(pragma_df[['name', 'type']], use_container_width=True, hide_index=True)
                    
                    # 2. Menampilkan pratinjau 5 baris pertama data
                    st.markdown("**Pratinjau Data (Limit 5):**")
                    sample_query = f"SELECT * FROM {table_name} LIMIT 5;"
                    try:
                        sample_df = pd.read_sql_query(sample_query, conn)
                        st.dataframe(sample_df, use_container_width=True, hide_index=True)
                    except Exception as e:
                        st.warning(f"Tidak dapat memuat pratinjau data: {e}")
                        
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
                    st.dataframe(result_df, use_container_width=True, hide_index=True)
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
