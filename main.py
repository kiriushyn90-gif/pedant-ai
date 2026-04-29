import os
import asyncio
import logging
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import google.generativeai as genai

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем ключи
TOKEN = os.environ.get("TELEGRAM_TOKEN")
AI_KEY = os.environ.get("GEMINI_KEY")

app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Эта строка ДОЛЖНА появиться в логах, когда ты напишешь боту
    logger.info(f"!!! ПРИНЯТО СООБЩЕНИЕ: {update.message.text}")
    try:
        genai.configure(api_key=AI_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(update.message.text)
        await update.message.reply_text(response.text)
    except Exception as e:
        logger.error(f"Ошибка Gemini: {e}")
        await update.message.reply_text("Ошибка ИИ. Проверь ключи.")

async def start_bot():
    if not TOKEN:
        logger.error("!!! ТОКЕН НЕ НАЙДЕН В ПАНЕЛИ RENDER !!!")
        return

    logger.info("--- ПОПЫТКА ПОДКЛЮЧЕНИЯ К TELEGRAM ---")
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    logger.info("--- БОТ УСПЕШНО ПОДКЛЮЧЕН И СЛУШАЕТ ---")

def run_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_bot())
    loop.run_forever()

if __name__ == '__main__':
    threading.Thread(target=run_loop, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
