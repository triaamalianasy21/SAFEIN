import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# 1. Konfigurasi Halaman Utama
st.set_page_config(page_title="SAFEIN Analysis", layout="wide")

@st.cache_data
def load_data():
    # Menggunakan Pathlib supaya server Streamlit Cloud nggak bingung nyari file
    base_dir = Path(__file__).parent
    file_path = base_dir / "main_data.csv"
    
    if not file_path.exists():
        st.error(f"File 'main_data.csv' tidak ditemukan di {file_path}")
        st.stop()
        
    df = pd.read_csv(file_path)
    df['date_time'] = pd.to_datetime(df['date_time'])
    return df

try:
    all_df = load_data()

    # --- SIDEBAR (NAVIGASI SAJA) ---
    st.sidebar.title("🛡️ SAFEIN Analysis")
    menu = st.sidebar.radio(
        "Pilih Analisis:",
        [
            "Overview Dashboard",
            "Pertanyaan 1: Tren Bulanan",
            "Pertanyaan 2: Top 5 Kategori",
            "Pertanyaan 3: Rasio Keuangan",
            "Pertanyaan 4: Deteksi Defisit",
            "Pertanyaan 5: Pola Kuartal",
            "Pertanyaan 6: Analisis Pinjaman (Loan)"
        ]
    )
    st.sidebar.divider()
    st.sidebar.caption("SAFEIN Capstone Project - 2026")

    # --- MAIN CONTENT ---
    st.title(f"📊 {menu}")

    # --- FILTER DI ATAS GRAFIK ---
    selected_types = st.multiselect(
        "Filter Tipe Transaksi:",
        options=['income', 'expenses'],
        default=['income', 'expenses'],
        key="main_filter"
    )

    filtered_df = all_df[all_df['type'].isin(selected_types)]
    income_df = filtered_df[filtered_df['type'] == 'income']
    expenses_df = filtered_df[filtered_df['type'] == 'expenses']

    st.divider()

    if not selected_types:
        st.warning("⚠️ Pilih setidaknya satu tipe agar grafik muncul!")
    
    else:
        if menu == "Overview Dashboard":
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Income", f"{income_df['amount'].sum():,.0f} BYN")
            col2.metric("Total Expenses", f"{expenses_df['amount'].sum():,.0f} BYN")
            col3.metric("Net Balance", f"{(income_df['amount'].sum() - expenses_df['amount'].sum()):,.0f} BYN")

        elif menu == "Pertanyaan 1: Tren Bulanan":
            monthly = filtered_df.groupby(['month', 'type'])['amount'].sum().unstack().fillna(0)
            fig, ax = plt.subplots(figsize=(12, 6))
            
            if 'income' in monthly.columns:
                ax.plot(monthly.index, monthly['income'], label='Pemasukan (Income)', marker='o', color='green', linewidth=2)
            if 'expenses' in monthly.columns:
                ax.plot(monthly.index, monthly['expenses'], label='Pengeluaran (Expenses)', marker='o', color='red', linewidth=2)
                if 'income' in monthly.columns:
                    ax.fill_between(monthly.index, monthly['income'], monthly['expenses'], color='gray', alpha=0.1)
                
                ax.annotate('Kondisi Defisit (Risiko)', xy=(3, 3272), xytext=(4, 3800),
                             arrowprops=dict(facecolor='black', shrink=0.05), color='red', fontweight='bold')
            
            ax.set_xticks(range(1, 13))
            ax.set_ylabel("Total Nominal (BYN)")
            ax.legend()
            ax.grid(True, linestyle='--', alpha=0.6)
            st.pyplot(fig)

        elif menu == "Pertanyaan 2: Top 5 Kategori":
            top_5 = expenses_df.groupby("category")["amount"].sum().sort_values(ascending=False).head(5)
            if not top_5.empty:
                fig, ax = plt.subplots(figsize=(10, 6))
                top_5.plot(kind='barh', color='salmon', ax=ax)
                for i, v in enumerate(top_5):
                    ax.text(v + 20, i, f"{v:,.0f} BYN", va='center', fontweight='bold')
                ax.invert_yaxis()
                st.pyplot(fig)
            else:
                st.info("Pastikan 'expenses' terpilih untuk melihat data ini.")

        elif menu == "Pertanyaan 3: Rasio Keuangan":
            t_exp = expenses_df['amount'].sum()
            t_inc = income_df['amount'].sum()
            if t_inc > 0:
                fig, ax = plt.subplots(figsize=(7, 7))
                ax.pie([t_exp, t_inc - t_exp], labels=['Total Pengeluaran', 'Sisa Saldo (Surplus)'], 
                        autopct='%1.1f%%', colors=['#ff9999','#66b3ff'], startangle=140, explode=(0.05, 0))
                st.pyplot(fig)

        elif menu == "Pertanyaan 4: Deteksi Defisit":
            m_full = all_df.groupby(['month', 'type'])['amount'].sum().unstack().fillna(0)
            m_full['net'] = m_full['income'] - m_full['expenses']
            colors = ['green' if x >= 0 else 'red' for x in m_full['net']]
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.bar(m_full.index, m_full['net'], color=colors)
            ax.axhline(0, color='black', linewidth=1)
            ax.set_xticks(range(1, 13))
            st.pyplot(fig)

        elif menu == "Pertanyaan 5: Pola Kuartal":
            exp_q = expenses_df.copy()
            exp_q['quarter'] = exp_q['month'].apply(lambda x: f'Q{(x-1)//3 + 1}')
            q_data = exp_q.groupby('quarter')['amount'].sum()
            if not q_data.empty:
                fig, ax = plt.subplots()
                q_data.plot(kind='bar', color='skyblue', edgecolor='navy', ax=ax)
                plt.xticks(rotation=0)
                st.pyplot(fig)

        elif menu == "Pertanyaan 6: Analisis Pinjaman (Loan)":
            cat_data = expenses_df.groupby('category')['amount'].sum().sort_values(ascending=False)
            if not cat_data.empty:
                colors = ['red' if x == 'Loan given' else 'lightgrey' for x in cat_data.index]
                fig, ax = plt.subplots(figsize=(12, 6))
                cat_data.plot(kind='bar', color=colors, ax=ax)
                plt.xticks(rotation=45, ha='right')
                st.pyplot(fig)

except Exception as e:
    st.error(f"Gagal memuat file: {e}")
