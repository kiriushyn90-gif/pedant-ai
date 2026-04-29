import os
import threading
import asyncio
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# КЛЮЧИ (Вставь свои аккуратно!)
TOKEN = "8740450028:AAGsZzWH-LBfKZnv8x9bZaGtckB-_U1Th5o"
AI_KEY = "AIzaSyBQW9qLIbiuEzPKjLUd97inT2dWv-g_xFg"

# Настройка ИИ
genai.configure(api_key=AI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask(__name__)
@app.route('/')
def home():
    return "Status: Online"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    try:
        # Прямой вызов модели
        response = model.generate_content(update.message.text)
        await update.message.reply_text(response.text)
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("Я задумался, повтори вопрос!")

if __name__ == '__main__':
    # Порт для Render
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port), daemon=True).start()
    
    # Запуск бота
    print("Starting bot...")
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.run_polling(drop_pending_updates=True)
    
