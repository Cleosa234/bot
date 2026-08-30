import os
import telebot
from groq import Groq
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# 1. Memuat variabel lingkungan
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# 2. Inisialisasi bot dan client AI
bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = Groq(api_key=GROQ_API_KEY)

# 3. System Prompt (menggunakan raw string 'r' agar karakter matematika aman)
SYSTEM_PROMPT = r"""Anda adalah asisten belajar virtual yang ramah dan fokus. 
Tugas Anda HANYA membantu pengguna memahami materi pelajaran, merangkum konsep, dan menjawab pertanyaan edukasi. 
Jika pengguna membahas topik di luar pembelajaran, Anda WAJIB menolak dengan sopan.

ATURAN PENTING DALAM MENULIS JAWABAN:
1. JANGAN PERNAH menggunakan format pemformatan matematika LaTeX seperti \( \), \[ \], \begin{cases}, atau \frac. 
2. Gunakan teks normal (plain text) dan karakter keyboard standar untuk semua rumus dan angka. 
3. Tulis pembagian dengan garis miring (contoh: 25.000 / 5 = 5.000).
4. Gunakan spasi dan baris baru yang rapi agar hitungan mudah dibaca di layar HP."""

# 4. Logika Bot Telegram
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
        bot.reply_to(message, ai_response, parse_mode="Markdown")
        
    except Exception as e:
        bot.reply_to(message, "Koneksi API bermasalah. Coba lagi nanti.")
        print(f"Error API: {e}")

# ==========================================
# 5. SERVER WEB FLASK UNTUK HOSTING RENDER
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Telegram Edukasi sedang berjalan online!"

def run_server():
    # Render secara otomatis akan memberikan port melalui environment variable
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    # Menjalankan server Flask di latar belakang (background thread)
    server_thread = Thread(target=run_server)
    server_thread.start()
    
    # Menjalankan bot Telegram
    print("Bot Telegram dan Server Web berjalan bersamaan...")
    bot.polling()
