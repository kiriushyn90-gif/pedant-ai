import os
import asyncio
import logging
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import google.generativeai as genai
import threading

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TELEGRAM_TOKEN")
AI_KEY = os.environ.get("GEMINI_KEY")

# Настройка ИИ сразу
if AI_KEY:
    genai.configure(api_key=AI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"!!! СООБЩЕНИЕ: {update.message.text}")
    try:
        response = model.generate_content(update.message.text)
        await update.message.reply_text(response.text)
    except Exception as e:
        logger.error(f"Ошибка: {e}")

async def run_bot():
    if not TOKEN:
        logger.error("!!! ТОКЕН НЕ НАЙДЕН")
        return
    
    logger.info("!!! ПОДКЛЮЧАЮСЬ К ТЕЛЕГРАМ...")
    app_tg = ApplicationBuilder().token(TOKEN).build()
    app_tg.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    await app_tg.initialize()
    await app_tg.start()
    await app_tg.updater.start_polling(drop_pending_updates=True)
    logger.info("!!! БОТ В СЕТИ !!!")

# Веб-сервер
app = Flask(__name__)
@app.route('/')
def health(): return "OK"

def start_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    # Сначала запускаем Flask в фоне
    threading.Thread(target=start_flask, daemon=True).start()
    
    # Затем запускаем бота в основном потоке
    asyncio.run(run_bot())
    
