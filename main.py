import os
import threading
import logging
import asyncio
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import google.generativeai as genai

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ЧИТАЕМ ПЕРЕМЕННЫЕ
TOKEN = os.environ.get("TELEGRAM_TOKEN")
AI_KEY = os.environ.get("GEMINI_KEY")

app = Flask(__name__)
@app.route('/')
def home(): return "Бот в эфире"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"!!! ПРИШЛО СООБЩЕНИЕ: {update.message.text}")
    try:
        genai.configure(api_key=AI_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(update.message.text)
        await update.message.reply_text(response.text)
    except Exception as e:
        logger.error(f"Ошибка ИИ: {e}")

async def start_bot():
    if not TOKEN:
        logger.error("!!! ОШИБКА: Переменная TELEGRAM_TOKEN не найдена в Render!")
        return

    logger.info(f"Пробую запустить бота с токеном: {TOKEN[:5]}***")
    try:
        application = ApplicationBuilder().token(TOKEN).build()
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        
        await application.initialize()
        await application.start()
        logger.info("!!! БОТ УСПЕШНО ПОДКЛЮЧИЛСЯ К TELEGRAM")
        await application.updater.start_polling(drop_pending_updates=True)
    except Exception as e:
        logger.error(f"!!! ОШИБКА ПОДКЛЮЧЕНИЯ: {e}")

def run_async():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_bot())

if __name__ == '__main__':
    threading.Thread(target=run_async, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
