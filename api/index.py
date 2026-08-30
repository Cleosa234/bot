import os
import telebot
from telebot.types import Update
from flask import Flask, request
from groq import Groq

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# KUNCI PERBAIKAN ADA DI SINI: tambahkan threaded=False
bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
client = Groq(api_key=GROQ_API_KEY)
app = Flask(__name__)

SYSTEM_PROMPT = r"""Anda adalah asisten belajar virtual yang ramah dan fokus. 
Jawab hanya hal edukasi. 
PENTING: Jangan gunakan format LaTeX seperti \( atau \[. Gunakan teks normal dan spasi yang rapi."""

@bot.message_handler(commands=['start', 'help'])
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
        print(f"Error AI: {e}")

@app.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def receive_update():
    json_string = request.get_data().decode('utf-8')
    update = Update.de_json(json_string)
    bot.process_new_updates([update])
    return 'OK', 200

@app.route('/')
def index():
    host_url = request.url_root.replace("http://", "https://")
    webhook_url = f"{host_url}{TELEGRAM_TOKEN}"
    
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    return f"Sistem Bot Vercel Aktif! Webhook terhubung ke: {webhook_url}", 200
