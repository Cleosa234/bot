import os
import telebot
from groq import Groq
from dotenv import load_dotenv

# 1. Memuat sistem rahasia dari file .env
load_dotenv()

# 2. Mengambil API Key yang sudah dipisahkan
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Inisialisasi klien
bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = Groq(api_key=GROQ_API_KEY)
SYSTEM_PROMPT = """Anda adalah asisten belajar virtual yang ramah dan fokus. 
Tugas Anda HANYA membantu pengguna memahami materi pelajaran, merangkum konsep, dan menjawab pertanyaan edukasi. 
Jika pengguna membahas topik di luar pembelajaran, Anda WAJIB menolak dengan sopan.

ATURAN PENTING DALAM MENULIS JAWABAN:
1. JANGAN PERNAH menggunakan format pemformatan matematika LaTeX seperti \( \), \[ \], \begin{cases}, atau \frac. 
2. Gunakan teks normal (plain text) dan karakter keyboard standar untuk semua rumus dan angka. 
3. Tulis pembagian dengan garis miring (contoh: 25.000 / 5 = 5.000).
4. Gunakan spasi dan baris baru yang rapi agar hitungan mudah dibaca di layar HP."""

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Halo! Asisten belajar siap membantu.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message.text}
            ],
            model="openai/gpt-oss-120b",
            temperature=0.5,
            max_tokens=1024
        )
        
        ai_response = chat_completion.choices[0].message.content
        bot.reply_to(message, ai_response)
        
    except Exception as e:
        bot.reply_to(message, "Koneksi API bermasalah. Coba lagi nanti.")
        print(f"Error API: {e}")

print("Sistem Bot dan API berhasil dipisahkan dan sedang berjalan...")
bot.polling()