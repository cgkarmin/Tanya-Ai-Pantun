import streamlit as st
import pandas as pd
import pygame
import time
from gtts import gTTS
import os
import speech_recognition as sr

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
    pygame.mixer.init()
    tts = gTTS(text=teks, lang='ms')
    tts.save("pantun_audio.mp3")
    pygame.mixer.music.load("pantun_audio.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(1)
    pygame.mixer.quit()
    os.remove("pantun_audio.mp3")

def reset_audio():
    """Reset pygame mixer"""
    pygame.mixer.quit()
    pygame.mixer.init()

# Streamlit UI
st.title("📜 Tanya AI Pantun")
st.write("Masukkan kata kunci untuk mencari pantun berdasarkan tema, jenis, atau isi pantun.")

# Butang Reset di bahagian atas untuk reset carian dan audio
col1, col2 = st.columns([0.9, 0.1])
with col2:
    if st.button("🔄", help="Reset Carian"):
        reset_audio()
        st.rerun()  # Gantikan experimental_rerun dengan st.rerun()

df = load_data()
if df is not None:
    mode = st.radio("Pilih kaedah input:", ["Taip", "Bercakap"])

    if mode == "Bercakap":
        st.info("🎤 Sila bercakap...")
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            try:
                audio = recognizer.listen(source, timeout=5)
                kata_kunci = recognizer.recognize_google(audio, language='ms')
                st.success(f"👤 Anda bertanya: **{kata_kunci}**")
            except sr.UnknownValueError:
                st.warning("❌ Maaf, saya tidak dapat mendengar dengan jelas.")
                kata_kunci = ""
            except sr.RequestError:
                st.error("❌ Ralat sistem suara! Sila cuba semula.")
                kata_kunci = ""
    else:
        kata_kunci = st.text_input("🔍 Masukkan kata kunci pantun:")

    if kata_kunci:
        hasil_pantun = cari_pantun(kata_kunci, df)
        if not hasil_pantun.empty:
            for index, row in hasil_pantun.iterrows():
                pantun = row['Pantun'].strip().replace("\\n", "\n")
                baris = pantun.split("\n")
                pantun_tersusun = "\n".join(baris[:4]) if len(baris) >= 4 else pantun
                pemantun = row.get('Pemantun', 'Tidak diketahui')
                tema = row.get('Tema', 'Tidak diketahui')
                jenis = row.get('Jenis', 'Tidak diketahui')
                markah = row.get('Markah', 'Tidak diketahui')

                with st.container():
                    st.write(f"**Pantun:**\n{pantun_tersusun}")
                    st.write(f"**Pemantun:** {pemantun}")
                    st.write(f"**Tema:** {tema}")
                    st.write(f"**Jenis:** {jenis}")
                    st.write(f"**Markah:** {markah}")

                    if st.button(f"🔊 Dengar Pantun {index}", key=f"audio_{index}"):
                        bercakap(pantun_tersusun)
                        reset_audio()  # Reset audio selepas memainkan pantun

        else:
            st.warning("❌ Tiada pantun ditemui. Sila cuba kata kunci lain.")
