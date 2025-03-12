import streamlit as st
import pandas as pd
import os
import time
import platform
import speech_recognition as sr

# Cuba import gTTS & pygame, jika gagal maka disable audio
try:
    from gtts import gTTS
    import pygame
    AUDIO_ENABLED = True
except ImportError:
    AUDIO_ENABLED = False  # Jika di Streamlit Cloud, audio dimatikan

# Muat naik fail pantun
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
    """Gunakan gTTS jika local, disable audio di Streamlit Cloud"""
    if AUDIO_ENABLED:
        pygame.mixer.init()
        tts = gTTS(text=teks, lang='ms')
        tts.save("pantun_audio.mp3")
        pygame.mixer.music.load("pantun_audio.mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(1)
        pygame.mixer.quit()
        os.remove("pantun_audio.mp3")
    else:
        st.warning("⚠ Audio tidak disokong dalam Streamlit Cloud.")

# UI Streamlit
st.title("📜 Tanya AI Pantun")
st.write("Masukkan kata kunci untuk mencari pantun berdasarkan tema, jenis, atau isi pantun.")

df = load_data()
if df is not None:
    kata_kunci = st.text_input("🔍 Masukkan kata kunci pantun:")

    if kata_kunci:
        hasil_pantun = cari_pantun(kata_kunci, df)
        if not hasil_pantun.empty:
            for index, row in hasil_pantun.iterrows():
                pantun = row['Pantun'].strip().replace("\\n", "\n")
                st.write(f"**Pantun:**\n{pantun}")

                if st.button(f"🔊 Dengar Pantun {index}", key=f"audio_{index}"):
                    bercakap(pantun)
        else:
            st.warning("❌ Tiada pantun ditemui.")
