import os
import telebot
from telebot.types import Update
from flask import Flask, request
from groq import Groq

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = Groq(api_key=GROQ_API_KEY)
app = Flask(__name__)

SYSTEM_PROMPT = r"""Anda adalah asisten belajar virtual yang ramah dan fokus. 
Tugas Anda HANYA membantu pengguna memahami materi pelajaran. Jika pengguna membahas topik di luar pembelajaran, Anda WAJIB menolak dengan sopan.

ATURAN PENTING:
1. JANGAN PERNAH menggunakan format matematika LaTeX seperti \( \), \[ \], \begin{cases}, atau \frac. 
2. Gunakan teks normal dan karakter keyboard standar. 
3. Tulis pembagian dengan garis miring.
4. Gunakan spasi yang rapi."""

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
        bot.reply_to(message, chat_completion.choices[0].message.content, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, "Koneksi API bermasalah. Coba lagi nanti.")

# 1. Jalur rahasia agar Telegram bisa mengirim pesan ke Vercel
@app.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def receive_update():
    json_string = request.get_data().decode('utf-8')
    update = Update.de_json(json_string)
    bot.process_new_updates([update])
    return 'OK', 200

# 2. Halaman utama web untuk pemicu otomatis
@app.route('/')
def index():
    host_url = request.url_root.replace("http://", "https://")
    webhook_url = f"{host_url}api/index/{TELEGRAM_TOKEN}"
    
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    return f"Sistem Bot Vercel Aktif! Webhook terhubung ke: {webhook_url}", 200