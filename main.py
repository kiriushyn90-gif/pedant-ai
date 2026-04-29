import os
import threading
import logging
import asyncio
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Получение ключей
TOKEN = os.environ.get("TELEGRAM_TOKEN")
AI_KEY = os.environ.get("GEMINI_KEY")

# Настройка Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает и готов к общению!"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    
    logger.info(f"Входящее сообщение: {update.message.text}")
    try:
        genai.configure(api_key=AI_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(update.message.text)
        await update.message.reply_text(response.text)
    except Exception as e:
        logger.error(f"Ошибка Gemini: {e}")
        await update.message.reply_text("Извини, нейросеть призадумалась. Попробуй позже.")

async def start_telegram():
    # НОВЫЙ СПОСОБ ЗАПУСКА ДЛЯ ВЕРСИИ 20+
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    await application.initialize()
    await application.start()
    logger.info("!!! TELEGRAM БОТ ЗАПУЩЕН УСПЕШНО")
    await application.updater.start_polling(drop_pending_updates=True)

def run_bot_in_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_telegram())
    loop.run_forever()

if __name__ == '__main__':
    # Запускаем телеграм в отдельном потоке
    threading.Thread(target=run_bot_in_thread, daemon=True).start()
    
    # Запускаем Flask
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
