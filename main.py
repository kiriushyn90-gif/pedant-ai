import os
import logging
import asyncio
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import google.generativeai as genai
import threading

# Настройка логов, чтобы мы видели всё в Render
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.environ.get("TELEGRAM_TOKEN")
AI_KEY = os.environ.get("GEMINI_KEY")

# Настройка Gemini
genai.configure(api_key=AI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Простейший веб-сервер для Render
app = Flask(__name__)
@app.route('/')
def health(): return "Бот работает"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    try:
        response = model.generate_content(update.message.text)
        await update.message.reply_text(response.text)
    except Exception as e:
        logging.error(f"Ошибка ИИ: {e}")

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def main():
    # Создаем приложение современным способом (v20+)
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("--- СТАРТ ПОЛЛИНГА ---")
    application.run_polling()

if __name__ == '__main__':
    # Запускаем Flask в отдельном потоке
    threading.Thread(target=run_flask, daemon=True).start()
    # Запускаем бота
    main()
    
