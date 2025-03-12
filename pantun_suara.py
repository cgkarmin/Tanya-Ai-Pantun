import speech_recognition as sr
import pandas as pd
import time
from gtts import gTTS
import os
from playsound import playsound

# Muat naik fail pantun yang telah dibersihkan
FILE_PATH = "Database_Pantun_Bersih.csv"

def load_data():
    """Memuatkan database pantun"""
    try:
        df = pd.read_csv(FILE_PATH)
        return df
    except FileNotFoundError:
        print("❌ Database pantun tidak ditemui!")
        return None

def cari_pantun(kata_kunci, df):
    """Mencari pantun berdasarkan kata kunci dalam semua lajur"""
    kata_kunci = kata_kunci.lower()
    hasil = df[df.apply(lambda row: row.astype(str).str.contains(kata_kunci, case=False, na=False).any(), axis=1)]
    return hasil

def bercakap(teks):
    """Menggunakan gTTS untuk menukar teks kepada audio dan memainkan suara"""
    tts = gTTS(text=teks, lang='ms')
    audio_file = "pantun_audio.mp3"
    tts.save(audio_file)
    playsound(audio_file)
    os.remove(audio_file)

def dengar_suara():
    """Mendengar suara pengguna dan menukar kepada teks"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Sila bercakap...")
        try:
            audio = recognizer.listen(source, timeout=5)
            kata_kunci = recognizer.recognize_google(audio, language='ms')
            print(f"👤 Anda bertanya: {kata_kunci}")
            return kata_kunci.lower()
        except sr.UnknownValueError:
            print("❌ Maaf, saya tidak dapat mendengar dengan jelas.")
            return None
        except sr.RequestError:
            print("❌ Ralat sistem suara! Sila cuba semula.")
            return None

# Muat data pantun
df = load_data()
if df is None:
    exit()

# Mula sesi interaktif
while True:
    kata_kunci = dengar_suara()
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

                print(f"\n📜 **Pantun:**\n{pantun_tersusun}")
                print(f"✍ **Pemantun:** {pemantun}")
                print(f"🎭 **Tema:** {tema}")
                print(f"📂 **Jenis:** {jenis}")
                print(f"⭐ **Markah:** {markah}")

                # Mainkan suara
                print("🔊 Membaca pantun...")
                start_time = time.time()
                bercakap(pantun_tersusun)
                elapsed_time = time.time() - start_time
                print(f"✅ Audio siap dalam {elapsed_time:.2f} saat.")
        else:
            print("❌ Tiada pantun ditemui. Sila cuba kata kunci lain.")

    # Tanya sama ada mahu meneruskan atau keluar
    lagi = input("\n🔄 Mahu bertanya lagi? (y/n): ").strip().lower()
    if lagi != 'y':
        print("🚪 Keluar dari program. Terima kasih!")
        break
