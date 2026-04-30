import streamlit as st
import sqlite3
import pandas as pd
import os
import time

# ─────────────────────────────────────────────
# KONFIGURASI HALAMAN
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="SQL Assessment – Data Analyst",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CSS CUSTOM
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Sora:wght@400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Sora', sans-serif; }

.stTextArea textarea {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 14px !important;
    background: #0f1117 !important;
    color: #e2e8f0 !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
}

.question-card {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    border: 1px solid #334155;
    border-left: 4px solid #3b82f6;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 16px;
}

.question-card h4 { color: #94a3b8; font-size: 13px; margin: 0 0 6px 0; letter-spacing: 1px; text-transform: uppercase; }
.question-card p  { color: #e2e8f0; font-size: 16px; margin: 0; line-height: 1.6; }

.score-badge {
    display: inline-block;
    background: linear-gradient(135deg, #1d4ed8, #7c3aed);
    color: white;
    padding: 6px 16px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 18px;
}

.hint-box {
    background: #172033;
    border: 1px dashed #3b82f6;
    border-radius: 8px;
    padding: 14px 18px;
    color: #93c5fd;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    margin-top: 8px;
}

.tag {
    display: inline-block;
    background: #1e3a5f;
    color: #60a5fa;
    font-size: 11px;
    padding: 2px 10px;
    border-radius: 12px;
    font-weight: 600;
    margin-right: 4px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

.stat-box {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 16px;
    text-align: center;
}
.stat-box .num  { font-size: 28px; font-weight: 700; color: #3b82f6; }
.stat-box .label { font-size: 12px; color: #64748b; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.5px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SETUP DATABASE OTOMATIS
# ─────────────────────────────────────────────
DB_PATH = "assessment.db"

def create_database():
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

    cur.executescript("""
    DROP TABLE IF EXISTS order_items;
    DROP TABLE IF EXISTS orders;
    DROP TABLE IF EXISTS products;
    DROP TABLE IF EXISTS customers;
    DROP TABLE IF EXISTS employees;

    CREATE TABLE customers (
        customer_id   INTEGER PRIMARY KEY,
        name          TEXT,
        city          TEXT,
        tier          TEXT,   -- 'Bronze','Silver','Gold','Platinum'
        join_date     TEXT
    );

    CREATE TABLE products (
        product_id  INTEGER PRIMARY KEY,
        name        TEXT,
        category    TEXT,
        price       REAL,
        stock       INTEGER
    );

    CREATE TABLE orders (
        order_id    INTEGER PRIMARY KEY,
        customer_id INTEGER,
        order_date  TEXT,
        status      TEXT,   -- 'Completed','Pending','Cancelled'
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    );

    CREATE TABLE order_items (
        item_id     INTEGER PRIMARY KEY,
        order_id    INTEGER,
        product_id  INTEGER,
        quantity    INTEGER,
        unit_price  REAL,
        FOREIGN KEY (order_id)   REFERENCES orders(order_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    );

    CREATE TABLE employees (
        employee_id INTEGER PRIMARY KEY,
        name        TEXT,
        department  TEXT,
        salary      REAL,
        hire_date   TEXT,
        manager_id  INTEGER
    );
    """)

    # Customers
    customers = [
        (1,  'Andi Pratama',    'Jakarta',   'Gold',     '2021-03-15'),
        (2,  'Siti Rahayu',     'Surabaya',  'Silver',   '2022-01-10'),
        (3,  'Budi Santoso',    'Bandung',   'Platinum', '2020-07-22'),
        (4,  'Dewi Lestari',    'Jakarta',   'Bronze',   '2023-05-01'),
        (5,  'Eko Wahyudi',     'Medan',     'Silver',   '2021-11-30'),
        (6,  'Fitri Handayani', 'Jakarta',   'Gold',     '2022-08-14'),
        (7,  'Gilang Ramadan',  'Yogyakarta','Bronze',   '2023-02-28'),
        (8,  'Hana Kusuma',     'Surabaya',  'Platinum', '2020-04-05'),
        (9,  'Irwan Fauzi',     'Bandung',   'Silver',   '2022-12-19'),
        (10, 'Julia Anggraeni', 'Jakarta',   'Gold',     '2021-06-08'),
        (11, 'Kevin Hermawan',  'Semarang',  'Bronze',   '2023-09-12'),
        (12, 'Laras Wulandari', 'Surabaya',  'Silver',   '2022-03-25'),
    ]
    cur.executemany("INSERT INTO customers VALUES (?,?,?,?,?)", customers)

    # Products
    products = [
        (1,  'Laptop ProMax',    'Electronics',  15000000, 50),
        (2,  'Mouse Wireless',   'Electronics',    350000, 200),
        (3,  'Keyboard Mekanikal','Electronics',   850000, 150),
        (4,  'Monitor 27"',      'Electronics',  4500000,  40),
        (5,  'Meja Kerja',       'Furniture',    2200000,  30),
        (6,  'Kursi Ergonomis',  'Furniture',    3500000,  25),
        (7,  'Buku Python',      'Books',          185000, 300),
        (8,  'Buku SQL Dasar',   'Books',          145000, 250),
        (9,  'Headphone Studio', 'Electronics',  1200000,  80),
        (10, 'Webcam HD',        'Electronics',    680000, 120),
        (11, 'Lampu Meja LED',   'Furniture',     275000,  90),
        (12, 'Tas Laptop',       'Accessories',   450000, 180),
    ]
    cur.executemany("INSERT INTO products VALUES (?,?,?,?,?)", products)

    # Orders
    orders = [
        (1,  1,  '2024-01-05', 'Completed'),
        (2,  3,  '2024-01-12', 'Completed'),
        (3,  2,  '2024-01-18', 'Completed'),
        (4,  5,  '2024-02-03', 'Pending'),
        (5,  8,  '2024-02-14', 'Completed'),
        (6,  1,  '2024-02-20', 'Completed'),
        (7,  6,  '2024-03-01', 'Cancelled'),
        (8,  3,  '2024-03-10', 'Completed'),
        (9,  10, '2024-03-22', 'Completed'),
        (10, 4,  '2024-04-05', 'Completed'),
        (11, 8,  '2024-04-11', 'Completed'),
        (12, 2,  '2024-04-19', 'Pending'),
        (13, 1,  '2024-05-02', 'Completed'),
        (14, 9,  '2024-05-15', 'Completed'),
        (15, 3,  '2024-05-28', 'Completed'),
        (16, 6,  '2024-06-03', 'Completed'),
        (17, 12, '2024-06-17', 'Completed'),
        (18, 7,  '2024-07-01', 'Cancelled'),
        (19, 5,  '2024-07-09', 'Completed'),
        (20, 10, '2024-07-25', 'Completed'),
    ]
    cur.executemany("INSERT INTO orders VALUES (?,?,?,?)", orders)

    # Order Items
    items = [
        (1,  1,  1,  1, 15000000),
        (2,  1,  2,  2,   350000),
        (3,  2,  4,  1,  4500000),
        (4,  2,  6,  1,  3500000),
        (5,  3,  7,  3,   185000),
        (6,  3,  8,  2,   145000),
        (7,  4,  9,  1,  1200000),
        (8,  5,  1,  1, 15000000),
        (9,  5,  3,  1,   850000),
        (10, 6,  5,  1,  2200000),
        (11, 7,  11, 2,   275000),
        (12, 8,  2,  3,   350000),
        (13, 8,  10, 1,   680000),
        (14, 9,  4,  1,  4500000),
        (15, 10, 12, 2,   450000),
        (16, 11, 6,  1,  3500000),
        (17, 11, 9,  1,  1200000),
        (18, 12, 7,  5,   185000),
        (19, 13, 1,  1, 15000000),
        (20, 13, 3,  1,   850000),
        (21, 14, 5,  2,  2200000),
        (22, 15, 4,  1,  4500000),
        (23, 16, 6,  1,  3500000),
        (24, 16, 2,  2,   350000),
        (25, 17, 12, 1,   450000),
        (26, 18, 11, 3,   275000),
        (27, 19, 9,  2,  1200000),
        (28, 20, 1,  1, 15000000),
    ]
    cur.executemany("INSERT INTO order_items VALUES (?,?,?,?,?)", items)

    # Employees
    employees = [
        (1,  'Raka Saputra',    'Engineering',  18000000, '2019-03-01', None),
        (2,  'Maya Putri',      'Engineering',  14000000, '2020-06-15', 1),
        (3,  'Doni Kurniawan',  'Engineering',  13500000, '2021-01-10', 1),
        (4,  'Sari Novita',     'Marketing',    12000000, '2019-08-20', None),
        (5,  'Bagas Wicaksono', 'Marketing',     9500000, '2022-03-05', 4),
        (6,  'Nadia Rahman',    'Marketing',     9000000, '2022-07-18', 4),
        (7,  'Teguh Prasetyo',  'Finance',      16000000, '2018-11-12', None),
        (8,  'Indah Permata',   'Finance',      11000000, '2021-09-01', 7),
        (9,  'Fajar Hidayat',   'Engineering',  15000000, '2020-02-14', 1),
        (10, 'Rini Susilowati', 'HR',           10500000, '2020-05-25', None),
    ]
    cur.executemany("INSERT INTO employees VALUES (?,?,?,?,?,?)", employees)

    conn.commit()
    conn.close()

if not os.path.exists(DB_PATH):
    create_database()

# ─────────────────────────────────────────────
# DAFTAR SOAL
# ─────────────────────────────────────────────
QUESTIONS = [
    {
        "title": "Eksplorasi Data Awal",
        "tags": ["SELECT", "LIMIT"],
        "task": "Tampilkan **10 baris pertama** dari tabel `customers` beserta **seluruh kolomnya**, diurutkan berdasarkan `customer_id` secara ascending.",
        "hint": "Gunakan SELECT *, ORDER BY, dan LIMIT",
        "solution": "SELECT * FROM customers ORDER BY customer_id LIMIT 10;",
        "points": 10,
    },
    {
        "title": "Filter & Kondisi",
        "tags": ["WHERE", "AND"],
        "task": "Tampilkan `name`, `city`, dan `tier` dari tabel `customers` yang berasal dari kota **'Jakarta'** dan memiliki tier **'Gold'** atau **'Platinum'**.",
        "hint": "Gunakan WHERE dengan kombinasi AND / OR, atau operator IN",
        "solution": "SELECT name, city, tier FROM customers WHERE city = 'Jakarta' AND tier IN ('Gold', 'Platinum');",
        "points": 10,
    },
    {
        "title": "Agregasi & Pengelompokan",
        "tags": ["GROUP BY", "COUNT", "ORDER BY"],
        "task": "Hitung **jumlah pelanggan** per `city`, tampilkan kolom `city` dan `jumlah_pelanggan`. Urutkan dari kota dengan pelanggan terbanyak ke tersedikit.",
        "hint": "Gunakan COUNT(*), GROUP BY, dan ORDER BY … DESC",
        "solution": "SELECT city, COUNT(*) AS jumlah_pelanggan FROM customers GROUP BY city ORDER BY jumlah_pelanggan DESC;",
        "points": 15,
    },
    {
        "title": "Produk & Rentang Harga",
        "tags": ["WHERE", "BETWEEN", "ORDER BY"],
        "task": "Tampilkan `name`, `category`, dan `price` dari tabel `products` yang harganya antara **500.000 – 5.000.000** (inklusif). Urutkan berdasarkan harga dari termahal ke termurah.",
        "hint": "Gunakan BETWEEN … AND … lalu ORDER BY price DESC",
        "solution": "SELECT name, category, price FROM products WHERE price BETWEEN 500000 AND 5000000 ORDER BY price DESC;",
        "points": 10,
    },
    {
        "title": "JOIN Antar Tabel",
        "tags": ["JOIN", "ON"],
        "task": "Tampilkan `order_id`, `name` (nama pelanggan), `order_date`, dan `status` dari tabel `orders`, dengan menggabungkan data dari tabel `customers`. Tampilkan hanya order yang berstatus **'Completed'**.",
        "hint": "Gunakan INNER JOIN … ON orders.customer_id = customers.customer_id, lalu filter WHERE status",
        "solution": "SELECT o.order_id, c.name, o.order_date, o.status FROM orders o JOIN customers c ON o.customer_id = c.customer_id WHERE o.status = 'Completed';",
        "points": 15,
    },
    {
        "title": "Total Pendapatan per Kategori",
        "tags": ["JOIN", "SUM", "GROUP BY"],
        "task": "Hitung **total pendapatan** (`quantity × unit_price`) per `category` produk. Tampilkan kolom `category` dan `total_pendapatan`. Urutkan dari pendapatan terbesar.",
        "hint": "JOIN order_items → products, lalu SUM(quantity * unit_price) GROUP BY category",
        "solution": "SELECT p.category, SUM(oi.quantity * oi.unit_price) AS total_pendapatan FROM order_items oi JOIN products p ON oi.product_id = p.product_id GROUP BY p.category ORDER BY total_pendapatan DESC;",
        "points": 20,
    },
    {
        "title": "Pelanggan Paling Aktif (HAVING)",
        "tags": ["GROUP BY", "HAVING", "COUNT"],
        "task": "Temukan pelanggan yang memiliki **lebih dari 2 order** (status apapun). Tampilkan `name` pelanggan dan `total_order`. Urutkan dari yang terbanyak.",
        "hint": "JOIN orders → customers, GROUP BY customer, gunakan HAVING COUNT(*) > 2",
        "solution": "SELECT c.name, COUNT(o.order_id) AS total_order FROM orders o JOIN customers c ON o.customer_id = c.customer_id GROUP BY c.customer_id, c.name HAVING COUNT(o.order_id) > 2 ORDER BY total_order DESC;",
        "points": 20,
    },
    {
        "title": "Produk Tidak Pernah Terjual",
        "tags": ["LEFT JOIN", "IS NULL"],
        "task": "Temukan produk yang **belum pernah dipesan sama sekali**. Tampilkan `product_id`, `name`, dan `category` produk tersebut.",
        "hint": "Gunakan LEFT JOIN antara products dan order_items, lalu filter WHERE order_items.product_id IS NULL",
        "solution": "SELECT p.product_id, p.name, p.category FROM products p LEFT JOIN order_items oi ON p.product_id = oi.product_id WHERE oi.product_id IS NULL;",
        "points": 20,
    },
    {
        "title": "Klasifikasi dengan CASE WHEN",
        "tags": ["CASE WHEN", "SELECT"],
        "task": "Tampilkan `name`, `salary`, dan kolom baru bernama `grade` dari tabel `employees`. Isi `grade` berdasarkan gaji: **'A'** jika salary ≥ 15.000.000, **'B'** jika 10.000.000 ≤ salary < 15.000.000, **'C'** jika di bawah 10.000.000. Urutkan berdasarkan salary DESC.",
        "hint": "Gunakan CASE WHEN salary >= 15000000 THEN 'A' WHEN salary >= 10000000 THEN 'B' ELSE 'C' END AS grade",
        "solution": "SELECT name, salary, CASE WHEN salary >= 15000000 THEN 'A' WHEN salary >= 10000000 THEN 'B' ELSE 'C' END AS grade FROM employees ORDER BY salary DESC;",
        "points": 20,
    },
    {
        "title": "Subquery – Top Spender",
        "tags": ["Subquery", "JOIN", "SUM"],
        "task": "Tampilkan `name` pelanggan dan `total_belanja` mereka (dari order yang **Completed** saja). Hanya tampilkan pelanggan yang total belanjaannya **di atas rata-rata** total belanja semua pelanggan. Urutkan dari terbesar.",
        "hint": "Hitung SUM per customer dari orders+order_items (WHERE status='Completed'), lalu filter HAVING SUM(...) > (SELECT AVG(total) FROM (subquery))",
        "solution": """SELECT c.name, SUM(oi.quantity * oi.unit_price) AS total_belanja
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'Completed'
GROUP BY c.customer_id, c.name
HAVING total_belanja > (
    SELECT AVG(total) FROM (
        SELECT SUM(oi2.quantity * oi2.unit_price) AS total
        FROM orders o2
        JOIN order_items oi2 ON o2.order_id = oi2.order_id
        WHERE o2.status = 'Completed'
        GROUP BY o2.customer_id
    )
)
ORDER BY total_belanja DESC;""",
        "points": 30,
    },
]

TOTAL_POINTS = sum(q["points"] for q in QUESTIONS)

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
defaults = {
    "current_q":   0,
    "scores":      [None] * len(QUESTIONS),   # None=belum, True=benar, False=salah
    "attempts":    [0]    * len(QUESTIONS),
    "started":     False,
    "finished":    False,
    "show_hint":   False,
    "show_sol":    False,
    "last_result": None,   # 'correct' | 'wrong' | 'error'
    "last_df":     None,
    "last_err":    "",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧠 SQL Assessment")
    st.caption("Data Analyst – Technical Test")
    st.divider()

    # Progress keseluruhan
    answered  = sum(1 for s in st.session_state.scores if s is not None)
    correct   = sum(1 for s in st.session_state.scores if s is True)
    earned    = sum(QUESTIONS[i]["points"] for i, s in enumerate(st.session_state.scores) if s is True)

    st.markdown(f"**Progress:** {answered} / {len(QUESTIONS)} soal")
    st.progress(answered / len(QUESTIONS))

    st.markdown(f"**Skor:** {earned} / {TOTAL_POINTS} poin")
    st.progress(earned / TOTAL_POINTS)

    st.divider()

    # Navigasi cepat
    st.markdown("**Navigasi Soal:**")
    for i, q in enumerate(QUESTIONS):
        s = st.session_state.scores[i]
        icon = "✅" if s is True else ("❌" if s is False else "⬜")
        label = f"{icon} Soal {i+1} ({q['points']}pt)"
        if st.button(label, key=f"nav_{i}", use_container_width=True):
            st.session_state.current_q    = i
            st.session_state.show_hint    = False
            st.session_state.show_sol     = False
            st.session_state.last_result  = None
            st.session_state.last_df      = None
            st.rerun()

    st.divider()

    # Skema database
    with st.expander("📋 Skema Database"):
        conn_s = sqlite3.connect(DB_PATH)
        tbl_df = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn_s)
        for tbl in tbl_df['name']:
            st.markdown(f"**`{tbl}`**")
            pragma = pd.read_sql_query(f"PRAGMA table_info('{tbl}');", conn_s)
            for _, row in pragma.iterrows():
                pk = " 🔑" if row['pk'] else ""
                st.caption(f"  `{row['name']}` — {row['type']}{pk}")
        conn_s.close()

    if st.button("🔄 Reset Semua", use_container_width=True):
        for k, v in defaults.items():
            st.session_state[k] = v
        st.rerun()

# ─────────────────────────────────────────────
# AREA UTAMA
# ─────────────────────────────────────────────
q_idx = st.session_state.current_q
q     = QUESTIONS[q_idx]

# Header
col_title, col_score = st.columns([3, 1])
with col_title:
    st.markdown(f"## Soal {q_idx + 1} dari {len(QUESTIONS)}: {q['title']}")
    tags_html = "".join(f'<span class="tag">{t}</span>' for t in q["tags"])
    st.markdown(tags_html, unsafe_allow_html=True)
with col_score:
    status = st.session_state.scores[q_idx]
    if status is True:
        st.success(f"✅ +{q['points']} poin")
    elif status is False:
        st.error("❌ Belum tepat")
    else:
        st.markdown(
            f'<div class="stat-box"><div class="num">{q["points"]}</div><div class="label">Poin Soal</div></div>',
            unsafe_allow_html=True
        )

st.divider()

# Kartu soal
st.markdown(
    f'<div class="question-card"><h4>📌 Instruksi</h4><p>{q["task"]}</p></div>',
    unsafe_allow_html=True,
)

# Hint toggle
h_col, s_col = st.columns([1, 1])
with h_col:
    if st.button("💡 Tampilkan Hint", use_container_width=True):
        st.session_state.show_hint = not st.session_state.show_hint
with s_col:
    if st.session_state.scores[q_idx] is True:
        if st.button("👁️ Lihat Solusi", use_container_width=True):
            st.session_state.show_sol = not st.session_state.show_sol

if st.session_state.show_hint:
    st.markdown(f'<div class="hint-box">💡 {q["hint"]}</div>', unsafe_allow_html=True)

if st.session_state.show_sol and st.session_state.scores[q_idx] is True:
    st.code(q["solution"], language="sql")

st.markdown("---")

# Input area
user_query = st.text_area(
    "✏️ Tulis Query SQL Anda di sini:",
    height=160,
    placeholder="SELECT ...",
    key=f"query_{q_idx}",
)

run_col, prev_col, next_col = st.columns([2, 1, 1])

with run_col:
    run_btn = st.button("▶ Jalankan & Periksa", type="primary", use_container_width=True)
with prev_col:
    prev_btn = st.button("⬅ Sebelumnya", use_container_width=True, disabled=(q_idx == 0))
with next_col:
    next_btn = st.button("Berikutnya ➡", use_container_width=True, disabled=(q_idx == len(QUESTIONS) - 1))

# Navigasi prev/next
if prev_btn:
    st.session_state.current_q   = q_idx - 1
    st.session_state.show_hint   = False
    st.session_state.show_sol    = False
    st.session_state.last_result = None
    st.session_state.last_df     = None
    st.rerun()

if next_btn:
    st.session_state.current_q   = q_idx + 1
    st.session_state.show_hint   = False
    st.session_state.show_sol    = False
    st.session_state.last_result = None
    st.session_state.last_df     = None
    st.rerun()

# Eksekusi & Validasi
if run_btn:
    if not user_query.strip():
        st.warning("⚠️ Silakan tulis query SQL terlebih dahulu.")
    else:
        st.session_state.attempts[q_idx] += 1
        conn_r = sqlite3.connect(DB_PATH)
        try:
            user_df = pd.read_sql_query(user_query, conn_r)
            sol_df  = pd.read_sql_query(q["solution"], conn_r)

            # Normalisasi: strip whitespace nama kolom & nilai string
            def normalize(df):
                df = df.copy()
                df.columns = [str(c).strip().lower() for c in df.columns]
                for col in df.select_dtypes(include='object').columns:
                    df[col] = df[col].astype(str).str.strip()
                return df.reset_index(drop=True)

            u_norm = normalize(user_df)
            s_norm = normalize(sol_df)

            is_correct = u_norm.equals(s_norm)

            st.session_state.last_result = "correct" if is_correct else "wrong"
            st.session_state.last_df     = user_df

            if is_correct and st.session_state.scores[q_idx] is not True:
                st.session_state.scores[q_idx] = True

        except Exception as e:
            st.session_state.last_result = "error"
            st.session_state.last_err    = str(e)
            st.session_state.last_df     = None
        finally:
            conn_r.close()

# Tampilkan hasil
if st.session_state.last_result == "correct":
    st.success(f"✅ **Jawaban Benar!** +{q['points']} poin diperoleh.")
    if st.session_state.last_df is not None:
        st.markdown("**Hasil Query Anda:**")
        st.dataframe(st.session_state.last_df, use_container_width=True, hide_index=True)
    if q_idx < len(QUESTIONS) - 1:
        if st.button("➡ Lanjut ke Soal Berikutnya", type="primary"):
            st.session_state.current_q   = q_idx + 1
            st.session_state.show_hint   = False
            st.session_state.show_sol    = False
            st.session_state.last_result = None
            st.session_state.last_df     = None
            st.rerun()
    else:
        if st.button("🏁 Lihat Hasil Akhir", type="primary"):
            st.session_state.finished = True
            st.rerun()

elif st.session_state.last_result == "wrong":
    att = st.session_state.attempts[q_idx]
    st.error(f"❌ Jawaban belum tepat. (Percobaan ke-{att}) Periksa nama kolom, urutan baris, dan nilai data.")
    if st.session_state.last_df is not None:
        st.markdown("**Hasil Query Anda:**")
        st.dataframe(st.session_state.last_df, use_container_width=True, hide_index=True)

elif st.session_state.last_result == "error":
    st.error(f"🔴 Error pada query Anda: `{st.session_state.last_err}`")

# ─────────────────────────────────────────────
# LAYAR SELESAI
# ─────────────────────────────────────────────
if st.session_state.finished or all(s is not None for s in st.session_state.scores):
    st.divider()
    st.balloons()

    earned     = sum(QUESTIONS[i]["points"] for i, s in enumerate(st.session_state.scores) if s is True)
    pct        = round(earned / TOTAL_POINTS * 100)
    correct_n  = sum(1 for s in st.session_state.scores if s is True)

    grade = "A" if pct >= 85 else ("B" if pct >= 70 else ("C" if pct >= 55 else "D"))

    st.markdown("## 🏁 Hasil Assessment")
    c1, c2, c3, c4 = st.columns(4)
    for col, label, val in [
        (c1, "Total Skor",    f"{earned}/{TOTAL_POINTS}"),
        (c2, "Persentase",    f"{pct}%"),
        (c3, "Soal Benar",    f"{correct_n}/{len(QUESTIONS)}"),
        (c4, "Grade",         grade),
    ]:
        with col:
            st.markdown(
                f'<div class="stat-box"><div class="num">{val}</div><div class="label">{label}</div></div>',
                unsafe_allow_html=True
            )

    st.markdown("---")
    st.markdown("### Detail Per Soal")
    rows = []
    for i, q2 in enumerate(QUESTIONS):
        s = st.session_state.scores[i]
        rows.append({
            "No":       i + 1,
            "Soal":     q2["title"],
            "Topik":    ", ".join(q2["tags"]),
            "Poin Maks": q2["points"],
            "Poin Didapat": q2["points"] if s is True else 0,
            "Status":   "✅ Benar" if s is True else ("❌ Salah" if s is False else "⬜ Belum Dijawab"),
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    if st.button("🔄 Ulangi Assessment", type="primary"):
        for k, v in defaults.items():
            st.session_state[k] = v
        st.rerun()
