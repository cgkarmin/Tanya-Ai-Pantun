import streamlit as st
import pandas as pd
import pygame
import time
from gtts import gTTS
import os
import speech_recognition as sr

# Muat naik fail pantun yang telah dibersihkan
FILE_PATH = "Database_Pantun_Bersih.csv"

# ✅ Pastikan fail CSV wujud sebelum membaca
def load_data():
    """Memuatkan database pantun"""
    if not os.path.exists(FILE_PATH):
        st.error("❌ Database pantun tidak ditemui!")
        return None
    
    df = pd.read_csv(FILE_PATH)
    
    if df.empty:
        st.warning("⚠ Database kosong! Sila periksa fail CSV.")
        return None
    
    return df

# ✅ Pastikan carian hanya dilakukan dalam lajur 'Pantun'
def cari_pantun(kata_kunci, df):
    """Mencari pantun berdasarkan kata kunci dalam lajur 'Pantun' sahaja"""
    kata_kunci = kata_kunci.lower()
    hasil = df[df['Pantun'].astype(str).str.contains(kata_kunci, case=False, na=False)]
    return hasil

# ✅ Pastikan audio diproses dan dimainkan
def bercakap(teks):
    """Menggunakan gTTS untuk menukar teks kepada audio dan memainkan suara"""
    pygame.mixer.init()
    tts = gTTS(text=teks, lang='ms')

    # Simpan fail audio
    tts.save("pantun_audio.mp3")

    # Paparkan tempoh pemprosesan
    start_time = time.time()

    # Mainkan audio
    pygame.mixer.music.load("pantun_audio.mp3")
    pygame.mixer.music.play()

    # Tunggu sehingga audio habis dimainkan
    while pygame.mixer.music.get_busy():
        time.sleep(1)

    # Kira tempoh masa yang diambil
    elapsed_time = time.time() - start_time
    st.write(f"✅ Audio siap dalam {elapsed_time:.2f} saat.")

    # Hapus fail audio selepas dimainkan
    pygame.mixer.quit()
    os.remove("pantun_audio.mp3")

# ✅ Pastikan sesi suara dikemas kini dengan betul
def dengar_suara():
    """Fungsi untuk menangkap input suara pengguna"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Sila bercakap...")
        try:
            audio = recognizer.listen(source, timeout=5)
            kata_kunci = recognizer.recognize_google(audio, language='ms')
            st.success(f"👤 Anda bertanya: **{kata_kunci}**")
            return kata_kunci
        except sr.UnknownValueError:
            st.warning("❌ Maaf, saya tidak dapat mendengar dengan jelas.")
            return None
        except sr.RequestError:
            st.error("❌ Ralat sistem suara! Sila cuba semula.")
            return None

# ✅ Mula program
st.title("📜 Tanya AI Pantun")
st.write("Masukkan kata kunci untuk mencari pantun berdasarkan tema, jenis, atau isi pantun.")

df = load_data()
if df is None:
    st.warning("⚠ Database tidak dimuatkan. Sila periksa fail CSV.")
    st.stop()

# 🔄 Butang Reset di bahagian atas untuk reset carian dan audio
if st.button("🔄 Reset Carian", help="Tekan untuk membersihkan carian dan audio"):
    st.session_state.kata_kunci = ""
    pygame.mixer.quit()
    pygame.mixer.init()
    st.rerun()

# ✅ Inisialisasi session_state jika belum ada
if "kata_kunci" not in st.session_state:
    st.session_state.kata_kunci = ""

# ✅ Pastikan pilihan input tidak menyebabkan paparan kosong
mode = st.radio("Pilih kaedah input:", ["Taip", "Bercakap"], key="input_mode")

if mode == "Bercakap":
    kata_kunci = dengar_suara()
    if kata_kunci:
        st.session_state.kata_kunci = kata_kunci
else:
    st.session_state.kata_kunci = st.text_input("🔍 Masukkan kata kunci pantun:", key="input_text")

# ✅ Pastikan hasil sentiasa dipaparkan, walaupun kosong
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

            st.write(f"**Pantun:**\n{pantun_tersusun}")
            st.write(f"**Pemantun:** {pemantun}")
            st.write(f"**Tema:** {tema}")
            st.write(f"**Jenis:** {jenis}")
            st.write(f"**Markah:** {markah}")

            if st.button(f"🔊 Dengar Pantun {index}", key=f"audio_{index}"):
                st.write("⏳ Menyediakan audio...")
                start_time = time.time()
                bercakap(pantun_tersusun)
                elapsed_time = time.time() - start_time
                st.write(f"✅ Audio siap dalam {elapsed_time:.2f} saat.")
    else:
        st.warning("❌ Tiada pantun ditemui. Sila cuba kata kunci lain.")
else:
    st.info("ℹ Sila masukkan kata kunci untuk mencari pantun.")
