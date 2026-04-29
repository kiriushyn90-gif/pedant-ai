import os
import threading
import logging
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# КЛЮЧИ
TOKEN = "8740450028:AAGsZzWH-LBfKZnv8x9bZaGtckB-_U1Th5o"
AI_KEY = "AIzaSyBQW9qLIbiuEzPKjLUd97inT2dWv-g_xFg"

# Настройка ИИ
genai.configure(api_key=AI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Веб-сервер для Render
app = Flask(__name__)
@app.route('/')
def home():
    return "OK"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    try:
        response = model.generate_content(update.message.text)
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text("Я призадумался...")

def run_bot():
    # Запуск бота выносим в функцию
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    # 1. Сначала запускаем бота в фоновом потоке
    threading.Thread(target=run_bot, daemon=True).start()
    
    # 2. А основной поток отдаем Flask, чтобы Render сразу увидел порт 10000
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
