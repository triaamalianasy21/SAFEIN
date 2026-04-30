import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# 1. Konfigurasi Halaman Dasar
st.set_page_config(
    page_title="SAFEIN Financial Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# 2. Fungsi Load Data (Tetap pakai main_data.csv)
@st.cache_data
def load_data():
    # --- BAGIAN INI BIAR BISA JALAN DI DEPLOYMENT ---
    # Mencari folder tempat dashboard.py berada
    base_dir = Path(__file__).parent 
    file_path = base_dir / "main_data.csv"
    # -----------------------------------------------
    
    df = pd.read_csv(file_path)
    # Konversi kolom waktu agar bisa diolah untuk tren
    df['date_time'] = pd.to_datetime(df['date_time'])
    return df

# Membungkus dalam try-except agar jika file tidak ada, dashboard tidak pecah
try:
    all_df = load_data()

    # 3. Header Dashboard
    st.title("📊 SAFEIN: Personal Finance Analysis Dashboard")
    st.markdown(f"**Nama: Tria Amalia Anasya** | Data Science Learning Path")
    st.write("Dashboard ini memvisualisasikan tren pengeluaran dan pemasukan untuk membantu pengelolaan anggaran.")

    # 4. Ringkasan Metrik Utama (Total Income, Expense, Balance)
    st.subheader("Financial Overview")
    col1, col2, col3 = st.columns(3)
    
    total_income = all_df[all_df['type'] == 'income']['amount'].sum()
    total_expense = all_df[all_df['type'] == 'expenses']['amount'].sum()
    balance = total_income - total_expense

    col1.metric("Total Pemasukan", f"{total_income:,.0f} BYN")
    col2.metric("Total Pengeluaran", f"{total_expense:,.0f} BYN", delta_color="inverse")
    col3.metric("Saldo Bersih (Balance)", f"{balance:,.0f} BYN")
    
    st.divider()

    # 5. Visualisasi 1: Tren Bulanan
    st.subheader("1. Tren Bulanan Pemasukan vs Pengeluaran 2025")
    
    # Mengelompokkan data berdasarkan bulan dan tipe
    monthly_trend = all_df.groupby(['month', 'type'])['amount'].sum().unstack().fillna(0)
    
    fig1, ax1 = plt.subplots(figsize=(12, 5))
    monthly_trend.plot(kind='line', marker='o', ax=ax1, color=['#2ecc71', '#e74c3c']) 
    ax1.set_ylabel("Jumlah (BYN)")
    ax1.set_xlabel("Bulan")
    ax1.grid(True, linestyle='--', alpha=0.6)
    st.pyplot(fig1)
    st.info("💡 Grafik ini menunjukkan pola arus kas setiap bulan untuk mengidentifikasi puncak pengeluaran.")

    # 6. Visualisasi 2: Top 5 Kategori Pengeluaran
    st.subheader("2. Top 5 Kategori Pengeluaran Terbesar")
    
    # Filter hanya data expenses
    expense_df = all_df[all_df['type'] == 'expenses']
    top_expenses = expense_df.groupby('category')['amount'].sum().sort_values(ascending=False).head(5)
    
    if not top_expenses.empty:
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        sns.barplot(x=top_expenses.values, y=top_expenses.index, palette="Reds_r", ax=ax2)
        ax2.set_xlabel("Total Pengeluaran (BYN)")
        ax2.set_ylabel("Kategori")
        st.pyplot(fig2)
    else:
        st.warning("Data pengeluaran tidak ditemukan.")

    st.divider()
    st.caption("Copyright © 2026 - SAFEIN Project (DBS Coding Camp)")

except FileNotFoundError:
    st.error("Error: File 'main_data.csv' tidak ditemukan. Pastikan file data berada di folder yang sama dengan dashboard.py.")
except Exception as e:
    st.error(f"Terjadi kesalahan sistem: {e}")
