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
        if df.empty:
            st.error("⚠ Database kosong! Sila periksa fail CSV.")
            return None
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

    # Paparkan proses audio sedang dimuatkan
    with st.spinner("🔊 Sedang menyediakan audio..."):
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
if st.button("🔄", help="Reset Carian"):
    reset_audio()
    st.session_state.kata_kunci = ""
    st.rerun()

df = load_data()
if df is not None:
    mode = st.radio("Pilih kaedah input:", ["Taip", "Bercakap"])

    if mode == "Bercakap":
        st.info("🎤 Sila bercakap...")
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            try:
                audio = recognizer.listen(source, timeout=5)
                st.session_state.kata_kunci = recognizer.recognize_google(audio, language='ms')
                st.success(f"👤 Anda bertanya: **{st.session_state.kata_kunci}**")
                reset_audio()  # Reset audio sebelum mencari pantun
            except sr.UnknownValueError:
                st.warning("❌ Maaf, saya tidak dapat mendengar dengan jelas.")
            except sr.RequestError:
                st.error("❌ Ralat sistem suara! Sila cuba semula.")
    else:
        st.session_state.kata_kunci = st.text_input("🔍 Masukkan kata kunci pantun:")

    if st.session_state.kata_kunci:
        hasil_pantun = cari_pantun(st.session_state.kata_kunci, df)
        if not hasil_pantun.empty:
            for index, row in hasil_pantun.iterrows():
                pantun = row['Pantun'].strip().replace("\\n", "\n")
                baris = pantun.split("\n")
                pantun_tersusun = "\n".join(baris[:4]) if len(baris) >= 4 else pantun
                pemantun = row.get('Pemantun', 'Tidak diketahui')
                tema = row.get('Tema', 'Tidak diketahui')
                jenis = row.get('Jenis', 'Tidak diketahui')
                markah = row.get('Markah', 'Tidak diketahui')

                # Paparan pantun dalam format tersusun
                st.write(f"**Pantun:**\n{pantun_tersusun}")
                st.write(f"**Pemantun:** {pemantun}")
                st.write(f"**Tema:** {tema}")
                st.write(f"**Jenis:** {jenis}")
                st.write(f"**Markah:** {markah}")

                # Butang untuk memainkan audio pantun
                if st.button(f"🔊 Dengar Pantun {index}", key=f"audio_{index}"):
                    st.write("⏳ Menyediakan audio...")
                    start_time = time.time()
                    bercakap(pantun_tersusun)
                    elapsed_time = time.time() - start_time
                    st.write(f"✅ Audio siap dalam {elapsed_time:.2f} saat.")
        else:
            st.warning("❌ Tiada pantun ditemui. Sila cuba kata kunci lain.")
