import streamlit as st
import pandas as pd
import pygame
import time
from gtts import gTTS
import os

# Muat naik fail pantun yang telah dibersihkan
FILE_PATH = "Database_Pantun_Bersih.csv"

def load_data():
    """Memuatkan database pantun"""
    try:
        df = pd.read_csv(FILE_PATH)
        return df
    except FileNotFoundError:
        st.error("❌ Database pantun tidak ditemui!")
        return None

def cari_pantun(kata_kunci, df):
    """Mencari pantun berdasarkan kata kunci dalam semua lajur"""
    kata_kunci = kata_kunci.lower()
    hasil = df[df.apply(lambda row: row.astype(str).str.contains(kata_kunci, case=False, na=False).any(), axis=1)]
    return hasil

def bercakap(teks):
    """Menggunakan gTTS untuk menukar teks kepada audio dan memainkan suara"""
    tts = gTTS(text=teks, lang='ms')
    tts.save("pantun_audio.mp3")
    pygame.mixer.init()
    pygame.mixer.music.load("pantun_audio.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(1)
    pygame.mixer.quit()
    os.remove("pantun_audio.mp3")

# Streamlit UI
st.title("📜 Tanya AI Pantun")
st.write("Masukkan kata kunci untuk mencari pantun berdasarkan tema, jenis, atau isi pantun.")

df = load_data()
if df is not None:
    kata_kunci = st.text_input("🔍 Masukkan kata kunci pantun:")
    if st.button("Cari Pantun") and kata_kunci:
        hasil_pantun = cari_pantun(kata_kunci, df)
        if not hasil_pantun.empty:
            for index, row in hasil_pantun.iterrows():
                pantun = row['Pantun'].strip().replace("\\n", "\n")
                baris = pantun.split("\n")
                if len(baris) >= 4:
                    pantun_tersusun = "\n".join(baris[:4])
                else:
                    pantun_tersusun =AV pantun
                
                pemantun = row['Pemantun'] if 'Pemantun' in row else 'Tidak diketahui'
                tema = row['Tema'] if 'Tema' in row else 'Tidak diketahui'
                jenis = row['Jenis'] if 'Jenis' in row else 'Tidak diketahui'
                markah = row['Markah'] if 'Markah' in row else 'Tidak diketahui'
                
                st.write(f"**Pantun:**\n{pantun_tersusun}")
                st.write(f"**Pemantun:** {pemantun}")
                st.write(f"**Tema:** {tema}")
                st.write(f"**Jenis:** {jenis}")
                st.write(f"**Markah:** {markah}")
                
                if st.button(f"🔊 Dengar Pantun {index}", key=index):
                    bercakap(pantun_tersusun)
        else:
            st.warning("❌ Tiada pantun ditemui. Sila cuba kata kunci lain.")
