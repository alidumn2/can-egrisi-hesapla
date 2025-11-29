import streamlit as st
import sqlite3
import pandas as pd

# --- VERİTABANI İŞLEMLERİ ---
def get_db_connection():
    conn = sqlite3.connect("notlar.db")
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS dersler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ad TEXT,
            kredi INTEGER,
            ort REAL,
            sapma REAL,
            notu REAL,
            t_skor REAL,
            harf TEXT
        )
    """)
    conn.commit()
    conn.close()

def db_ekle(ad, kredi, ort, sapma, notu, t_skor, harf):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO dersler (ad, kredi, ort, sapma, notu, t_skor, harf) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (ad, kredi, ort, sapma, notu, t_skor, harf))
    conn.commit()
    conn.close()

def db_sil(id_list):
    conn = get_db_connection()
    c = conn.cursor()
    # Çoklu silme işlemi
    for d_id in id_list:
        c.execute("DELETE FROM dersler WHERE id=?", (d_id,))
    conn.commit()
    conn.close()

# --- HESAPLAMA MANTIĞI ---
def harf_notu_belirle(T, X):
    if X >= 80.0:
        if T >= 59.00: return "AA"
        elif T >= 54.00: return "BA"
        elif T >= 49.00: return "BB"
        elif T >= 44.00: return "CB"
        elif T >= 39.00: return "CC"
        elif T >= 34.00: return "DC"
        elif T >= 29.00: return "DD"
        elif T >= 24.00: return "FD"
        else: return "FF"
    elif X >= 70.01:
        if T >= 58.99: return "AA"
        elif T >= 53.99: return "BA"
        elif T >= 48.99: return "BB"
        elif T >= 43.99: return "CB"
        elif T >= 38.99: return "CC"
        elif T >= 33.99: return "DC"
        elif T >= 28.99: return "DD"
        elif T >= 23.99: return "FD"
        else: return "FF"
    elif X >= 62.51:
        if T >= 60.99: return "AA"
        elif T >= 55.99: return "BA"
        elif T >= 50.99: return "BB"
        elif T >= 45.99: return "CB"
        elif T >= 40.99: return "CC"
        elif T >= 35.99: return "DC"
        elif T >= 30.99: return "DD"
        elif T >= 25.99: return "FD"
        else: return "FF"
    elif X >= 57.51:
        if T >= 62.99: return "AA"
        elif T >= 57.99: return "BA"
        elif T >= 52.99: return "BB"
        elif T >= 47.99: return "CB"
        elif T >= 42.99: return "CC"
        elif T >= 37.99: return "DC"
        elif T >= 32.99: return "DD"
        elif T >= 27.99: return "FD"
        else: return "FF"
    elif X >= 52.51:
        if T >= 64.99: return "AA"
        elif T >= 59.99: return "BA"
        elif T >= 54.99: return "BB"
        elif T >= 49.99: return "CB"
        elif T >= 44.99: return "CC"
        elif T >= 39.99: return "DC"
        elif T >= 34.99: return "DD"
        elif T >= 29.99: return "FD"
        else: return "FF"
    elif X >= 47.51:
        if T >= 66.99: return "AA"
        elif T >= 61.99: return "BA"
        elif T >= 56.99: return "BB"
        elif T >= 51.99: return "CB"
        elif T >= 46.99: return "CC"
        elif T >= 41.99: return "DC"
        elif T >= 36.99: return "DD"
        elif T >= 31.99: return "FD"
        else: return "FF"
    elif X >= 42.51:
        if T >= 69.00: return "AA"
        elif T >= 64.00: return "BA"
        elif T >= 59.00: return "BB"
        elif T >= 54.00: return "CB"
        elif T >= 49.00: return "CC"
        elif T >= 44.00: return "DC"
        elif T >= 39.00: return "DD"
        elif T >= 34.00: return "FD"
        else: return "FF"
    else:
        if T >= 71.00: return "AA"
        elif T >= 66.00: return "BA"
        elif T >= 61.00: return "BB"
        elif T >= 56.00: return "CB"
        elif T >= 51.00: return "CC"
        elif T >= 46.00: return "DC"
        elif T >= 41.00: return "DD"
        elif T >= 36.00: return "FD"
        else: return "FF"

def harf_katsayisi_getir(harf):
    katsayilar = {"AA": 4.0, "BA": 3.5, "BB": 3.0, "CB": 2.5, "CC": 2.0, "DC": 1.5, "DD": 1.0, "FD": 0.5, "FF": 0.0}
    return katsayilar.get(harf, 0.0)

# --- WEB ARAYÜZÜ (STREAMLIT) ---
st.set_page_config(page_title="Çan Eğrisi Hesaplayıcı", page_icon="🎓", layout="wide")
init_db() # Veritabanını başlat

# Başlık
st.title("🎓 Üniversite Çan Eğrisi Hesaplayıcı")
st.markdown("Derslerini ekle, T-Skorunu otomatik hesapla ve GANO'nu gör.")

# --- SOL KENAR ÇUBUĞU (VERİ GİRİŞİ) ---
with st.sidebar:
    st.header("➕ Yeni Ders Ekle")
    with st.form("ders_ekle_form", clear_on_submit=True):
        ad = st.text_input("Ders Adı")
        kredi = st.number_input("Kredi", min_value=1, max_value=20, value=3)
        ort = st.number_input("Sınıf Ortalaması", min_value=0.0, max_value=100.0, step=0.1)
        sapma = st.number_input("Standart Sapma", min_value=0.01, max_value=50.0, value=10.0, step=0.1)
        notu = st.number_input("Senin Notun", min_value=0.0, max_value=100.0, step=0.1)
        
        submitted = st.form_submit_button("Hesapla ve Kaydet")
        
        if submitted:
            if not ad:
                st.error("Lütfen ders adı girin.")
            elif sapma == 0:
                st.error("Standart sapma 0 olamaz.")
            else:
                # Hesaplama
                t_skor = ((notu - ort) / sapma) * 10 + 50
                harf = harf_notu_belirle(t_skor, ort)
                
                # DB'ye yaz
                db_ekle(ad, kredi, ort, sapma, notu, t_skor, harf)
                st.success(f"{ad} Eklendi! Harf: {harf}")

# --- ANA EKRAN (TABLO VE SONUÇLAR) ---
conn = get_db_connection()
df = pd.read_sql_query("SELECT * FROM dersler", conn)
conn.close()

if not df.empty:
    # 1. GANO HESAPLAMA
    toplam_kredi = df['kredi'].sum()
    df['katsayi'] = df['harf'].apply(harf_katsayisi_getir)
    toplam_agirlik = (df['katsayi'] * df['kredi']).sum()
    
    gano = 0.0
    if toplam_kredi > 0:
        gano = toplam_agirlik / toplam_kredi
    
    # Metrik gösterimi
    col1, col2, col3 = st.columns(3)
    col1.metric("Toplam Ders", len(df))
    col2.metric("Toplam Kredi", toplam_kredi)
    col3.metric("Genel Ortalama (GANO)", f"{gano:.2f}")
    
    st.divider()
    
    # 2. TABLOYU GÖSTER
    st.subheader("📋 Ders Listesi")
    
    # Tabloyu düzenleyelim (görsel olarak)
    df_goster = df[['id', 'ad', 'kredi', 'ort', 'sapma', 'notu', 't_skor', 'harf']].copy()
    df_goster.columns = ['ID', 'Ders Adı', 'Kredi', 'Sınıf Ort.', 'Sapma', 'Notun', 'T-Skoru', 'Harf']
    
    st.dataframe(df_goster, use_container_width=True, hide_index=True)
    
    # 3. SİLME İŞLEMİ
    st.divider()
    with st.expander("🗑️ Ders Silme İşlemleri"):
        ders_secimi = st.multiselect(
            "Silmek istediğiniz dersleri seçin:",
            options=df['id'].tolist(),
            format_func=lambda x: df[df['id'] == x]['ad'].values[0]
        )
        
        if st.button("Seçilenleri Sil", type="primary"):
            if ders_secimi:
                db_sil(ders_secimi)
                st.rerun() # Sayfayı yenile
            else:
                st.warning("Lütfen silinecek bir ders seçin.")
else:
    st.info("Henüz hiç ders eklenmemiş. Sol menüden ders ekleyebilirsin. 👈")